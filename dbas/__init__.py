"""
Core compontent of D-BAS. The Dialog-Based Argumentation Software avoids the pitfalls of unstructured systems such as
asynchronous threaded discussions and it is usable by any participant without training while still supporting the full
complexity of real-world argumentation. The key idea is to let users exchange arguments with each other in the form of
a time-shifted dialog where arguments are presented and acted upon one-at-a-time.

.. sectionauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de>
"""

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from pyramid.static import QueryStringConstantCacheBuster

from dbas.security import groupfinder

from sqlalchemy import engine_from_config
from dbas.database import load_discussion_database, load_news_database

import logging
import time


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    # authentication and authorization
    authn_policy = AuthTktAuthenticationPolicy('89#s3cr3t_15', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()

    # log settings
    log = logging.getLogger(__name__)
    for k, v in settings.items():
        log.debug('__init__() '.upper() + 'main() <' + str(k) + ' : ' + str(v) + '>')

    # load database
    discussion_engine = engine_from_config(settings, 'sqlalchemy-discussion.')  # , connect_args={'client_encoding': 'utf8'}
    news_engine       = engine_from_config(settings, 'sqlalchemy-news.')  # , connect_args={'client_encoding': 'utf8'}
    load_discussion_database(discussion_engine)
    load_news_database(news_engine)

    # session management and cache region support with pyramid_beaker
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings)

    # creating the configurator
    settings = {'pyramid.default_locale_name': 'en',
                'mail.host': 'imap.googlemail.com',
                'mail.port': '465',
                'mail.username': 'dbas.hhu@gmail.com',
                'mail.password': 'orpcihtyuecxhoup',
                'mail.ssl': 'True',
                'mail.tls': 'False',
                'mail.default_sender': 'dbas.hhu@gmail.com'
                }

    # creating the configurator    cache_regions = set_cache_regions_from_settings
    config = Configurator(settings=settings, root_factory='dbas.security.RootFactory')
    config.add_translation_dirs('dbas:locale')  # add this before the locale negotiator
    config.set_default_csrf_options(require_csrf=True)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_session_factory(session_factory)

    # Include apps
    config.include('api', route_prefix='/api')
    config.include('graph', route_prefix='/graph')
    config.include('export', route_prefix='/export')
    config.include('admin', route_prefix='/admin')
    config.include('websocket', route_prefix='/ws')
    config.include('webhook', route_prefix='/deploy')

    # includings for the config
    config.include('pyramid_chameleon')
    config.include('pyramid_mailer')
    config.include('pyramid_beaker')

    config.add_static_view(name='static', path='dbas:static/', cache_max_age=3600)
    config.add_static_view(name='ws', path='websocket:static/', cache_max_age=3600)
    config.add_static_view(name='rv', path='review:static/', cache_max_age=3600)
    config.add_cache_buster('static', QueryStringConstantCacheBuster(str(int(time.time()))))
    config.add_cache_buster('websocket:static/', QueryStringConstantCacheBuster(str(int(time.time()))))

    # adding routes
    config.add_route('main_page', '/')
    config.add_route('main_contact', '/contact')
    config.add_route('main_settings', '/settings')
    config.add_route('main_notification', '/notifications')
    config.add_route('main_news', '/news')
    config.add_route('main_imprint', '/imprint')
    config.add_route('main_publications', '/publications')

    # ajax for navigation logic, administration, settings and editing/viewing log
    config.add_route('ajax_user_login', '{url:.*}ajax_user_login')
    config.add_route('ajax_user_logout', '{url:.*}ajax_user_logout')
    config.add_route('ajax_set_new_start_statement', '/{url:.*}ajax_set_new_start_statement')
    config.add_route('ajax_set_new_start_premise', '/{url:.*}ajax_set_new_start_premise')
    config.add_route('ajax_set_new_premises_for_argument', '/{url:.*}ajax_set_new_premises_for_argument')
    config.add_route('ajax_set_correcture_of_statement', '/{url:.*}ajax_set_correcture_of_statement')
    config.add_route('ajax_set_new_issue', '/{url:.*}ajax_set_new_issue')
    config.add_route('ajax_get_logfile_for_statement', '/{url:.*}ajax_get_logfile_for_statement')
    config.add_route('ajax_get_shortened_url', '/{url:.*}ajax_get_shortened_url')
    config.add_route('ajax_user_registration', '/{url:.*}ajax_user_registration')
    config.add_route('ajax_user_password_request', '/{url:.*}ajax_user_password_request')
    config.add_route('ajax_fuzzy_search', '/{url:.*}ajax_fuzzy_search')
    config.add_route('ajax_switch_language', '{url:.*}ajax_switch_language{params:.*}')
    config.add_route('ajax_send_notification', '{url:.*}ajax_send_notification')
    config.add_route('ajax_get_infos_about_argument', '/{url:.*}ajax_get_infos_about_argument')
    config.add_route('ajax_get_user_with_same_opinion', '/{url:.*}ajax_get_user_with_same_opinion')
    config.add_route('ajax_get_public_user_data', '/{url:.*}ajax_get_public_user_data')
    config.add_route('ajax_get_user_history', 'ajax_get_user_history')
    config.add_route('ajax_get_all_edits', 'ajax_get_all_edits')
    config.add_route('ajax_get_all_posted_statements', 'ajax_get_all_posted_statements')
    config.add_route('ajax_get_all_argument_votes', 'ajax_get_all_argument_votes')
    config.add_route('ajax_get_all_statement_votes', 'ajax_get_all_statement_votes')
    config.add_route('ajax_set_user_setting', 'ajax_set_user_setting')
    config.add_route('ajax_set_user_language', 'ajax_set_user_language')
    config.add_route('ajax_delete_user_history', 'ajax_delete_user_history')
    config.add_route('ajax_delete_statistics', 'ajax_delete_statistics')
    config.add_route('ajax_get_news', 'ajax_get_news')
    config.add_route('ajax_send_news', 'ajax_send_news')
    config.add_route('ajax_notification_read', 'ajax_notification_read')
    config.add_route('ajax_notification_delete', 'ajax_notification_delete')
    config.add_route('ajax_get_arguments_by_statement_uid', 'ajax_get_arguments_by_statement/{uid}')
    config.add_route('ajax_additional_service', '{stuff:.*}additional_service')
    config.add_route('ajax_flag_argument', '{url:.*}ajax_flag_argument')
    config.add_route('ajax_review_delete_argument', '{url:.*}ajax_review_delete_argument')
    config.add_route('ajax_review_optimization_argument', '{url:.*}ajax_review_optimization_argument')
    config.add_route('ajax_review_edit_argument', '{url:.*}ajax_review_edit_argument')
    config.add_route('ajax_undo_review', '{url:.*}ajax_undo_review')
    config.add_route('ajax_cancel_review', '{url:.*}ajax_cancel_review')
    config.add_route('ajax_review_lock', '{url:.*}ajax_review_lock')
    config.add_route('ajax_review_unlock', '{url:.*}ajax_review_unlock')

    # ajax for navigation logic at the end, otherwise the * pattern will do shit
    config.add_route('main_user', '/user/{nickname}')
    config.add_route('discussion_reaction', '/discuss/{slug}/reaction/{arg_id_user}/{mode}/{arg_id_sys}')
    config.add_route('discussion_justify', '/discuss/{slug}/justify/{statement_or_arg_id}/{mode}*relation')
    config.add_route('discussion_attitude', '/discuss/{slug}/attitude/*statement_id')
    config.add_route('discussion_choose', '/discuss/{slug}/choose/{is_argument}/{supportive}/{id}*pgroup_ids')
    config.add_route('discussion_jump', '/discuss/{slug}/jump/{arg_id}')
    config.add_route('discussion_finish', '/discuss/finish')
    config.add_route('discussion_init', '/discuss*slug')

    # review section
    config.add_route('review_index', '/review')
    config.add_route('review_reputation', '/review/reputation')
    config.add_route('review_history', '/review/history')
    config.add_route('review_ongoing', '/review/ongoing')
    config.add_route('review_content', '/review/{queue}')

    # read the input and start
    config.scan()
    return config.make_wsgi_app()
