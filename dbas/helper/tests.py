"""
Utility functions for testing.

.. codeauthor:: Christian Meter <meter@cs.uni-duesseldorf.de
.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""
import os
import transaction

from paste.deploy import appconfig
from dbas.database import DBDiscussionSession as dbs
from dbas.database.discussion_model import SeenStatement, ClickedStatement, SeenArgument, ClickedArgument, User


def path_to_settings(ini_file):
    """
    Find directory of ini-file relative to this directory (currently two directories up).

    :param ini_file: name of ini-file, e.g. development.ini
    :type: str
    :return: path to directory containing ini-file
    :rtype: str
    """
    dir_name = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(dir_name, ini_file)


def add_settings_to_appconfig(ini_file="development.ini"):
    """
    Configure appconfig to set correct ini-file. Defaults to development.ini for testing purposes.
    If dbas runs inside a docker container and no ini-file is provided, then load the docker.ini.

    :param ini_file: name of ini-file
    :return: config with loaded ini-file
    :rtype: dict
    """
    if os.path.isfile("/.dockerenv") and not ini_file:
        return appconfig("config:" + path_to_settings("docker.ini"))
    return appconfig("config:" + path_to_settings(ini_file))


def verify_dictionary_of_view(_self, some_dict):
    """
    Check for keys in the dict

    :param _self: Instance of unittest.TestCase
    :param some_dict: dict()
    :return: None
    :rtype: None
    """
    _self.assertIn('layout', some_dict)
    _self.assertIn('ui_locales', some_dict['extras'])
    _self.assertIn('title', some_dict)
    _self.assertIn('extras', some_dict)


def clear_seen_by_of(nickname):
    """
    Clears every "SeenBy" rows of the user

    :param nickname: User.nickname
    :return: None
    """
    db_user = dbs.query(User).filter_by(nickname=nickname).first()
    dbs.query(SeenStatement).filter_by(user_uid=db_user.uid).delete()
    dbs.query(SeenArgument).filter_by(user_uid=db_user.uid).delete()
    transaction.commit()


def clear_clicks_of(nickname):
    """
    Clears ever clicked elements of the user

    :param nickname: User.nickname
    :return: None
    """
    db_user = dbs.query(User).filter_by(nickname=nickname).first()
    dbs.query(ClickedStatement).filter_by(author_uid=db_user.uid).delete()
    dbs.query(ClickedArgument).filter_by(author_uid=db_user.uid).delete()
    transaction.commit()
