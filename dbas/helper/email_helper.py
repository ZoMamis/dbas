"""
Provides class for sending an email

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

import smtplib

from socket import error as socket_error
from dbas.database import DBDiscussionSession

from dbas.database.discussion_model import User, TextVersion, Argument, Settings, Language, Statement
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from dbas.logger import logger
from dbas.strings import Translator, TextGenerator


def send_mail_due_to_new_argument(current_user, url, request):
    """
    Will send an email to the author of the argument.

    :param current_user: User.nickname
    :param url: current url
    :param request: self.request
    :return: duple with boolean for sent message, message-string
    """
    db_settings = DBDiscussionSession.query(Settings).filter_by(author_uid=current_user.uid).first()
    db_language = DBDiscussionSession.query(Language).filter_by(uid=db_settings.lang_uid).first()

    _t = Translator(db_language.ui_locales)
    subject = _t.get(_t.emailArgumentAddTitle)
    body = _t.get(_t.emailArgumentAddBody) + '\n' + url
    recipient = current_user.email

    return send_mail(request, subject, body, recipient, db_language.ui_locales)


def send_mail_due_to_edit_text(statement_uid, previous_author, current_author, url, request):
    """
    Will send an email to the author of the statement.

    :param statement_uid: Statement.uid
    :param previous_author: User
    :param current_author: User
    :param url: current url
    :param request: self.request
    :return: duple with boolean for sent message, message-string
    """
    db_statement = DBDiscussionSession.query(Statement).filter_by(uid=statement_uid).first()
    db_textversion_old = DBDiscussionSession.query(TextVersion).filter_by(statement_uid=statement_uid).first()
    db_textversion_new = DBDiscussionSession.query(TextVersion).filter_by(uid=db_statement.uid).first()

    db_previous_author = DBDiscussionSession.query(User).filter_by(uid=previous_author).first() if isinstance(previous_author, int) else previous_author
    db_current_author = DBDiscussionSession.query(User).filter_by(uid=current_author).first() if isinstance(current_author, int) else current_author

    db_settings = DBDiscussionSession.query(Settings).filter_by(author_uid=db_previous_author.uid).first()
    db_language = DBDiscussionSession.query(Language).filter_by(uid=db_settings.lang_uid).first()

    _t = Translator(db_language.ui_locales)
    subject = _t.get(_t.textversionChangedTopic)
    body = TextGenerator.get_text_for_edit_text_message(db_language.ui_locales, db_current_author.public_nickname,
                                                        db_textversion_old.content, db_textversion_new.content, url, False)
    recipient = db_previous_author.email

    return send_mail(request, subject, body, recipient, db_language.ui_locales)


def send_mail(request, subject, body, recipient, lang):
    """
    Try except block for sending an email

    :param request: current request
    :param subject: subject text of the mail
    :param body: body text of the mail
    :param recipient: recipient of the mail
    :param lang: current language
    :return: duple with boolean for sent message, message-string
    """
    logger('EmailHelper', 'send_mail', 'sending mail with subject \'' + subject + '\' to ' + recipient)
    _t = Translator(lang)
    send_message = False
    mailer = get_mailer(request)
    body = body + "\n\n---\n" + _t.get(_t.emailBodyText)
    message = Message(subject=subject, sender='dbas.hhu@gmail.com', recipients=[recipient], body=body)
    # try sending an catching errors
    try:
        mailer.send_immediately(message, fail_silently=False)
        send_message = True
        message = _t.get(_t.emailWasSent)
    except smtplib.SMTPConnectError as exception:
        logger('EmailHelper', 'send_mail', 'error while sending')
        code = str(exception.smtp_code)
        error = str(exception.smtp_error)
        logger('EmailHelper', 'send_mail', 'exception smtplib.SMTPConnectError smtp_code ' + code)
        logger('EmailHelper', 'send_mail', 'exception smtplib.SMTPConnectError smtp_error ' + error)
        message = _t.get(_t.emailWasNotSent)
    except socket_error as serr:
        logger('EmailHelper', 'send_mail', 'error while sending')
        logger('EmailHelper', 'send_mail', 'socket_error ' + str(serr))
        message = _t.get(_t.emailWasNotSent)

    return send_message, message
