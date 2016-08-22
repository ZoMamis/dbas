"""
Provides helping function for issues.

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

from slugify import slugify
import dbas.user_management as UserHandler

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, User, Issue, Language, Statement
from dbas.lib import sql_timestamp_pretty_print
from dbas.logger import logger
from dbas.strings.translator import Translator
from dbas.url_manager import UrlManager


def set_issue(info, title, lang, nickname, transaction, ui_locales):
    """
    Inserts new issue into database

    :param info: String
    :param title: String
    :param lang: String
    :param nickname: User.nickname
    :param transaction: transaction
    :param ui_locales: ui_locales
    :return: True, '' on success, False, String on error
    """
    _tn = Translator(ui_locales)

    db_user = DBDiscussionSession.query(User).filter_by(nickname=nickname).first()
    if not UserHandler.is_user_author(nickname):
        return False, _tn.get(_tn.noRights)

    if len(info) < 10:
        return False, (_tn.get(_tn.notInsertedErrorBecauseEmpty) + ' (' + _tn.get(_tn.minLength) + ': 10)')

    db_duplicates1 = DBDiscussionSession.query(Issue).filter_by(title=title).all()
    db_duplicates2 = DBDiscussionSession.query(Issue).filter_by(info=info).all()
    if db_duplicates1 or db_duplicates2:
        return False, _tn.get(_tn.duplicate)

    db_lang = DBDiscussionSession.query(Language).filter_by(ui_locales=lang).first()
    if not db_lang:
        return False, _tn.get(_tn.internalError)

    DBDiscussionSession.add(Issue(title=title, info=info, author_uid=db_user.uid, lang_uid=db_lang.uid))
    DBDiscussionSession.flush()

    transaction.commit()

    return True, ''


def __get_title_for_issue_uid(uid):
    """
    Returns the title or none for the issue uid

    :param uid: Issue.uid
    :return: String
    """
    #  logger('QueryHelper', 'get_title_for_issue_uid', str(uid))
    db_issue = DBDiscussionSession.query(Issue).filter_by(uid=uid).first()
    return db_issue.title if db_issue else 'none'


def __get_slug_for_issue_uid(uid):
    """
    Returns the slug of the title or none for the issue uid

    :param uid: Issue.uid
    :return: String
    """
    #  logger('QueryHelper', 'get_slug_for_issue_uid', str(uid))
    db_issue = DBDiscussionSession.query(Issue).filter_by(uid=uid).first()
    return slugify(db_issue.title) if db_issue else 'none'


def __get_info_for_issue_uid(uid):
    """
    Returns the slug or none for the issue uid

    :param uid: Issue.uid
    :return: String
    """
    #  logger('QueryHelper', 'get_info_for_issue_uid', str(uid))
    db_issue = DBDiscussionSession.query(Issue).filter_by(uid=uid).first()
    return db_issue.info if db_issue else 'none'


def __get_date_for_issue_uid(uid, lang):
    """
    Returns the date or none for the issue uid

    :param uid: Issue.uid
    :param lang: ui_locales ui_locales
    :return: String
    """
    #  logger('QueryHelper', 'get_date_for_issue_uid', str(uid))
    db_issue = DBDiscussionSession.query(Issue).filter_by(uid=uid).first()
    return sql_timestamp_pretty_print(db_issue.date, lang) if db_issue else 'none'


def prepare_json_of_issue(uid, application_url, lang, for_api):
    """
    Prepares slug, info, argument count and the date of the issue as dict

    :param uid: Issue.uid
    :param application_url: application_url
    :param lang: ui_locales
    :param for_api: Boolean
    :return: Issue-dict()
    """
    logger('issueHelper', 'prepare_json_of_issue', 'main')
    slug = __get_slug_for_issue_uid(uid)
    title = __get_title_for_issue_uid(uid)
    info = __get_info_for_issue_uid(uid)
    stat_count = get_number_of_statements(uid)
    date = __get_date_for_issue_uid(uid, lang)

    db_issues = DBDiscussionSession.query(Issue).all()
    all_array = []
    for issue in db_issues:
        issue_dict = get_issue_dict_for(issue, application_url, for_api, uid, lang)
        all_array.append(issue_dict)

    _t = Translator(lang)
    tooltip = _t.get(_t.discussionInfoTooltip1) + ' ' + date + ' '
    tooltip += _t.get(_t.discussionInfoTooltip2) + ' ' + str(stat_count) + ' '
    tooltip += (_t.get(_t.discussionInfoTooltip3sg if stat_count == 1 else _t.discussionInfoTooltip3pl))

    return {'slug': slug,
            'info': info,
            'title': title,
            'uid': uid,
            'stat_count': stat_count,
            'date': date,
            'all': all_array,
            'tooltip': tooltip,
            'intro': _t.get(_t.currentDiscussion)}


def get_number_of_arguments(issue):
    """
    Returns number of arguments for the issue

    :param issue: Issue Issue.uid
    :return: Integer
    """
    return len(DBDiscussionSession.query(Argument).filter_by(issue_uid=issue).all())


def get_number_of_statements(issue):
    """
    Returns number of statements for the issue

    :param issue: Issue Issue.uid
    :return: Integer
    """
    return len(DBDiscussionSession.query(Statement).filter_by(issue_uid=issue).all())


def get_issue_dict_for(issue, application_url, for_api, uid, lang):
    """
    Creates an dictionary for the issue

    :param issue: Issue
    :param application_url:
    :param for_api: Boolean
    :param uid: current selected Issue.uid
    :param lang: ui_locales
    :return: dict()
    """
    _um = UrlManager(application_url, issue.get_slug(), for_api)
    issue_dict = dict()
    issue_dict['uid']               = str(issue.uid)
    issue_dict['slug']              = issue.get_slug()
    issue_dict['title']             = issue.title
    issue_dict['url']               = _um.get_slug_url(False) if str(uid) != str(issue.uid) else ''
    issue_dict['review_url']        = _um.get_review_url(False) if str(uid) != str(issue.uid) else ''
    issue_dict['info']              = issue.info
    issue_dict['stat_count']        = get_number_of_statements(issue.uid)
    issue_dict['date']              = sql_timestamp_pretty_print(issue.date, lang)
    issue_dict['author']            = issue.users.public_nickname
    issue_dict['author_url']        = application_url + '/user/' + str(issue.users.public_nickname)
    issue_dict['enabled']           = 'disabled' if str(uid) == str(issue.uid) else 'enabled'
    return issue_dict


def get_id_of_slug(slug, request, save_id_in_session):
    """
    Returns the uid

    :param slug: slug
    :param request: self.request for a fallback
    :param save_id_in_session: Boolean
    :return: uid
    """
    db_issues = DBDiscussionSession.query(Issue).all()
    for issue in db_issues:
        if str(slugify(issue.title)) == str(slug):
            if save_id_in_session:
                request.session['issue'] = issue.uid
            return issue.uid
    return get_issue_id(request)


def get_issue_id(request):
    """
    Returns issue uid

    :param request: self.request
    :return: uid
    """
    # first matchdict, then params, then session, afterwards fallback
    issue = request.matchdict['issue'] if 'issue' in request.matchdict \
        else request.params['issue'] if 'issue' in request.params \
        else request.session['issue'] if 'issue' in request.session \
        else DBDiscussionSession.query(Issue).first().uid

    # save issue in session
    request.session['issue'] = 1 if str(issue) is 'undefined' else issue

    return issue


def get_title_for_slug(slug):
    """

    :param slug:
    :return:
    """
    db_issues = DBDiscussionSession.query(Issue).all()
    for issue in db_issues:
        if str(slugify(issue.title)) == str(slug):
            return issue.title
    return None
