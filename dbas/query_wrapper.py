"""
Provides helping function for querying the database.

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Statement, Argument, Premise


def get_not_disabled_statement_as_query():
    return DBDiscussionSession.query(Statement).filter_by(is_disabled=False)


def get_not_disabled_arguments_as_query():
    return DBDiscussionSession.query(Argument).filter_by(is_disabled=False)


def get_not_disabled_premises_as_query():
    return DBDiscussionSession.query(Premise).filter_by(is_disabled=False)
