"""
Core component of D-BAS.

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

import json

import dbas.handler.news as news_handler
import dbas.helper.history as history_helper
import dbas.helper.issue as issue_helper
import dbas.review.helper.flags as review_flag_helper
import dbas.review.helper.history as review_history_helper
import dbas.review.helper.main as review_main_helper
import dbas.review.helper.queues as review_queue_helper
import dbas.review.helper.reputation as review_reputation_helper
import dbas.review.helper.subpage as review_page_helper
import dbas.strings.matcher as fuzzy_string_matcher
import dbas.user_management as user_manager
import requests
import transaction
from subprocess import check_output, CalledProcessError
from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import User, Group, Issue, Argument, Message, Settings, Language, ReviewDeleteReason, sql_timestamp_pretty_print
from dbas.handler.opinion import get_infos_about_argument,  get_user_with_same_opinion_for_argument, \
    get_user_with_same_opinion_for_statements, get_user_with_opinions_for_attitude, \
    get_user_with_same_opinion_for_premisegroups, get_user_and_opinions_for_argument
from dbas.helper.dictionary.discussion import DiscussionDictHelper
from dbas.helper.dictionary.items import ItemDictHelper
from dbas.helper.dictionary.main import DictionaryHelper
from dbas.helper.notification import send_notification, count_of_new_notifications, get_box_for
from dbas.helper.query import get_logfile_for_statements, revoke_content, insert_as_statements, \
    process_input_of_premises_for_arguments_and_receive_url, process_input_of_start_premises_and_receive_url, \
    process_seen_statements
from dbas.helper.references import get_references_for_argument, get_references_for_statements, set_reference
from dbas.helper.views import preparation_for_view, get_nickname, try_to_contact, handle_justification_step, \
    try_to_register_new_user_via_ajax, request_password, prepare_parameter_for_justification, login_user
from dbas.helper.voting import add_vote_for_argument, clear_vote_and_seen_values_of_user
from dbas.input_validator import is_integer, is_position, is_statement_forbidden, check_belonging_of_argument, \
    check_reaction, check_belonging_of_premisegroups, check_belonging_of_statement
from dbas.lib import get_language, escape_string, get_discussion_language, \
    get_user_by_private_or_public_nickname, is_user_author, \
    get_all_arguments_with_text_and_url_by_statement_id, get_slug_by_statement_uid, get_profile_picture, \
    get_changelog
from dbas.logger import logger
from dbas.review.helper.reputation import add_reputation_for, rep_reason_first_position, \
    rep_reason_first_justification, rep_reason_first_argument_click, \
    rep_reason_first_new_argument, rep_reason_new_statement
from dbas.strings.keywords import Keywords as _
from dbas.strings.translator import Translator
from dbas.url_manager import UrlManager
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.security import forget
from pyramid.view import view_config, notfound_view_config, forbidden_view_config
from pyshorteners.shorteners import Shortener
from requests.exceptions import ReadTimeout
from sqlalchemy import and_
from websocket.lib import send_request_for_recent_delete_review_to_socketio, \
    send_request_for_recent_optimization_review_to_socketio, send_request_for_recent_edit_review_to_socketio, \
    send_request_for_info_popup_to_socketio
from dbas.database.initializedb import nick_of_anonymous_user
from dbas.handler.rss import get_list_of_all_feeds

name = 'D-BAS'
version = '1.1.2'
full_version = version + 'b'
project_name = name + ' ' + full_version

# move this into the ini file when the time is right
auto_completion_url = 'http://localhost:5103'
recommender_system_url = 'http://localhost:5104'


def base_layout():
    return get_renderer('templates/basetemplate.pt').implementation().macros['layout']


# main page
@view_config(route_name='main_page', renderer='templates/index.pt', permission='everybody')
@forbidden_view_config(renderer='templates/index.pt')
def main_page(request):
    """
    View configuration for the main page

    :return: HTTP 200 with several information
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_page', 'def', 'main, request.params: ' + str(request.params))
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    session_expired = True if 'session_expired' in request.params and request.params['session_expired'] == 'true' else False
    ui_locales      = get_language(request)
    _dh             = DictionaryHelper(ui_locales, ui_locales)
    extras_dict     = _dh.prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    _dh.add_language_options_for_extra_dict(extras_dict)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': name + ' ' + full_version,
        'project': project_name,
        'extras': extras_dict,
        'session_expired': session_expired
    }


# contact page
@view_config(route_name='main_contact', renderer='templates/contact.pt', permission='everybody', require_csrf=False)
def main_contact(request):
    """
    View configuration for the contact view.

    :return: dictionary with title and project username as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_contact', 'def', 'main, request.params: ' + str(request.params))
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    contact_error = False
    send_message = False
    message = ''

    ui_locales = get_language(request)

    username        = escape_string(request.params['name']) if 'name' in request.params else ''
    email           = escape_string(request.params['mail']) if 'mail' in request.params else ''
    phone           = escape_string(request.params['phone']) if 'phone' in request.params else ''
    content         = escape_string(request.params['content']) if 'content' in request.params else ''
    recaptcha       = request.params['g-recaptcha-response'] if 'g-recaptcha-response' in request.params else ''

    if 'form.contact.submitted' in request.params:
        contact_error, message, send_message = try_to_contact(request, username, email, phone, content, ui_locales, recaptcha)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    ui_locales = get_language(request)
    _t = Translator(ui_locales)
    placeholder = {
        'name': _t.get(_.exampleName),
        'mail': _t.get(_.exampleMail),
        'phone': _t.get(_.examplePhone),
        'message': _t.get(_.exampleMessage)
    }

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _t.get(_.contact),
        'project': project_name,
        'extras': extras_dict,
        'was_message_send': send_message,
        'contact_error': contact_error,
        'message': message,
        'name': username,
        'mail': email,
        'phone': phone,
        'content': content,
        'spamanswer': '',
        'placeholder': placeholder
    }


# settings page, when logged in
@view_config(route_name='main_settings', renderer='templates/settings.pt', permission='use')
def main_settings(request):
    """
    View configuration for the content view. Only logged in user can reach this page.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_settings', 'def', 'main, request.params: ' + str(request.params))
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    ui_locales  = get_language(request)
    old_pw      = ''
    new_pw      = ''
    confirm_pw  = ''
    message     = ''
    success     = False
    error       = False
    db_user     = DBDiscussionSession.query(User).filter_by(nickname=str(request_authenticated_userid)).join(Group).first()
    _uh         = user_manager
    _t          = Translator(ui_locales)

    if not db_user:
        return HTTPFound(location=UrlManager(request.application_url).get_404([request.path[1:]]))

    if db_user and 'form.passwordchange.submitted' in request.params:
        old_pw = escape_string(request.params['passwordold'])
        new_pw = escape_string(request.params['password'])
        confirm_pw = escape_string(request.params['passwordconfirm'])

        message, success = _uh.change_password(db_user, old_pw, new_pw, confirm_pw, ui_locales)
        error = not success

    _dh = DictionaryHelper(ui_locales)
    extras_dict = _dh.prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    settings_dict = _dh.prepare_settings_dict(success, old_pw, new_pw, confirm_pw, error, message, db_user, request.application_url)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _t.get(_.settings),
        'project': project_name,
        'extras': extras_dict,
        'settings': settings_dict
    }


# message page, when logged in
@view_config(route_name='main_notification', renderer='templates/notifications.pt', permission='use')
def main_notifications(request):
    """
    View configuration for the content view. Only logged in user can reach this page.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_notifications', 'def', 'main')
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)

    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid, append_notifications=True)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': 'Messages',
        'project': project_name,
        'extras': extras_dict
    }


# news page for everybody
@view_config(route_name='main_news', renderer='templates/news.pt', permission='everybody')
def main_news(request):
    """
    View configuration for the news.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_news', 'def', 'main')
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    ui_locales = get_language(request)
    is_author = is_user_author(request_authenticated_userid)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': 'News',
        'project': project_name,
        'extras': extras_dict,
        'is_author': is_author,
        'news': news_handler.get_news(get_language(request))
    }


# public users page for everybody
@view_config(route_name='main_user', renderer='templates/user.pt', permission='everybody')
def main_user(request):
    """
    View configuration for the public users.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    request_authenticated_userid = request.authenticated_userid
    logger('main_user', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('main_user', 'def', 'main, request.params: ' + str(params))

    nickname = match_dict['nickname'] if 'nickname' in match_dict else ''
    nickname = nickname.replace('%20', ' ')
    logger('main_user', 'def', 'nickname: ' + str(nickname))

    current_user = get_user_by_private_or_public_nickname(nickname)
    if current_user is None:
        logger('main_user', 'def', 'no user: ' + str(nickname), error=True)
        return HTTPFound(location=UrlManager(request.application_url).get_404([request.path[1:]]))

    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    ui_locales = get_language(request)
    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    user_dict = user_manager.get_information_of(current_user, ui_locales)

    db_user_of_request = DBDiscussionSession.query(User).filter_by(nickname=request_authenticated_userid).first()
    can_send_notification = False
    if db_user_of_request:
        can_send_notification = current_user.uid != db_user_of_request.uid

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': user_dict['public_nick'],
        'project': project_name,
        'extras': extras_dict,
        'user': user_dict,
        'can_send_notification': can_send_notification
    }


# imprint
@view_config(route_name='main_imprint', renderer='templates/imprint.pt', permission='everybody')
def main_imprint(request):
    """
    View configuration for the imprint.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_imprint', 'def', 'main')
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    import pkg_resources
    extras_dict.update({'pyramid_version': pkg_resources.get_distribution('pyramid').version})
    try:
        # extras_dict.update({'dbas_build': check_output(['git', 'rev-parse', '--short', 'HEAD'])})  # hash only
        extras_dict.update({'dbas_build': check_output(["git", "describe"])})
    except CalledProcessError:
        extras_dict.update({'dbas_build': full_version})

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.imprint),
        'project': project_name,
        'extras': extras_dict,
        'imprint': get_changelog(5)
    }


# imprint
@view_config(route_name='main_publications', renderer='templates/publications.pt', permission='everybody')
def main_publications(request):
    """
    View configuration for the publications.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_publications', 'def', 'main')
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.publications),
        'project': project_name,
        'extras': extras_dict
    }


# imprint
@view_config(route_name='main_rss', renderer='templates/rss.pt', permission='everybody')
def main_rss(request):
    """
    View configuration for the publications.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_rss', 'def', 'main')
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    rss = get_list_of_all_feeds(ui_locales)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': 'RSS',
        'project': project_name,
        'extras': extras_dict,
        'rss': rss
    }


# 404 page
@notfound_view_config(renderer='templates/404.pt')
def notfound(request):
    """
    View configuration for the 404 page.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('notfound', 'def', 'main in ' + str(request.method) + '-request' +
           ', path: ' + request.path +
           ', view name: ' + request.view_name +
           ', params: ' + str(request.params))
    path = request.path
    if path.startswith('/404/'):
        path = path[4:]

    param_error = True if 'param_error' in request.params and request.params['param_error'] == 'true' else False
    revoked_content = True if 'revoked_content' in request.params and request.params['revoked_content'] == 'true' else False

    request.response.status = 404
    ui_locales = get_language(request)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    # return HTTPFound(location=UrlManager(request.application_url, for_api=False).get_404([request.path[1:]]))

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': 'Error',
        'project': project_name,
        'page_notfound_viewname': path,
        'extras': extras_dict,
        'param_error': param_error,
        'revoked_content': revoked_content
    }


# ####################################
# DISCUSSION                         #
# ####################################


# content page
@view_config(route_name='discussion_init', renderer='templates/content.pt', permission='everybody')
def discussion_init(request, for_api=False, api_data=None):
    """
    View configuration for the content view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data: Dictionary, containing data of a user who logged in via API
    :return: dictionary
    """
    # '/a*slug'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    logger('discussion_init', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('discussion_init', 'def', 'main, request.params: ' + str(params))
    request_authenticated_userid = request.authenticated_userid

    nickname, session_expired, history = preparation_for_view(for_api, api_data, request, request_authenticated_userid)
    if session_expired:
        return user_logout(request, True)

    count_of_slugs = len(match_dict['slug']) if 'slug' in match_dict and isinstance(match_dict['slug'], ()) else 1
    if count_of_slugs > 1:
        logger('discussion_init', 'def', 'to many slugs', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]], True))

    ui_locales = get_language(request)
    if for_api:
        slug = match_dict['slug'] if 'slug' in match_dict else ''
    else:
        slug = match_dict['slug'][0] if 'slug' in match_dict and len(match_dict['slug']) > 0 else ''

    last_topic = history_helper.get_saved_issue(nickname)
    issue      = last_topic if len(slug) == 0 and last_topic != 0 else issue_helper.get_id_of_slug(slug, request, True)

    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict      = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, for_api)
    item_dict       = ItemDictHelper(disc_ui_locales, issue, request.application_url, for_api).get_array_for_start(nickname)
    history_helper.save_issue_uid(issue, nickname)

    discussion_dict = DiscussionDictHelper(disc_ui_locales, nickname=nickname, main_page=request.application_url, slug=slug)\
        .get_dict_for_start(position_count=(len(item_dict['elements'])))
    extras_dict     = DictionaryHelper(ui_locales, disc_ui_locales).prepare_extras_dict(slug, False, True,
                                                                                        False, True, request,
                                                                                        application_url=request.application_url,
                                                                                        for_api=for_api, nickname=request_authenticated_userid)

    if len(item_dict['elements']) == 1:
        DictionaryHelper(disc_ui_locales, disc_ui_locales).add_discussion_end_text(discussion_dict, extras_dict, nickname, at_start=True)

    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict

    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# attitude page
@view_config(route_name='discussion_attitude', renderer='templates/content.pt', permission='everybody')
def discussion_attitude(request, for_api=False, api_data=None):
    """
    View configuration for the content view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data:
    :return: dictionary
    """
    # '/discuss/{slug}/attitude/{statement_id}'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    request_authenticated_userid = request.authenticated_userid
    logger('discussion_attitude', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('discussion_attitude', 'def', 'main, request.params: ' + str(params))

    nickname, session_expired, history = preparation_for_view(for_api, api_data, request, request_authenticated_userid)
    if session_expired:
        return user_logout(request, True)

    ui_locales      = get_language(request)
    slug            = match_dict['slug'] if 'slug' in match_dict else ''
    statement_id    = match_dict['statement_id'][0] if 'statement_id' in match_dict else ''
    issue           = issue_helper.get_id_of_slug(slug, request, True) if len(slug) > 0 else issue_helper.get_issue_id(request)

    if not is_integer(statement_id, True) \
            or not check_belonging_of_statement(issue, statement_id):
        logger('discussion_attitude', 'def', 'param error', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]], True))
    if is_statement_forbidden(statement_id):
        logger('discussion_attitude', 'def', 'forbidden statement', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]], revoked_content=True))

    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, for_api)

    discussion_dict = DiscussionDictHelper(disc_ui_locales, nickname, history, main_page=request.application_url, slug=slug)\
        .get_dict_for_attitude(statement_id)
    if not discussion_dict:
        logger('discussion_attitude', 'def', 'no discussion dict', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([slug, statement_id]))

    item_dict = ItemDictHelper(disc_ui_locales, issue, request.application_url, for_api, path=request.path, history=history)\
        .prepare_item_dict_for_attitude(statement_id)
    extras_dict = DictionaryHelper(ui_locales, disc_ui_locales).prepare_extras_dict(issue_dict['slug'], False, True,
                                                                                    False, True, request,
                                                                                    application_url=request.application_url,
                                                                                    for_api=for_api, nickname=request_authenticated_userid)
    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict

    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# justify page
@view_config(route_name='discussion_justify', renderer='templates/content.pt', permission='everybody')
def discussion_justify(request, for_api=False, api_data=None):
    """
    View configuration for the content view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data:
    :return: dictionary
    """
    # '/discuss/{slug}/justify/{statement_or_arg_id}/{mode}*relation'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('discussion_justify', 'def', 'main, request.matchdict: ' + str(request.matchdict))
    logger('discussion_justify', 'def', 'main, request.params: ' + str(request.params))
    request_authenticated_userid = request.authenticated_userid

    nickname, session_expired, history = preparation_for_view(for_api, api_data, request, request_authenticated_userid)
    if session_expired:
        return user_logout(request, True)

    ui_locales = get_language(request)
    slug, statement_or_arg_id, mode, supportive, relation, issue, disc_ui_locales, issue_dict = prepare_parameter_for_justification(request, for_api)

    item_dict, discussion_dict, extras_dict = handle_justification_step(request, for_api, api_data, ui_locales, nickname)
    if type(item_dict) is HTTPFound:
        return item_dict

    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict
    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# reaction page
@view_config(route_name='discussion_reaction', renderer='templates/content.pt', permission='everybody')
def discussion_reaction(request, for_api=False, api_data=None):
    """
    View configuration for the content view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data:
    :return: dictionary
    """
    # '/discuss/{slug}/reaction/{arg_id_user}/{mode}*arg_id_sys'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    logger('discussion_reaction', 'def', 'main, request.matchdict: ' + str(match_dict))
    request_authenticated_userid = request.authenticated_userid

    slug            = match_dict['slug'] if 'slug' in match_dict else ''
    arg_id_user     = match_dict['arg_id_user'] if 'arg_id_user' in match_dict else ''
    attack          = match_dict['mode'] if 'mode' in match_dict else ''
    arg_id_sys      = match_dict['arg_id_sys'] if 'arg_id_sys' in match_dict else ''
    tmp_argument    = DBDiscussionSession.query(Argument).get(arg_id_user)
    issue           = issue_helper.get_id_of_slug(slug, request, True) if len(slug) > 0 else issue_helper.get_issue_id(request)

    valid_reaction = check_reaction(arg_id_user, arg_id_sys, attack)
    if not tmp_argument or not valid_reaction\
            or not valid_reaction and not check_belonging_of_argument(issue, arg_id_user)\
            or not valid_reaction and not check_belonging_of_argument(issue, arg_id_sys):
        logger('discussion_reaction', 'def', 'wrong belonging of arguments', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]]))

    supportive = tmp_argument.is_supportive
    nickname, session_expired, history = preparation_for_view(for_api, api_data, request, request_authenticated_userid)
    if session_expired:
        return user_logout(request, True)

    # sanity check
    if not [c for c in ('undermine', 'rebut', 'undercut', 'support', 'overbid', 'end') if c in attack]:
        logger('discussion_reaction', 'def', 'wrong value in attack', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]], True))
    ui_locales      = get_language(request)

    # set votes and reputation
    add_rep, broke_limit = add_reputation_for(nickname, rep_reason_first_argument_click)
    # ATM NOT NEEDED, BECAUSE BROKE LIMIT WILL BE SET AS DATA TAG INTO THE TEMPLATE
    # send message if the user is now able to review
    # if broke_limit:
    #     _t = Translator(ui_locales)
    #     try:
    #         args = (nickname, _t.get(_.youAreAbleToReviewNow), request.application_url + '/review', False, 5, )
    #         _thread.start_new_thread(send_request_for_info_popup_to_socketio_with_delay, args)
    #     except:
    #         logger('discussion_reaction', 'def', 'unable to start thread', error=True)

    add_vote_for_argument(arg_id_user, nickname)

    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict      = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, for_api)

    _dh             = DictionaryHelper(ui_locales, disc_ui_locales)
    _ddh            = DiscussionDictHelper(disc_ui_locales, nickname, history, main_page=request.application_url, slug=slug)
    _idh            = ItemDictHelper(disc_ui_locales, issue, request.application_url, for_api, path=request.path, history=history)
    discussion_dict = _ddh.get_dict_for_argumentation(arg_id_user, supportive, arg_id_sys, attack, history, nickname)
    item_dict       = _idh.get_array_for_reaction(arg_id_sys, arg_id_user, supportive, attack, discussion_dict['gender'])
    extras_dict     = _dh.prepare_extras_dict(slug, True, True, True, True, request, argument_id=arg_id_sys,
                                              application_url=request.application_url, for_api=for_api,
                                              argument_for_island=arg_id_user, attack=attack,
                                              nickname=request_authenticated_userid, broke_limit=broke_limit)

    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict

    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# finish page
@view_config(route_name='discussion_finish', renderer='templates/finish.pt', permission='everybody')
def discussion_finish(request):
    """

    :param request: request of the web server
    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    logger('discussion_finish', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('discussion_finish', 'def', 'main, request.params: ' + str(params))
    ui_locales      = get_language(request)
    nickname        = request.authenticated_userid
    session_expired = user_manager.update_last_action(nickname)
    history_helper.save_path_in_database(nickname, request.path)
    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, nickname)
    summary_dict = user_manager.get_summary_of_today(nickname)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': 'Finish',
        'project': project_name,
        'extras': extras_dict,
        'summary': summary_dict,
        'show_summary': len(summary_dict) != 0
    }


# choosing page
@view_config(route_name='discussion_choose', renderer='templates/content.pt', permission='everybody')
def discussion_choose(request, for_api=False, api_data=None):
    """
    View configuration for the choosing view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data:
    :return: dictionary
    """
    # '/discuss/{slug}/choose/{is_argument}/{supportive}/{id}*pgroup_ids'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    logger('discussion_choose', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('discussion_choose', 'def', 'main, request.params: ' + str(params))

    request_authenticated_userid = request.authenticated_userid
    slug            = match_dict['slug'] if 'slug' in match_dict else ''
    is_argument     = match_dict['is_argument'] if 'is_argument' in match_dict else ''
    is_supportive   = match_dict['supportive'] if 'supportive' in match_dict else ''
    uid             = match_dict['id'] if 'id' in match_dict else ''
    pgroup_ids      = match_dict['pgroup_ids'] if 'id' in match_dict else ''

    is_argument = True if is_argument is 't' else False
    is_supportive = True if is_supportive is 't' else False

    ui_locales      = get_language(request)
    issue           = issue_helper.get_id_of_slug(slug, request, True) if len(slug) > 0 else issue_helper.get_issue_id(request)
    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict      = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, for_api)

    for pgroup in pgroup_ids:
        if not is_integer(pgroup):
            logger('discussion_choose', 'def', 'integer error', error=True)
            return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]]))

    if not check_belonging_of_premisegroups(issue, pgroup_ids) or not is_integer(uid):
        logger('discussion_choose', 'def', 'wrong belonging of pgroup', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]]))

    nickname, session_expired, history = preparation_for_view(for_api, api_data, request, request_authenticated_userid)
    if session_expired:
        return user_logout(request, True)

    discussion_dict = DiscussionDictHelper(ui_locales, nickname, history, main_page=request.application_url, slug=slug)\
        .get_dict_for_choosing(uid, is_argument, is_supportive)
    item_dict       = ItemDictHelper(disc_ui_locales, issue, request.application_url, for_api, path=request.path, history=history)\
        .get_array_for_choosing(uid, pgroup_ids, is_argument, is_supportive, nickname)
    if not item_dict:
        logger('discussion_choose', 'def', 'no item dict', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]]))

    extras_dict     = DictionaryHelper(ui_locales, disc_ui_locales).prepare_extras_dict(slug, False, True,
                                                                                        True, True, request,
                                                                                        application_url=request.application_url,
                                                                                        for_api=for_api, nickname=request_authenticated_userid)

    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict

    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# jump page
@view_config(route_name='discussion_jump', renderer='templates/content.pt', permission='everybody')
def discussion_jump(request, for_api=False, api_data=None):
    """
    View configuration for the jump view.

    :param request: request of the web server
    :param for_api: Boolean
    :param api_data:
    :return: dictionary
    """
    # '/discuss/{slug}/jump/{arg_id}'
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    match_dict = request.matchdict
    params = request.params
    request_authenticated_userid = request.authenticated_userid
    logger('discussion_jump', 'def', 'main, request.matchdict: ' + str(match_dict))
    logger('discussion_jump', 'def', 'main, request.params: ' + str(params))

    nickname = get_nickname(request_authenticated_userid, for_api, api_data)
    history = params['history'] if 'history' in params else ''

    if for_api and api_data:
        slug = api_data["slug"]
        arg_uid = api_data["arg_uid"]
    else:
        slug = match_dict['slug'] if 'slug' in match_dict else ''
        arg_uid = match_dict['arg_id'] if 'arg_id' in match_dict else ''

    session_expired = user_manager.update_last_action(nickname)
    history_helper.save_path_in_database(nickname, request.path)
    history_helper.save_history_in_cookie(request, request.path, history)
    if session_expired:
        return user_logout(request, True)

    ui_locales = get_language(request)
    issue = issue_helper.get_id_of_slug(slug, request, True) if len(slug) > 0 else issue_helper.get_issue_id(request)
    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, for_api)

    if not check_belonging_of_argument(issue, arg_uid):
        logger('discussion_choose', 'def', 'no item dict', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=for_api).get_404([request.path[1:]]))

    _ddh = DiscussionDictHelper(disc_ui_locales, nickname, history, main_page=request.application_url, slug=slug)
    _idh = ItemDictHelper(disc_ui_locales, issue, request.application_url, for_api, path=request.path, history=history)
    discussion_dict = _ddh.get_dict_for_jump(arg_uid)
    item_dict = _idh.get_array_for_jump(arg_uid, slug, for_api)
    extras_dict = DictionaryHelper(ui_locales, disc_ui_locales).prepare_extras_dict(slug, False, True,
                                                                                    True, True, request,
                                                                                    application_url=request.application_url,
                                                                                    for_api=for_api, nickname=request_authenticated_userid)

    return_dict = dict()
    return_dict['issues'] = issue_dict
    return_dict['discussion'] = discussion_dict
    return_dict['items'] = item_dict
    return_dict['extras'] = extras_dict

    if for_api:
        return return_dict
    else:
        return_dict['layout'] = base_layout()
        return_dict['language'] = str(ui_locales)
        return_dict['title'] = issue_dict['title']
        return_dict['project'] = project_name
        return return_dict


# ####################################
# REVIEW                             #
# ####################################

# index page for reviews
@view_config(route_name='review_index', renderer='templates/review.pt', permission='use')
def main_review(request):
    """
    View configuration for the review index.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('main_review', 'main', 'def ' + str(request.matchdict))
    ui_locales = get_language(request)
    nickname = request.authenticated_userid
    session_expired = user_manager.update_last_action(nickname)
    history_helper.save_path_in_database(nickname, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    issue = issue_helper.get_issue_id(request)
    disc_ui_locales = get_discussion_language(request, issue)
    issue_dict = issue_helper.prepare_json_of_issue(issue, request.application_url, disc_ui_locales, False)
    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, nickname)

    review_dict = review_queue_helper.get_review_queues_as_lists(request.application_url, _tn, nickname)
    count, all_rights = review_reputation_helper.get_reputation_of(nickname)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.review),
        'project': project_name,
        'extras': extras_dict,
        'review': review_dict,
        'privilege_list': review_reputation_helper.get_privilege_list(_tn),
        'reputation_list': review_reputation_helper.get_reputation_list(_tn),
        'issues': issue_dict,
        'reputation': {'count': count,
                       'has_all_rights': all_rights}
    }


# content page for reviews
@view_config(route_name='review_content', renderer='templates/review_content.pt', permission='use')
def review_content(request):
    """
    View configuration for the review content.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_content', 'main', 'def ' + str(request.matchdict))
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    subpage_name = request.matchdict['queue']
    subpage_dict = review_page_helper.get_subpage_elements_for(request, subpage_name,
                                                               request_authenticated_userid, _tn)
    if not subpage_dict['elements'] and not subpage_dict['has_access'] and not subpage_dict['no_arguments_to_review']:
        logger('review_content', 'def', 'subpage error', error=True)
        return HTTPFound(location=UrlManager(request.application_url, for_api=False).get_404([request.path[1:]]))

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.review),
        'project': project_name,
        'extras': extras_dict,
        'subpage': subpage_dict,
        'lock_time': review_queue_helper.max_lock_time_in_sec
    }


# history page for reviews
@view_config(route_name='review_history', renderer='templates/review_history.pt', permission='use')
def review_history(request):
    """
    View configuration for the review history.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_history', 'main', 'def ' + str(request.matchdict))
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    history = review_history_helper.get_review_history(request.application_url, request_authenticated_userid, _tn)
    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)
    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.review_history),
        'project': project_name,
        'extras': extras_dict,
        'history': history
    }


# history page for reviews
@view_config(route_name='review_ongoing', renderer='templates/review_history.pt', permission='use')
def ongoing_history(request):
    """
    View configuration for the current reviews.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('ongoing_history', 'main', 'def ' + str(request.matchdict))
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    history = review_history_helper.get_ongoing_reviews(request.application_url, request_authenticated_userid, _tn)
    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.review_history),
        'project': project_name,
        'extras': extras_dict,
        'history': history
    }


# reputation_borders page for reviews
@view_config(route_name='review_reputation', renderer='templates/review_reputation.pt', permission='use')
def review_reputation(request):
    """
    View configuration for the review reputation_borders.

    :return: dictionary with title and project name as well as a value, weather the user is logged in
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_reputation', 'main', 'def ' + str(request.matchdict))
    ui_locales = get_language(request)
    request_authenticated_userid = request.authenticated_userid
    session_expired = user_manager.update_last_action(request_authenticated_userid)
    history_helper.save_path_in_database(request_authenticated_userid, request.path)
    _tn = Translator(ui_locales)
    if session_expired:
        return user_logout(request, True)

    extras_dict = DictionaryHelper(ui_locales).prepare_extras_dict_for_normal_page(request, request_authenticated_userid)

    reputation_dict = review_history_helper.get_reputation_history_of(request_authenticated_userid, _tn)

    return {
        'layout': base_layout(),
        'language': str(ui_locales),
        'title': _tn.get(_.review),
        'project': project_name,
        'extras': extras_dict,
        'reputation': reputation_dict
    }


# #####################################
# ADDITIONAL AJAX STUFF # USER THINGS #
# #####################################


# ajax - getting complete track of the user
@view_config(route_name='ajax_get_user_history', renderer='json')
def get_user_history(request):
    """
    Request the complete user track.

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('get_user_history', 'def', 'main')
    ui_locales = get_language(request)
    return_list = history_helper.get_history_from_database(request_authenticated_userid, ui_locales)
    return json.dumps(return_list)


# ajax - getting all text edits
@view_config(route_name='ajax_get_all_posted_statements', renderer='json')
def get_all_posted_statements(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('get_all_posted_statements', 'def', 'main')
    ui_locales = get_language(request)
    return_array, edits = user_manager.get_textversions_of_user(request_authenticated_userid, ui_locales)
    return json.dumps(return_array)


# ajax - getting all text edits
@view_config(route_name='ajax_get_all_edits', renderer='json')
def get_all_edits_of_user(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('get_all_edits_of_user', 'def', 'main')
    ui_locales = get_language(request)
    statements, return_array = user_manager.get_textversions_of_user(request_authenticated_userid, ui_locales)
    return json.dumps(return_array)


# ajax - getting all votes for arguments
@view_config(route_name='ajax_get_all_argument_votes', renderer='json')
def get_all_argument_votes(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('get_all_argument_votes', 'def', 'main')
    ui_locales = get_language(request)
    return_array = user_manager.get_votes_of_user(request_authenticated_userid, True, ui_locales)
    return json.dumps(return_array)


# ajax - getting all votes for statements
@view_config(route_name='ajax_get_all_statement_votes', renderer='json')
def get_all_statement_votes(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)
    logger('get_all_statement_votes', 'def', 'main')
    ui_locales = get_language(request)
    return_array = user_manager.get_votes_of_user(request_authenticated_userid, False, ui_locales)
    return json.dumps(return_array)


# ajax - deleting complete history of the user
@view_config(route_name='ajax_delete_user_history', renderer='json')
def delete_user_history(request):
    """
    Request the complete user history.

    :param request: request of the web server
    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)

    logger('delete_user_history', 'def', 'main')
    history_helper.delete_history_in_database(request_authenticated_userid)
    return_dict = dict()
    return_dict['removed_data'] = 'true'  # necessary

    return json.dumps(return_dict)


# ajax - deleting complete history of the user
@view_config(route_name='ajax_delete_statistics', renderer='json')
def delete_statistics(request):
    """
    Request the complete user history.

    :param request: request of the web server
    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)

    logger('delete_statistics', 'def', 'main')

    return_dict = dict()
    return_dict['removed_data'] = 'true' if clear_vote_and_seen_values_of_user(request_authenticated_userid) else 'false'

    return json.dumps(return_dict)


# ajax - user login
@view_config(route_name='ajax_user_login', renderer='json')
def user_login(request, nickname=None, password=None, for_api=False, keep_login=False):
    """
    Will login the user by his nickname and password

    :param request: request of the web server
    :param nickname: Manually provide nickname (e.g. from API)
    :param password: Manually provide password (e.g. from API)
    :param for_api: Manually provide boolean (e.g. from API)
    :param keep_login: Manually provide boolean (e.g. from API)
    :return: dict() with error
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('user_login', 'def', 'main, request.params: ' + str(request.params))

    lang = get_language(request)
    _tn = Translator(lang)
    error = ''

    try:
        value = login_user(request, nickname, password, for_api, keep_login, _tn)
        if type(value) == str:  # error
            error = value
        elif type(value) == dict:  # api
            return value
        elif type(value) == HTTPFound:  # success
            return value

    except KeyError as e:
        error = _tn.get(_.internalKeyError)
        logger('user_login', 'error', repr(e))

    return_dict = {'error': error}

    logger('user_login', 'return', str(return_dict))
    return json.dumps(return_dict)


# ajax - user logout
@view_config(route_name='ajax_user_logout', renderer='json')
def user_logout(request, redirect_to_main=False):
    """
    Will logout the user

    :param request: request of the web server
    :param redirect_to_main: Boolean
    :return: HTTPFound with forgotten headers
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('user_logout', 'def', 'main, user: ' + str(request.authenticated_userid) + ', redirect_to_main: ' + str(redirect_to_main))
    request.session.invalidate()
    headers = forget(request)
    if redirect_to_main:
        return HTTPFound(
            location=request.application_url + '?session_expired=true',
            headers=headers,
        )
    else:
        request.response.headerlist.extend(headers)
        return request.response


# ajax - registration of users
@view_config(route_name='ajax_user_registration', renderer='json')
def user_registration(request):
    """
    Registers new user

    :return: dict() with success and message
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('user_registration', 'def', 'main, request.params: ' + str(request.params))

    # default values
    success = ''
    error = ''
    info = ''
    return_dict = dict()

    ui_locales = request.params['lang'] if 'lang' in request.params else None
    if not ui_locales:
        ui_locales = get_language(request)
    _t = Translator(ui_locales)

    # getting params
    try:
        success, info = try_to_register_new_user_via_ajax(request, ui_locales)

    except KeyError as e:
        logger('user_registration', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['success']      = str(success)
    return_dict['error']        = str(error)
    return_dict['info']         = str(info)

    return json.dumps(return_dict)


# ajax - password requests
@view_config(route_name='ajax_user_password_request', renderer='json')
def user_password_request(request):
    """
    Sends an email, when the user requests his password

    :return: dict() with success and message
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('user_password_request', 'def', 'main, request.params: ' + str(request.params))

    success = ''
    info = ''
    return_dict = dict()
    ui_locales = request.params['lang'] if 'lang' in request.params else None
    if not ui_locales:
        ui_locales = get_language(request)
    _t = Translator(ui_locales)

    try:
        success, error, info = request_password(request, ui_locales)

    except KeyError as e:
        logger('user_password_request', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['success'] = str(success)
    return_dict['error']   = str(error)
    return_dict['info']    = str(info)

    logger('user_password_request', 'success', str(success))
    logger('user_password_request', 'error', str(error))
    logger('user_password_request', 'info', str(info))

    return json.dumps(return_dict)


# ajax - set boolean for receiving information
@view_config(route_name='ajax_set_user_setting', renderer='json')
def set_user_settings(request):
    """
    Will logout the user

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_user_settings', 'def', 'main, request.params: ' + str(request.params))
    _tn = Translator(get_language(request))

    try:
        error = ''
        public_nick = ''
        public_page_url = ''
        gravatar_url = ''
        settings_value = True if request.params['settings_value'] == 'True' else False
        service = request.params['service']
        db_user = DBDiscussionSession.query(User).filter_by(nickname=request.authenticated_userid).first()
        if db_user:
            public_nick = db_user.public_nickname
            db_setting = DBDiscussionSession.query(Settings).get(db_user.uid)

            if service == 'mail':
                db_setting.set_send_mails(settings_value)

            elif service == 'notification':
                db_setting.set_send_notifications(settings_value)

            elif service == 'public_nick':
                db_setting.set_show_public_nickname(settings_value)
                if settings_value:
                    db_user.set_public_nickname(db_user.nickname)
                elif db_user.nickname == db_user.public_nickname:
                    user_manager.refresh_public_nickname(db_user)
                public_nick = db_user.public_nickname
            else:
                error = _tn.get(_.keyword)

            transaction.commit()
            public_page_url = request.application_url + '/user/' + (db_user.nickname if settings_value else public_nick)
            gravatar_url = get_profile_picture(db_user, 80, ignore_privacy_settings=settings_value)
        else:
            error = _tn.get(_.checkNickname)
    except KeyError as e:
        error = _tn.get(_.internalKeyError)
        public_nick = ''
        public_page_url = ''
        gravatar_url = ''
        logger('set_user_settings', 'error', repr(e))

    return_dict = {'error': error, 'public_nick': public_nick, 'public_page_url': public_page_url, 'gravatar_url': gravatar_url}
    return json.dumps(return_dict)


# ajax - set boolean for receiving information
@view_config(route_name='ajax_set_user_language', renderer='json')
def set_user_language(request):
    """
    Will logout the user

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_user_language', 'def', 'main, request.params: ' + str(request.params))
    _tn = Translator(get_language(request))

    try:
        error = ''
        current_lang = ''
        ui_locales = request.params['ui_locales']
        db_user = DBDiscussionSession.query(User).filter_by(nickname=request.authenticated_userid).first()
        if db_user:
            db_settings = DBDiscussionSession.query(Settings).get(db_user.uid)
            if db_settings:
                db_language = DBDiscussionSession.query(Language).filter_by(ui_locales=ui_locales).first()
                if db_language:
                    current_lang = db_language.name
                    db_settings.set_lang_uid(db_language.uid)
                    transaction.commit()
                else:
                    error = _tn.get(_.internalError)
            else:
                error = _tn.get(_.checkNickname)
        else:
            error = _tn.get(_.checkNickname)
    except KeyError as e:
        error = _tn.get(_.internalKeyError)
        ui_locales = ''
        current_lang = ''
        logger('set_user_settings', 'error', repr(e))

    return_dict = {'error': error, 'ui_locales': ui_locales, 'current_lang': current_lang}
    return json.dumps(return_dict)


# ajax - sending notification
@view_config(route_name='ajax_send_notification', renderer='json')
def send_some_notification(request):
    """
    Set a new message into the inbox of an recipient, and the outbox of the sender.

    :return: dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('send_some_notification', 'def', 'main, request.params: ' + str(request.params))

    error = ''
    ts = ''
    uid = ''
    gravatar = ''
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    try:
        recipient = str(request.params['recipient']).replace('%20', ' ')
        title     = request.params['title']
        text      = request.params['text']
        db_recipient = get_user_by_private_or_public_nickname(recipient)
        if len(title) < 5 or len(text) < 5:
            error = _tn.get(_.empty_notification_input) + ' (' + _tn.get(_.minLength) + ': 5)'
        elif not db_recipient or recipient == 'admin' or recipient == nick_of_anonymous_user:
            error = _tn.get(_.recipientNotFound)
        else:
            db_author = DBDiscussionSession.query(User).filter_by(nickname=request.authenticated_userid).first()
            if not db_author:
                error = _tn.get(_.notLoggedIn)
            if db_author.uid == db_recipient.uid:
                error = _tn.get(_.senderReceiverSame)
            else:
                db_notification = send_notification(db_author, db_recipient, title, text, request.application_url)
                uid = db_notification.uid
                ts = sql_timestamp_pretty_print(db_notification.timestamp, ui_locales)
                gravatar = get_profile_picture(db_recipient, 20)

    except (KeyError, AttributeError):
        error = _tn.get(_.internalKeyError)

    return_dict = {'error': error, 'timestamp': ts, 'uid': uid, 'recipient_avatar': gravatar}
    return json.dumps(return_dict)


# #######################################
# ADDTIONAL AJAX STUFF # SET NEW THINGS #
# #######################################


# ajax - send new start statement
@view_config(route_name='ajax_set_new_start_statement', renderer='json')
def set_new_start_statement(request, for_api=False, api_data=None):
    """
    Inserts a new statement into the database, which should be available at the beginning

    :param request: request of the web server
    :param for_api: boolean
    :param api_data: api_data
    :return: a status code, if everything was successful
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_new_start_statement', 'def', 'ajax, request.params: ' + str(request.params))

    logger('set_new_start_statement', 'def', 'main')

    discussion_lang = get_discussion_language(request)
    _tn = Translator(discussion_lang)
    return_dict = dict()
    return_dict['error'] = ''
    return_dict['statement_uids'] = []
    try:
        if for_api and api_data:
            nickname  = api_data["nickname"]
            statement = api_data["statement"]
            issue     = api_data["issue_id"]
            slug      = api_data["slug"]
        else:
            nickname    = request.authenticated_userid
            statement   = request.params['statement']
            issue       = issue_helper.get_issue_id(request)
            slug        = DBDiscussionSession.query(Issue).get(issue).get_slug()

        # escaping will be done in QueryHelper().set_statement(...)
        user_manager.update_last_action(nickname)
        new_statement = insert_as_statements(request, statement, nickname, issue, is_start=True)

        if new_statement == -1:
            return_dict['error'] = _tn.get(_.notInsertedErrorBecauseEmpty) + ' (' + _tn.get(_.minLength) + ': 10)'
        elif new_statement == -2:
            return_dict['error'] = _tn.get(_.noRights)
        else:
            url = UrlManager(request.application_url, slug, for_api).get_url_for_statement_attitude(False, new_statement[0].uid)
            return_dict['url'] = url
            return_dict['statement_uids'].append(new_statement[0].uid)

            # add reputation
            add_rep, broke_limit = add_reputation_for(nickname, rep_reason_first_position)
            if not add_rep:
                add_rep, broke_limit = add_reputation_for(nickname, rep_reason_new_statement)
                # send message if the user is now able to review
            if broke_limit:
                # ui_locales = get_language(request)
                # _t = Translator(ui_locales)
                # send_request_for_info_popup_to_socketio(nickname, _t.get(_.youAreAbleToReviewNow), request.application_url + '/review')
                url += '#access-review'
                return_dict['url'] = url

    except KeyError as e:
        logger('set_new_start_statement', 'error', repr(e))
        return_dict['error'] = _tn.get(_.notInsertedErrorBecauseInternal)

    return json.dumps(return_dict)


# ajax - send new start premise
@view_config(route_name='ajax_set_new_start_premise', renderer='json')
def set_new_start_premise(request, for_api=False, api_data=None):
    """
    Sets new premise for the start

    :param request: request of the web server
    :param for_api: boolean
    :param api_data:
    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_new_start_premise', 'def', 'main, request.params: ' + str(request.params))

    return_dict = dict()
    lang = get_language(request)
    _tn = Translator(lang)
    try:
        if for_api and api_data:
            nickname      = api_data['nickname']
            premisegroups = api_data['statement']
            issue         = api_data['issue_id']
            conclusion_id = api_data['conclusion_id']
            supportive    = api_data['supportive']
        else:
            nickname        = request.authenticated_userid
            issue           = issue_helper.get_issue_id(request)
            premisegroups   = json.loads(request.params['premisegroups'])
            conclusion_id   = request.params['conclusion_id']
            supportive      = True if request.params['supportive'].lower() == 'true' else False

        # escaping will be done in QueryHelper().set_statement(...)
        user_manager.update_last_action(nickname)

        url, statement_uids, error = process_input_of_start_premises_and_receive_url(request, premisegroups,
                                                                                     conclusion_id, supportive, issue,
                                                                                     nickname, for_api,
                                                                                     request.application_url, lang)

        return_dict['error'] = error
        return_dict['statement_uids'] = statement_uids

        # add reputation
        add_rep, broke_limit = add_reputation_for(nickname, rep_reason_first_justification)
        if not add_rep:
            add_rep, broke_limit = add_reputation_for(nickname, rep_reason_new_statement)
            # send message if the user is now able to review
        if broke_limit:
            ui_locales = get_language(request)
            _t = Translator(ui_locales)
            send_request_for_info_popup_to_socketio(nickname, _t.get(_.youAreAbleToReviewNow),  request.application_url + '/review')
            url += '#access-review'
            return_dict['url'] = url

        if url == -1:
            return json.dumps(return_dict)

        return_dict['url'] = url
    except KeyError as e:
        logger('set_new_start_premise', 'error', repr(e))
        return_dict['error'] = _tn.get(_.notInsertedErrorBecauseInternal)

    return json.dumps(return_dict)


# ajax - send new premises
@view_config(route_name='ajax_set_new_premises_for_argument', renderer='json')
def set_new_premises_for_argument(request, for_api=False, api_data=None):
    """
    Sets a new premise for an argument

    :param request: request of the web server
    :param api_data:
    :param for_api: boolean
    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_new_premises_for_argument', 'def', 'main, request.params: ' + str(request.params))

    return_dict = dict()
    lang = get_language(request)
    _tn = Translator(lang)

    try:
        if for_api and api_data:
            nickname      = api_data['nickname']
            premisegroups = api_data['statement']
            issue         = api_data['issue_id']
            arg_uid       = api_data['arg_uid']
            attack_type   = api_data['attack_type']
        else:
            nickname = request.authenticated_userid
            premisegroups = json.loads(request.params['premisegroups'])
            issue = issue_helper.get_issue_id(request)
            arg_uid = request.params['arg_uid']
            attack_type = request.params['attack_type']

        # escaping will be done in QueryHelper().set_statement(...)
        url, statement_uids, error = process_input_of_premises_for_arguments_and_receive_url(request,
                                                                                             arg_uid, attack_type,
                                                                                             premisegroups, issue,
                                                                                             nickname, for_api,
                                                                                             request.application_url, lang)
        user_manager.update_last_action(nickname)

        return_dict['error'] = error
        return_dict['statement_uids'] = statement_uids

        # add reputation
        add_rep, broke_limit = add_reputation_for(nickname, rep_reason_first_new_argument)
        if not add_rep:
            add_rep, broke_limit = add_reputation_for(nickname, rep_reason_new_statement)
            # send message if the user is now able to review
        if broke_limit:
            # ui_locales = get_language(request)
            # _t = Translator(ui_locales)
            # send_request_for_info_popup_to_socketio(nickname, _t.get(_.youAreAbleToReviewNow), request.application_url + '/review')
            url += '#access-review'
            return_dict['url'] = url

        if url == -1:
            return json.dumps(return_dict)

        return_dict['url'] = url

    except KeyError as e:
        logger('set_new_premises_for_argument', 'error', repr(e))
        return_dict['error'] = _tn.get(_.notInsertedErrorBecauseInternal)

    logger('set_new_premises_for_argument', 'def', 'returning ' + str(return_dict))
    return json.dumps(return_dict)


# ajax - set new textvalue for a statement
@view_config(route_name='ajax_set_correction_of_statement', renderer='json')
def set_correction_of_statement(request):
    """
    Sets a new textvalue for a statement

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_correction_of_statement', 'def', 'main, request.params: ' + str(request.params))
    nickname = request.authenticated_userid
    user_manager.update_last_action(nickname)

    _tn = Translator(get_language(request))

    return_dict = dict()
    try:
        elements = json.loads(request.params['elements'])
        return_dict['error'] = review_queue_helper.add_proposals_for_statement_corrections(elements, nickname, _tn)
    except KeyError as e:
        return_dict['error'] = _tn.get(_.noCorrections)
        logger('set_correction_of_statement', 'error', repr(e))

    return json.dumps(return_dict)


# ajax - set notification as read
@view_config(route_name='ajax_notification_read', renderer='json')
def set_notification_read(request):
    """
    Set notification as read

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)

    logger('set_notification_read', 'def', 'main ' + str(request.params))
    return_dict = dict()
    ui_locales = get_language(request)
    _t = Translator(ui_locales)

    try:
        db_user = DBDiscussionSession.query(User).filter_by(nickname=request_authenticated_userid).first()
        if db_user:
            DBDiscussionSession.query(Message).filter(and_(Message.uid == request.params['id'],
                                                           Message.to_author_uid == db_user.uid,
                                                           Message.is_inbox == True)).first().set_read(True)
            transaction.commit()
            return_dict['unread_messages'] = count_of_new_notifications(request_authenticated_userid)
            return_dict['error'] = ''
        else:
            return_dict['error'] = _t.get(_.noRights)
    except KeyError as e:
        logger('set_message_read', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - deletes a notification
@view_config(route_name='ajax_notification_delete', renderer='json')
def set_notification_delete(request):
    """
    Request the removal of a notification

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)

    logger('set_notification_delete', 'def', 'main ' + str(request.params))
    return_dict = dict()
    ui_locales = get_language(request)
    _t = Translator(ui_locales)

    try:
        db_user = DBDiscussionSession.query(User).filter_by(nickname=request_authenticated_userid).first()
        if db_user:
            # inbox
            DBDiscussionSession.query(Message).filter(and_(Message.uid == request.params['id'],
                                                           Message.to_author_uid == db_user.uid,
                                                           Message.is_inbox == True)).delete()
            # send
            DBDiscussionSession.query(Message).filter(and_(Message.uid == request.params['id'],
                                                           Message.from_author_uid == db_user.uid,
                                                           Message.is_inbox == False)).delete()
            transaction.commit()
            return_dict['unread_messages'] = count_of_new_notifications(request_authenticated_userid)
            return_dict['total_in_messages'] = str(len(get_box_for(request_authenticated_userid, ui_locales, request.application_url, True)))
            return_dict['total_out_messages'] = str(len(get_box_for(request_authenticated_userid, ui_locales, request.application_url, False)))
            return_dict['error'] = ''
            return_dict['success'] = _t.get(_.messageDeleted)
        else:
            return_dict['error'] = _t.get(_.noRights)
            return_dict['success'] = ''
    except KeyError as e:
        logger('set_message_read', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)
        return_dict['success'] = ''

    return json.dumps(return_dict)


# ajax - set new issue
@view_config(route_name='ajax_set_new_issue', renderer='json')
def set_new_issue(request):
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    request_authenticated_userid = request.authenticated_userid
    user_manager.update_last_action(request_authenticated_userid)

    logger('set_new_issue', 'def', 'main ' + str(request.params))
    return_dict = dict()
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)
    was_set = False

    try:
        info = escape_string(request.params['info'])
        long_info = escape_string(request.params['long_info'])
        title = escape_string(request.params['title'])
        lang = escape_string(request.params['lang'])
        was_set, error = issue_helper.set_issue(info, long_info, title, lang, request_authenticated_userid, ui_locales)
        if was_set:
            db_issue = DBDiscussionSession.query(Issue).filter(and_(Issue.title == title,
                                                                    Issue.info == info)).first()
            return_dict['issue'] = issue_helper.get_issue_dict_for(db_issue, request.application_url, False, 0, ui_locales)
    except KeyError as e:
        logger('set_new_issue', 'error', repr(e))
        error = _tn.get(_.notInsertedErrorBecauseInternal)

    return_dict['error'] = '' if was_set else error
    return json.dumps(return_dict)


# ajax - set seen premisegroup
@view_config(route_name='ajax_set_seen_statements', renderer='json')
def set_seen_statements(request):
    """
    Set statements as seen, when they were hidden

    :return: json
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_seen_statements', 'def', 'main ' + str(request.params))
    return_dict = dict()
    ui_locales = get_language(request)
    _t = Translator(ui_locales)

    try:
        uids = json.loads(request.params['uids'])
        # are the statements connected to an argument?
        additional_argument = None
        if 'justify' in request.path:
            url = request.path[request.path.index('justify/') + len('justify/'):]
            additional_argument = int(url[:url.index('/')])

        error = process_seen_statements(uids, request.authenticated_userid, _t, additional_argument=additional_argument)
        return_dict['error'] = error
    except KeyError as e:
        logger('set_seen_statements', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ###################################
# ADDTIONAL AJAX STUFF # GET THINGS #
# ###################################


# ajax - getting changelog of a statement
@view_config(route_name='ajax_get_logfile_for_statements', renderer='json')
def get_logfile_for_some_statements(request):
    """
    Returns the changelog of a statement

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_logfile_for_statements', 'def', 'main, request.params: ' + str(request.params))
    user_manager.update_last_action(request.authenticated_userid)

    return_dict = dict()
    ui_locales = get_language(request)

    try:
        uids = json.loads(request.params['uids'])
        issue = request.params['issue']
        ui_locales = get_discussion_language(request, issue)
        return_dict = get_logfile_for_statements(uids, ui_locales, request.application_url)
        return_dict['error'] = ''
    except KeyError as e:
        logger('get_logfile_for_premisegroup', 'error', repr(e))
        _tn = Translator(ui_locales)
        return_dict['error'] = _tn.get(_.noCorrections)

    return json.dumps(return_dict)


# ajax - for shorten url
@view_config(route_name='ajax_get_shortened_url', renderer='json')
def get_shortened_url(request):
    """
    Shortens url with the help of a python lib

    :return: dictionary with shortend url
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    user_manager.update_last_action(request.authenticated_userid)

    logger('get_shortened_url', 'def', 'main')

    return_dict = dict()

    try:
        url = request.params['url']
        # google_api_key = 'AIzaSyAw0aPsBsAbqEJUP_zJ9Fifbhzs8xkNSw0' # browser is
        # google_api_key = 'AIzaSyDneaEJN9FNGUpXHDZahe9Rhb21FsFNS14' # server id
        # service = 'GoogleShortener'
        # service_url = 'https://goo.gl/'
        # shortener = Shortener(service, api_key=google_api_key)

        # bitly_login = 'dbashhu'
        # bitly_key = ''
        # bitly_token = 'R_d8c4acf2fb554494b65529314d1e11d1'

        # service = 'BitlyShortener'
        # service_url = 'https://bitly.com/'
        # shortener = Shortener(service, bitly_token=bitly_token)

        service = 'TinyurlShortener'
        service_ = 'Tinyurl'
        service_url = 'http://tinyurl.com/'
        shortener = Shortener(service_)

        short_url = format(shortener.short(url))
        return_dict['url'] = short_url
        return_dict['service'] = service
        return_dict['service_url'] = service_url

        return_dict['error'] = ''
    except KeyError as e:
        logger('get_shortened_url', 'error', repr(e))
        _tn = Translator(get_discussion_language(request))
        return_dict['error'] = _tn.get(_.internalKeyError)
    except ReadTimeout as e:
        logger('get_shortened_url', 'read timeout error', repr(e))
        _tn = Translator(get_discussion_language(request))
        return_dict['error'] = _tn.get(_.internalError)

    return json.dumps(return_dict)


# ajax - for getting all news
@view_config(route_name='ajax_get_news', renderer='json')
def get_news(request):
    """
    ajax interface for getting news

    :return: json-set with all news
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_news', 'def', 'main')
    return_dict = news_handler.get_news(get_language(request))
    return json.dumps(return_dict)


# ajax - for getting argument infos
@view_config(route_name='ajax_get_infos_about_argument', renderer='json')
def get_all_infos_about_argument(request):
    """
    ajax interface for getting a dump

    :return: json-set with everything
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_all_infos_about_argument', 'def', 'main, request.params: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        uid = request.params['uid']
        if not is_integer(uid):
            return_dict['error'] = _t.get(_.internalError)
        else:
            return_dict = get_infos_about_argument(uid, request.application_url, request.authenticated_userid, _t)
            return_dict['error'] = ''
    except KeyError as e:
        logger('get_infos_about_argument', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for getting all users with the same opinion
@view_config(route_name='ajax_get_user_with_same_opinion', renderer='json')
def get_users_with_same_opinion(request):
    """
    ajax interface for getting a dump
    :return: json-set with everything
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_users_with_same_opinion', 'def', 'main: ' + str(request.params))
    nickname = request.authenticated_userid
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    return_dict = dict()
    try:
        params = request.params
        ui_locales  = params['lang'] if 'lang' in params else 'en'
        uids        = params['uids']
        is_arg = params['is_argument'] == 'true' if 'is_argument' in params else False
        is_att = params['is_attitude'] == 'true' if 'is_attitude' in params else False
        is_rea = params['is_reaction'] == 'true' if 'is_reaction' in params else False
        is_pos = params['is_position'] == 'true' if 'is_position' in params else False
        is_sup = params['is_supporti'] if 'is_supporti' in params else None

        if is_arg:
            if is_rea:
                uids = json.loads(uids)
                return_dict = get_user_and_opinions_for_argument(uids, nickname, ui_locales, request.application_url, request.path)
            else:
                return_dict = get_user_with_same_opinion_for_argument(uids, nickname, ui_locales, request.application_url)
        elif is_pos:
            uids = json.loads(uids)
            uids = uids if isinstance(uids, list) else [uids]
            return_dict = get_user_with_same_opinion_for_statements(uids, is_sup, nickname, ui_locales, request.application_url)
        else:
            if is_att:
                return_dict = get_user_with_opinions_for_attitude(uids, nickname, ui_locales, request.application_url)
            else:
                uids = json.loads(uids)
                uids = uids if isinstance(uids, list) else [uids]
                return_dict = get_user_with_same_opinion_for_premisegroups(uids, nickname, ui_locales, request.application_url)
        return_dict['info'] = _tn.get(_.otherParticipantsDontHaveOpinionForThisStatement) if len(uids) == 0 else ''
        return_dict['error'] = ''
    except KeyError as e:
        logger('get_users_with_same_opinion', 'error', repr(e))
        return_dict['error'] = _tn.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for getting all users with the same opinion
@view_config(route_name='ajax_get_public_user_data', renderer='json')
def get_public_user_data(request):
    """

    :param request: request of the web server
    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_public_user_data', 'def', 'main: ' + str(request.params))
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    return_dict = dict()
    try:
        nickname = request.params['nickname']
        return_dict = user_manager.get_public_information_data(nickname, ui_locales)
        return_dict['error'] = '' if len(return_dict) != 0 else _tn.get(_.internalKeyError)

    except KeyError as e:
        logger('get_public_user_data', 'error', repr(e))
        return_dict['error'] = _tn.get(_.internalKeyError)

    return json.dumps(return_dict)


@view_config(route_name='ajax_get_arguments_by_statement_uid', renderer='json')
def get_arguments_by_statement_uid(request):
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_arguments_by_statement_uid', 'def', 'main: ' + str(request.matchdict))
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    return_dict = dict()
    try:
        uid = request.matchdict['uid']
        if not is_integer(uid):
            return_dict['error'] = _tn.get(_.internalKeyError)
        else:
            slug = get_slug_by_statement_uid(uid)
            _um = UrlManager(request.application_url, slug)
            return_dict['arguments'] = get_all_arguments_with_text_and_url_by_statement_id(uid, _um, True, is_jump=True)
            return_dict['error'] = ''

    except KeyError as e:
        logger('get_arguments_by_statement_uid', 'error', repr(e))
        return_dict['error'] = _tn.get(_.internalKeyError)

    return json.dumps(return_dict)


@view_config(route_name='ajax_get_references', renderer='json')
def get_references(request):
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('get_references', 'def', 'main: ' + str(request.params))
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    try:
        # uid is an integer if it is an argument and a list otherwise
        uid = json.loads(request.params['uid'])
        is_argument = True if str(request.params['is_argument']) == 'true' else False
        are_all_integer = all(is_integer(id) for id in uid) if isinstance(uid, list) else is_integer(uid)

        error = ''
        if are_all_integer:
            if is_argument:
                data, text = get_references_for_argument(uid, request.application_url)
            else:
                data, text = get_references_for_statements(uid, request.application_url)
        else:
            logger('get_references', 'def', 'uid is not an integer')
            data = ''
            text = ''
            error = _tn.get(_.internalKeyError)

    except KeyError as e:
        logger('get_references', 'error', repr(e))
        error = _tn.get(_.internalKeyError)

    return_dict = {'error': error,
                   'data': data,
                   'text': text}

    return json.dumps(return_dict)


@view_config(route_name='ajax_set_references', renderer='json')
def set_references(request):
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('set_references', 'def', 'main: ' + str(request.params))
    ui_locales = get_language(request)
    _tn = Translator(ui_locales)

    try:
        nickname    = request.authenticated_userid
        issue_uid   = issue_helper.get_issue_id(request)

        uid         = request.params['uid']
        reference   = escape_string(json.loads(request.params['reference']))
        source      = escape_string(json.loads(request.params['ref_source']))
        success     = set_reference(reference, source, nickname, uid, issue_uid)
        return_dict = {'error': '' if success else _tn.get(_.internalKeyError)}

    except KeyError as e:
        logger('set_references', 'error', repr(e))
        return_dict = {'error': _tn.get(_.internalKeyError)}

    return json.dumps(return_dict)


# ########################################
# ADDTIONAL AJAX STUFF # ADDITION THINGS #
# ########################################


# ajax - for language switch
@view_config(route_name='ajax_switch_language', renderer='json')
def switch_language(request):
    """
    Switches the language

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    user_manager.update_last_action(request.authenticated_userid)
    logger('switch_language', 'def', 'main, request.params: ' + str(request.params))

    return_dict = dict()
    ui_locales = None
    try:
        ui_locales = request.params['lang'] if 'lang' in request.params else None
        db_lang = DBDiscussionSession.query(Language).filter_by(ui_locales=ui_locales).first()
        if not db_lang or not ui_locales:
            ui_locales = get_language(request)
        request.response.set_cookie('_LOCALE_', str(ui_locales))
        request._LOCALE_ = ui_locales
        return_dict['error'] = ''
        return_dict['ui_locales'] = ui_locales
    except KeyError as e:
        logger('swich_language', 'error', repr(e))
        if not ui_locales:
            ui_locales = 'en'
        _t = Translator(ui_locales)
        return_dict['error'] = _t.get(_.internalError)

    return json.dumps(return_dict)


# ajax - for sending news
@view_config(route_name='ajax_send_news', renderer='json')
def send_news(request):
    """
    ajax interface for settings news

    :return: json-set with new news
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('send_news', 'def', 'main, request.params: ' + str(request.params))
    _tn = Translator(get_language(request))

    try:
        title = escape_string(request.params['title'])
        text = escape_string(request.params['text'])
        return_dict, success = news_handler.set_news(request, title, text, request.authenticated_userid, get_language(request), request.application_url)
        return_dict['error'] = '' if success else _tn.get(_.noRights)
    except KeyError as e:
        return_dict = dict()
        logger('send_news', 'error', repr(e))
        return_dict['error'] = _tn.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for fuzzy search
@view_config(route_name='ajax_fuzzy_search', renderer='json')
def fuzzy_search(request, for_api=False, api_data=None):
    """
    ajax interface for fuzzy string search

    :param request: request of the web server
    :param for_api: boolean
    :param api_data: data
    :return: json-set with all matched strings
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('fuzzy_search', 'def', 'main, for_api: ' + str(for_api) + ', request.params: ' + str(request.params))

    _tn = Translator(get_language(request))
    request_authenticated_userid = request.authenticated_userid

    try:
        value = api_data['value'] if for_api else request.params['value']
        mode = str(api_data['mode']) if for_api else str(request.params['type'])
        issue = api_data['issue'] if for_api else issue_helper.get_issue_id(request)
        extra = request.params['extra'] if 'extra' in request.params else None

        logger('Graph.lib', 'get_doj_data', 'main')

        try:
            url = auto_completion_url + '?issue={}&mode={}&value={}'.format(str(issue), str(mode), str(value))
            resp = requests.get(url)
            if resp.status_code == 200:
                return_dict = json.loads(resp.text)
                if for_api:
                    return return_dict
                return json.dumps(return_dict)

        except Exception as e:
            logger('fuzzy_search', 'def', 'Error grepping data via microserver: ' + str(e))

        return_dict = fuzzy_string_matcher.get_prediction(_tn, for_api, api_data, request_authenticated_userid, value, mode, issue, extra)

    except KeyError as e:
        return_dict = {'error': _tn.get(_.internalKeyError)}
        logger('fuzzy_search', 'error', repr(e))

    if for_api:
        return return_dict
    return json.dumps(return_dict)


# ajax - for additional service
@view_config(route_name='ajax_additional_service', renderer='json')
def additional_service(request):
    """

    :return: json-dict()
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('additional_service', 'def', 'main, request.params: ' + str(request.params))

    try:
        rtype = request.params['type']
        if rtype == "chuck":
            data = requests.get('http://api.icndb.com/jokes/random')
        else:
            data = requests.get('http://api.yomomma.info/')

        for a in data.json():
            logger('additional_service', 'main', str(a) + ': ' + str(data.json()[a]))

    except KeyError as e:
        logger('additional_service', 'error', repr(e))
        return json.dumps(dict())

    return data.json()


# #######################################
# ADDITIONAL AJAX STUFF # REVIEW THINGS #
# #######################################


# ajax - for flagging arguments
@view_config(route_name='ajax_flag_argument_or_statement', renderer='json')
def flag_argument_or_statement(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('flag_argument_or_statement', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = {'error': _t.get(_.internalError)}

    try:
        uid = request.params['uid']
        reason = request.params['reason']
        is_argument = True if request.params['is_argument'] == 'true' else False
        nickname = request.authenticated_userid
        db_user = DBDiscussionSession.query(User).filter_by(nickname=nickname).first()
        if not db_user:
            return_dict = {'error': _t.get(_.noRights)}
        else:
            db_reason = DBDiscussionSession.query(ReviewDeleteReason).filter_by(reason=reason).first()

            if not is_integer(uid):
                logger('flag_argument_or_statement', 'def', 'invalid uid', error=True)
            elif db_reason is None and reason != 'optimization':
                logger('flag_argument_or_statement', 'def', 'invalid reason', error=True)
            else:
                success, info, error = review_flag_helper.flag_argument(uid, reason, db_user, is_argument)
                return_dict = {
                    'success': '' if isinstance(success, str) else _t.get(success),
                    'info': '' if isinstance(info, str) else _t.get(info),
                    'error': '' if isinstance(error, str) else _t.get(error)
                }
    except KeyError as e:
        logger('flag_argument', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for feedback on flagged arguments
@view_config(route_name='ajax_review_delete_argument', renderer='json')
def review_delete_argument(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_delete_argument', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        should_delete = True if str(request.params['should_delete']) == 'true' else False
        review_uid = request.params['review_uid']
        nickname = request.authenticated_userid
        if not is_integer(review_uid):
            logger('review_delete_argument', 'def', 'invalid uid', error=True)
            error = _t.get(_.internalKeyError)
        else:
            error = review_main_helper.add_review_opinion_for_delete(nickname, should_delete, review_uid, _t, request.application_url)
            if len(error) == 0:
                send_request_for_recent_delete_review_to_socketio(nickname, request.application_url)
    except KeyError as e:
        logger('review_delete_argument', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['error'] = error
    return json.dumps(return_dict)


# ajax - for feedback on flagged arguments
@view_config(route_name='ajax_review_edit_argument', renderer='json')
def review_edit_argument(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_edit_argument', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        is_edit_okay = True if str(request.params['is_edit_okay']) == 'true' else False
        review_uid = request.params['review_uid']
        nickname = request.authenticated_userid
        if not is_integer(review_uid):
            logger('review_delete_argument', 'error', str(review_uid) + ' is no int')
            error = _t.get(_.internalKeyError)
        else:
            error = review_main_helper.add_review_opinion_for_edit(nickname, is_edit_okay, review_uid, _t, request.application_url)
            if len(error) == 0:
                send_request_for_recent_edit_review_to_socketio(nickname, request.application_url)
    except KeyError as e:
        logger('review_delete_argument', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['error'] = error
    return json.dumps(return_dict)


# ajax - for feedback on optimization arguments
@view_config(route_name='ajax_review_optimization_argument', renderer='json')
def review_optimization_argument(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_optimization_argument', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        should_optimized = True if str(request.params['should_optimized']) == 'true' else False
        review_uid = request.params['review_uid']
        new_data = json.loads(request.params['new_data']) if 'new_data' in request.params else None
        nickname = request.authenticated_userid

        if not is_integer(review_uid):
            logger('review_delete_argument', 'error', str(review_uid) + ' is no int')
            error = _t.get(_.internalKeyError)
        else:
            error = review_main_helper.add_review_opinion_for_optimization(nickname, should_optimized, review_uid, new_data, _t, request.application_url)

            if len(error) == 0:
                send_request_for_recent_optimization_review_to_socketio(nickname, request.application_url)

    except KeyError as e:
        logger('review_optimization_argument', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['error'] = error
    return json.dumps(return_dict)


# ajax - for undoing reviews
@view_config(route_name='ajax_undo_review', renderer='json')
def undo_review(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('undo_review', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        queue = request.params['queue']
        uid = request.params['uid']
        nickname = request.authenticated_userid

        if is_user_author(nickname):
            success, error = review_history_helper.revoke_old_decision(queue, uid, ui_locales, nickname)
            return_dict['success'] = success
            return_dict['error'] = error
        else:
            return_dict['info'] = _t.get(_.justLookDontTouch)

    except KeyError as e:
        logger('undo_review', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for canceling reviews
@view_config(route_name='ajax_cancel_review', renderer='json')
def cancel_review(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('cancel_review', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    try:
        queue = request.params['queue']
        uid = request.params['uid']
        nickname = request.authenticated_userid

        if is_user_author(nickname):
            success, error = review_history_helper.cancel_ongoing_decision(queue, uid, ui_locales, nickname)
            return_dict['success'] = success
            return_dict['error'] = error
        else:
            return_dict['info'] = _t.get(_.justLookDontTouch)

    except KeyError as e:
        logger('undo_review', 'error', repr(e))
        return_dict['error'] = _t.get(_.internalKeyError)

    return json.dumps(return_dict)


# ajax - for undoing reviews
@view_config(route_name='ajax_review_lock', renderer='json', require_csrf=False)
def review_lock(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('review_lock', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    info = ''
    error = ''
    success = ''
    is_locked = False

    try:
        review_uid = request.params['review_uid']
        lock = True if request.params['lock'] == 'true' else False
        is_locked = True

        if not is_integer(review_uid):
            error = _t.get(_.internalKeyError)
        else:
            if lock:
                success, info, error, is_locked = review_queue_helper.lock_optimization_review(request.authenticated_userid, review_uid, _t)
            else:
                review_queue_helper.unlock_optimization_review(review_uid)
                is_locked = False
                success = _t.get(_.dataUnlocked)

    except KeyError as e:
        logger('review_lock', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['info'] = info
    return_dict['error'] = error
    return_dict['success'] = success
    return_dict['is_locked'] = is_locked

    return json.dumps(return_dict)


# ajax - for revoking content
@view_config(route_name='ajax_revoke_content', renderer='json', require_csrf=False)
def revoke_some_content(request):
    """

    :return:
    """
    #  logger('- - - - - - - - - - - -', '- - - - - - - - - - - -', '- - - - - - - - - - - -')
    logger('revoke_some_content', 'def', 'main: ' + str(request.params))
    ui_locales = get_discussion_language(request)
    _t = Translator(ui_locales)
    return_dict = dict()

    info = ''
    success = ''
    is_deleted = False

    try:
        uid = request.params['uid']
        is_argument = True if request.params['is_argument'] == 'true' else False

        if not is_integer(uid):
            error = _t.get(_.internalKeyError)
        else:
            error, is_deleted = revoke_content(uid, is_argument, request.authenticated_userid, _t)

    except KeyError as e:
        logger('review_lock', 'error', repr(e))
        error = _t.get(_.internalKeyError)

    return_dict['info'] = info
    return_dict['error'] = error
    return_dict['success'] = success
    return_dict['is_deleted'] = is_deleted
    transaction.commit()

    return json.dumps(return_dict)
