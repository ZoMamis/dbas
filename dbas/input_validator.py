"""
Methods for validating input params given via url or ajax

.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

from .database import DBDiscussionSession
from .database.discussion_model import Argument, Statement, Premise
from .logger import logger
from sqlalchemy import and_


class Validator:
    """
    Methods for saving or reading data out of current session. Additionally these values can be aligned.
    """

    @staticmethod
    def is_integer(variable, ignore_empty_case=False):
        """
        Validates if variable is an integer.

        :param variable: some input
        :param ignore_empty_case:
        :rtype: boolean
        """
        if variable is None:
            return False
        if ignore_empty_case:
            if len(str(variable)) == 0:
                return True
        try:
            int(variable)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def check_reaction(attacked_arg_uid, attacking_arg_uid, relation, is_history=False):
        """
        Checks whether the attacked argument uid and the attacking argument uid are connected via the given relation

        :param attacked_arg_uid: Argument.uid
        :param attacking_arg_uid: Argument.uid
        :param relation: String
        :param is_history: Boolean
        :return: Boolean
        """
        logger('Validator', 'check_reaction', relation + ' from ' + str(attacking_arg_uid) + ' to ' + str(attacked_arg_uid))

        if not Validator.is_integer(attacked_arg_uid) or not Validator.is_integer(attacking_arg_uid):
            return False

        if Validator.is_argument_forbidden(attacked_arg_uid) or Validator.is_argument_forbidden(attacking_arg_uid):
            return False

        if relation == 'undermine':
            return Validator.related_with_undermine(attacked_arg_uid, attacking_arg_uid)

        elif relation == 'undercut':
            return Validator.related_with_undercut(attacked_arg_uid, attacking_arg_uid)

        elif relation == 'rebut':
            return Validator.related_with_rebut(attacked_arg_uid, attacking_arg_uid)

        elif relation.startswith('end') and not is_history:
            if str(attacking_arg_uid) != '0':
                return False
            return True

        else:
            logger('Validator', 'check_reaction', 'else-case')
            return False

    @staticmethod
    def check_belonging_of_statement(issue_uid, statement_uid):
        """
        Check whether current Statement.uid belongs to the given Issue

        :param issue_uid: Issue.uid
        :param statement_uid: Statement.uid
        :return:
        """
        db_statement = DBDiscussionSession.query(Statement).filter(and_(Statement.uid == statement_uid,
                                                                        Statement.issue_uid == issue_uid)).first()
        return True if db_statement else False

    @staticmethod
    def check_belonging_of_argument(issue_uid, argument_uid):
        """
        Check whether current Argument.uid belongs to the given Issue

        :param issue_uid: Issue.uid
        :param argument_uid: Argument.uid
        :return: Boolean
        """
        db_argument = DBDiscussionSession.query(Argument).filter(and_(Argument.uid == argument_uid,
                                                                      Argument.issue_uid == issue_uid)).first()
        return True if db_argument else False

    @staticmethod
    def check_belonging_of_premisegroups(issue_uid, premisegroups):
        """
        Check whether all Groups in Premisgroups belongs to the given Issue

        :param issue_uid: Issue.uid
        :param premisegroups: [PremiseGroup.uid]
        :return: Boolean
        """
        for group_id in premisegroups:
            db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=group_id).all()
            for premise in db_premises:
                if premise.issue_uid != issue_uid:
                    return False
        return True

    @staticmethod
    def is_position(statement_uid):
        """
        True if current statement is a position

        :param statement_uid: Statement.uid
        :return: Boolean
        """
        db_statement = DBDiscussionSession.query(Statement).filter_by(uid=statement_uid).first()
        return True if db_statement.is_startpoint else False

    @staticmethod
    def related_with_undermine(attacked_arg_uid, attacking_arg_uid):
        """

        :param attacked_arg_uid: Argument.uid
        :param attacking_arg_uid: Argument.uid
        :return: Boolean
        """
        # conclusion of the attacking argument
        db_attacking_arg = DBDiscussionSession.query(Argument).filter_by(uid=attacking_arg_uid).join(Statement).first()
        if not db_attacking_arg:
            return False

        # which pgroups has the conclusion as premise
        db_attacked_premise = DBDiscussionSession.query(Premise).filter_by(statement_uid=db_attacking_arg.statements.uid).first()
        if not db_attacked_premise:
            return False

        # and does the attacked argument has this premisegroup as premisegroup
        db_attacked_arg = DBDiscussionSession.query(Argument).filter(and_(Argument.uid == attacked_arg_uid,
                                                                          Argument.premisesgroup_uid == db_attacked_premise.premisesgroup_uid)).first()
        return True if db_attacked_arg else False

    @staticmethod
    def related_with_undercut(attacked_arg_uid, attacking_arg_uid):
        """

        :param attacked_arg_uid: Argument.uid
        :param attacking_arg_uid: Argument.uid
        :return: Boolean
        """
        db_attacking_arg = DBDiscussionSession.query(Argument).filter(and_(Argument.uid == attacking_arg_uid,
                                                                           Argument.argument_uid == attacked_arg_uid)).first()
        return True if db_attacking_arg else False

    @staticmethod
    def related_with_rebut(attacked_arg_uid, attacking_arg_uid):
        """

        :param attacked_arg_uid: Argument.uid
        :param attacking_arg_uid: Argument.uid
        :return: Boolean
        """
        db_attacking_arg = DBDiscussionSession.query(Argument).filter_by(uid=attacking_arg_uid).first()
        db_attacked_arg = DBDiscussionSession.query(Argument).filter_by(uid=attacked_arg_uid).first()
        if not db_attacked_arg or not db_attacking_arg:
            return False

        # do have both arguments the same conclusion?
        same_conclusion = db_attacking_arg.conclusion_uid == db_attacked_arg.conclusion_uid
        not_none = db_attacked_arg.conclusion_uid is not None
        attacking1 = not db_attacking_arg.is_supportive and db_attacked_arg.is_supportive
        attacking2 = not db_attacked_arg.is_supportive and db_attacking_arg.is_supportive
        attacking = attacking1 or attacking2
        return True if same_conclusion and not_none and attacking else False

    @staticmethod
    def get_relation_between_arguments(arg1_uid, arg2_uid):
        """

        :param arg1_uid: Argument.uid
        :param arg2_uid: Argument.uid
        :return: String or None
        """

        if Validator.related_with_undermine(arg1_uid, arg2_uid):
            return 'undermine'

        elif Validator.related_with_undercut(arg1_uid, arg2_uid):
            return 'undercut'

        elif Validator.related_with_rebut(arg1_uid, arg2_uid):
            return 'rebut'

        return None

    @staticmethod
    def is_argument_forbidden(uid):
        db_arg = DBDiscussionSession.query(Argument).filter_by(uid=uid).first()
        return db_arg.is_disabled
