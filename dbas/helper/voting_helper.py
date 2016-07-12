"""
Class for handling votes of each user.

Functions for setting votes of users. They set votes by clicking the statements in D-BAS.
We are not deleting opposite votes for detecting opinion changes!

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""


import dbas.user_management as UserHandler

from sqlalchemy import and_
from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, Statement, Premise, VoteArgument, VoteStatement, User, StatementSeenBy, ArgumentSeenBy
from dbas.logger import logger


def add_vote_for_argument(argument_uid, user, transaction):
    """
    Increases the votes of a given argument.

    :param argument_uid: id of the argument
    :param user: self.request.authenticated_userid
    :param transaction: transaction
    :return: increased votes of the argument
    """
    db_user = DBDiscussionSession.query(User).filter_by(nickname=user).first()
    if not UserHandler.is_user_logged_in(user) or not db_user:
        return None

    logger('VotingHelper', 'add_vote_for_argument', 'increasing argument ' + str(argument_uid) + ' vote')
    db_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid).first()

    # set vote for the argument (relation), its premisegroup and conclusion
    __vote_argument(db_argument, db_user, True)
    __vote_premisesgroup(db_argument.premisesgroup_uid, db_user, True)

    # user has seen this argument
    if db_user:
        __argument_seen_by_user(db_user.uid, argument_uid)

    if db_argument.argument_uid is None:
        db_conclusion = DBDiscussionSession.query(Statement).filter_by(uid=db_argument.conclusion_uid).first()
        __vote_statement(db_conclusion, db_user, True)
    else:
        # check for inconsequences
        db_conclusion_argument = DBDiscussionSession.query(Argument).filter_by(argument_uid=db_argument.argument_uid).first()
        db_conclusion_conclusion = DBDiscussionSession.query(Statement).filter_by(uid=db_conclusion_argument.conclusion_uid).first()
        if db_argument.is_supportive:
            if db_conclusion_argument.is_supportive:
                # argument supportive -> conclusion supportive
                __vote_argument(db_conclusion_argument, db_user, True)
                __vote_premisesgroup(db_conclusion_argument.premisesgroup_uid, db_user, True)
                __vote_statement(db_conclusion_conclusion, db_user, True)
            else:
                # argument supportive -> conclusion attacking
                __vote_argument(db_conclusion_argument, db_user, True)
                __vote_premisesgroup(db_conclusion_argument.premisesgroup_uid, db_user, True)
                __vote_statement(db_conclusion_conclusion, db_user, False)
        else:
            if db_conclusion_argument.is_supportive:
                # argument attacking -> conclusion supportive
                __vote_argument(db_conclusion_argument, db_user, False)
                __vote_premisesgroup(db_conclusion_argument.premisesgroup_uid, db_user, True)
                __vote_statement(db_conclusion_conclusion, db_user, False)
            else:
                # argument attacking -> conclusion attacking
                __vote_argument(db_conclusion_argument, db_user, False)
                __vote_premisesgroup(db_conclusion_argument.premisesgroup_uid, db_user, True)
                __vote_statement(db_conclusion_conclusion, db_user, True)

    # vote redundancy will be handled in the accept and decline methods!

    # return count of votes for this argument
    db_votes = DBDiscussionSession.query(VoteArgument).filter(and_(VoteArgument.argument_uid == db_argument.uid,
                                                                   VoteArgument.is_valid == True)).all()

    transaction.commit()

    return len(db_votes)


def add_vote_for_statement(statement_uid, user, supportive, transaction):
    """
    Adds a vote for the given statements

    :param statement_uid: Statement.uid
    :param user: User.nickname
    :param supportive: boolean
    :param transaction: Transaction
    :return: Boolean
    """
    logger('VotingHelper', 'add_vote_for_statement', 'increasing statement ' + str(statement_uid) + ' vote')

    db_statement = DBDiscussionSession.query(Statement).filter_by(uid=statement_uid).first()
    db_user = DBDiscussionSession.query(User).filter_by(nickname=user).first()
    if db_user:
        __vote_statement(db_statement, db_user, supportive)
        __statement_seen_by_user(db_user.uid, statement_uid)
        transaction.commit()
    return False


def clear_votes_of_user(transaction, user):
    """
    Deletes all votes of given user

    :param transaction: Transaction
    :param user: User.nickname
    :return: None
    """
    db_user = DBDiscussionSession.query(User).filter_by(nickname=user).first()
    if not db_user:
        return False

    DBDiscussionSession.query(VoteArgument).filter_by(author_uid=db_user.uid).delete()
    DBDiscussionSession.query(VoteStatement).filter_by(author_uid=db_user.uid).delete()
    DBDiscussionSession.query(StatementSeenBy).filter_by(user_uid=db_user.uid).delete()
    DBDiscussionSession.query(ArgumentSeenBy).filter_by(user_uid=db_user.uid).delete()
    DBDiscussionSession.flush()
    transaction.commit()
    return True


def __vote_argument(argument, user, is_up_vote):
    """
    Check if there is a vote for the argument. If not, we will create a new one, otherwise the current one will be
    invalid an we will create a new entry.

    :param argument: Argument
    :param user: User
    :param is_up_vote: Boolean
    :return: None
    """
    if argument is None:
        logger('VotingHelper', '__vote_argument', 'argument is None')
        return

    logger('VotingHelper', '__vote_argument', 'argument ' + str(argument.uid) + ', user ' + user.nickname)

    db_vote = DBDiscussionSession.query(VoteArgument).filter(and_(VoteArgument.argument_uid == argument.uid,
                                                                  VoteArgument.author_uid == user.uid,
                                                                  VoteArgument.is_up_vote == is_up_vote,
                                                                  VoteArgument.is_valid == True)).first()

    # old one will be invalid
    db_old_votes = DBDiscussionSession.query(VoteArgument).filter(and_(VoteArgument.argument_uid == argument.uid,
                                                                       VoteArgument.author_uid == user.uid,
                                                                       VoteArgument.is_valid == True)).all()

    # we are not deleting oppositve votes for detecting opinion changes!

    if db_vote in db_old_votes:
        db_old_votes.remove(db_vote)

    for old_vote in db_old_votes:
        old_vote.set_valid(False)
        old_vote.update_timestamp()
    DBDiscussionSession.flush()

    if not db_vote:
        db_new_vote = VoteArgument(argument_uid=argument.uid, author_uid=user.uid, is_up_vote=is_up_vote, is_valid=True)
        DBDiscussionSession.add(db_new_vote)
        DBDiscussionSession.flush()


def __vote_statement(statement, user, is_up_vote):
    """
    Check if there is a vote for the statement. If not, we will create a new one, otherwise the current one will be
    invalid an we will create a new entry.

    :param statement: Statement
    :param user: User
    :param is_up_vote: Boolean
    :return: None
    """
    if statement is None:
        logger('VotingHelper', '__vote_statement', 'statement is None')
        return

    logger('VotingHelper', '__vote_statement', 'statement ' + str(statement.uid) + ', user ' + user.nickname)

    # check for duplicate
    db_vote = DBDiscussionSession.query(VoteStatement).filter(and_(VoteStatement.statement_uid == statement.uid,
                                                                   VoteStatement.author_uid == user.uid,
                                                                   VoteStatement.is_up_vote == is_up_vote,
                                                                   VoteStatement.is_valid == True)).first()

    # old one will be invalid
    db_old_votes = DBDiscussionSession.query(VoteStatement).filter(and_(VoteStatement.statement_uid == statement.uid,
                                                                        VoteStatement.author_uid == user.uid,
                                                                        VoteStatement.is_valid == True)).all()

    # we are not deleting oppositve votes for detecting opinion changes!

    if db_vote in db_old_votes:
        db_old_votes.remove(db_vote)

    for old_vote in db_old_votes:
        old_vote.set_valid(False)
        old_vote.update_timestamp()
    DBDiscussionSession.flush()

    if not db_vote:
        db_new_vote = VoteStatement(statement_uid=statement.uid, author_uid=user.uid, is_up_vote=is_up_vote, is_valid=True)
        DBDiscussionSession.add(db_new_vote)
        DBDiscussionSession.flush()


def __vote_premisesgroup(premisesgroup_uid, user, is_up_vote):
    """
    Calls statemens-methods for every premise.

    :param premisegroup_uid: PremiseGroup.uid
    :param user: User
    :param is_up_vote: Boolean
    :return:
    """
    if premisesgroup_uid is None or premisesgroup_uid == 0:
        logger('VotingHelper', '__vote_premisesgroup', 'premisegroup_uid is None')
        return

    logger('VotingHelper', '__vote_premisesgroup', 'premisegroup_uid ' + str(premisesgroup_uid) + ', user ' + user.nickname)

    db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=premisesgroup_uid).all()
    for premise in db_premises:
        db_statement = DBDiscussionSession.query(Statement).filter_by(uid=premise.statement_uid).first()
        __vote_statement(db_statement, user, is_up_vote)


def __argument_seen_by_user(user_uid, argument_uid):
    """
    Adds an reference for an seen argument

    :param user_uid:
    :param argument_uid:
    :return:
    """
    db_seen_by = DBDiscussionSession.query(ArgumentSeenBy).filter(and_(ArgumentSeenBy.argument_uid == argument_uid,
                                                                       ArgumentSeenBy.user_uid == user_uid)).first()
    if not db_seen_by:
        new_entry = ArgumentSeenBy(argument_uid=argument_uid, user_uid=user_uid)
        DBDiscussionSession.add(new_entry)
        DBDiscussionSession.flush()


def __statement_seen_by_user(user_uid, statement_uid):
    """
    Adds an reference for an seen statement

    :param user_uid:
    :param argument_uid:
    :return:
    """
    db_seen_by = DBDiscussionSession.query(StatementSeenBy).filter(and_(StatementSeenBy.statement_uid == statement_uid,
                                                                        StatementSeenBy.user_uid == user_uid)).first()
    if not db_seen_by:
        new_entry = StatementSeenBy(statement_uid=statement_uid, user_uid=user_uid)
        DBDiscussionSession.add(new_entry)
        DBDiscussionSession.flush()
