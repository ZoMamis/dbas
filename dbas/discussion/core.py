from typing import Union

import dbas.handler.issue as issue_helper
from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, User
from dbas.handler import user
from dbas.handler.voting import add_click_for_argument
from dbas.helper.dictionary.discussion import DiscussionDictHelper
from dbas.helper.dictionary.items import ItemDictHelper
from dbas.helper.views import handle_justification_step
from dbas.input_validator import is_integer, is_statement_forbidden, check_belonging_of_statement, \
    check_belonging_of_argument, check_belonging_of_premisegroups, related_with_support, check_reaction, \
    check_belonging_of_arguments
from dbas.logger import logger
from dbas.query_wrapper import get_not_disabled_arguments_as_query
from dbas.review.helper.reputation import add_reputation_for, rep_reason_first_argument_click
from dbas.strings.keywords import Keywords as _
from dbas.strings.translator import Translator


def init(request_dict) -> Union[dict, None]:
    """
    Initialize the discussion. Creates helper and returns a dictionary containing the first elements needed for the
    discussion.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection with first elements for the discussion
    """
    logger('Core', 'main')
    application_url = request_dict['app_url']
    db_issue = request_dict['issue']
    slug = db_issue.slug
    db_user = request_dict['user']

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    _ddh = DiscussionDictHelper(disc_ui_locales, nickname=db_user.nickname, slug=slug)

    item_dict = ItemDictHelper(disc_ui_locales, db_issue).get_array_for_start(db_user)
    discussion_dict = _ddh.get_dict_for_start(position_count=(len(item_dict['elements'])))

    return {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }


def attitude(request_dict) -> Union[dict, None]:
    """
    Initialize the attitude step for a position in a discussion. Creates helper and returns a dictionary containing
    the first elements needed for the discussion.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdict for the discussion
    """
    logger('Core', 'attitude')

    db_issue = request_dict['issue']
    application_url = request_dict['app_url']
    history = request_dict['history']
    tmp = request_dict['matchdict']['statement_id']
    statement_uid = tmp[0] if len(tmp) > 0 else tmp
    slug = db_issue.slug
    db_user = request_dict['user']

    if not is_integer(statement_uid, True) \
            or not check_belonging_of_statement(db_issue.uid, statement_uid)\
            or is_statement_forbidden(statement_uid):
        logger('Core', 'param error / forbidden statement {}'.format(statement_uid), error=True)
        return None

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    _ddh = DiscussionDictHelper(disc_ui_locales, db_user.nickname, history, slug=slug)
    discussion_dict = _ddh.get_dict_for_attitude(statement_uid)
    if not discussion_dict:
        logger('Core', 'no discussion dict', error=True)
        return None

    _idh = ItemDictHelper(disc_ui_locales, db_issue, path=request_dict['path'], history=history)
    item_dict = _idh.prepare_item_dict_for_attitude(statement_uid)

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def justify(request_dict) -> Union[dict, None]:
    """
    Initialize the justification step for a statement or an argument in a discussion. Creates helper and
    returns a dictionary containing the necessary elements needed for the discussion.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdict for the discussion
    """
    logger('Core', 'main')

    db_issue = request_dict['issue']
    application_url = request_dict['app_url']
    db_user = request_dict['user']

    request_dict['user'] = db_user
    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)

    item_dict, discussion_dict = handle_justification_step(request_dict)
    if not all([item_dict, discussion_dict]):
        return None

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def reaction(request_dict) -> Union[dict, None]:
    """
    Initialize the reaction step for a position in a discussion. Creates helper and returns a dictionary containing
    different feedback options for the confrontation with an argument in a discussion.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdict for the discussion
    """
    logger('Core', 'main')

    nickname = request_dict['nickname']
    db_issue = request_dict['issue']
    application_url = request_dict['app_url']
    history = request_dict['history']
    slug = db_issue.slug
    db_user = request_dict['user']

    # get parameters
    arg_id_user = request_dict['matchdict'].get('arg_id_user')
    attack = request_dict['matchdict'].get('mode')
    arg_id_sys = request_dict['matchdict'].get('arg_id_sys')
    tmp_argument = DBDiscussionSession.query(Argument).get(arg_id_user)

    if not check_reaction(arg_id_user, arg_id_sys, attack) or not check_belonging_of_arguments(db_issue.uid, [arg_id_user, arg_id_sys]):
        logger('discussion_reaction', 'wrong belonging of arguments', error=True)
        return None

    # set votes and reputation
    add_rep, broke_limit = add_reputation_for(nickname, rep_reason_first_argument_click)
    add_click_for_argument(arg_id_user, nickname)

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    supportive = tmp_argument.is_supportive
    _ddh = DiscussionDictHelper(disc_ui_locales, db_user.nickname, history, slug=slug, broke_limit=broke_limit)
    _idh = ItemDictHelper(disc_ui_locales, db_issue, path=request_dict['path'], history=history)
    discussion_dict = _ddh.get_dict_for_argumentation(arg_id_user, supportive, arg_id_sys, attack, history, db_user)
    item_dict = _idh.get_array_for_reaction(arg_id_sys, arg_id_user, supportive, attack, discussion_dict['gender'])

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def support(request_dict) -> Union[dict, None]:
    """
    Initialize the support step for the end of a branch in a discussion. Creates helper and returns a dictionary
    containing the first elements needed for the discussion.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdictfor the discussion
    """
    logger('Core', 'main')

    db_issue = request_dict['issue']
    history = request_dict['history']
    db_user = request_dict['user']
    slug = db_issue.slug
    arg_user_uid = request_dict.get('arg_user_uid', request_dict['matchdict'].get('arg_id_user', ''))
    arg_system_uid = request_dict.get('arg_system_uid', request_dict['matchdict'].get('arg_id_sys', ''))

    application_url = request_dict['app_url']
    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    if not check_belonging_of_argument(db_issue.uid, arg_user_uid) or \
            not check_belonging_of_argument(db_issue.uid, arg_system_uid) or \
            not related_with_support(arg_user_uid, arg_system_uid):
        logger('Core', 'no item dict', error=True)
        return None

    _ddh = DiscussionDictHelper(disc_ui_locales, db_user.nickname, history, slug=slug)
    _idh = ItemDictHelper(disc_ui_locales, db_issue, path=request_dict['path'], history=history)
    discussion_dict = _ddh.get_dict_for_supporting_each_other(arg_system_uid, arg_user_uid, db_user.nickname)
    item_dict = _idh.get_array_for_support(arg_system_uid, slug)

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def choose(request_dict) -> Union[dict, None]:
    """
    Initialize the choose step for more than one premise in a discussion. Creates helper and returns a dictionary
    containing several feedback options regarding this argument.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdictfor the discussion
    """
    logger('Core', 'main')

    is_argument = request_dict['matchdict'].get('is_argument', '').lower()
    is_supportive = request_dict['matchdict'].get('supportive', '').lower()
    uid = request_dict['matchdict'].get('id', '')
    pgroup_ids = request_dict['matchdict'].get('pgroup_ids', '')

    db_issue = request_dict['issue']
    ui_locales = request_dict['ui_locales']
    application_url = request_dict['app_url']
    history = request_dict['history']
    db_user = request_dict['user']
    slug = db_issue.slug

    is_argument = True if is_argument is 'true' else False
    is_supportive = True if is_supportive is 'true' else False

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    for pgroup in pgroup_ids:
        if not is_integer(pgroup):
            logger('core', 'integer error', error=True)
            return None

    if not check_belonging_of_premisegroups(db_issue.uid, pgroup_ids) or not is_integer(uid):
        logger('core', 'wrong belonging of pgroup', error=True)
        return None

    _ddh = DiscussionDictHelper(ui_locales, db_user.nickname, history, slug=slug)
    _idh = ItemDictHelper(disc_ui_locales, db_issue, path=request_dict['path'], history=history)
    discussion_dict = _ddh.get_dict_for_choosing(uid, is_argument, is_supportive)
    item_dict = _idh.get_array_for_choosing(uid, pgroup_ids, is_argument, is_supportive, db_user.nickname)

    if not item_dict:
        logger('discussion_choose', 'no item dict', error=True)
        return None

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def jump(request_dict) -> Union[dict, None]:
    """
    Initialize the jump step for an argument in a discussion. Creates helper and returns a dictionary containing
    several feedback options regarding this argument.

    :param request_dict: dict out of pyramid's request object including issue, slug and history and more
    :rtype: dict
    :return: prepared collection matchdict for the discussion
    """
    logger('Core', 'main')

    arg_uid = request_dict.get('arg_uid', request_dict['matchdict'].get('arg_id'))
    db_issue = request_dict.get('issue')
    history = request_dict.get('history')
    application_url = request_dict.get('app_url')
    db_user = request_dict['user']
    slug = db_issue.slug

    if not check_belonging_of_argument(db_issue.uid, arg_uid):
        logger('Core', 'no item dict', error=True)
        return None

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    _ddh = DiscussionDictHelper(disc_ui_locales, db_user.nickname, history, slug=slug)
    _idh = ItemDictHelper(disc_ui_locales, db_issue, path=request_dict['path'], history=history)
    discussion_dict = _ddh.get_dict_for_jump(arg_uid)
    item_dict = _idh.get_array_for_jump(arg_uid, slug)

    prepared_discussion = {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }

    return prepared_discussion


def finish(request_dict) -> Union[dict, None]:
    logger('Core', 'main')

    application_url = request_dict['app_url']
    db_issue = request_dict['issue']
    history = request_dict['history']
    slug = db_issue.slug
    db_user = request_dict['user']

    # get parameters
    arg_id = request_dict['matchdict'].get('arg_id')
    last_arg = get_not_disabled_arguments_as_query().filter_by(uid=arg_id).first()
    if not last_arg:
        logger('Core', 'no argument', error=True)
        return None

    issue_dict = issue_helper.prepare_json_of_issue(db_issue, application_url, db_user)
    disc_ui_locales = issue_dict['lang']

    _ddh = DiscussionDictHelper(disc_ui_locales, db_user.nickname, history, slug=slug)
    discussion_dict = _ddh.get_dict_for_argumentation(arg_id, last_arg.is_supportive, None, 'end_attack', history, db_user)
    item_dict = ItemDictHelper.get_empty_dict()

    return {
        'issues': issue_dict,
        'discussion': discussion_dict,
        'items': item_dict,
        'title': issue_dict['title']
    }


def dexit(ui_locales: str, db_user: User) -> Union[dict, None]:
    """
    Exit the discussion. Creates helper and returns a dictionary containing the summary of today.

    :param ui_locales:
    :param db_user:
    :rtype: dict
    :return: prepared collection with summary of current day's actions of the user
    """
    return {
        'title': Translator(ui_locales).get(_.finishTitle),
        'summary': user.get_summary_of_today(db_user)
    }
