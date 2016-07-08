# -*- coding: utf-8 -*-
"""
TODO

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""


import arrow
import os
import sys
import transaction
import random
import dbas.password_handler as passwordHandler

from math import trunc
from dbas.logger import logger
from sqlalchemy import engine_from_config, and_
from pyramid.paster import get_appsettings, setup_logging
from dbas.database.discussion_model import User, Argument, Statement, TextVersion, PremiseGroup, Premise, Group, Issue,\
    Notification, Settings, VoteArgument, VoteStatement, StatementReferences, Language, ArgumentSeenBy, StatementSeenBy
from dbas.database.news_model import News
from dbas.database import DiscussionBase, NewsBase, DBDiscussionSession, DBNewsSession


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main_discussion(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    discussion_engine = engine_from_config(settings, 'sqlalchemy-discussion.')
    DBDiscussionSession.configure(bind=discussion_engine)
    DiscussionBase.metadata.create_all(discussion_engine)

    with transaction.manager:
        user0, user1, user2, user3, user4, user5, user6, usert00, usert01, usert02, usert03, usert04, usert05, usert06, usert07, usert08, usert09, usert10, usert11, usert12, usert13, usert14, usert15, usert16, usert17, usert18, usert19, usert20, usert21, usert22, usert23, usert24, usert25, usert26, usert27, usert28, usert29, usert30 = set_up_users(DBDiscussionSession)
        lang1, lang2 = set_up_language(DBDiscussionSession)
        issue1, issue2, issue4, issue5 = set_up_issue(DBDiscussionSession, user2, lang1, lang2)
        set_up_settings(DBDiscussionSession, user0, user1, user2, user3, user4, user5, user6, usert00, usert01, usert02, usert03, usert04, usert05, usert06, usert07, usert08, usert09, usert10, usert11, usert12, usert13, usert14, usert15, usert16, usert17, usert18, usert19, usert20, usert21, usert22, usert23, usert24, usert25, usert26, usert27, usert28, usert29, usert30)
        setup_discussion_database(DBDiscussionSession, user2, issue1, issue2, issue4, issue5)
        transaction.commit()


def main_discussion_reload(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    discussion_engine = engine_from_config(settings, 'sqlalchemy-discussion.')
    DBDiscussionSession.configure(bind=discussion_engine)
    DiscussionBase.metadata.create_all(discussion_engine)

    with transaction.manager:
        drop_discussion_database(DBDiscussionSession)
        main_author = DBDiscussionSession.query(User).filter_by(nickname='Tobias').first()
        lang1, lang2 = set_up_language(DBDiscussionSession)
        issue1, issue2, issue4, issue5 = set_up_issue(DBDiscussionSession, main_author, lang1, lang2)
        setup_discussion_database(DBDiscussionSession, main_author, issue1, issue2, issue4, issue5)
        setup_dummy_votes(DBDiscussionSession)
        transaction.commit()


def main_dummy_votes(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    discussion_engine = engine_from_config(settings, 'sqlalchemy-discussion.')
    DBDiscussionSession.configure(bind=discussion_engine)
    DiscussionBase.metadata.create_all(discussion_engine)

    with transaction.manager:
        setup_dummy_votes(DBDiscussionSession)
        transaction.commit()


def main_news(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    news_engine = engine_from_config(settings, 'sqlalchemy-news.')
    DBNewsSession.configure(bind=news_engine)
    NewsBase.metadata.create_all(news_engine)

    with transaction.manager:
        setup_news_db(DBNewsSession)
        transaction.commit()


def setup_news_db(session):
    news01 = News(title='Anonymous users after vacation',
                  date=arrow.get('2015-09-24'),
                  author='Tobias Krauthoff',
                  news='After two and a half week of vacation we have a new feature. The discussion is now available for anonymous ' +
                       'users, therefore everyone can participate, but only registered users can make and edit statements.')
    news02 = News(title='Vacation done',
                  date=arrow.get('2015-09-23'),
                  author='Tobias Krauthoff',
                  news='After two and a half weeks of vacation a new feature was done. Hence anonymous users can participate, the ' +
                       'discussion is open for all, but commiting end editing statements is for registeres users only.')
    news03 = News(title='New URL-Schemes',
                  date=arrow.get('2015-09-01'),
                  author='Tobias Krauthoff',
                  news='Now D-BAS has unique urls for the discussion, therefore these urls can be shared.')
    news04 = News(title='Long time, no see!',
                  date=arrow.get('2015-08-31'),
                  author='Tobias Krauthoff',
                  news='In the mean time we have developed a new, better, more logically data structure. Additionally the navigation ' +
                       'was refreshed.')
    news05 = News(title='i18n/l10n',
                  date=arrow.get('2015-07-28'),
                  author='Tobias Krauthoff',
                  news='Internationalization is now working :)')
    news06 = News(title='i18n',
                  date=arrow.get('2015-07-22'),
                  author='Tobias Krauthoff',
                  news='Still working on i18n-problems of chameleon templates due to lingua. If this is fixed, i18n of jQuery will ' +
                       'happen. Afterwards l10n will take place.')
    news07 = News(title='Design & Research',
                  date=arrow.get('2015-07-13'),
                  author='Tobias Krauthoff',
                  news='D-BAS is still under construction. Meanwhile the index page was recreated and we are improving our algorithm for ' +
                       'the guided view mode. Next to this we are inventing a bunch of metrics for measuring the quality of discussion ' +
                       'in several software programs.')
    news08 = News(title='Session Management / CSRF',
                  date=arrow.get('2015-06-25'),
                  author='Tobias Krauthoff',
                  news='D-BAS is no able to manage a session as well as it has protection against CSRF.')
    news09 = News(title='Edit/Changelog',
                  date=arrow.get('2015-06-24'),
                  author='Tobias Krauthoff',
                  news='Now, each user can edit positions and arguments. All changes will be saved and can be watched. Future work is ' +
                       'the chance to edit the relations between positions.')
    news10 = News(title='Simple Navigation was improved',
                  date=arrow.get('2015-06-19'),
                  author='Tobias Krauthoff',
                  news='Because the first kind of navigation was finished recently, D-BAS is now dynamically. That means, that each user ' +
                       'can add positions and arguments on his own.<br><i>Open issues</i> are i18n, a framework for JS-tests as well as ' +
                       'the content of the popups.')
    news11 = News(title='Simple Navigation ready',
                  date=arrow.get('2015-06-09'),
                  author='Tobias Krauthoff',
                  news='First beta of D-BAS navigation is now ready. Within this kind the user will be permantly confronted with ' +
                       'arguments, which have a attack relation to the current selected argument/position. For an justification the user ' +
                       'can select out of all arguments, which have a attack relation to the \'attacking\' argument. Unfortunately the ' +
                       'support-relation are currently useless except for the justification for the position at start.')
    news12 = News(title='Workshop',
                  date=arrow.get('2015-05-27'),
                  author='Tobias Krauthoff',
                  news='Today: A new workshop at the O.A.S.E. :)')
    news13 = News(title='Admin Interface',
                  date=arrow.get('2015-05-29'),
                  author='Tobias Krauthoff',
                  news='Everything is growing, we have now a little admin interface and a navigation for the discussion is finshed, ' +
                       'but this is very basic and simple')
    news14 = News(title='Sharing',
                  date=arrow.get('2015-05-27'),
                  author='Tobias Krauthoff',
                  news='Every news can now be shared via FB, G+, Twitter and Mail. Not very important, but in some kind it is...')
    news15 = News(title='Tests and JS',
                  date=arrow.get('2015-05-26'),
                  author='Tobias Krauthoff',
                  news='Front-end tests with Splinter are now finished. They are great and easy to manage. Additionally I\'am working ' +
                       'on JS, so we can navigate in a static graph. Next to this, the I18N is waiting...')
    news16 = News(title='JS Starts',
                  date=arrow.get('2015-05-18'),
                  author='Tobias Krauthoff',
                  news='Today started the funny part about the dialog based part, embedded in the content page.')
    news18 = News(title='No I18N + L10N',
                  date=arrow.get('2015-05-18'),
                  author='Tobias Krauthoff',
                  news='Interationalization and localization is much more diffult than described by the pyramid. This has something todo ' +
                       'with Chameleon 2, Lingua and Babel, so this feature has to wait.')
    news19 = News(title='I18N + L10N',
                  date=arrow.get('2015-05-12'),
                  author='Tobias Krauthoff',
                  news='D-BAS, now with internationalization and translation.')
    news20 = News(title='Settings',
                  date=arrow.get('2015-05-10'),
                  author='Tobias Krauthoff',
                  news='New part of the website is finished: a settings page for every user.')
    news21 = News(title='About the Workshop in Karlsruhe',
                  date=arrow.get('2015-05-09'),
                  author='Tobias Krauthoff',
                  news='The workshop was very interesting. We have had very interesting talks and got much great feedback vom Jun.-Prof. ' +
                       'Dr. Betz and Mr. Voigt. A repetition will be planed for the middle of july.')
    news22 = News(title='Workshop in Karlsruhe',
                  date=arrow.get('2015-05-07'),
                  author='Tobias Krauthoff',
                  news='The working group \'functionality\' will drive to Karlsruhe for a workshop with Jun.-Prof. Dr. Betz as well as ' +
                       'with C. Voigt until 08.05.2015. Our main topics will be the measurement of quality of discussions and the design of ' +
                       'online-participation. I think, this will be very interesting!')
    news23 = News(title='System will be build up',
                  date=arrow.get('2015-05-01'),
                  author='Tobias Krauthoff',
                  news='Currently I am working a lot at the system. This work includes:<br><ul><li>frontend-design with CSS and ' +
                       'jQuery</li><li>backend-development with pything</li><li>development of unit- and integration tests</li><li>a ' +
                       'database scheme</li><li>validating and deserializing data with ' +
                       '<a href="http://docs.pylonsproject.org/projects/colander/en/latest/">Colander</a></li><li>translating string ' +
                       'with <a href="http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html#localization-deployment-settings">internationalization</a></li></ul>')
    news24 = News(title='First set of tests',
                  date=arrow.get('2015-05-06'),
                  author='Tobias Krauthoff',
                  news='Finished first set of unit- and integration tests for the database and frontend.')
    news25 = News(title='Page is growing',
                  date=arrow.get('2015-05-05'),
                  author='Tobias Krauthoff',
                  news='The contact page is now working as well as the password-request option.')
    news26 = News(title='First mockup',
                  date=arrow.get('2015-05-01'),
                  author='Tobias Krauthoff',
                  news='The webpage has now a contact, login and register site.')
    news27 = News(title='Start',
                  date=arrow.get('2015-04-14'),
                  author='Tobias Krauthoff',
                  news='I\'ve started with the Prototype.')
    news28 = News(title='First steps',
                  date=arrow.get('2014-12-01'),
                  author='Tobias Krauthoff',
                  news='I\'ve started with with my PhD.')
    news29 = News(title='New logic for inserting',
                  date=arrow.get('2015-10-14'),
                  author='Tobias Krauthoff',
                  news='Logic for inserting statements was redone. Everytime, where the user can add information via a textarea, '
                       'only the area is visible, which is logically correct. Therefore the decisions are based on argumentations theory.')
    news30 = News(title='Different topics',
                  date=arrow.get('2015-10-15'),
                  author='Tobias Krauthoff',
                  news='Since today we can switch between different topics :) Unfortunately this feature is not really tested ;-)')
    news31 = News(title='Stable release',
                  date=arrow.get('2015-11-10'),
                  author='Tobias Krauthoff',
                  news='After two weeks of debugging, a first and stable version is online. Now we can start with the interessing things!')
    news32 = News(title='Design Update',
                  date=arrow.get('2015-11-11'),
                  author='Tobias Krauthoff',
                  news='Today we released a new material-oriented design. Enjoy it!')
    news33 = News(title='Improved Bootstrapping',
                  date=arrow.get('2015-11-16'),
                  author='Tobias Krauthoff',
                  news='Bootstraping is one of the main challenges in discussion. Therefore we have a two-step process for this task!')
    news34 = News(title='Breadcrumbs',
                  date=arrow.get('2015-11-24'),
                  author='Tobias Krauthoff',
                  news='Now we have a breadcrumbs with shortcuts for every step in our discussion. This feature will be im improved soon!')
    news35 = News(title='Logic improvements',
                  date=arrow.get('2015-12-01'),
                  author='Tobias Krauthoff',
                  news='Every week we try to improve the look and feel of the discussions navigation. Sometimes just a few words are '
                       'edited, but on other day the logic itself gets an update. So keep on testing :)')
    news36 = News(title='Piwik',
                  date=arrow.get('2015-12-08'),
                  author='Tobias Krauthoff',
                  news='Today Piwik was installed. It will help to improve the services of D-BAS!')
    news37 = News(title='Happy new Year',
                  date=arrow.get('2016-01-01'),
                  author='Tobias Krauthoff',
                  news='Frohes Neues Jahr ... Bonne Annee ... Happy New Year ... Feliz Ano Nuevo ... Feliz Ano Novo')
    news38 = News(title='Island View and Pictures',
                  date=arrow.get('2016-01-06'),
                  author='Tobias Krauthoff',
                  news='D-BAS will be more personal and results driven. Therefore the new release has profile pictures for '
                       'everyone. They are powered by gravatar and are based on a md5-hash of the users email. Next to this '
                       'a new view was published - the island view. Do not be shy and try it in discussions ;-) Last '
                       'improvement just collects the attacks and supports for arguments...this is needed for our next big '
                       'thing :) Stay tuned!')
    news39 = News(title='Refactoring',
                  date=arrow.get('2016-01-27'),
                  author='Tobias Krauthoff',
                  news='D-BAS refactored the last two weeks. During this time, a lot of JavaScript was removed. Therefore '
                       'D-BAS uses Chameleon with TAL in the Pyramid-Framework. So D-BAS will be more stable and faster. '
                       'The next period all functions will be tested and recovered.')
    news40 = News(title='API',
                  date=arrow.get('2016-01-29'),
                  author='Tobias Krauthoff',
                  news='Now D-BAS has an API. Just replace the "discuss"-tag in your url with api to get your current steps raw data.')
    news41 = News(title='Voting Model',
                  date=arrow.get('2016-01-05'),
                  author='Tobias Krauthoff',
                  news='Currently we are improving out model of voting for arguments as well as statements. Therefore we are working'
                       'together with our colleage out of the theoretical computer science...because D-BAS datastructure can be '
                       'formalized to be compatible with frameworks of Dung.')
    news42 = News(title='Premisegroups',
                  date=arrow.get('2016-02-09'),
                  author='Tobias Krauthoff',
                  news='Now we have a mechanism for unclear statements. For example the user enters "I want something because '
                       'A and B". The we do not know, whether A and B must hold at the same time, or if she wants something '
                       'when A or B holds. Therefore the system requests feedback.')
    news43 = News(title='Notification System',
                  date=arrow.get('2016-02-16'),
                  author='Tobias Krauthoff',
                  news='Yesterday we have develope a minimal notification system. This system could send information to every author, '
                       'if one of their statement was edited. More features are comming soon!')
    news44 = News(title='Speech Bubble System',
                  date=arrow.get('2016-03-02'),
                  author='Tobias Krauthoff',
                  news='After one week of testing, we released a new minor version of D-BAS. Instead of the text presentation,'
                       'we will use chat-like style :) Come on and try it! Additionally anonymous users will have a history now!')
    news45 = News(title='COMMA16',
                  date=arrow.get('2016-04-05'),
                  author='Tobias Krauthoff',
                  news='After much work, testing and debugging, we now have version of D-BAS, which will be submitted '
                       ' to <a href="http://www.ling.uni-potsdam.de/comma2016" target="_blank">COMMA 2016</a>.')
    news46 = News(title='History Management',
                  date=arrow.get('2016-04-26'),
                  author='Tobias Krauthoff',
                  news='We have changed D-BAS\' history management. Now you can bookmark any link in any discussion and '
                       'your history will always be with you!')
    news47 = News(title='Development is going on',
                  date=arrow.get('2016-04-05'),
                  author='Tobias Krauthoff',
                  news='Recently we improved some features, which will be released in future. Firstly there will be an '
                       'island view for every argument, where the participants can see every premise for current reactions. '
                       'Secondly the opinion barometer is still under development. For a more recent update, have a look '
                       'at our imprint.')
    news48 = News(title='COMMA16',
                  date=arrow.get('2016-06-24'),
                  author='Tobias Krauthoff',
                  news='We are happy to announce, that our paper for the COMMA16 was accepted. In the meantime many little '
                       'improvements as well as first user tests were done.')
    news49 = News(title='COMMA16',
                  date=arrow.get('2016-07-05'),
                  author='Tobias Krauthoff',
                  news='Today we released a new text-based sidebar for a better experience. Have fun!')
    news_array = [news01, news02, news03, news04, news05, news06, news07, news08, news09, news10, news11, news12,
                  news13, news14, news15, news16, news29, news18, news19, news20, news21, news22, news23, news24,
                  news25, news26, news27, news28, news30, news31, news32, news33, news34, news35, news36, news37,
                  news38, news39, news40, news41, news42, news43, news44, news45, news46, news47, news48, news49]
    session.add_all(news_array[::-1])
    session.flush()


def drop_discussion_database(session):
    """

    :param session:
    :return:
    """
    db_textversions = session.query(TextVersion).all()
    for tmp in db_textversions:
        tmp.set_statement(None)

    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(VoteArgument).delete()) + ' in VoteArgument')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(VoteStatement).delete()) + ' in VoteStatement')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(ArgumentSeenBy).delete()) + ' in VoteArgument')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(StatementSeenBy).delete()) + ' in VoteStatement')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Notification).delete()) + ' in Notification')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(StatementReferences).delete()) + ' in StatementReferences')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Argument).delete()) + ' in Argument')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Premise).delete()) + ' in Premise')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(PremiseGroup).delete()) + ' in PremiseGroup')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Statement).delete()) + ' in Statement')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(TextVersion).delete()) + ' in TextVersion')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Issue).delete()) + ' in Issue')
    logger('INIT_DB', 'DROP', 'deleted ' + str(session.query(Language).delete()) + ' in Language')
    session.flush()


def set_up_users(session):
    """
    Creates all users

    :param session: database session
    :return: User
    """

    # adding groups
    group0 = Group(name='admins')
    group1 = Group(name='authors')
    group2 = Group(name='users')
    session.add_all([group0, group1, group2])
    session.flush()

    # adding some dummy users
    pwt = passwordHandler.get_hashed_password('iamatestuser2016')
    pw0 = passwordHandler.get_hashed_password('QMuxpuPXwehmhm2m93#I;)QX§u4qjqoiwhebakb)(4hkblkb(hnzUIQWEGgalksd')
    pw1 = passwordHandler.get_hashed_password('pjÖKAJSDHpuiashw89ru9hsidhfsuihfapiwuhrfj098UIODHASIFUSHDF')
    pw2 = passwordHandler.get_hashed_password('tobias')
    pw3 = passwordHandler.get_hashed_password('martin')
    pw4 = passwordHandler.get_hashed_password('christian')
    pw5 = passwordHandler.get_hashed_password('daszimistdoof123#')
    pw6 = passwordHandler.get_hashed_password('daszimistdoof321!')

    user0 = User(firstname='anonymous', surname='anonymous', nickname='anonymous', email='', password=pw0, group=group0.uid, gender='m')
    user1 = User(firstname='admin', surname='admin', nickname='admin', email='dbas.hhu@gmail.com', password=pw1, group=group0.uid, gender='m')
    user2 = User(firstname='Tobias', surname='Krauthoff', nickname='Tobias', email='krauthoff@cs.uni-duesseldorf.de', password=pw2, group=group0.uid, gender='m')
    user3 = User(firstname='Martin', surname='Mauve', nickname='Martin', email='mauve@cs.uni-duesseldorf.de', password=pw3, group=group0.uid, gender='m')
    user4 = User(firstname='Christian', surname='Meter', nickname='Christian', email='meter@cs.uni-duesseldorf.de', password=pw4, group=group0.uid, gender='m')
    user5 = User(firstname='Raphael', surname='Bialon', nickname='Яaphael', email='bialon@cs.uni-duesseldorf.de', password=pw5, group=group1.uid, gender='m')
    user6 = User(firstname='Alexander', surname='Schneider', nickname='WeGi', email='aschneider@cs.uni-duesseldorf.de', password=pw6, group=group1.uid, gender='m')

    usert00 = User(firstname='Pascal', surname='Lux', nickname='Pascal', email='.tobias.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert01 = User(firstname='Kurt', surname='Hecht', nickname='Kurt', email='t.obias.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert02 = User(firstname='Torben', surname='Hartl', nickname='Torben', email='to.bias.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert03 = User(firstname='Thorsten', surname='Scherer', nickname='Thorsten', email='tob.ias.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert04 = User(firstname='Friedrich', surname='Schutte', nickname='Friedrich', email='tobi.as.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert05 = User(firstname='Aayden', surname='Westermann', nickname='Aayden', email='tobia.s.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert06 = User(firstname='Hermann', surname='Grasshoff', nickname='Hermann', email='tobias.krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert07 = User(firstname='Wolf', surname='Himmler', nickname='Wolf', email='tobias..krauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert08 = User(firstname='Jakob', surname='Winter', nickname='Jakob', email='tobias.k.rauthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert09 = User(firstname='Alwin', surname='Wechter', nickname='Alwin', email='tobias.kr.authoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert10 = User(firstname='Walter', surname='Weisser', nickname='Walter', email='tobias.kra.uthoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert11 = User(firstname='Volker', surname='Keitel', nickname='Volker', email='tobias.krau.thoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert12 = User(firstname='Benedikt', surname='Feuerstein', nickname='Benedikt', email='tobias.kraut.hoff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert13 = User(firstname='Engelbert', surname='Gottlieb', nickname='Engelbert', email='tobias.krauth.off@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert14 = User(firstname='Elias', surname='Auerbach', nickname='Elias', email='tobias.krautho.ff@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert15 = User(firstname='Rupert', surname='Wenz', nickname='Rupert', email='tobias.krauthof.f@gmail.com', password=pwt, group=group2.uid, gender='m')
    usert16 = User(firstname='Marga', surname='Wegscheider', nickname='Marga', email='t.obias.krautho.ff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert17 = User(firstname='Larissa', surname='Clauberg', nickname='Larissa', email='to.bias.krauth.off@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert18 = User(firstname='Emmi', surname='Rosch', nickname='Emmi', email='tob.ias.kraut.hoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert19 = User(firstname='Konstanze', surname='Krebs', nickname='Konstanze', email='tobi.as.krau.thoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert20 = User(firstname='Catrin', surname='Fahnrich', nickname='Catrin', email='tobia.s.kra.uthoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert21 = User(firstname='Antonia', surname='Bartram', nickname='Antonia', email='tobias..kr.authoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert22 = User(firstname='Nora', surname='Kempf', nickname='Nora', email='tobias..k.rauthoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert23 = User(firstname='Julia', surname='Wetter', nickname='Julia', email='tobias.k..rauthoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert24 = User(firstname='Jutta', surname='Munch', nickname='Jutta', email='tobias.kr..authoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert25 = User(firstname='Helga', surname='Heilmann', nickname='Helga', email='tobias..kra.uthoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert26 = User(firstname='Denise', surname='Tietjen', nickname='Denise', email='tobia.s.krau.thoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert27 = User(firstname='Hanne', surname='Beckmann', nickname='Hanne', email='tobi.as.kraut.hoff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert28 = User(firstname='Elly', surname='Landauer', nickname='Elly', email='tob.ias.krauth.off@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert29 = User(firstname='Sybille', surname='Redlich', nickname='Sybille', email='to.bias.krautho.ff@gmail.com', password=pwt, group=group2.uid, gender='f')
    usert30 = User(firstname='Ingeburg', surname='Fischer', nickname='Ingeburg', email='t.obias.krauthof.f@gmail.com', password=pwt, group=group2.uid, gender='f')

    session.add_all([user0, user1, user2, user3, user4, user5, user6, usert00])
    session.add_all([usert01, usert02, usert03, usert04, usert05, usert06, usert07, usert08, usert09, usert10])
    session.add_all([usert11, usert12, usert13, usert14, usert15, usert16, usert17, usert18, usert19, usert20])
    session.add_all([usert21, usert22, usert23, usert24, usert25, usert26, usert27, usert28, usert29, usert30])
    session.flush()

    return user0, user1, user2, user3, user4, user5, user6, usert00, usert01, usert02, usert03, usert04, usert05, usert06, usert07, usert08, usert09, usert10, usert11, usert12, usert13, usert14, usert15, usert16, usert17, usert18, usert19, usert20, usert21, usert22, usert23, usert24, usert25, usert26, usert27, usert28, usert29, usert30


def set_up_settings(session, user0, user1, user2, user3, user4, user5, user6, usert00, usert01, usert02, usert03, usert04, usert05,
                    usert06, usert07, usert08, usert09, usert10, usert11, usert12, usert13, usert14, usert15, usert16,
                    usert17, usert18, usert19, usert20, usert21, usert22, usert23, usert24, usert25, usert26, usert27,
                    usert28, usert29, usert30):
    # adding settings
    settings0 = Settings(author_uid=user0.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings1 = Settings(author_uid=user1.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings2 = Settings(author_uid=user2.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings3 = Settings(author_uid=user3.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings4 = Settings(author_uid=user4.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings5 = Settings(author_uid=user5.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settings6 = Settings(author_uid=user6.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst00 = Settings(author_uid=usert00.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst01 = Settings(author_uid=usert01.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst02 = Settings(author_uid=usert02.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst03 = Settings(author_uid=usert03.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst04 = Settings(author_uid=usert04.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst05 = Settings(author_uid=usert05.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst06 = Settings(author_uid=usert06.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst07 = Settings(author_uid=usert07.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst08 = Settings(author_uid=usert08.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst09 = Settings(author_uid=usert09.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst10 = Settings(author_uid=usert10.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst11 = Settings(author_uid=usert11.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst12 = Settings(author_uid=usert12.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst13 = Settings(author_uid=usert13.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst14 = Settings(author_uid=usert14.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst15 = Settings(author_uid=usert15.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst16 = Settings(author_uid=usert16.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst17 = Settings(author_uid=usert17.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst18 = Settings(author_uid=usert18.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst19 = Settings(author_uid=usert19.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst20 = Settings(author_uid=usert20.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst21 = Settings(author_uid=usert21.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst22 = Settings(author_uid=usert22.uid, send_mails=True, send_notifications=True, should_show_public_nickname=False)
    settingst23 = Settings(author_uid=usert23.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst24 = Settings(author_uid=usert24.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst25 = Settings(author_uid=usert25.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst26 = Settings(author_uid=usert26.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst27 = Settings(author_uid=usert27.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst28 = Settings(author_uid=usert28.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst29 = Settings(author_uid=usert29.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    settingst30 = Settings(author_uid=usert30.uid, send_mails=True, send_notifications=True, should_show_public_nickname=True)
    session.add_all([settings0, settings1, settings2, settings3, settings4, settings5, settings6])
    session.add_all([settingst00, settingst01, settingst02, settingst03, settingst04, settingst05, settingst06])
    session.add_all([settingst07, settingst08, settingst09, settingst10, settingst11, settingst12, settingst13])
    session.add_all([settingst14, settingst15, settingst16, settingst17, settingst18, settingst19, settingst20])
    session.add_all([settingst21, settingst22, settingst23, settingst24, settingst25, settingst26, settingst27])
    session.add_all([settingst28, settingst29, settingst30])
    session.flush()

    import dbas.user_management as UserHandler
    UserHandler.refresh_public_nickname(usert07)
    UserHandler.refresh_public_nickname(usert08)
    UserHandler.refresh_public_nickname(usert09)
    UserHandler.refresh_public_nickname(usert10)
    UserHandler.refresh_public_nickname(usert11)
    UserHandler.refresh_public_nickname(usert12)
    UserHandler.refresh_public_nickname(usert13)
    UserHandler.refresh_public_nickname(usert14)
    UserHandler.refresh_public_nickname(usert15)
    UserHandler.refresh_public_nickname(usert16)
    UserHandler.refresh_public_nickname(usert17)
    UserHandler.refresh_public_nickname(usert18)
    UserHandler.refresh_public_nickname(usert19)
    UserHandler.refresh_public_nickname(usert20)
    UserHandler.refresh_public_nickname(usert21)
    UserHandler.refresh_public_nickname(usert22)

    # Adding welcome notifications
    notification0 = Notification(from_author_uid=user1.uid, to_author_uid=user2.uid, topic='Welcome', content='Welcome to the novel dialog-based argumentation system...')
    notification1 = Notification(from_author_uid=user1.uid, to_author_uid=user3.uid, topic='Welcome', content='Welcome to the novel dialog-based argumentation system...')
    notification2 = Notification(from_author_uid=user1.uid, to_author_uid=user4.uid, topic='Welcome', content='Welcome to the novel dialog-based argumentation system...')
    notification3 = Notification(from_author_uid=user1.uid, to_author_uid=user5.uid, topic='Welcome', content='Welcome to the novel dialog-based argumentation system...')
    notification4 = Notification(from_author_uid=user1.uid, to_author_uid=user6.uid, topic='Welcome', content='Welcome to the novel dialog-based argumentation system...')
    session.add_all([notification0, notification1, notification2, notification3, notification4])
    session.flush()


def set_up_language(session):
    """

    :param session:
    :return:
    """
    # adding languages
    lang1 = Language(name='English', ui_locales='en')
    lang2 = Language(name='Deutsch', ui_locales='de')
    session.add_all([lang1, lang2])
    session.flush()
    return lang1, lang2


def set_up_issue(session, user, lang1, lang2):
    """

    :param session:
    :param user:
    :param lang1:
    :param lang2:
    :return:
    """
    # adding our main issue
    issue1 = Issue(title='Town has to cut spending ', info='Our town needs to cut spending. Please discuss ideas how this should be done.', author_uid=user.uid, lang_uid=lang1.uid)
    issue2 = Issue(title='Cat or Dog', info='Your familiy argues about whether to buy a cat or dog as pet. Now your opinion matters!', author_uid=user.uid, lang_uid=lang1.uid)
    #  issue3 = Issue(title='Make the world better', info='How can we make this world a better place?', author_uid=user.uid, lang='en')
    issue4 = Issue(title='Elektroautos', info='Elektroautos - Die Autos der Zukunft? Bitte diskutieren Sie dazu.', author_uid=user.uid, lang_uid=lang2.uid)
    issue5 = Issue(title='Unterstützung der Sekretariate', info='Unsere Sekretariate in der Informatik sind arbeitsmäßig stark überlastet. Bitte diskutieren Sie Möglichkeiten um dies zu verbessern.', author_uid=user.uid, lang_uid=lang2.uid)
    session.add_all([issue1, issue2, issue4, issue5])
    session.flush()
    return issue1, issue2, issue4, issue5


def setup_dummy_votes(session):
    """
    Drops all votes and init new dummy votes

    :param session: DBDiscussionSession
    :return:
    """
    DBDiscussionSession.query(VoteStatement).delete()
    DBDiscussionSession.query(VoteArgument).delete()

    db_arguments = DBDiscussionSession.query(Argument).all()
    db_statements = DBDiscussionSession.query(Statement).all()
    firstnames = ['Tobias', 'Pascal', 'Kurt', 'Torben', 'Thorsten', 'Friedrich', 'Aayden', 'Hermann', 'Wolf', 'Jakob',
                  'Alwin', 'Walter', 'Volker', 'Benedikt', 'Engelbert', 'Elias', 'Rupert', 'Marga', 'Larissa', 'Emmi',
                  'Konstanze', 'Catrin', 'Antonia', 'Nora', 'Nora', 'Jutta', 'Helga', 'Denise', 'Hanne', 'Elly',
                  'Sybille', 'Ingeburg']

    new_votes = []
    arg_up = 0
    arg_down = 0
    stat_up = 0
    stat_down = 0
    max_interval = len(firstnames) - 1
    for argument in db_arguments:
        up_votes = random.randint(1, max_interval)
        down_votes = random.randint(1, max_interval)
        arg_up += up_votes
        arg_down += down_votes

        tmp_firstname = list(firstnames)
        for i in range(0, up_votes):
            nick = tmp_firstname[random.randint(0, len(tmp_firstname) - 1)]
            db_rnd_tst_user = DBDiscussionSession.query(User).filter_by(firstname=nick).first()
            if not session.query(VoteArgument).filter(and_(VoteArgument.argument_uid == argument.uid,
                                                           VoteArgument.author_uid == db_rnd_tst_user.uid,
                                                           VoteArgument.is_up_vote == True,
                                                           VoteArgument.is_valid == True)).first():
                new_votes.append(VoteArgument(argument_uid=argument.uid, author_uid=db_rnd_tst_user.uid, is_up_vote=True, is_valid=True))
                tmp_firstname.remove(nick)

        tmp_firstname = list(firstnames)
        for i in range(0, down_votes):
            nick = tmp_firstname[random.randint(0, len(tmp_firstname) - 1)]
            db_rnd_tst_user = DBDiscussionSession.query(User).filter_by(firstname=nick).first()
            if not session.query(VoteArgument).filter(and_(VoteArgument.argument_uid == argument.uid,
                                                           VoteArgument.author_uid == db_rnd_tst_user.uid,
                                                           VoteArgument.is_up_vote == False,
                                                           VoteArgument.is_valid == True)).first():
                new_votes.append(VoteArgument(argument_uid=argument.uid, author_uid=db_rnd_tst_user.uid, is_up_vote=False, is_valid=True))
                tmp_firstname.remove(nick)

    for statement in db_statements:
        up_votes = random.randint(1, max_interval)
        down_votes = random.randint(1, max_interval)
        stat_up += up_votes
        stat_down += down_votes

        tmp_firstname = list(firstnames)
        for i in range(0, up_votes):
            nick = tmp_firstname[random.randint(0, len(tmp_firstname) - 1)]
            db_rnd_tst_user = DBDiscussionSession.query(User).filter_by(firstname=nick).first()
            if not session.query(VoteStatement).filter(and_(VoteStatement.statement_uid == statement.uid,
                                                            VoteStatement.author_uid == db_rnd_tst_user.uid,
                                                            VoteStatement.is_up_vote == True,
                                                            VoteStatement.is_valid == True)).first():
                new_votes.append(VoteStatement(statement_uid=statement.uid, author_uid=db_rnd_tst_user.uid, is_up_vote=True, is_valid=True))
                tmp_firstname.remove(nick)

        tmp_firstname = list(firstnames)
        for i in range(0, down_votes):
            nick = tmp_firstname[random.randint(0, len(tmp_firstname) - 1)]
            db_rnd_tst_user = DBDiscussionSession.query(User).filter_by(firstname=nick).first()
            if not session.query(VoteStatement).filter(and_(VoteStatement.statement_uid == statement.uid,
                                                            VoteStatement.author_uid == db_rnd_tst_user.uid,
                                                            VoteStatement.is_up_vote == False,
                                                            VoteStatement.is_valid == True)).first():
                new_votes.append(VoteStatement(statement_uid=statement.uid, author_uid=db_rnd_tst_user.uid, is_up_vote=False, is_valid=True))
                tmp_firstname.remove(nick)

    rat_arg_up = str(trunc(arg_up / len(db_arguments) * 100) / 100)
    rat_arg_down = str(trunc(arg_down / len(db_arguments) * 100) / 100)
    rat_stat_up = str(trunc(stat_up / len(db_statements) * 100) / 100)
    rat_stat_down = str(trunc(stat_down / len(db_statements) * 100) / 100)

    logger('INIT_DB', 'Dummy Votes', 'Created ' + str(arg_up) + ' up votes for ' + str(len(db_arguments)) + ' arguments (' + rat_arg_up + ' votes/argument)')
    logger('INIT_DB', 'Dummy Votes', 'Created ' + str(arg_down) + ' down votes for ' + str(len(db_arguments)) + ' arguments (' + rat_arg_down + ' votes/argument)')
    logger('INIT_DB', 'Dummy Votes', 'Created ' + str(stat_up) + ' up votes for ' + str(len(db_statements)) + ' statements (' + rat_stat_up + ' votes/statement)')
    logger('INIT_DB', 'Dummy Votes', 'Created ' + str(stat_down) + ' down votes for ' + str(len(db_statements)) + ' statements (' + rat_stat_down + ' votes/statement)')

    session.add_all(new_votes)
    session.flush()

    # random timestamps
    db_votestatements = session.query(VoteStatement).all()
    for vs in db_votestatements:
        vs.timestamp = arrow.utcnow().replace(days=-random.randint(0, 25))

    db_votearguments = session.query(VoteArgument).all()
    for va in db_votearguments:
        va.timestamp = arrow.utcnow().replace(days=-random.randint(0, 25))


def setup_discussion_database(session, user, issue1, issue2, issue4, issue5):
    """
    Fills the database with dummy date, created by given user

    :param session: database session
    :param user: main author
    :param issue1: issue1
    :param issue2: issue2
    :param issue4: issue4
    :param issue5: issue5
    :return:
    """

    # Adding all textversions
    textversion1 = TextVersion(content="We should get a cat.", author=user.uid)
    textversion2 = TextVersion(content="We should get a dog.", author=user.uid)
    textversion3 = TextVersion(content="We could get both, a cat and a dog.", author=user.uid)
    textversion4 = TextVersion(content="Cats are very independent.", author=user.uid)
    textversion5 = TextVersion(content="Cats are capricious.", author=user.uid)
    textversion6 = TextVersion(content="Dogs can act as watch dogs.", author=user.uid)
    textversion7 = TextVersion(content="You have to take the dog for a walk every day, which is tedious.", author=user.uid)
    textversion8 = TextVersion(content="We have no use for a watch dog.", author=user.uid)
    textversion9 = TextVersion(content="Going for a walk with the dog every day is good for social interaction and physical exercise.", author=user.uid)
    textversion10 = TextVersion(content="It would be no problem.", author=user.uid)
    textversion11 = TextVersion(content="A cat and a dog will generally not get along well.", author=user.uid)
    textversion12 = TextVersion(content="We do not have enough money for two pets.", author=user.uid)
    textversion13 = TextVersion(content="A dog costs taxes and will be more expensive than a cat.", author=user.uid)
    textversion14 = TextVersion(content="Cats are fluffy.", author=user.uid)
    textversion15 = TextVersion(content="Cats are small.", author=user.uid)
    textversion16 = TextVersion(content="Fluffy animals losing much hair and I'm allergic to animal hair.", author=user.uid)
    textversion17 = TextVersion(content="You could use a automatic vacuum cleaner.", author=user.uid)
    textversion18 = TextVersion(content="Cats ancestors are animals in wildlife, who are hunting alone and not in groups.", author=user.uid)
    textversion19 = TextVersion(content="This is not true for overbred races.", author=user.uid)
    textversion20 = TextVersion(content="This lies in their the natural conditions.", author=user.uid)
    textversion21 = TextVersion(content="The purpose of a pet is to have something to take care of.", author=user.uid)
    textversion22 = TextVersion(content="Several cats of friends of mine are real as*holes.", author=user.uid)
    textversion23 = TextVersion(content="The fact, that cats are capricious, is based on the cats race.", author=user.uid)
    textversion24 = TextVersion(content="Not every cat is capricious.", author=user.uid)
    textversion25 = TextVersion(content="This is based on the cats race and a little bit on the breeding.", author=user.uid)
    textversion26 = TextVersion(content="Next to the taxes you will need equipment like a dog lead, anti-flea-spray, and so on.", author=user.uid)
    textversion27 = TextVersion(content="The equipment for running costs of cats and dogs are nearly the same.", author=user.uid)
    textversion29 = TextVersion(content="This is just a claim without any justification.", author=user.uid)
    textversion30 = TextVersion(content="In Germany you have to pay for your second dog even more taxes!", author=user.uid)
    textversion31 = TextVersion(content="It is important, that pets are small and fluffy!", author=user.uid)
    textversion32 = TextVersion(content="Cats are little, sweet and innocent cuddle toys.", author=user.uid)
    textversion33 = TextVersion(content="Do you have ever seen a sphinx cat or savannah cats?", author=user.uid)
    textversion34 = TextVersion(content="Even overbred races can be taught.", author=user.uid)
    textversion35 = TextVersion(content="Several pets are nice to have and you do not have to take much care of them, for example turtles or cats, which are living outside.", author=user.uid)
    textversion36 = TextVersion(content="It is much work to take care of both animals.", author=user.uid)
    textversion101 = TextVersion(content="The city should reduce the number of street festivals.", author=user.uid)
    textversion102 = TextVersion(content="We should shut down university park.", author=user.uid)
    textversion103 = TextVersion(content="We should close public swimming pools.", author=user.uid)
    textversion105 = TextVersion(content="Reducing the number of street festivals can save up to $50.000 a year.", author=user.uid)
    textversion106 = TextVersion(content="Every street festival is funded by large companies.", author=user.uid)
    textversion107 = TextVersion(content="Then we will have more money to expand out pedestrian zone", author=user.uid)
    textversion108 = TextVersion(content="Our city will get more attractive for shopping.", author=user.uid)
    textversion109 = TextVersion(content="Street festivals attract many people, which will increase the citys income.", author=user.uid)
    textversion110 = TextVersion(content="Spending of the city for these festivals are higher than the earnings.", author=user.uid)
    textversion111 = TextVersion(content="Money does not solve problems of our society.", author=user.uid)
    textversion112 = TextVersion(content="Criminals use university park to sell drugs.", author=user.uid)
    textversion113 = TextVersion(content="Shutting down university park will save $100.000 a year.", author=user.uid)
    textversion114 = TextVersion(content="We should not give in to criminals.", author=user.uid)
    textversion115 = TextVersion(content="The number of police patrols has been increased recently.", author=user.uid)
    textversion116 = TextVersion(content="This is the only park in our city.", author=user.uid)
    textversion117 = TextVersion(content="There are many parks in neighbouring towns.", author=user.uid)
    textversion118 = TextVersion(content="The city is planing a new park in the upcoming month.", author=user.uid)
    textversion119 = TextVersion(content="Parks are very important for our climate.", author=user.uid)
    textversion120 = TextVersion(content="Our swimming pools are very old and it would take a major investment to repair them.", author=user.uid)
    textversion121 = TextVersion(content="Schools need the swimming pools for their sports lessons.", author=user.uid)
    textversion122 = TextVersion(content="The rate of non-swimmers is too high.", author=user.uid)
    textversion123 = TextVersion(content="The police cannot patrol in the park for 24/7.", author=user.uid)
    textversion200 = TextVersion(content="E-Autos keine Emissionen verursachen.", author=user.uid)
    textversion201 = TextVersion(content="Elektroautos sehr g&uuml;nstig im Unterhalt sind", author=user.uid)
    textversion202 = TextVersion(content="E-Autos optimal f&uuml;r den Stadtverkehr sind.", author=user.uid)
    textversion203 = TextVersion(content="sie keine stinkenden Abgase produzieren.", author=user.uid)
    textversion204 = TextVersion(content="die Herstellung der Autos und Batterien die Umwelt stark belasten", author=user.uid)
    textversion205 = TextVersion(content="sie sehr teuer in der Anschaffung sind.", author=user.uid)
    textversion206 = TextVersion(content="die Reichweite von Elektroautos ausreichend f&uuml;r mindestens 300km ist.", author=user.uid)
    textversion207 = TextVersion(content="die Ladezeit der Batterie bis zu 12h dauern kann und so lange man tags&uuml;ber nicht warten kann.", author=user.uid)
    textversion208 = TextVersion(content="die Umweltbelastung und Rohstoffabh&auml;ngigkeit durch Batterien sehr hoch ist.", author=user.uid)
    textversion209 = TextVersion(content="die Umweltbelastung durch Batterien immernoch viel geringer als durch Verbrennungsmotoren ist.", author=user.uid)
    textversion210 = TextVersion(content="in der Stadt Fahrr&auml;der und oeffentliche Verkehrsmittel besser sind.", author=user.uid)
    textversion211 = TextVersion(content="man gezielt 'tanken' kann, genauso wie bei einem herk&ouml;mmlichen KFZ.", author=user.uid)
    textversion301 = TextVersion(content="durch rücksichtsvolle Verhaltensanpassungen der wissenschaftlichen Mitarbeitenden der Arbeitsaufwand der Sekretärinnen gesenkt werden könnte", author=user.uid)
    textversion302 = TextVersion(content="wir Standard-Formulare, wie Urlaubsanträge, selbst faxen können", author=user.uid)
    textversion303 = TextVersion(content="etliche Abläufe durch ein besseres Zusammenarbeiten optimiert werden können. Dies sollte auch schriftlich als Anleitungen festgehalten werden, damit neue Angestellt einen leichten Einstieg finden", author=user.uid)
    textversion304 = TextVersion(content="viele Arbeiten auch durch die Mitarbeiter erledigt werden können", author=user.uid)
    textversion305 = TextVersion(content="\"rücksichtsvolle Verhaltensanpassungen\" viel zu allgemein gehalten ist", author=user.uid)
    textversion306 = TextVersion(content="das Faxgerät nicht immer zugänglich ist, wenn die Sekretärinnen nicht anwesend sind", author=user.uid)
    textversion307 = TextVersion(content="wir keine eigenen Faxgeräte haben und so oder so entweder bei Martin stören müssten oder doch bei Sabine im Büro landen würden", author=user.uid)

    session.add_all([textversion1, textversion2, textversion3, textversion4, textversion5, textversion6])
    session.add_all([textversion7, textversion8, textversion9, textversion10, textversion11, textversion12])
    session.add_all([textversion13, textversion14, textversion15, textversion16, textversion17, textversion18])
    session.add_all([textversion19, textversion20, textversion21, textversion22, textversion23, textversion24])
    session.add_all([textversion25, textversion26, textversion27, textversion29, textversion30, textversion31])
    session.add_all([textversion32, textversion33, textversion34, textversion35, textversion36])
    session.add_all([textversion101, textversion102, textversion103, textversion105])
    session.add_all([textversion106, textversion107, textversion108, textversion109, textversion110, textversion111])
    session.add_all([textversion112, textversion113, textversion114, textversion115, textversion116, textversion117])
    session.add_all([textversion118, textversion119, textversion120, textversion121, textversion122, textversion123])
    session.add_all([textversion200, textversion201, textversion202, textversion203, textversion204, textversion205])
    session.add_all([textversion206, textversion207, textversion208, textversion209, textversion210, textversion211])
    session.add_all([textversion301, textversion302, textversion303, textversion304, textversion305, textversion306])
    session.add_all([textversion307])
    session.flush()

    # random timestamps
    db_textversions = session.query(TextVersion).all()
    for tv in db_textversions:
        tv.timestamp = arrow.utcnow().replace(days=-random.randint(0, 25))

    # adding all statements
    statement1 = Statement(textversion=textversion1.uid, is_position=True, issue=issue2.uid)
    statement2 = Statement(textversion=textversion2.uid, is_position=True, issue=issue2.uid)
    statement3 = Statement(textversion=textversion3.uid, is_position=True, issue=issue2.uid)
    statement4 = Statement(textversion=textversion4.uid, is_position=False, issue=issue2.uid)
    statement5 = Statement(textversion=textversion5.uid, is_position=False, issue=issue2.uid)
    statement6 = Statement(textversion=textversion6.uid, is_position=False, issue=issue2.uid)
    statement7 = Statement(textversion=textversion7.uid, is_position=False, issue=issue2.uid)
    statement8 = Statement(textversion=textversion8.uid, is_position=False, issue=issue2.uid)
    statement9 = Statement(textversion=textversion9.uid, is_position=False, issue=issue2.uid)
    statement10 = Statement(textversion=textversion10.uid, is_position=False, issue=issue2.uid)
    statement11 = Statement(textversion=textversion11.uid, is_position=False, issue=issue2.uid)
    statement12 = Statement(textversion=textversion12.uid, is_position=False, issue=issue2.uid)
    statement13 = Statement(textversion=textversion13.uid, is_position=False, issue=issue2.uid)
    statement14 = Statement(textversion=textversion14.uid, is_position=False, issue=issue2.uid)
    statement15 = Statement(textversion=textversion15.uid, is_position=False, issue=issue2.uid)
    statement16 = Statement(textversion=textversion16.uid, is_position=False, issue=issue2.uid)
    statement17 = Statement(textversion=textversion17.uid, is_position=False, issue=issue2.uid)
    statement18 = Statement(textversion=textversion18.uid, is_position=False, issue=issue2.uid)
    statement19 = Statement(textversion=textversion19.uid, is_position=False, issue=issue2.uid)
    statement20 = Statement(textversion=textversion20.uid, is_position=False, issue=issue2.uid)
    statement21 = Statement(textversion=textversion21.uid, is_position=False, issue=issue2.uid)
    statement22 = Statement(textversion=textversion22.uid, is_position=False, issue=issue2.uid)
    statement23 = Statement(textversion=textversion23.uid, is_position=False, issue=issue2.uid)
    statement24 = Statement(textversion=textversion24.uid, is_position=False, issue=issue2.uid)
    statement25 = Statement(textversion=textversion25.uid, is_position=False, issue=issue2.uid)
    statement26 = Statement(textversion=textversion26.uid, is_position=False, issue=issue2.uid)
    statement27 = Statement(textversion=textversion27.uid, is_position=False, issue=issue2.uid)
    statement29 = Statement(textversion=textversion29.uid, is_position=False, issue=issue2.uid)
    statement30 = Statement(textversion=textversion30.uid, is_position=False, issue=issue2.uid)
    statement31 = Statement(textversion=textversion31.uid, is_position=False, issue=issue2.uid)
    statement32 = Statement(textversion=textversion32.uid, is_position=False, issue=issue2.uid)
    statement33 = Statement(textversion=textversion33.uid, is_position=False, issue=issue2.uid)
    statement34 = Statement(textversion=textversion34.uid, is_position=False, issue=issue2.uid)
    statement35 = Statement(textversion=textversion35.uid, is_position=False, issue=issue2.uid)
    statement36 = Statement(textversion=textversion36.uid, is_position=False, issue=issue2.uid)
    statement101 = Statement(textversion=textversion101.uid, is_position=True, issue=issue1.uid)
    statement102 = Statement(textversion=textversion102.uid, is_position=True, issue=issue1.uid)
    statement103 = Statement(textversion=textversion103.uid, is_position=True, issue=issue1.uid)
    statement105 = Statement(textversion=textversion105.uid, is_position=False, issue=issue1.uid)
    statement106 = Statement(textversion=textversion106.uid, is_position=False, issue=issue1.uid)
    statement107 = Statement(textversion=textversion107.uid, is_position=False, issue=issue1.uid)
    statement108 = Statement(textversion=textversion108.uid, is_position=False, issue=issue1.uid)
    statement109 = Statement(textversion=textversion109.uid, is_position=False, issue=issue1.uid)
    statement110 = Statement(textversion=textversion110.uid, is_position=False, issue=issue1.uid)
    statement111 = Statement(textversion=textversion111.uid, is_position=False, issue=issue1.uid)
    statement112 = Statement(textversion=textversion112.uid, is_position=False, issue=issue1.uid)
    statement113 = Statement(textversion=textversion113.uid, is_position=False, issue=issue1.uid)
    statement114 = Statement(textversion=textversion114.uid, is_position=False, issue=issue1.uid)
    statement115 = Statement(textversion=textversion115.uid, is_position=False, issue=issue1.uid)
    statement116 = Statement(textversion=textversion116.uid, is_position=False, issue=issue1.uid)
    statement117 = Statement(textversion=textversion117.uid, is_position=False, issue=issue1.uid)
    statement118 = Statement(textversion=textversion118.uid, is_position=False, issue=issue1.uid)
    statement119 = Statement(textversion=textversion119.uid, is_position=False, issue=issue1.uid)
    statement120 = Statement(textversion=textversion120.uid, is_position=False, issue=issue1.uid)
    statement121 = Statement(textversion=textversion121.uid, is_position=False, issue=issue1.uid)
    statement122 = Statement(textversion=textversion122.uid, is_position=False, issue=issue1.uid)
    statement123 = Statement(textversion=textversion123.uid, is_position=False, issue=issue1.uid)
    statement200 = Statement(textversion=textversion200.uid, is_position=True, issue=issue4.uid)
    statement201 = Statement(textversion=textversion201.uid, is_position=True, issue=issue4.uid)
    statement202 = Statement(textversion=textversion202.uid, is_position=True, issue=issue4.uid)
    statement203 = Statement(textversion=textversion203.uid, is_position=False, issue=issue4.uid)
    statement204 = Statement(textversion=textversion204.uid, is_position=False, issue=issue4.uid)
    statement205 = Statement(textversion=textversion205.uid, is_position=False, issue=issue4.uid)
    statement206 = Statement(textversion=textversion206.uid, is_position=False, issue=issue4.uid)
    statement207 = Statement(textversion=textversion207.uid, is_position=False, issue=issue4.uid)
    statement208 = Statement(textversion=textversion208.uid, is_position=False, issue=issue4.uid)
    statement209 = Statement(textversion=textversion209.uid, is_position=False, issue=issue4.uid)
    statement210 = Statement(textversion=textversion210.uid, is_position=False, issue=issue4.uid)
    statement211 = Statement(textversion=textversion211.uid, is_position=False, issue=issue4.uid)
    statement301 = Statement(textversion=textversion301.uid, is_position=True, issue=issue5.uid)
    statement302 = Statement(textversion=textversion302.uid, is_position=True, issue=issue5.uid)
    statement303 = Statement(textversion=textversion303.uid, is_position=False, issue=issue5.uid)
    statement304 = Statement(textversion=textversion304.uid, is_position=False, issue=issue5.uid)
    statement305 = Statement(textversion=textversion305.uid, is_position=False, issue=issue5.uid)
    statement306 = Statement(textversion=textversion306.uid, is_position=False, issue=issue5.uid)
    statement307 = Statement(textversion=textversion307.uid, is_position=False, issue=issue5.uid)

    session.add_all([statement1, statement2, statement3, statement4, statement5, statement6, statement7])
    session.add_all([statement8, statement9, statement10, statement11, statement12, statement13, statement14])
    session.add_all([statement15, statement16, statement17, statement18, statement19, statement20, statement21])
    session.add_all([statement22, statement23, statement24, statement25, statement26, statement27, statement29])
    session.add_all([statement30, statement31, statement32, statement33, statement34, statement35, statement36])
    session.add_all([statement101, statement102, statement103, statement105, statement106, statement107, statement108])
    session.add_all([statement109, statement110, statement111, statement112, statement113, statement114, statement115])
    session.add_all([statement116, statement117, statement118, statement119, statement120, statement121, statement122])
    session.add_all([statement123])
    session.add_all([statement200, statement201, statement202, statement203, statement204, statement205, statement206])
    session.add_all([statement207, statement208, statement209, statement210, statement211])
    session.add_all([statement301, statement302, statement303, statement304, statement305, statement306, statement307])

    session.flush()

    session.flush()

    # set textversions
    textversion1.set_statement(statement1.uid)
    textversion2.set_statement(statement2.uid)
    textversion3.set_statement(statement3.uid)
    textversion4.set_statement(statement4.uid)
    textversion5.set_statement(statement5.uid)
    textversion6.set_statement(statement6.uid)
    textversion7.set_statement(statement7.uid)
    textversion8.set_statement(statement8.uid)
    textversion9.set_statement(statement9.uid)
    textversion10.set_statement(statement10.uid)
    textversion11.set_statement(statement11.uid)
    textversion12.set_statement(statement12.uid)
    textversion13.set_statement(statement13.uid)
    textversion14.set_statement(statement14.uid)
    textversion15.set_statement(statement15.uid)
    textversion16.set_statement(statement16.uid)
    textversion17.set_statement(statement17.uid)
    textversion18.set_statement(statement18.uid)
    textversion19.set_statement(statement19.uid)
    textversion20.set_statement(statement20.uid)
    textversion21.set_statement(statement21.uid)
    textversion22.set_statement(statement22.uid)
    textversion23.set_statement(statement23.uid)
    textversion24.set_statement(statement24.uid)
    textversion25.set_statement(statement25.uid)
    textversion26.set_statement(statement26.uid)
    textversion27.set_statement(statement27.uid)
    textversion29.set_statement(statement29.uid)
    textversion30.set_statement(statement30.uid)
    textversion31.set_statement(statement31.uid)
    textversion32.set_statement(statement32.uid)
    textversion33.set_statement(statement33.uid)
    textversion34.set_statement(statement34.uid)
    textversion35.set_statement(statement35.uid)
    textversion36.set_statement(statement36.uid)
    textversion101.set_statement(statement101.uid)
    textversion102.set_statement(statement102.uid)
    textversion103.set_statement(statement103.uid)
    textversion105.set_statement(statement105.uid)
    textversion106.set_statement(statement106.uid)
    textversion107.set_statement(statement107.uid)
    textversion108.set_statement(statement108.uid)
    textversion109.set_statement(statement109.uid)
    textversion110.set_statement(statement110.uid)
    textversion111.set_statement(statement111.uid)
    textversion112.set_statement(statement112.uid)
    textversion113.set_statement(statement113.uid)
    textversion114.set_statement(statement114.uid)
    textversion115.set_statement(statement115.uid)
    textversion116.set_statement(statement116.uid)
    textversion117.set_statement(statement117.uid)
    textversion118.set_statement(statement118.uid)
    textversion119.set_statement(statement119.uid)
    textversion120.set_statement(statement120.uid)
    textversion121.set_statement(statement121.uid)
    textversion122.set_statement(statement122.uid)
    textversion123.set_statement(statement123.uid)
    textversion200.set_statement(statement200.uid)
    textversion201.set_statement(statement201.uid)
    textversion202.set_statement(statement202.uid)
    textversion203.set_statement(statement203.uid)
    textversion204.set_statement(statement204.uid)
    textversion205.set_statement(statement205.uid)
    textversion206.set_statement(statement206.uid)
    textversion207.set_statement(statement207.uid)
    textversion208.set_statement(statement208.uid)
    textversion209.set_statement(statement209.uid)
    textversion210.set_statement(statement210.uid)
    textversion211.set_statement(statement211.uid)
    textversion301.set_statement(statement301.uid)
    textversion302.set_statement(statement302.uid)
    textversion303.set_statement(statement303.uid)
    textversion304.set_statement(statement304.uid)
    textversion305.set_statement(statement305.uid)
    textversion306.set_statement(statement306.uid)
    textversion307.set_statement(statement307.uid)

    # adding all premisegroups
    premisegroup1 = PremiseGroup(author=user.uid)
    premisegroup2 = PremiseGroup(author=user.uid)
    premisegroup3 = PremiseGroup(author=user.uid)
    premisegroup4 = PremiseGroup(author=user.uid)
    premisegroup5 = PremiseGroup(author=user.uid)
    premisegroup6 = PremiseGroup(author=user.uid)
    premisegroup7 = PremiseGroup(author=user.uid)
    premisegroup8 = PremiseGroup(author=user.uid)
    premisegroup9 = PremiseGroup(author=user.uid)
    premisegroup10 = PremiseGroup(author=user.uid)
    premisegroup11 = PremiseGroup(author=user.uid)
    premisegroup12 = PremiseGroup(author=user.uid)
    premisegroup13 = PremiseGroup(author=user.uid)
    premisegroup14 = PremiseGroup(author=user.uid)
    premisegroup15 = PremiseGroup(author=user.uid)
    premisegroup16 = PremiseGroup(author=user.uid)
    premisegroup17 = PremiseGroup(author=user.uid)
    premisegroup18 = PremiseGroup(author=user.uid)
    premisegroup19 = PremiseGroup(author=user.uid)
    premisegroup20 = PremiseGroup(author=user.uid)
    premisegroup21 = PremiseGroup(author=user.uid)
    premisegroup22 = PremiseGroup(author=user.uid)
    premisegroup23 = PremiseGroup(author=user.uid)
    premisegroup24 = PremiseGroup(author=user.uid)
    premisegroup25 = PremiseGroup(author=user.uid)
    premisegroup26 = PremiseGroup(author=user.uid)
    premisegroup27 = PremiseGroup(author=user.uid)
    premisegroup28 = PremiseGroup(author=user.uid)
    premisegroup29 = PremiseGroup(author=user.uid)
    premisegroup105 = PremiseGroup(author=user.uid)
    premisegroup106 = PremiseGroup(author=user.uid)
    premisegroup107 = PremiseGroup(author=user.uid)
    premisegroup108 = PremiseGroup(author=user.uid)
    premisegroup109 = PremiseGroup(author=user.uid)
    premisegroup110 = PremiseGroup(author=user.uid)
    premisegroup111 = PremiseGroup(author=user.uid)
    premisegroup112 = PremiseGroup(author=user.uid)
    premisegroup113 = PremiseGroup(author=user.uid)
    premisegroup114 = PremiseGroup(author=user.uid)
    premisegroup115 = PremiseGroup(author=user.uid)
    premisegroup116 = PremiseGroup(author=user.uid)
    premisegroup117 = PremiseGroup(author=user.uid)
    premisegroup118 = PremiseGroup(author=user.uid)
    premisegroup119 = PremiseGroup(author=user.uid)
    premisegroup120 = PremiseGroup(author=user.uid)
    premisegroup121 = PremiseGroup(author=user.uid)
    premisegroup122 = PremiseGroup(author=user.uid)
    premisegroup123 = PremiseGroup(author=user.uid)
    premisegroup203 = PremiseGroup(author=user.uid)
    premisegroup204 = PremiseGroup(author=user.uid)
    premisegroup205 = PremiseGroup(author=user.uid)
    premisegroup206 = PremiseGroup(author=user.uid)
    premisegroup207 = PremiseGroup(author=user.uid)
    premisegroup208 = PremiseGroup(author=user.uid)
    premisegroup209 = PremiseGroup(author=user.uid)
    premisegroup210 = PremiseGroup(author=user.uid)
    premisegroup211 = PremiseGroup(author=user.uid)
    premisegroup303 = PremiseGroup(author=user.uid)
    premisegroup304 = PremiseGroup(author=user.uid)
    premisegroup305 = PremiseGroup(author=user.uid)
    premisegroup306 = PremiseGroup(author=user.uid)
    premisegroup307 = PremiseGroup(author=user.uid)

    session.add_all([premisegroup1, premisegroup2, premisegroup3, premisegroup4, premisegroup5, premisegroup6])
    session.add_all([premisegroup7, premisegroup8, premisegroup9, premisegroup10, premisegroup11, premisegroup12])
    session.add_all([premisegroup13, premisegroup14, premisegroup15, premisegroup16, premisegroup17, premisegroup18])
    session.add_all([premisegroup19, premisegroup20, premisegroup21, premisegroup22, premisegroup23, premisegroup24])
    session.add_all([premisegroup25, premisegroup26, premisegroup27, premisegroup28, premisegroup29])
    session.add_all([premisegroup105, premisegroup106, premisegroup107, premisegroup108, premisegroup109])
    session.add_all([premisegroup110, premisegroup111, premisegroup112, premisegroup113, premisegroup114])
    session.add_all([premisegroup115, premisegroup116, premisegroup117, premisegroup118, premisegroup119])
    session.add_all([premisegroup120, premisegroup121, premisegroup122, premisegroup123])
    session.add_all([premisegroup203, premisegroup204, premisegroup205, premisegroup206, premisegroup207])
    session.add_all([premisegroup208, premisegroup209, premisegroup210, premisegroup211])
    session.add_all([premisegroup303, premisegroup304, premisegroup305, premisegroup306, premisegroup307])
    session.flush()

    premise1 = Premise(premisesgroup=premisegroup1.uid, statement=statement4.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise2 = Premise(premisesgroup=premisegroup2.uid, statement=statement5.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise3 = Premise(premisesgroup=premisegroup3.uid, statement=statement6.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise4 = Premise(premisesgroup=premisegroup4.uid, statement=statement7.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise5 = Premise(premisesgroup=premisegroup5.uid, statement=statement8.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise6 = Premise(premisesgroup=premisegroup6.uid, statement=statement9.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise7 = Premise(premisesgroup=premisegroup7.uid, statement=statement10.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise8 = Premise(premisesgroup=premisegroup8.uid, statement=statement11.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise9 = Premise(premisesgroup=premisegroup9.uid, statement=statement12.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise10 = Premise(premisesgroup=premisegroup10.uid, statement=statement13.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise11 = Premise(premisesgroup=premisegroup11.uid, statement=statement14.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise12 = Premise(premisesgroup=premisegroup11.uid, statement=statement15.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise13 = Premise(premisesgroup=premisegroup12.uid, statement=statement16.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise14 = Premise(premisesgroup=premisegroup13.uid, statement=statement17.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise15 = Premise(premisesgroup=premisegroup14.uid, statement=statement18.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise16 = Premise(premisesgroup=premisegroup15.uid, statement=statement19.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise17 = Premise(premisesgroup=premisegroup16.uid, statement=statement20.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise18 = Premise(premisesgroup=premisegroup17.uid, statement=statement21.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise19 = Premise(premisesgroup=premisegroup18.uid, statement=statement22.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise20 = Premise(premisesgroup=premisegroup19.uid, statement=statement23.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise21 = Premise(premisesgroup=premisegroup20.uid, statement=statement24.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise22 = Premise(premisesgroup=premisegroup21.uid, statement=statement25.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise23 = Premise(premisesgroup=premisegroup22.uid, statement=statement26.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise24 = Premise(premisesgroup=premisegroup23.uid, statement=statement27.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise25 = Premise(premisesgroup=premisegroup24.uid, statement=statement29.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise26 = Premise(premisesgroup=premisegroup25.uid, statement=statement30.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise27 = Premise(premisesgroup=premisegroup26.uid, statement=statement31.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise28 = Premise(premisesgroup=premisegroup27.uid, statement=statement32.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise29 = Premise(premisesgroup=premisegroup28.uid, statement=statement33.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise30 = Premise(premisesgroup=premisegroup29.uid, statement=statement36.uid, is_negated=False, author=user.uid, issue=issue2.uid)
    premise105 = Premise(premisesgroup=premisegroup105.uid, statement=statement105.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise106 = Premise(premisesgroup=premisegroup106.uid, statement=statement106.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise107 = Premise(premisesgroup=premisegroup107.uid, statement=statement107.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise108 = Premise(premisesgroup=premisegroup108.uid, statement=statement108.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise109 = Premise(premisesgroup=premisegroup109.uid, statement=statement109.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise110 = Premise(premisesgroup=premisegroup110.uid, statement=statement110.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise111 = Premise(premisesgroup=premisegroup111.uid, statement=statement111.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise112 = Premise(premisesgroup=premisegroup112.uid, statement=statement112.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise113 = Premise(premisesgroup=premisegroup113.uid, statement=statement113.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise114 = Premise(premisesgroup=premisegroup114.uid, statement=statement114.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise115 = Premise(premisesgroup=premisegroup115.uid, statement=statement115.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise116 = Premise(premisesgroup=premisegroup116.uid, statement=statement116.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise117 = Premise(premisesgroup=premisegroup117.uid, statement=statement117.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise118 = Premise(premisesgroup=premisegroup118.uid, statement=statement118.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise119 = Premise(premisesgroup=premisegroup119.uid, statement=statement119.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise120 = Premise(premisesgroup=premisegroup120.uid, statement=statement120.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise121 = Premise(premisesgroup=premisegroup121.uid, statement=statement121.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise122 = Premise(premisesgroup=premisegroup122.uid, statement=statement122.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise123 = Premise(premisesgroup=premisegroup123.uid, statement=statement123.uid, is_negated=False, author=user.uid, issue=issue1.uid)
    premise203 = Premise(premisesgroup=premisegroup203.uid, statement=statement203.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise204 = Premise(premisesgroup=premisegroup204.uid, statement=statement204.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise205 = Premise(premisesgroup=premisegroup205.uid, statement=statement205.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise206 = Premise(premisesgroup=premisegroup206.uid, statement=statement206.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise207 = Premise(premisesgroup=premisegroup207.uid, statement=statement207.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise208 = Premise(premisesgroup=premisegroup208.uid, statement=statement208.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise209 = Premise(premisesgroup=premisegroup209.uid, statement=statement209.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise210 = Premise(premisesgroup=premisegroup210.uid, statement=statement210.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise211 = Premise(premisesgroup=premisegroup211.uid, statement=statement211.uid, is_negated=False, author=user.uid, issue=issue4.uid)
    premise303 = Premise(premisesgroup=premisegroup303.uid, statement=statement303.uid, is_negated=False, author=user.uid, issue=issue5.uid)
    premise304 = Premise(premisesgroup=premisegroup304.uid, statement=statement304.uid, is_negated=False, author=user.uid, issue=issue5.uid)
    premise305 = Premise(premisesgroup=premisegroup305.uid, statement=statement305.uid, is_negated=False, author=user.uid, issue=issue5.uid)
    premise306 = Premise(premisesgroup=premisegroup306.uid, statement=statement306.uid, is_negated=False, author=user.uid, issue=issue5.uid)
    premise307 = Premise(premisesgroup=premisegroup307.uid, statement=statement307.uid, is_negated=False, author=user.uid, issue=issue5.uid)

    session.add_all([premise1, premise2, premise3, premise4, premise5, premise6, premise7, premise8, premise9])
    session.add_all([premise10, premise11, premise12, premise13, premise14, premise15, premise16, premise17])
    session.add_all([premise18, premise19, premise20, premise21, premise22, premise23, premise24, premise25])
    session.add_all([premise26, premise27, premise28, premise29, premise30])
    session.add_all([premise105, premise106, premise107, premise108, premise109, premise110, premise111, premise112])
    session.add_all([premise113, premise114, premise115, premise116, premise117, premise118, premise119, premise120])
    session.add_all([premise121, premise122, premise123])
    session.add_all([premise203, premise204, premise205, premise206, premise207, premise208, premise209, premise210])
    session.add_all([premise211])
    session.add_all([premise303, premise304, premise305, premise306, premise307])
    session.flush()

    # adding all arguments and set the adjacency list
    argument1 = Argument(premisegroup=premisegroup1.uid, issupportive=True, author=user.uid, conclusion=statement1.uid, issue=issue2.uid)
    argument2 = Argument(premisegroup=premisegroup2.uid, issupportive=False, author=user.uid, conclusion=statement1.uid, issue=issue2.uid)
    argument3 = Argument(premisegroup=premisegroup3.uid, issupportive=True, author=user.uid, conclusion=statement2.uid, issue=issue2.uid)
    argument4 = Argument(premisegroup=premisegroup4.uid, issupportive=False, author=user.uid, conclusion=statement2.uid, issue=issue2.uid)
    argument5 = Argument(premisegroup=premisegroup5.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument6 = Argument(premisegroup=premisegroup6.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument7 = Argument(premisegroup=premisegroup7.uid, issupportive=True, author=user.uid, conclusion=statement3.uid, issue=issue2.uid)
    argument8 = Argument(premisegroup=premisegroup8.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument9 = Argument(premisegroup=premisegroup9.uid, issupportive=False, author=user.uid, conclusion=statement10.uid, issue=issue2.uid)
    argument10 = Argument(premisegroup=premisegroup10.uid, issupportive=True, author=user.uid, conclusion=statement1.uid, issue=issue2.uid)
    argument11 = Argument(premisegroup=premisegroup11.uid, issupportive=True, author=user.uid, conclusion=statement1.uid, issue=issue2.uid)
    argument12 = Argument(premisegroup=premisegroup12.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument13 = Argument(premisegroup=premisegroup13.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument14 = Argument(premisegroup=premisegroup14.uid, issupportive=True, author=user.uid, conclusion=statement4.uid, issue=issue2.uid)
    argument15 = Argument(premisegroup=premisegroup15.uid, issupportive=False, author=user.uid, conclusion=statement4.uid, issue=issue2.uid)
    argument16 = Argument(premisegroup=premisegroup16.uid, issupportive=True, author=user.uid, conclusion=statement4.uid, issue=issue2.uid)
    argument17 = Argument(premisegroup=premisegroup17.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument18 = Argument(premisegroup=premisegroup18.uid, issupportive=True, author=user.uid, conclusion=statement5.uid, issue=issue2.uid)
    argument19 = Argument(premisegroup=premisegroup19.uid, issupportive=False, author=user.uid, conclusion=statement5.uid, issue=issue2.uid)
    argument20 = Argument(premisegroup=premisegroup20.uid, issupportive=False, author=user.uid, conclusion=statement5.uid, issue=issue2.uid)
    argument21 = Argument(premisegroup=premisegroup21.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument22 = Argument(premisegroup=premisegroup22.uid, issupportive=False, author=user.uid, conclusion=statement13.uid, issue=issue2.uid)
    argument23 = Argument(premisegroup=premisegroup23.uid, issupportive=True, author=user.uid, conclusion=statement13.uid, issue=issue2.uid)
    argument24 = Argument(premisegroup=premisegroup24.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    argument25 = Argument(premisegroup=premisegroup25.uid, issupportive=True, author=user.uid, conclusion=statement13.uid, issue=issue2.uid)
    argument26 = Argument(premisegroup=premisegroup26.uid, issupportive=True, author=user.uid, conclusion=statement14.uid, issue=issue2.uid)
    argument27 = Argument(premisegroup=premisegroup26.uid, issupportive=True, author=user.uid, conclusion=statement15.uid, issue=issue2.uid)
    argument28 = Argument(premisegroup=premisegroup27.uid, issupportive=True, author=user.uid, conclusion=statement14.uid, issue=issue2.uid)
    # argument28 = Argument(premisegroup=premisegroup27.uid, issupportive=True, author=user.uid, conclusion=statement15.uid, issue=issue2.uid)
    # argument29 = Argument(premisegroup=premisegroup28.uid, issupportive=False, author=user.uid, conclusion=statement14.uid, issue=issue2.uid)
    argument30 = Argument(premisegroup=premisegroup28.uid, issupportive=False, author=user.uid, conclusion=statement15.uid, issue=issue2.uid)
    argument31 = Argument(premisegroup=premisegroup29.uid, issupportive=False, author=user.uid, issue=issue2.uid)
    ####
    argument101 = Argument(premisegroup=premisegroup105.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement101.uid)
    argument102 = Argument(premisegroup=premisegroup106.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument103 = Argument(premisegroup=premisegroup107.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement105.uid)
    argument104 = Argument(premisegroup=premisegroup108.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement107.uid)
    argument105 = Argument(premisegroup=premisegroup109.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement101.uid)
    argument106 = Argument(premisegroup=premisegroup110.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument107 = Argument(premisegroup=premisegroup111.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument108 = Argument(premisegroup=premisegroup112.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement102.uid)
    argument109 = Argument(premisegroup=premisegroup113.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement102.uid)
    argument110 = Argument(premisegroup=premisegroup115.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement112.uid)
    # argument111 = Argument(premisegroup=premisegroup114.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument112 = Argument(premisegroup=premisegroup116.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement102.uid)
    argument113 = Argument(premisegroup=premisegroup117.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument114 = Argument(premisegroup=premisegroup118.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement116.uid)
    argument115 = Argument(premisegroup=premisegroup119.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement116.uid)
    argument116 = Argument(premisegroup=premisegroup120.uid, issupportive=True, author=user.uid, issue=issue1.uid, conclusion=statement103.uid)
    argument117 = Argument(premisegroup=premisegroup121.uid, issupportive=False, author=user.uid, issue=issue1.uid)
    argument118 = Argument(premisegroup=premisegroup122.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement103.uid)
    argument119 = Argument(premisegroup=premisegroup123.uid, issupportive=False, author=user.uid, issue=issue1.uid, conclusion=statement115.uid)
    ####
    argument201 = Argument(premisegroup=premisegroup203.uid, issupportive=True, author=user.uid, issue=issue4.uid, conclusion=statement200.uid)
    argument202 = Argument(premisegroup=premisegroup204.uid, issupportive=False, author=user.uid, issue=issue4.uid, conclusion=statement200.uid)
    argument203 = Argument(premisegroup=premisegroup205.uid, issupportive=False, author=user.uid, issue=issue4.uid, conclusion=statement201.uid)
    argument204 = Argument(premisegroup=premisegroup206.uid, issupportive=True, author=user.uid, issue=issue4.uid, conclusion=statement202.uid)
    argument205 = Argument(premisegroup=premisegroup207.uid, issupportive=False, author=user.uid, issue=issue4.uid, conclusion=statement202.uid)
    argument206 = Argument(premisegroup=premisegroup208.uid, issupportive=False, author=user.uid, issue=issue4.uid)
    argument207 = Argument(premisegroup=premisegroup209.uid, issupportive=False, author=user.uid, issue=issue4.uid)
    argument208 = Argument(premisegroup=premisegroup210.uid, issupportive=False, author=user.uid, issue=issue4.uid)
    argument209 = Argument(premisegroup=premisegroup211.uid, issupportive=False, author=user.uid, issue=issue4.uid)
    ####
    argument303 = Argument(premisegroup=premisegroup303.uid, issupportive=True, author=user.uid, issue=issue5.uid, conclusion=statement301.uid)
    argument304 = Argument(premisegroup=premisegroup304.uid, issupportive=True, author=user.uid, issue=issue5.uid, conclusion=statement301.uid)
    argument305 = Argument(premisegroup=premisegroup305.uid, issupportive=False, author=user.uid, issue=issue5.uid, conclusion=statement301.uid)
    argument306 = Argument(premisegroup=premisegroup306.uid, issupportive=False, author=user.uid, issue=issue5.uid, conclusion=statement302.uid)
    argument307 = Argument(premisegroup=premisegroup307.uid, issupportive=False, author=user.uid, issue=issue5.uid, conclusion=statement302.uid)

    session.add_all([argument1, argument2, argument3, argument4, argument5, argument6, argument7, argument8])
    session.add_all([argument9, argument10, argument11, argument12, argument13, argument14, argument15])
    session.add_all([argument16, argument17, argument18, argument19, argument20, argument21, argument22])
    session.add_all([argument23, argument24, argument25, argument26, argument27, argument28])  # , argument29])
    session.add_all([argument30, argument31])
    session.add_all([argument101, argument102, argument103, argument104, argument105, argument106, argument107])
    session.add_all([argument108, argument109, argument110, argument112, argument113, argument114])  # , argument111])
    session.add_all([argument115, argument116, argument117, argument118, argument119])
    session.add_all([argument201, argument202, argument203, argument204, argument205, argument206, argument207])
    session.add_all([argument208, argument209])
    session.add_all([argument303, argument304, argument305, argument306, argument307])
    session.flush()

    argument5.conclusions_argument(argument3.uid)
    argument6.conclusions_argument(argument4.uid)
    argument8.conclusions_argument(argument7.uid)
    argument12.conclusions_argument(argument11.uid)
    argument13.conclusions_argument(argument12.uid)
    argument17.conclusions_argument(argument1.uid)
    argument21.conclusions_argument(argument2.uid)
    argument24.conclusions_argument(argument10.uid)
    argument26.conclusions_argument(argument11.uid)
    argument31.conclusions_argument(argument14.uid)
    argument102.conclusions_argument(argument101.uid)
    argument106.conclusions_argument(argument105.uid)
    argument107.conclusions_argument(argument105.uid)
    # argument111.conclusions_argument(argument110.uid)
    argument113.conclusions_argument(argument112.uid)
    argument117.conclusions_argument(argument116.uid)
    argument206.conclusions_argument(argument201.uid)
    argument207.conclusions_argument(argument202.uid)
    argument208.conclusions_argument(argument204.uid)
    argument209.conclusions_argument(argument205.uid)
    session.flush()
