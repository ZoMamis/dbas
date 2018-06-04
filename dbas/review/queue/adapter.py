from typing import Union

from beaker.session import Session

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import User, ReviewSplit, ReviewOptimization, ReviewMerge, ReviewEdit, ReviewDelete, \
    ReviewDuplicate
from dbas.lib import get_profile_picture
from dbas.review import FlaggedBy
from dbas.review.mapper import get_review_model_by_key, get_last_reviewer_by_key, get_title_by_key
from dbas.review.queue import review_queues, key_ongoing, key_history
from dbas.review.queue.delete import DeleteQueue
from dbas.review.queue.duplicate import DuplicateQueue
from dbas.review.queue.edit import EditQueue
from dbas.review.queue.lib import get_review_count_for
from dbas.review.queue.merge import MergeQueue
from dbas.review.queue.optimization import OptimizationQueue
from dbas.review.queue.split import SplitQueue
from dbas.review.reputation import get_reputation_of, reputation_icons, reputation_borders
from dbas.strings.keywords import Keywords as _
from dbas.strings.lib import start_with_capital
from dbas.strings.translator import Translator


class QueueAdapter():
    """
    Adapter for the different queue adaptees
    """

    def __init__(self,
                 queue: Union[DeleteQueue, DuplicateQueue, EditQueue, MergeQueue, OptimizationQueue, SplitQueue] = None,
                 db_user: User = None,
                 application_url: str = '',
                 translator: Translator = '',
                 **kwargs):
        """

        :param queue:
        :param db_user:
        :param application_url:
        :param translator:
        """
        self.queue = queue
        self.db_user: User = db_user
        self.application_url = application_url
        self.translator = translator
        self.kwargs = kwargs

    def get_subpage_of_queue(self, session: Session, queue_name: str):
        """

        :return:
        """
        button_set = {f'is_{key}': False for key in review_queues}
        button_set[f'is_{queue_name}'] = True
        subpage_dict = self.queue.get_queue_information(self.db_user, session, self.application_url, self.translator)

        ret_dict = {
            'page_name': queue_name,
            'reviewed_element': subpage_dict,
            'session': subpage_dict['session']
        }
        if subpage_dict['text'] is None and subpage_dict['reason'] is None and subpage_dict['stats'] is None:
            return self.__wrap_subpage_dict({}, button_set)

        return self.__wrap_subpage_dict(ret_dict, button_set)

    def add_vote(self, db_review: Union[ReviewDelete, ReviewDuplicate, ReviewEdit, ReviewMerge, ReviewOptimization,
                                        ReviewSplit], is_okay: bool):
        """
        Adds an vote for this queue. If any (positive or negative) limit is reached, the flagged element will ...

        :param db_review: review element which should be voted
        :param is_okay: True, if the element is rightly flagged
        :return:
        """
        return self.queue.add_vote(db_user=self.db_user, db_review=db_review, is_okay=is_okay,
                                   application_url=self.application_url,
                                   translator=self.translator, **self.kwargs)

    def add_review(self):
        """
        Just adds a new element

        :return:
        """
        return self.queue.add_review(self.db_user)

    def get_review_count(self, review_uid: int):
        """

        :return:
        """
        return self.queue.get_review_count(review_uid)

    def cancel_ballot(self, db_review: Union[ReviewDelete, ReviewDuplicate, ReviewEdit, ReviewMerge,
                                             ReviewOptimization, ReviewSplit]):
        """

        :return:
        """
        return self.queue.cancel_ballot(self.db_user, db_review)

    def revoke_ballot(self, db_review: Union[ReviewDelete, ReviewDuplicate, ReviewEdit, ReviewMerge,
                                             ReviewOptimization, ReviewSplit]):
        """

        :param db_review:
        :return:
        """
        return self.queue.revoke_ballot(self.db_user, db_review)

    def is_element_flagged(self, argument_uid: int = None, statement_uid: int = None,
                           premisegroup_uid: int = None) -> Union[FlaggedBy, None]:
        """

        :param argument_uid:
        :param statement_uid:
        :param premisegroup_uid:
        :return:
        """

        status = [self.__is_anything_flagged_for_delete(argument_uid, statement_uid, self.db_user),
                  self.__is_anything_flagged_for_duplication(statement_uid, self.db_user),
                  self.__is_anything_flagged_for_edit(argument_uid, statement_uid, self.db_user),
                  self.__is_anything_flagged_for_optimization(argument_uid, statement_uid, self.db_user),
                  self.__is_anything_flagged_for_merge(premisegroup_uid, self.db_user),
                  self.__is_anything_flagged_for_split(premisegroup_uid, self.db_user)]

        if FlaggedBy.user in status:
            return FlaggedBy.user

        if FlaggedBy.other in status:
            return FlaggedBy.other
        return None

    def get_review_queues_as_lists(self):
        """

        :return:
        """
        review_list = []
        for key in review_queues:
            review_list.append(self.__get_queue_information(key))

        review_list.append(self.__get_history_information())
        if self.db_user.is_author() or self.db_user.is_admin():
            review_list.append(self.__get_ongoing_information())

        return review_list

    def __get_queue_information(self, queue_name: str):
        """

        :param queue_name:
        :return:
        """
        last_reviewer = get_last_reviewer_by_key(queue_name)
        table = get_review_model_by_key(queue_name)
        task_count = get_review_count_for(table, last_reviewer, self.db_user)
        count, all_rights = get_reputation_of(self.db_user)
        visit_key_str = _.get_key_by_string('visit{}Queue'.format(start_with_capital(queue_name)))
        visit_limit_key_str = _.get_key_by_string('visit{}QueueLimitation'.format(start_with_capital(queue_name)))
        return {
            'task_name': get_title_by_key(queue_name),
            'id': queue_name,
            'url': f'{self.application_url}/review/{queue_name}',
            'icon': reputation_icons[queue_name],
            'task_count': task_count,
            'is_allowed': count >= reputation_borders[queue_name] or all_rights,
            'is_allowed_text': self.translator.get(visit_key_str),
            'is_not_allowed_text': self.translator.get(visit_limit_key_str).format(str(reputation_borders[queue_name])),
            'last_reviews': self.__get_last_reviewer_of(last_reviewer, self.application_url)
        }

    def __get_history_information(self):
        count, all_rights = get_reputation_of(self.db_user)
        return {
            'task_name': self.translator.get(_.queueHistory),
            'id': key_history,
            'url': f'{self.application_url}/review/{key_history}',
            'icon': reputation_icons[key_history],
            'task_count': self.__get_review_count_for_history(True),
            'is_allowed': count >= reputation_borders[key_history] or all_rights,
            'is_allowed_text': self.translator.get(_.visitHistoryQueue),
            'is_not_allowed_text': self.translator.get(_.visitHistoryQueueLimitation).format(
                str(reputation_borders[key_history])),
            'last_reviews': list()
        }

    def __get_ongoing_information(self):
        return {
            'task_name': self.translator.get(_.queueOngoing),
            'id': key_ongoing,
            'url': f'{self.application_url}/review/{key_ongoing}',
            'icon': reputation_icons[key_ongoing],
            'task_count': self.__get_review_count_for_history(False),
            'is_allowed': True,
            'is_allowed_text': self.translator.get(_.visitOngoingQueue),
            'is_not_allowed_text': '',
            'last_reviews': list()
        }

    @staticmethod
    def __get_review_count_for_history(is_executed):
        """

        :param is_executed:
        :return:
        """
        count = 0
        tables = [get_review_model_by_key(key) for key in review_queues]
        for table in tables:
            count += DBDiscussionSession.query(table).filter_by(is_executed=is_executed).count()
        return count

    @staticmethod
    def __get_last_reviewer_of(reviewer_type, main_page):
        """
        Returns a list with the last reviewers of the given type. Multiple reviewers are filtered

        :param reviewer_type:
        :param main_page:
        :return:
        """
        #  logger('ReviewQueues', '__get_last_reviewer_of', 'main')
        users_array = list()
        db_reviews = DBDiscussionSession.query(reviewer_type).order_by(reviewer_type.uid.desc()).all()
        limit = min(5, len(db_reviews))
        index = 0
        while index < limit:
            db_review = db_reviews[index]
            db_user = DBDiscussionSession.query(User).get(db_review.reviewer_uid)
            if db_user:
                tmp_dict = dict()
                tmp_dict['img_src'] = get_profile_picture(db_user, 40)
                tmp_dict['url'] = f'{main_page}/user/{db_user.uid}'
                tmp_dict['name'] = db_user.global_nickname
                # skip it, if it is already in
                if tmp_dict in users_array:
                    limit += 1 if len(db_reviews) > limit else 0
                else:
                    users_array.append(tmp_dict)
            else:
                limit += 1 if len(db_reviews) > limit else 0
            index += 1
        return users_array

    @staticmethod
    def __wrap_subpage_dict(ret_dict, button_set):
        """
        Set up dict()

        :param ret_dict: dict()
        :param button_set: dict()
        :return: dict()
        """
        session = {}
        if ret_dict and 'session' in ret_dict:
            session = ret_dict['session']
            ret_dict.pop('session')

        return {
            'elements': ret_dict,
            'no_arguments_to_review': len(ret_dict) is 0,
            'button_set': button_set,
            'session': session
        }

    @staticmethod
    def __is_anything_flagged_for_delete(argument_uid, statement_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewDelete).filter_by(
            argument_uid=argument_uid,
            statement_uid=statement_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None

    @staticmethod
    def __is_anything_flagged_for_duplication(statement_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewDuplicate).filter_by(
            duplicate_statement_uid=statement_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None

    @staticmethod
    def __is_anything_flagged_for_edit(argument_uid, statement_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewEdit).filter_by(
            argument_uid=argument_uid,
            statement_uid=statement_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None

    @staticmethod
    def __is_anything_flagged_for_merge(pgroup_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewMerge).filter_by(
            premisegroup_uid=pgroup_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None

    @staticmethod
    def __is_anything_flagged_for_optimization(argument_uid, statement_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewOptimization).filter_by(
            argument_uid=argument_uid,
            statement_uid=statement_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None

    @staticmethod
    def __is_anything_flagged_for_split(pgroup_uid, db_user):
        db_review = DBDiscussionSession.query(ReviewSplit).filter_by(
            premisegroup_uid=pgroup_uid,
            is_executed=False,
            is_revoked=False)
        if db_review.filter_by(detector_uid=db_user.uid).count() > 0:
            return FlaggedBy.user
        if db_review.count() > 0:
            return FlaggedBy.other
        return None
