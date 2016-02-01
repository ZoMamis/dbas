from sqlalchemy import and_
from .database import DBDiscussionSession
from .database.discussion_model import Argument, Statement, Premise, Vote, User
from .logger import logger

# @author Tobias Krauthoff
# @email krauthoff@cs.uni-duesseldorf.de
# @copyright Krauthoff 2015-2016


class VotingHelper(object):

	def add_vote_for_argument(self, argument_uid, user, transaction):
		"""
		Increses the votes of a given argument
		:param argument_uid: id of the argument
		:param user: self.request.authenticated_userid
		:param transaction: transaction
		:return: increased votes of the argument
		"""
		logger('VotingHelper', 'add_vote_for_argument', 'increasing argument ' + str(argument_uid) + ' vote')
		db_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid).first()
		# db_vote, already_voted = self.__check_and_set_vote_uid(db_argument, user)
		self.__check_and_set_vote_uid(db_argument, user)
		# TODO: WHATS WITH THE TRAIL?

		# some logical assumptions, where the conclusion is an argument
		if db_argument.conclusion_uid == 0:
			# self.add_vote_for_argument(db_argument.argument_uid, user, transaction)

			# check for inconsequences
			db_conclusion_arguments = DBDiscussionSession.query(Argument).filter_by(argument_uid=db_argument.argument_uid).all()
			for conclusion_argument in db_conclusion_arguments:
				# our argument is supportive, so let's have a look at arguments, which  attacks our conclusion argument OR
				# our argument is  attacking, so let's have a look at arguments, which supports our conclusion argument
				if db_argument.is_supportive and not conclusion_argument.is_supportive \
						or not db_argument.is_supportive and not conclusion_argument.is_supportive:
					self.remove_vote_for_argument(conclusion_argument.uid, user)
#
		# let's check, if the user voted for the oposite
		db_opposite_argument = DBDiscussionSession.query(Argument).filter(and_(Argument.premisesgroup_uid == db_argument.premisesgroup_uid,
		                                                                       Argument.conclusion_uid == db_argument.conclusion_uid,
		                                                                       Argument.argument_uid == db_argument.argument_uid,
		                                                                       Argument.is_supportive != db_argument.is_supportive)).first()
		if db_opposite_argument:
			self.remove_vote_for_argument(db_opposite_argument.uid, user)

		# return count of votes
		db_votes = DBDiscussionSession.query(Vote).filter(and_(Vote.argument_uid == db_argument.uid, True if Vote.is_valid else False)).all()

		transaction.commit()

		return len(db_votes)

	def remove_vote_for_argument(self, argument_uid, user):
		"""
		Decreses the vote of a given argument
		:param argument_uid: id of the argument
		:param user: self.request.authenticated_userid
		:return: decreased vote of the argument
		"""
		logger('VotingHelper', 'remove_vote_for_argument', 'decreasing argument ' + str(argument_uid) + ' vote')
		db_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid).first()
		db_user = DBDiscussionSession.query(User).filter_by(nickname=user).first()

		# remove votes
		DBDiscussionSession.query(Vote).filter(and_(Vote.argument_uid == db_argument.uid,
		                                            Vote.author_uid == db_user.uid)).first().set_valid(False)
		# TODO: WHATS WITH THE TRAIL?

		# return count of votes
		db_votes = DBDiscussionSession.query(Vote).filter(and_(Vote.argument_uid == db_argument.uid, True if Vote.is_valid else False)).all()

		return len(db_votes)

	def __check_and_set_vote_uid(self, db_argument, user):
		"""
		Check if the given argument has a voteing uid
		:param db_argument: Argument
		:param user: self.request.authenticated_userid
		:return: Vote, boolean for already voted
		"""

		# get vote
		db_user = DBDiscussionSession.query(User).filter_by(nickname=user).first()
		if not db_user:
			return None, None
		db_vote = DBDiscussionSession.query(Vote).filter(and_(Vote.argument_uid == db_argument.uid,
		                                                      Vote.author_uid == db_user.uid)).first()
		# TODO: INVALID AND CREATE NEW ENTRY?

		already_voted = False
		# do we have a vote?
		if not db_vote:
			db_vote = Vote(argument_uid=db_argument.uid, author_uid=db_user.uid, is_up_vote=True, is_valid=True)
			DBDiscussionSession.add(db_vote)
			DBDiscussionSession.flush()
		else:
			db_vote.set_valid(True)
			db_vote.update_timestamp()
			already_voted = True

		return db_vote, already_voted
