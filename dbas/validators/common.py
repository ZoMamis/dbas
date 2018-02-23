"""
General validators with no need for a specific namespace.
"""

from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Language
from dbas.handler.language import get_language_from_cookie
from dbas.handler.user import update_last_action
from dbas.strings.keywords import Keywords as _
from dbas.strings.translator import Translator
from dbas.validators.lib import add_error, escape_if_string


def valid_language(request):
    """
    Given a nickname of a user, return the object from the database.

    :param request:
    :return:
    """
    lang = escape_if_string(request.json_body, 'lang')
    _tn = Translator(get_language_from_cookie(request))
    if not lang:
        add_error(request, 'valid_language', 'Invalid language', _tn.get(_.checkLanguage))
        return False

    db_lang = DBDiscussionSession.query(Language).filter_by(ui_locales=lang).first()
    if db_lang:
        request.validated['lang'] = db_lang
        return True
    else:
        add_error(request, 'valid_language', 'Invalid language {}'.format(lang), _tn.get(_.checkLanguage))
        return False


def valid_lang_cookie_fallback(request):
    """
    Get provided language from form, else interpret it from the request.

    :param request:
    :return:
    """
    lang = escape_if_string(request.json_body, 'lang')
    if not lang:
        lang = get_language_from_cookie(request)
    request.validated['lang'] = lang


def check_authentication(request):
    """
    Checks whether the user is authenticated and if not logs user out.

    :param request:
    :return:
    """
    session_expired = update_last_action(request.authenticated_userid)
    if session_expired:
        request.session.invalidate()
        headers = forget(request)
        location = request.application_url + 'discuss?session_expired=true',
        raise HTTPFound(
            location=location,
            headers=headers
        )
