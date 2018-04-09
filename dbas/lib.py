"""
Common, pure functions used by the D-BAS.


.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""
import hashlib
import locale
import os
import re
import warnings
from collections import defaultdict
from datetime import datetime
from enum import Enum, auto
from html import escape, unescape
from typing import List
from urllib import parse
from uuid import uuid4

from sqlalchemy import func

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, Premise, Statement, TextVersion, Issue, User, Settings, \
    ClickedArgument, ClickedStatement, MarkedArgument, MarkedStatement, PremiseGroup
from dbas.logger import logger
from dbas.strings.keywords import Keywords as _
from dbas.strings.translator import Translator

nick_of_anonymous_user = 'anonymous'

fallback_lang = 'en'
tag_type = 'span'
start_attack = '<{} data-argumentation-type="attack">'.format(tag_type)
start_argument = '<{} data-argumentation-type="argument">'.format(tag_type)
start_position = '<{} data-argumentation-type="position">'.format(tag_type)
start_content = '<{} class="triangle-content-text">'.format(tag_type)
start_pro = '<{} data-attitude="pro">'.format(tag_type)
start_con = '<{} data-attitude="con">'.format(tag_type)
start_tag = '<{}>'.format(tag_type)
end_tag = '</{}>'.format(tag_type)


class BubbleTypes(Enum):
    USER = auto()
    SYSTEM = auto()
    STATUS = auto()
    INFO = auto()


class Relations(Enum):
    UNDERMINE = 'undermine'
    UNDERCUT = 'undercut'
    REBUT = 'rebut'
    SUPPORT = 'support'


class Attitudes(Enum):
    AGREE = 'agree'
    DISAGREE = 'disagree'
    DONNT_KNOW = 'dontknow'


def get_global_url():
    """
    Returns the global url of the project.
    Important: the global url has to be in setup.py like "url='http://foo.bar'"

    :return: String
    """
    path = str(os.path.realpath(__file__ + '/../../setup.py'))
    lines = [line.rstrip('\n').strip() for line in open(path)]

    return str([l[l.index('htt'):-2] for l in lines if 'url=' in l][0])


def get_changelog(no):
    """
    Returns the 'no' last entries from the changelog

    :param no: int
    :return: list
    """
    path = str(os.path.realpath(__file__ + '/../../CHANGELOG.md'))
    lines = [line.rstrip('\n').strip() for line in open(path) if len(line.rstrip('\n').strip()) > 0]
    changelog = []
    title = ''
    body = []
    for l in lines:
        if l.startswith('#'):
            if len(title) > 0:
                changelog.append({'title': title, 'body': body})
                body = []
            title = l.replace('### ', '')
        else:
            body.append(l.replace('- ', ''))

    return changelog[0:no]


def is_development_mode(registry):
    """
    Returns true, if mode is set to development in current ini file.

    :param registry: request.registry
    :return: Boolean
    """
    if 'mode' in registry.settings:
        return registry.settings['mode'] == 'development'
    return False


def escape_string(text):
    """
    Escapes all html special chars.

    :param text: string
    :return: html.escape(text)
    """
    return escape(text)


def get_discussion_language(matchdict, params, session, current_issue_uid=None):
    """
    Returns Language.ui_locales
    CALL AFTER issue_handler.get_id_of_slug(..)!

    :param matchdict: matchdict of the current request
    :param params: params of the current request
    :param session: session of the current request
    :param current_issue_uid: uid
    :return:
    """
    if not current_issue_uid:
        current_issue = DBDiscussionSession.query(Issue).filter(Issue.is_disabled == False,
                                                                Issue.is_private == False).first()
        current_issue_uid = current_issue.uid if current_issue else None

    # first matchdict, then params, then session, afterwards fallback
    issue = matchdict['issue'] if 'issue' in matchdict \
        else params['issue'] if 'issue' in params \
        else session['issue'] if 'issue' in session \
        else current_issue_uid

    db_issue = DBDiscussionSession.query(Issue).get(issue)

    return db_issue.lang if db_issue else 'en'


def python_datetime_pretty_print(ts, lang):
    """
    Pretty print of a locale

    :param ts:  Timestamp
    :param lang: ui_locales
    :return: String
    """
    formatter = '%b. %d.'
    if lang == 'de':
        try:
            locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
            formatter = '%d. %b.'
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF8')

    return datetime.strptime(str(ts), '%Y-%m-%d').strftime(formatter)


def get_all_arguments_by_statement(statement_uid, include_disabled=False):
    """
    Returns a list of all arguments where the statement is a conclusion or member of the premisegroup

    :param statement_uid: Statement.uid
    :param include_disabled: Boolean
    :return: [Arguments]
    """
    logger('DBAS.LIB', 'main {}, include_disabled {}'.format(statement_uid, include_disabled))
    db_arguments = __get_arguments_of_conclusion(statement_uid, include_disabled)
    return_array = [arg for arg in db_arguments] if db_arguments else []

    premises = DBDiscussionSession.query(Premise).filter_by(statement_uid=statement_uid)
    if not include_disabled:
        premises = premises.filter_by(is_disabled=False)
    premises = premises.all()

    for p in premises:
        return_array += __get_argument_of_premisegroup(p.premisegroup_uid, include_disabled)

    db_undercuts = []
    for arg in return_array:
        db_undercuts += __get_undercuts_of_argument(arg.uid, include_disabled)

    db_undercutted_undercuts = []
    for arg in db_undercuts:
        db_undercutted_undercuts += __get_undercuts_of_argument(arg.uid, include_disabled)

    return_array = list(set(return_array + db_undercuts + db_undercutted_undercuts))

    logger('DBAS.LIB', 'returning arguments {}'.format([arg.uid for arg in return_array]))
    return return_array if len(return_array) > 0 else None


def __get_argument_of_premisegroup(premisegroup_uid, include_disabled):
    """
    Returns all arguments with the given premisegroup

    :param premisegroup_uid: PremisgGroup.uid
    :param include_disabled: Boolean
    :return: list of Arguments
    """
    db_arguments = DBDiscussionSession.query(Argument).filter_by(premisegroup_uid=premisegroup_uid)
    if not include_disabled:
        db_arguments = db_arguments.filter_by(is_disabled=False)
    return db_arguments.all() if db_arguments else []


def __get_undercuts_of_argument(argument_uid, include_disabled):
    """
    Returns all undercuts fo the given argument

    :param argument_uid: Argument.uid
    :param include_disabled: boolean
    :return: list of Arguments
    """
    db_undercuts = DBDiscussionSession.query(Argument).filter_by(argument_uid=argument_uid)
    if not include_disabled:
        db_undercuts = db_undercuts.filter_by(is_disabled=False)
    return db_undercuts.all() if db_undercuts else []


def __get_arguments_of_conclusion(statement_uid, include_disabled):
    """
    Returns all arguments, where the statement is set as conclusion

    :param statement_uid: Statement.uid
    :param include_disabled: Boolean
    :return: list of arguments
    """
    db_arguments = DBDiscussionSession.query(Argument).filter_by(conclusion_uid=statement_uid)
    if not include_disabled:
        db_arguments = db_arguments.filter_by(is_disabled=False)
    return db_arguments.all() if db_arguments else []


def get_all_arguments_with_text_by_statement_id(statement_uid):
    """
    Given a statement_uid, it returns all arguments, which use this statement and adds
    the corresponding text to it, which normally appears in the bubbles. The resulting
    text depends on the provided language.

    :param statement_uid: uid to a statement, which should be analyzed
    :return: list of dictionaries containing some properties of these arguments
    :rtype: list
    """
    logger('DBAS.LIB', 'main ' + str(statement_uid))
    arguments = get_all_arguments_by_statement(statement_uid)
    results = []
    if arguments:
        results = [{'uid': arg.uid, 'text': get_text_for_argument_uid(arg.uid)} for arg in arguments]
    return results


def get_all_arguments_with_text_and_url_by_statement_id(db_statement, urlmanager, color_statement=False,
                                                        is_jump=False):
    """
    Given a statement_uid, it returns all arguments, which use this statement and adds
    the corresponding text to it, which normally appears in the bubbles. The resulting
    text depends on the provided language.

    :param db_statement: Statement
    :param urlmanager:
    :param color_statement: True, if the statement (specified by the ID) should be colored
    :return: list of dictionaries containing some properties of these arguments
    :rtype: list
    """
    logger('DBAS.LIB', 'main ' + str(db_statement.uid))
    arguments = get_all_arguments_by_statement(db_statement.uid)
    uids = [arg.uid for arg in arguments] if arguments else None
    results = list()
    sb = '<{} data-argumentation-type="position">'.format(tag_type) if color_statement else ''
    se = '</{}>'.format(tag_type) if color_statement else ''

    if not uids:
        return []

    uids.sort()
    for uid in uids:
        statement_text = db_statement.get_text()
        attack_type = 'jump' if is_jump else ''
        argument_text = get_text_for_argument_uid(uid, anonymous_style=True, attack_type=attack_type)
        pos = argument_text.lower().find(statement_text.lower())

        argument_text = argument_text[:pos] + sb + argument_text[pos:]
        pos += len(statement_text) + len(sb)
        argument_text = argument_text[:pos] + se + argument_text[pos:]

        results.append({
            'uid': uid,
            'text': argument_text,
            'url': urlmanager.get_url_for_jump(uid)
        })
    return results


def get_slug_by_statement_uid(uid):
    """
    Returns slug for the given Issue.uid

    :param uid: Issue.uid
    :return: String
    """
    db_statement = DBDiscussionSession.query(Statement).get(uid)
    return resolve_issue_uid_to_slug(db_statement.issue_uid)


def get_text_for_argument_uid(uid, nickname=None, with_html_tag=False, start_with_intro=False, first_arg_by_user=False,
                              user_changed_opinion=False, rearrange_intro=False, colored_position=False,
                              attack_type=None, minimize_on_undercut=False, is_users_opinion=True,
                              anonymous_style=False, support_counter_argument=False):
    """
    Returns current argument as string like "conclusion, because premise1 and premise2"

    :param uid: Integer
    :param with_html_tag: Boolean
    :param start_with_intro: Boolean
    :param first_arg_by_user: Boolean
    :param user_changed_opinion: Boolean
    :param rearrange_intro: Boolean
    :param colored_position: Boolean
    :param attack_type: String
    :param minimize_on_undercut: Boolean
    :param anonymous_style: Boolean
    :param support_counter_argument: Boolean
    :return: String
    """
    logger('DBAS.LIB', 'main {}'.format(uid))
    db_argument = DBDiscussionSession.query(Argument).get(uid)
    if not db_argument:
        return None

    lang = db_argument.lang
    _t = Translator(lang)
    premisegroup_by_user = False
    author_uid = None
    db_user = DBDiscussionSession.query(User).filter_by(nickname=str(nickname)).first()

    if db_user:
        author_uid = db_user.uid
        pgroup = DBDiscussionSession.query(PremiseGroup).get(db_argument.premisegroup_uid)
        marked_argument = DBDiscussionSession.query(MarkedArgument).filter_by(
            argument_uid=uid,
            author_uid=db_user.uid).first()
        premisegroup_by_user = pgroup.author_uid == db_user.uid or marked_argument is not None

    # getting all argument id
    arg_array = [db_argument]
    while db_argument.argument_uid:
        db_argument = DBDiscussionSession.query(Argument).get(db_argument.argument_uid)
        arg_array.append(db_argument)

    if attack_type == 'jump':
        return __build_argument_for_jump(arg_array, with_html_tag)

    if len(arg_array) == 1:
        # build one argument only
        return __build_single_argument(arg_array[0], rearrange_intro, with_html_tag, colored_position, attack_type, _t,
                                       start_with_intro, is_users_opinion, anonymous_style, support_counter_argument,
                                       author_uid)

    else:
        # get all pgroups and at last, the conclusion
        return __build_nested_argument(arg_array, first_arg_by_user, user_changed_opinion, with_html_tag,
                                       start_with_intro, minimize_on_undercut, anonymous_style, premisegroup_by_user,
                                       _t)


def __build_argument_for_jump(arg_array: List[Argument], with_html_tag):
    """
    Build tet for an argument, if we jump to this argument

    :param arg_array: [Argument]
    :param with_html_tag: Boolean
    :return: String
    """
    tag_premise = ('<' + tag_type + ' data-argumentation-type="attack">') if with_html_tag else ''
    tag_conclusion = ('<' + tag_type + ' data-argumentation-type="argument">') if with_html_tag else ''
    tag_end = ('</' + tag_type + '>') if with_html_tag else ''
    lang = arg_array[0].lang
    _t = Translator(lang)

    if len(arg_array) == 1:
        ret_value = __build_val_for_jump(arg_array[0], tag_premise, tag_conclusion, tag_end, _t)

    elif len(arg_array) == 2:
        ret_value = __build_val_for_undercut(arg_array, tag_premise, tag_conclusion, tag_end, _t)

    else:
        ret_value = __build_val_for_undercutted_undercut(arg_array, tag_premise, tag_conclusion, tag_end, _t)

    return ret_value.replace('  ', ' ')


def __build_val_for_jump(db_argument, tag_premise, tag_conclusion, tag_end, _t):
    premises = db_argument.get_premisegroup_text()
    if premises[-1] != '.':
        premises += '.'
    conclusion = db_argument.get_conclusion_text()

    because = _t.get(_.because).lower()
    conclusion = tag_conclusion + conclusion + tag_end
    premises = tag_premise + premises + tag_end

    intro = (start_con + _t.get(_.isNotRight).lower() + end_tag) if not db_argument.is_supportive else ''
    ret_value = '{} {} {} {}'.format(conclusion, intro, because, premises)
    if _t.get_lang() == 'de':
        intro = _t.get(_.itIsTrueThatAnonymous) if db_argument.is_supportive else _t.get(_.itIsFalseThatAnonymous)
        intro = intro[0:1].upper() + intro[1:]
        intro = (start_pro if db_argument.is_supportive else start_con) + intro + end_tag
        ret_value = '{} {}, {} {}'.format(intro, conclusion, because, premises)

    return ret_value


def __build_val_for_undercut(arg_array: List[Argument], tag_premise, tag_conclusion, tag_end, _t):
    db_undercut = arg_array[0]
    db_conclusion_argument = arg_array[1]
    premise = db_undercut.get_premisegroup_text()
    conclusion_premise = db_conclusion_argument.get_premisegroup_text()
    conclusion_conclusion = db_conclusion_argument.get_conclusion_text()

    premise = tag_premise + premise + tag_end
    conclusion_premise = tag_conclusion + conclusion_premise + tag_end
    conclusion_conclusion = tag_conclusion + conclusion_conclusion + tag_end

    intro = (_t.get(_.statementAbout) + ' ') if _t.get_lang() == 'de' else ''
    bind = start_con + _t.get(_.isNotAGoodReasonFor) + end_tag
    because = _t.get(_.because)
    ret_value = '{}{} {} {}. {} {}.'.format(intro, conclusion_premise, bind, conclusion_conclusion, because, premise)

    return ret_value


def __build_val_for_undercutted_undercut(arg_array: List[Argument], tag_premise, tag_conclusion, tag_end, _t):
    premise1 = arg_array[0].get_premisegroup_text()
    premise2 = arg_array[1].get_premisegroup_text()
    premise3 = arg_array[2].get_premisegroup_text()
    conclusion = arg_array[2].get_conclusion_text()

    bind = start_con + _t.get(_.isNotAGoodReasonAgainstArgument) + end_tag
    because = _t.get(_.because)
    seperator = ',' if _t.get_lang() == 'de' else ''

    premise1 = tag_premise + premise1 + tag_end
    premise2 = tag_conclusion + premise2 + tag_end
    argument = '{}{} {} {}'.format(conclusion, seperator, because.lower(), premise3)
    argument = tag_conclusion + argument + tag_end

    # P2 ist kein guter Grund gegen das Argument, dass C weil P3. Weil P1
    ret_value = '{} {} {}. {} {}'.format(premise2, bind, argument, because, premise1)
    return ret_value


def __build_single_argument(db_argument: Argument, rearrange_intro: bool, with_html_tag: bool, colored_position: bool,
                            attack_type: str, _t: Translator, start_with_intro: bool, is_users_opinion: bool,
                            anonymous_style: bool, support_counter_argument: bool=False, author_uid=None):
    """
    Build up argument text for a single argument

    Please, do not touch this!

    :param uid: Argument.uid
    :param rearrange_intro: Boolean
    :param with_html_tag: Boolean
    :param colored_position: Boolean
    :param attack_type: String
    :param _t: Translator
    :param start_with_intro: Boolean
    :param is_users_opinion: Boolean
    :param anonymous_style: Boolean
    :param support_counter_argument: Boolean
    :param author_uid: User.uid
    :return: String
    """
    premises_text = db_argument.get_premisegroup_text()
    conclusion_text = db_argument.get_conclusion_text()
    lang = db_argument.lang

    if lang != 'de':
        premises_text = premises_text[0:1].lower() + premises_text[1:]  # pretty print

    premises_text, conclusion_text, sb, sb_none, se = __get_tags_for_building_single_argument(with_html_tag,
                                                                                              attack_type,
                                                                                              colored_position,
                                                                                              premises_text,
                                                                                              conclusion_text)

    marked_element = False
    if author_uid:
        db_marked = DBDiscussionSession.query(MarkedArgument).filter(MarkedArgument.argument_uid == db_argument.uid,
                                                                     MarkedArgument.author_uid == author_uid).first()
        marked_element = db_marked is not None

    you_have_the_opinion_that = _t.get(_.youHaveTheOpinionThat).format('').strip()

    if lang == 'de':
        ret_value = __build_single_argument_for_de(_t, sb, se, you_have_the_opinion_that, start_with_intro,
                                                   anonymous_style, rearrange_intro, db_argument, attack_type, sb_none,
                                                   marked_element, lang, premises_text, conclusion_text,
                                                   is_users_opinion,
                                                   support_counter_argument)
    else:
        ret_value = __build_single_argument_for_en(_t, sb, se, you_have_the_opinion_that, marked_element,
                                                   conclusion_text,
                                                   premises_text, db_argument)
    return ret_value.replace('  ', ' ')


def __get_tags_for_building_single_argument(with_html_tag, attack_type, colored_position, premises, conclusion):
    sb_none = start_tag if with_html_tag else ''
    se = end_tag if with_html_tag else ''
    if attack_type not in ['dont_know', 'jump']:
        sb = start_tag if with_html_tag else ''
        if colored_position:
            sb = start_position if with_html_tag else ''

        if attack_type == Relations.UNDERMINE:
            premises = sb + premises + se
        else:
            conclusion = sb + conclusion + se
    else:
        sb = start_argument if with_html_tag else ''
        sb_tmp = start_attack if with_html_tag else ''
        premises = sb + premises + se
        conclusion = sb_tmp + conclusion + se
    return premises, conclusion, sb, sb_none, se


def __build_single_argument_for_de(_t, sb, se, you_have_the_opinion_that, start_with_intro, anonymous_style,
                                   rearrange_intro, db_argument, attack_type, sb_none, marked_element, lang,
                                   premises, conclusion, is_users_opinion, support_counter_argument):
    if start_with_intro and not anonymous_style:
        intro = _t.get(_.itIsTrueThat) if db_argument.is_supportive else _t.get(_.itIsFalseThat)
        if rearrange_intro:
            intro = _t.get(_.itTrueIsThat) if db_argument.is_supportive else _t.get(_.itFalseIsThat)

        ret_value = (sb_none if attack_type in ['dont_know'] else sb) + intro + se + ' '

    elif is_users_opinion and not anonymous_style:
        ret_value = sb_none
        if support_counter_argument:
            ret_value += _t.get(_.youAgreeWithThecounterargument)
        elif marked_element:
            ret_value += you_have_the_opinion_that
        else:
            ret_value += _t.get(_.youArgue)
        ret_value += se + ' '

    else:
        tmp = _t.get(_.itIsTrueThatAnonymous if db_argument.is_supportive else _.itIsFalseThatAnonymous)
        ret_value = sb_none + sb + tmp + se + ' '
    ret_value += ' {}{}{} '.format(sb, _t.get(_.itIsNotRight), se) if not db_argument.is_supportive else ''
    ret_value += conclusion
    ret_value += ', ' if lang == 'de' else ' '
    ret_value += sb_none + _t.get(_.because).lower() + se + ' ' + premises
    return ret_value


def __build_single_argument_for_en(_t, sb, se, you_have_the_opinion_that, marked_element, conclusion, premises, db_arg):
    tmp = sb + ' ' + _t.get(_.isNotRight).lower() + se + ', ' + _t.get(_.because).lower() + ' '
    ret_value = (you_have_the_opinion_that + ' ' if marked_element else '') + conclusion + ' '
    ret_value += _t.get(_.because).lower() if db_arg.is_supportive else tmp
    ret_value += ' ' + premises
    return ret_value


def __build_nested_argument(arg_array: List[Argument], first_arg_by_user, user_changed_opinion, with_html_tag,
                            start_with_intro, minimize_on_undercut, anonymous_style, premisegroup_by_user, _t):
    """

    :param arg_array:
    :param first_arg_by_user:
    :param user_changed_opinion:
    :param with_html_tag:
    :param start_with_intro:
    :param minimize_on_undercut:
    :param anonymous_style:
    :param premisegroup_by_user:
    :param _t:
    :return:
    """
    # get all pgroups and at last, the conclusion
    pgroups = []
    supportive = []
    arg_array = arg_array[::-1]
    local_lang = arg_array[0].lang

    # grepping all arguments in the chain
    for db_argument in arg_array:
        text = db_argument.get_premisegroup_text()

        pgroups.append(text)
        supportive.append(db_argument.is_supportive)

    conclusion = arg_array[0].get_conclusion_text()

    # html tags for framing
    sb = start_position if with_html_tag else ''
    se = end_tag if with_html_tag else ''

    because = (', ' if local_lang == 'de' else ' ') + _t.get(_.because).lower() + ' '

    if len(arg_array) % 2 is 0 and not first_arg_by_user and not anonymous_style:  # system starts
        ret_value = _t.get(_.earlierYouArguedThat if user_changed_opinion else _.otherUsersSaidThat) + ' '
        tmp_users_opinion = True  # user after system

    elif not anonymous_style:  # user starts
        ret_value = (_t.get(_.soYourOpinionIsThat) + ': ') if start_with_intro else ''
        tmp_users_opinion = False  # system after user
        conclusion = se + conclusion[0:1].upper() + conclusion[1:]  # pretty print

    else:
        ret_value = _t.get(_.someoneArgued) + ' '
        tmp_users_opinion = False

    tmp = _t.get(_.itFalseIsThat) + ' ' if not supportive[0] else ''
    ret_value += tmp + conclusion + because + pgroups[0] + '.'
    del pgroups[0]

    # just display the last premise group on undercuts, because the story is always saved in all bubbles
    if minimize_on_undercut and not user_changed_opinion and len(pgroups) > 2:
        return _t.get(_.butYouCounteredWith).strip() + ' ' + sb + pgroups[len(pgroups) - 1] + se + '.'

    for i, pgroup in enumerate(pgroups):
        ret_value += ' '
        if tmp_users_opinion and not anonymous_style:
            tmp = _.butYouCounteredWithArgument if premisegroup_by_user else _.butYouCounteredWithInterest
            ret_value += _t.get(_.otherParticipantsConvincedYouThat if user_changed_opinion else tmp)
        elif not anonymous_style:
            ret_value += _t.get(_.youAgreeWithThatNow)
        else:
            ret_value += _t.get(_.otherUsersSaidThat) if i == 0 else _t.get(_.thenOtherUsersSaidThat)

        ret_value += sb + ' ' + pgroups[i] + '.'
        tmp_users_opinion = not tmp_users_opinion

    return ret_value.replace('  ', ' ')


def get_text_for_premisegroup_uid(uid):
    """
    Returns joined text of the premise group and the premise ids

    :param uid: premisegroup_uid
    :return: text, uids
    """
    warnings.warn("Use PremiseGroup.get_text() instead.", DeprecationWarning)

    db_premises = DBDiscussionSession.query(Premise).filter_by(premisegroup_uid=uid).join(Statement).all()
    if len(db_premises) == 0:
        return ''
    texts = [premise.get_text() for premise in db_premises]
    lang = DBDiscussionSession.query(Statement).get(db_premises[0].statements.uid).lang
    _t = Translator(lang)

    return ' {} '.format(_t.get(_.aand)).join(texts)


def get_text_for_statement_uid(uid: int, colored_position=False):
    """
    Returns text of statement with given uid

    :param uid: Statement.uid
    :param colored_position: Boolean
    :return: String
    """
    warnings.warn("Use Statement.get_text() or Statement.get_html() instead.", DeprecationWarning)

    if not isinstance(uid, int):
        return None
    db_statement = DBDiscussionSession.query(Statement).get(uid)
    if not db_statement:
        return None

    db_textversion = DBDiscussionSession.query(TextVersion).order_by(TextVersion.uid.desc()).get(
        db_statement.textversion_uid)
    content = db_textversion.content

    while content.endswith(('.', '?', '!')):
        content = content[:-1]

    sb, se = '', ''
    if colored_position:
        sb = '<{} data-argumentation-type="position">'.format(tag_type)
        se = '</{}>'.format(tag_type)

    return sb + content + se


def get_text_for_premise(uid: int, colored_position: bool = False):
    """
    Returns text of premise with given uid

    :param uid: Statement.uid
    :param colored_position: Boolean
    :return: String
    """
    db_premise = DBDiscussionSession.query(Premise).get(uid)
    if db_premise:
        return db_premise.get_text(html=colored_position)
    else:
        return None


def get_text_for_conclusion(argument, start_with_intro=False, rearrange_intro=False, is_users_opinion=True):
    """
    Check the arguments conclusion whether it is an statement or an argument and returns the text

    :param argument: Argument
    :param start_with_intro: Boolean
    :param rearrange_intro: Boolean
    :return: String
    """
    if argument.argument_uid:
        return get_text_for_argument_uid(argument.argument_uid, start_with_intro, rearrange_intro=rearrange_intro,
                                         is_users_opinion=is_users_opinion)
    else:
        return argument.get_conclusion_text()


def resolve_issue_uid_to_slug(uid):
    """
    Given the issue uid query database and return the correct slug of the issue.

    :param uid: issue_uid
    :type uid: int
    :return: Slug of issue
    :rtype: str
    """
    issue = DBDiscussionSession.query(Issue).get(uid)
    return issue.slug if issue else None


def get_all_attacking_arg_uids_from_history(history):
    """
    Returns all arguments of the history, which attacked the user

    :param history: String
    :return: [Arguments.uid]
    :rtype: list
    """
    try:
        splitted_history = history.split('-')
        uids = []
        for part in splitted_history:
            if 'reaction' in part:
                parts = part.split('/')
                pos = parts.index('reaction')
                uids.append(part.split('/')[pos + 3])
        return uids
    except AttributeError:
        return []


def get_user_by_private_or_public_nickname(nickname):
    """
    Gets the user by his (public) nickname, based on the option, whether his nickname is public or not

    :param nickname: Nickname of the user
    :return: Current user or None
    """
    db_user = get_user_by_case_insensitive_nickname(nickname)
    db_public_user = get_user_by_case_insensitive_public_nickname(nickname)
    uid = 0

    if db_user:
        uid = db_user.uid
    elif db_public_user:
        uid = db_public_user.uid

    db_settings = DBDiscussionSession.query(Settings).filter_by(author_uid=uid).first()

    if not db_settings:
        return None

    if db_settings.should_show_public_nickname and db_user:
        return db_user
    elif not db_settings.should_show_public_nickname and db_public_user:
        return db_public_user

    return None


def get_user_by_case_insensitive_nickname(nickname):
    """
    Returns user with given nickname

    :param nickname: String
    :return: User or None
    """
    return DBDiscussionSession.query(User).filter(func.lower(User.nickname) == func.lower(nickname)).first()


def get_user_by_case_insensitive_public_nickname(public_nickname):
    """
    Returns user with given public nickname

    :param public_nickname: String
    :return: User or None
    """
    return DBDiscussionSession.query(User).filter(
        func.lower(User.public_nickname) == func.lower(public_nickname)).first()


def pretty_print_options(message):
    """
    Some modifications for pretty printing.
    Use uppercase for first letter in text and a single dot for the end if there isn't one already.

    :param message: String
    :return:  String
    """

    # check for html
    if message[0:1] == '<':
        pos = message.index('>')
        message = message[0:pos + 1] + message[pos + 1:pos + 2].upper() + message[pos + 2:]
    else:
        message = message[0:1].upper() + message[1:]

    # check for html
    if message[-1] == '>':
        pos = message.rfind('<')
        if message[pos - 1:pos] not in ['.', '?', '!']:
            message = message[0:pos] + '.' + message[pos:]
    elif not message.endswith(tuple(['.', '?', '!'])) and id is not 'now':
        message += '.'

    return message


def create_speechbubble_dict(bubble_type, is_markable=False, is_author=False, uid='', url='', message='',
                             omit_url=False, argument_uid=None, statement_uid=None, is_supportive=None,
                             nickname='anonymous', lang='en', is_users_opinion=False):
    """
    Creates an dictionary which includes every information needed for a bubble.

    :param bubble_type: BubbleTypes
    :param is_markable: Boolean
    :param is_author: Boolean
    :param uid: id of bubble
    :param url: URL
    :param message: String
    :param omit_url: Boolean
    :param argument_uid: Argument.uid
    :param statement_uid: Statement.uid
    :param is_supportive: Boolean
    :param nickname: String
    :param omit_url: Boolean
    :param lang: is_users_opinion
    :param is_users_opinion: Boolean
    :return: dict()
    """
    if uid is not 'now':
        message = pretty_print_options(message)

    # check for users opinion
    if bubble_type is BubbleTypes.USER and nickname != 'anonymous':
        db_user = DBDiscussionSession.query(User).filter_by(nickname=nickname).first()
        db_marked = None
        if argument_uid is not None and db_user is not None:
            db_marked = DBDiscussionSession.query(MarkedArgument).filter(
                MarkedArgument.argument_uid == argument_uid,
                MarkedArgument.author_uid == db_user.uid).first()

        if statement_uid is not None and db_user is not None:
            db_marked = DBDiscussionSession.query(MarkedStatement).filter(
                MarkedStatement.statement_uid == statement_uid,
                MarkedStatement.author_uid == db_user.uid).first()

        is_users_opinion = db_marked is not None

    speech = {
        'is_user': bubble_type is BubbleTypes.USER,
        'is_system': bubble_type is BubbleTypes.SYSTEM,
        'is_status': bubble_type is BubbleTypes.STATUS,
        'is_info': bubble_type is BubbleTypes.INFO,
        'is_markable': is_markable,
        'is_author': is_author,
        'id': uid if len(str(uid)) > 0 else uuid4().hex,
        'url': url,
        'message': message,
        'omit_url': omit_url,
        'data_type': 'argument' if argument_uid else 'statement' if statement_uid else 'None',
        'data_argument_uid': argument_uid,
        'data_statement_uid': statement_uid,
        'data_is_supportive': is_supportive,
        'is_users_opinion': is_users_opinion,
    }

    votecount_keys = __get_text_for_click_and_mark_count(nickname, bubble_type is BubbleTypes.USER, argument_uid,
                                                         statement_uid, speech, lang)

    speech['votecounts_message'] = votecount_keys[speech['votecounts']]

    return speech


def __get_text_for_click_and_mark_count(nickname, is_user, argument_uid, statement_uid, speech, lang):
    """
    Build text for a bubble, how many other participants have the same interest?

    :param nickname: User.nickname
    :param is_user: boolean
    :param argument_uid: Argument.uid
    :param statement_uid: Statement.uid
    :param speech: dict()
    :param lang: ui_locales
    :return: [String]
    """

    if not nickname:
        nickname = 'anonymous'

    db_user = DBDiscussionSession.query(User).filter_by(nickname=nickname).first()
    if not db_user:
        db_user = DBDiscussionSession.query(User).filter_by(nickname='anonymous').first()

    db_clicks, db_marks = __get_clicks_and_marks(argument_uid, statement_uid, db_user)

    _t = Translator(lang)
    speech['votecounts'] = len(db_clicks) if db_clicks else 0
    if db_marks:
        speech['votecounts'] += len(db_marks)

    votecount_keys = defaultdict(lambda: "{} {}.".format(speech['votecounts'], _t.get(_.voteCountTextMore)))

    if is_user and db_user.gender == 'm':
        gender_key = _.voteCountTextFirstM
    elif is_user and db_user.gender == 'f':
        gender_key = _.voteCountTextFirstF
    else:
        gender_key = _.voteCountTextFirst

    votecount_keys[0] = '{}.'.format(_t.get(gender_key))
    votecount_keys[1] = _t.get(_.voteCountTextOneOther) + '.'

    return votecount_keys


def __get_clicks_and_marks(argument_uid, statement_uid, db_user):
    db_clicks = None
    db_marks = None
    if argument_uid:
        db_clicks = DBDiscussionSession.query(ClickedArgument). \
            filter(ClickedArgument.argument_uid == argument_uid,
                   ClickedArgument.is_up_vote == True,
                   ClickedArgument.is_valid,
                   ClickedArgument.author_uid != db_user.uid).all()
        db_marks = DBDiscussionSession.query(MarkedArgument). \
            filter(MarkedArgument.argument_uid == argument_uid,
                   MarkedArgument.author_uid != db_user.uid).all()

    elif statement_uid:
        db_clicks = DBDiscussionSession.query(ClickedStatement). \
            filter(ClickedStatement.statement_uid == statement_uid,
                   ClickedStatement.is_up_vote == True,
                   ClickedStatement.is_valid,
                   ClickedStatement.author_uid != db_user.uid).all()
        db_marks = DBDiscussionSession.query(MarkedStatement). \
            filter(MarkedStatement.statement_uid == statement_uid,
                   MarkedStatement.author_uid != db_user.uid).all()

    return db_clicks, db_marks


def is_argument_disabled_due_to_disabled_statements(argument):
    """
    Returns true if any involved statement is disabled.

    :param argument: Argument
    :return: Boolean
    """
    if argument.conclusion_uid is None:
        # check conclusion of given arguments conclusion
        db_argument = DBDiscussionSession.query(Argument).get(argument.argument_uid)
        conclusion = DBDiscussionSession(Statement).get(db_argument.conclusion_uid)
        if conclusion.is_disabled:
            return True
        # check premisegroup of given arguments conclusion
        premises = __get_all_premises_of_argument(db_argument)
        for premise in premises:
            if premise.statements.is_disabled:
                return True
    else:
        # check conclusion of given argument
        print(argument.conclusion_uid)
        conclusion = DBDiscussionSession.query(Statement).get(argument.conclusion_uid)
        if conclusion.is_disabled:
            return True

    # check premisegroup of given argument
    premises = __get_all_premises_of_argument(argument)
    for premise in premises:
        if premise.statements.is_disabled:
            return True

    return False


def is_author_of_statement(db_user: User, statement_uid: int) -> bool:
    """
    Is the user with given nickname author of the statement?

    :param db_user: User
    :param statement_uid: Statement.uid
    :return: Boolean
    """
    db_user = db_user if db_user and db_user.nickname != nick_of_anonymous_user else None
    if not db_user:
        return False

    db_textversion = DBDiscussionSession.query(TextVersion).filter_by(statement_uid=statement_uid).order_by(
        TextVersion.uid.asc()).first()  # TODO #432
    if not db_textversion:
        return False
    return db_textversion.author_uid == db_user.uid


def is_author_of_argument(db_user: User, argument_uid: int) -> bool:
    """
    Is the user with given nickname author of the argument?

    :param db_user: User
    :param argument_uid: Argument.uid
    :return: Boolean
    """
    db_user = db_user if db_user and db_user.nickname != nick_of_anonymous_user else None
    if not db_user:
        return False
    db_argument = DBDiscussionSession.query(Argument).filter(Argument.uid == argument_uid,
                                                             Argument.author_uid == db_user.uid).first()
    return True if db_argument else False


def __get_all_premises_of_argument(argument):
    """
    Returns list with all premises of the argument.

    :param argument: Argument
    :return: list()
    """
    ret_list = []
    db_premises = DBDiscussionSession.query(Premise).filter_by(premisegroup_uid=argument.premisegroup_uid).join(
        Statement).all()
    for premise in db_premises:
        ret_list.append(premise)
    return ret_list


def get_profile_picture(user: User, size: int = 80, ignore_privacy_settings: bool = False):
    """
    Returns the url to a https://secure.gravatar.com picture, with the option wavatar and size of 80px

    :param user: User
    :param size: Integer, default 80
    :param ignore_privacy_settings:
    :return: String
    """
    additional_id = ''
    if user and isinstance(user, User):
        additional_id = '' if user.settings.should_show_public_nickname or ignore_privacy_settings else 'x'

    return __get_gravatar(user, additional_id, size)


def get_public_profile_picture(user: User, size: int = 80):
    """
    Returns the url to a https://secure.gravatar.com picture, with the option wavatar and size of 80px
    If the user doesn't want an public profile, an anonymous image will be returned

    :param user: User
    :param size: Integer, default 80
    :return: String
    """
    additional_id = 'y'
    if user and isinstance(user, User):
        additional_id = ''
        if user.settings.should_show_public_nickname:
            additional_id = 'x'
        if len(str(user.oauth_provider)) > 0:
            additional_id = '{}{}'.format(user.oauth_provider, user.oauth_provider_id)

    return __get_gravatar(user, additional_id, size)


def __get_gravatar(user, additional_id, size):
    if user:
        if str(user.email) == 'None':
            email = (user.nickname + additional_id).encode('utf-8')
        else:
            email = (user.email + additional_id).encode('utf-8')
    else:
        url = get_global_url()
        url = url[url.index('//') + 2:]
        email = ('unknown@' + url).encode('utf-8')
    gravatar_url = 'https://secure.gravatar.com/avatar/{}?'.format(hashlib.md5(email.lower()).hexdigest())
    gravatar_url += parse.urlencode({'d': 'wavatar', 's': str(size)})

    return gravatar_url


def get_author_data(uid, gravatar_on_right_side=True, linked_with_users_page=True, profile_picture_size=20):
    """
    Returns a-tag with gravatar of current author and users page as href

    :param uid: Uid of the author
    :param gravatar_on_right_side: True, if the gravatar is on the right of authors name
    :param linked_with_users_page: True, if the text is a link to the authors site
    :param profile_picture_size: Integer
    :return: HTML-String
    """
    db_user = DBDiscussionSession.query(User).get(int(uid))
    if not db_user:
        return None, 'Missing author with uid ' + str(uid), False

    nick = db_user.global_nickname
    img_src = get_profile_picture(db_user, profile_picture_size)
    link_begin = ''
    link_end = ''
    if linked_with_users_page:
        link_begin = '<a href="/user/{}" title="{}">'.format(db_user.uid, nick)
        link_end = '</a>'

    side = 'left' if gravatar_on_right_side else 'right'
    img = '<img class="img-circle" src="{}" style="padding-{}: 0.3em">'.format(img_src, side)

    if gravatar_on_right_side:
        return db_user, '{}{}{}{}'.format(link_begin, nick, img, link_end), True
    else:
        return db_user, '{}{}{}{}'.format(link_begin, img, nick, link_end), True


def bubbles_already_last_in_list(bubble_list, bubbles):
    """
    Are the given bubbles already at the end of the bubble list

    :param bubble_list: list of Bubbles
    :param bubbles:  list of bubbles
    :return: Boolean
    """
    if isinstance(bubbles, list):
        length = len(bubbles)
    else:
        length = 1
        bubbles = [bubbles]

    if len(bubble_list) < length:
        return False

    for bubble in bubbles:
        if 'message' not in bubble:
            return False

    start_index = - length
    is_already_in = False
    for bubble in bubbles:

        last = bubble_list[start_index]
        if 'message' not in last or 'message' not in bubble:
            return False

        text1 = unhtmlify(last['message'].lower()).strip()
        text2 = unhtmlify(bubble['message'].lower()).strip()
        is_already_in = is_already_in or (text1 == text2)
        start_index += 1

    return is_already_in


def unhtmlify(html):
    """
    Remove html-tags and unescape encoded html-entities.

    :param html: Evil-string containing html
    :return:
    """
    return unescape(re.sub(r'<.*?>', '', html))
