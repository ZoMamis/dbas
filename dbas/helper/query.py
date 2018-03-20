"""
Provides helping function for database querys.

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de>
"""

import transaction
from pyshorteners import Shorteners, Shortener
from pyshorteners.exceptions import ShorteningErrorException
from requests.exceptions import ReadTimeout, ConnectionError
from typing import Union
from urllib3.exceptions import NewConnectionError

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, Statement, User, TextVersion, RevokedContent, \
    RevokedContentHistory, MarkedArgument, MarkedStatement, Language
from dbas.handler.history import get_bubble_from_reaction_step, get_splitted_history
from dbas.helper.dictionary.bubbles import get_user_bubble_text_for_justify_statement
from dbas.helper.relation import get_rebuts_for_argument_uid, get_undermines_for_argument_uid, \
    get_undercuts_for_argument_uid, get_supports_for_argument_uid
from dbas.lib import pretty_print_options, get_all_arguments_by_statement, nick_of_anonymous_user
from dbas.logger import logger
from dbas.strings.keywords import Keywords as _
from dbas.strings.translator import Translator


def mark_statement_or_argument(stmt_or_arg: Union[Statement, Argument], step, is_supportive, should_mark, history,
                               ui_loc, db_user) -> dict:
    """
    Marks statement or argument as current users opinion and returns status about the action

    :param uid: ID of statement or argument
    :param step: kind of step in current discussion
    :param is_supportive: Boolean if the mark is supportive
    :param should_mark: Boolean if it should be (un-)marked
    :param history: Users history
    :param ui_loc: Current language
    :param db_user: User
    :rtype: dict
    :return: Dictionary with new text for the current bubble, where the user marked her opinion
    """
    _t = Translator(ui_loc)
    prepared_dict = __mark_or_unmark_it(stmt_or_arg, should_mark, db_user, _t)
    prepared_dict['text'] = __get_text_for_justification_or_reaction_bubble(stmt_or_arg, is_supportive, db_user, step,
                                                                            history, _t)
    return prepared_dict


def __mark_or_unmark_it(stmt_or_arg: Union[Statement, Argument], should_mark, db_user, _t):
    """
    Marks or unmark an argument/statement, which represents the users opinion

    :param stmt_or_arg: Statement.uid / Argument.uid
    :param should_mark: Boolean
    :param db_user: User
    :param _t: Translator
    :return: String, String
    """
    logger('QueryHelper', '{} {}'.format(stmt_or_arg.uid, db_user.nickname))

    is_argument = isinstance(stmt_or_arg, Argument)
    table = MarkedArgument if is_argument else MarkedStatement
    column = MarkedArgument.argument_uid if is_argument else MarkedStatement.statement_uid

    if should_mark:
        db_el = DBDiscussionSession.query(table).filter(column == stmt_or_arg.uid).first()
        logger('QueryHelper', 'Element is present{}'.format(' now' if db_el else ''))
        if not db_el:
            new_el = MarkedArgument(argument=stmt_or_arg.uid, user=db_user.uid) if is_argument else MarkedStatement(
                statement=stmt_or_arg.uid,
                user=db_user.uid)
            DBDiscussionSession.add(new_el)
    else:
        logger('QueryHelper', 'Element is deleted')
        DBDiscussionSession.query(table).filter(column == stmt_or_arg.uid).delete()

    DBDiscussionSession.flush()
    transaction.commit()

    return {'success': _t.get(_.opinionSaved), 'error': ''}


def set_user_language(db_user: User, ui_locales) -> dict:
    """
    Changes the users language of the web frontend

    :param db_user: User
    :param ui_locales: current ui_locales
    :rtype: dict
    :return: prepared collection with status information
    """
    _tn = Translator(ui_locales)

    db_settings = db_user.settings
    db_language = DBDiscussionSession.query(Language).filter_by(ui_locales=ui_locales).first()

    if not db_language:
        return {'error': _tn.get(_.internalError), 'ui_locales': ui_locales, 'current_lang': ''}

    current_lang = db_language.name
    db_settings.set_lang_uid(db_language.uid)
    transaction.commit()

    return {'error': '', 'ui_locales': ui_locales, 'current_lang': current_lang}


def __get_text_for_justification_or_reaction_bubble(stmt_or_arg: Union[Statement, Argument], is_supportive, db_user,
                                                    step, history, _tn):
    """
    Returns text for an justification or reaction bubble of the user

    :param stmt_or_arg: Argument.uid / Statement.uid
    :param is_supportive: Boolean
    :param db_user: User
    :param step: String
    :param history: String
    :param _tn: Translator
    :return: String
    """
    if isinstance(stmt_or_arg, Argument):
        splitted_history = get_splitted_history(history)
        bubbles = get_bubble_from_reaction_step(step, db_user, _tn.get_lang(), splitted_history, '', color_steps=True)
        text = bubbles[0]['message'] if bubbles else ''
    else:
        text, tmp = get_user_bubble_text_for_justify_statement(stmt_or_arg.uid, db_user, is_supportive, _tn)
        text = pretty_print_options(text)

    return text


def __get_attack_or_support_for_justification_of_argument_uid(argument_uid, is_supportive):
    """
    Returns attacks or support for the reaction on an argument

    :param argument_uid: Argument.uid
    :param is_supportive: Boolean
    :return: [dict()]
    """
    return_array = []
    logger('QueryHelper', 'db_undercut against Argument.argument_uid==' + str(argument_uid))
    db_related_arguments = DBDiscussionSession.query(Argument).filter(Argument.is_supportive == is_supportive,
                                                                      Argument.argument_uid == argument_uid).all()
    given_relations = set()
    index = 0

    if not db_related_arguments:
        return None

    for relation in db_related_arguments:
        if relation.premisesgroup_uid not in given_relations:
            given_relations.add(relation.premisesgroup_uid)
            tmp_dict = dict()
            tmp_dict['id'] = relation.uid
            tmp_dict['text'] = relation.get_premisegroup_text()
            return_array.append(tmp_dict)
            index += 1
    return return_array


def revoke_author_of_statement_content(statement, db_user):
    """
    Revokes the statement - e.g. the user is not the author anymore

    :param statement: Statement
    :param db_user: User
    :return:
    """
    logger('QueryHelper', str(statement.uid))

    # get element, which should be revoked
    db_element = __revoke_statement(db_user, statement)
    DBDiscussionSession.add(RevokedContent(db_user.uid, statement=db_element.uid))
    DBDiscussionSession.flush()
    transaction.commit()
    return True


def revoke_author_of_argument_content(argument, db_user):
    """
    Revokes the argument - e.g. the user is not the author anymore

    :param argument: Argument
    :param db_user: User
    :return:
    """
    logger('QueryHelper', str(argument.uid))

    # get element, which should be revoked
    db_element = __revoke_argument(db_user, argument)
    DBDiscussionSession.add(RevokedContent(db_user.uid, argument=db_element.uid))
    DBDiscussionSession.flush()
    transaction.commit()
    return True


def __revoke_statement(db_user, db_statement):
    """
    Revokes the user as author of the statement

    :param db_user: User
    :param db_statement: Statement
    :return: Statement, Boolean, String
    """
    logger('QueryHelper', 'Statement {} will be revoked (old author {})'.format(db_statement.uid, db_user.uid) + ')')
    __remove_user_from_arguments_with_statement(db_statement, db_user)

    db_anonymous = DBDiscussionSession.query(User).filter_by(nickname=nick_of_anonymous_user).first()
    logger('QueryHelper',
           'Statement {} will get a new author {} (old author {})'.format(db_statement.uid, db_anonymous.uid,
                                                                          db_user.uid))
    db_statement.author_uid = db_anonymous.uid
    __transfer_textversion_to_new_author(db_statement.uid, db_user.uid, db_anonymous.uid)

    DBDiscussionSession.add(db_statement)
    DBDiscussionSession.flush()
    transaction.commit()

    return db_statement


def __revoke_argument(db_user, db_argument):
    """
    Revokes the user as author of the argument

    :param db_user: User.uid
    :param argument_uid: Argument.uid
    :return: Argument, Boolean, String
    """
    # does the argument has any attack or supports?
    relations = [get_undermines_for_argument_uid(db_argument.uid),
                 get_supports_for_argument_uid(db_argument.uid),
                 get_undercuts_for_argument_uid(db_argument.uid),
                 get_rebuts_for_argument_uid(db_argument.uid)]
    is_involved = sum([len(rel) if rel else 0 for rel in relations]) > 0

    if is_involved:
        logger('QueryHelper', 'Author of argument {} changed from {} to anonymous'.format(db_argument.uid, db_user.uid))
        db_new_author = DBDiscussionSession.query(User).filter_by(nickname=nick_of_anonymous_user).first()
        db_argument.author_uid = db_new_author.uid
    else:
        logger('QueryHelper', 'Disabling argument {}'.format(db_argument.uid))
        db_argument.set_disable(True)

    DBDiscussionSession.add(db_argument)
    DBDiscussionSession.flush()
    transaction.commit()

    return db_argument


def __disable_textversions(statement_uid, author_uid):
    """
    Disables the textversions of the given statement

    :param statement_uid: Statement.uid
    :param author_uid: User.uid
    :return: None
    """
    # TODO #432
    db_textversion = DBDiscussionSession.query(TextVersion).filter(TextVersion.statement_uid == statement_uid,
                                                                   TextVersion.author_uid == author_uid).all()
    for textversion in db_textversion:
        logger('QueryHelper', str(textversion.uid))
        textversion.set_disable(True)
        DBDiscussionSession.add(textversion)

    DBDiscussionSession.flush()
    transaction.commit()


def __transfer_textversion_to_new_author(statement_uid, old_author_uid, new_author_uid):
    """
    Sets a new author for the given textversion and creates a row in RevokedContentHistory

    :param statement_uid: Statement.uid
    :param old_author_uid: User.uid
    :param new_author_uid: User.uid
    :return: Boolean
    """
    logger('QueryHelper',
           'Textversion of {} will change author from {} to {}'.format(statement_uid, old_author_uid, new_author_uid))
    # TODO #432
    db_textversion = DBDiscussionSession.query(TextVersion).filter(TextVersion.statement_uid == statement_uid,
                                                                   TextVersion.author_uid == old_author_uid).all()
    if not db_textversion:
        return False

    for textversion in db_textversion:
        textversion.author_uid = new_author_uid
        DBDiscussionSession.add(textversion)
        DBDiscussionSession.add(RevokedContentHistory(old_author_uid, new_author_uid, textversion_uid=textversion.uid))
        DBDiscussionSession.flush()
        transaction.commit()

    return True


def __remove_user_from_arguments_with_statement(db_statement, db_user):
    """
    Calls revoke_content(...) for all arguments, where the Statement.uid is used

    :param db_statement: Statement
    :param db_user: User
    :return: None
    """
    logger('QueryHelper', '{} with user{}'.format(db_statement.uid, db_user.uid))
    db_arguments = get_all_arguments_by_statement(db_statement.uid, True)
    for arg in db_arguments:
        if arg.author_uid == db_user.uid:
            revoke_author_of_argument_content(arg, db_user)


def get_default_locale_name(registry):
    return registry.settings.get('pyramid.default_locale_name', 'en')


def get_short_url(url) -> dict:
    """
    Shortens the url via external service.

    :param url: Url as string, which should be shortened
    :rtype: dict
    :return: dictionary with the url, services name and the url of the service or an error
    """
    service = Shorteners.TINYURL
    service_text = service
    service_url = 'http://tinyurl.com/'
    short_url = ''
    try:
        short_url = format(Shortener(service).short(url))
    except (ReadTimeout, ConnectionError, NewConnectionError, ShorteningErrorException) as e:
        logger('getter', repr(e), error=True)
        service_text = Translator('en').get(_.serviceNotAvailable)

    return {
        'url': short_url,
        'service': service,
        'service_url': service_url,
        'service_text': service_text,
    }
