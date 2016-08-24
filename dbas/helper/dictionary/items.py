"""
Provides helping function for dictionaries, which are used for the radio buttons.

.. codeauthor: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

import random
from sqlalchemy import and_
import dbas.recommender_system as RecommenderSystem

from dbas.database import DBDiscussionSession
from dbas.database.discussion_model import Argument, Statement, TextVersion, Premise, Issue
from dbas.lib import get_text_for_statement_uid, get_all_attacking_arg_uids_from_history
from dbas.logger import logger
from dbas.strings.translator import Translator
from dbas.strings.text_generator import TextGenerator
from dbas.url_manager import UrlManager


class ItemDictHelper(object):
    """
    Provides all functions for creating the radio buttons.
    """

    def __init__(self, lang, issue_uid, application_url, for_api=False, path='', history=''):
        """
        Initialize default values

        :param lang: ui_locales
        :param issue_uid: Issue.uid
        :param application_url: application_url
        :param for_api: boolean
        :param path: String
        :param history: String
        :return:
        """
        self.lang = lang
        self.issue_uid = issue_uid
        self.application_url = application_url
        self.for_api = for_api
        if for_api:
            self.path = path[len('/api/' + DBDiscussionSession.query(Issue).filter_by(uid=issue_uid).first().get_slug()):]
        else:
            self.path = path[len('/discuss/' + DBDiscussionSession.query(Issue).filter_by(uid=issue_uid).first().get_slug()):]
        if len(history) > 0:
            self.path = history + '-' + self.path

    def get_array_for_start(self, logged_in):
        """
        Prepares the dict with all items for the first step in discussion, where the user chooses a position.

        :param logged_in: Boolean or String
        :return:
        """
        db_statements = DBDiscussionSession.query(Statement)\
            .filter(and_(Statement.is_startpoint == True, Statement.issue_uid == self.issue_uid))\
            .join(TextVersion, TextVersion.uid == Statement.textversion_uid).all()
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()

        statements_array = []
        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)

        if db_statements:
            for statement in db_statements:
                statements_array.append(self.__create_answer_dict(statement.uid,
                                                                  [{'title': get_text_for_statement_uid(statement.uid), 'id': statement.uid}],
                                                                  'start',
                                                                  _um.get_url_for_statement_attitude(True, statement.uid)))
            _tn = Translator(self.lang)
            if logged_in:
                statements_array.append(self.__create_answer_dict('start_statement',
                                                                  [{'title': _tn.get(_tn.newConclusionRadioButtonText), 'id': 0}],
                                                                  'start',
                                                                  'add'))
            else:
                statements_array.append(self.__create_answer_dict('login', [{'id': '0', 'title': _tn.get(_tn.wantToStateNewPosition)}], 'justify', 'login'))

        return statements_array

    def prepare_item_dict_for_attitude(self, statement_uid):
        """
        Prepares the dict with all items for the second step in discussion, where the user chooses her attitude.

        :param statement_uid: Statement.uid
        :return:
        """
        logger('ItemDictHelper', 'prepare_item_dict_for_attitude', 'def')
        _tn = Translator(self.lang)

        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()
        # text = get_text_for_statement_uid(statement_uid)
        statements_array = []

        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)

        # colon = ' ' if self.lang == 'de' else ': '
        titleT = _tn.get(_tn.iAgreeWithInColor)  # + colon + text
        titleF = _tn.get(_tn.iDisagreeWithInColor)  # + colon + text
        titleD = _tn.get(_tn.iHaveNoOpinionYetInColor)  # + colon + text
        urlT = _um.get_url_for_justifying_statement(True, statement_uid, 't')
        urlF = _um.get_url_for_justifying_statement(True, statement_uid, 'f')
        urlD = _um.get_url_for_justifying_statement(True, statement_uid, 'd')
        statements_array.append(self.__create_answer_dict('agree', [{'title': titleT, 'id': 'agree'}], 'agree', urlT))
        statements_array.append(self.__create_answer_dict('disagree', [{'title': titleF, 'id': 'disagree'}], 'disagree', urlF))
        statements_array.append(self.__create_answer_dict('dontknow', [{'title': titleD, 'id': 'dontknow'}], 'dontknow', urlD))

        return statements_array

    def get_array_for_justify_statement(self, statement_uid, nickname, is_supportive):
        """
        Prepares the dict with all items for the third step in discussion, where the user justifies his position.

        :param statement_uid: Statement.uid
        :param nickname: User.nickname
        :param is_supportive: Boolean
        :return:
        """
        logger('ItemDictHelper', 'get_array_for_justify_statement', 'def')
        statements_array = []
        _tn = Translator(self.lang)
        _rh = RecommenderSystem
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()
        db_arguments = RecommenderSystem.get_arguments_by_conclusion(statement_uid, is_supportive)

        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)

        if db_arguments:
            for argument in db_arguments:
                # get all premises in the premisegroup of this argument
                db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=argument.premisesgroup_uid).all()
                premise_array = []
                for premise in db_premises:
                    text = get_text_for_statement_uid(premise.statement_uid)
                    premise_array.append({'title': text, 'id': premise.statement_uid})

                # get attack for each premise, so the urls will be unique
                arg_id_sys, attack = _rh.get_attack_for_argument(argument.uid, self.lang, history=self.path)
                already_used = 'reaction/' + str(argument.uid) + '/' in self.path
                additional_text = '(' + _tn.get(_tn.youUsedThisEarlier) + ')'
                statements_array.append(self.__create_answer_dict(str(argument.uid),
                                                                  premise_array,
                                                                  'justify',
                                                                  _um.get_url_for_reaction_on_argument(True, argument.uid, attack, arg_id_sys),
                                                                  already_used=already_used,
                                                                  already_used_text=additional_text))

        if nickname:
            statements_array.append(self.__create_answer_dict('start_premise',
                                                              [{'title': _tn.get(_tn.newPremiseRadioButtonText), 'id': 0}],
                                                              'justify',
                                                              'add'))
        else:
            # elif len(statements_array) == 1:
            statements_array.append(self.__create_answer_dict('login', [{'id': '0', 'title': _tn.get(_tn.onlyOneItem)}], 'justify', 'login'))

        return statements_array

    def get_array_for_justify_argument(self, argument_uid, attack_type, logged_in):
        """
        Prepares the dict with all items for a step in discussion, where the user justifies his attack she has done.

        :param argument_uid: Argument.uid
        :param attack_type: String
        :param logged_in: Boolean or String
        :return:
        """
        logger('ItemDictHelper', 'get_array_for_justify_argument', 'def: arg ' + str(argument_uid) + ', attack ' + attack_type)
        statements_array = []
        _tn = Translator(self.lang)
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()
        db_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid).first()

        db_arguments = []
        # description in docs: dbas/logic
        if attack_type == 'undermine':
            db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=db_argument.premisesgroup_uid).all()
            for premise in db_premises:
                arguments = DBDiscussionSession.query(Argument).filter(and_(Argument.conclusion_uid == premise.statement_uid,
                                                                            Argument.is_supportive == False,
                                                                            Argument.issue_uid == self.issue_uid)).all()
                db_arguments = db_arguments + arguments

        elif attack_type == 'undercut':
            db_arguments = DBDiscussionSession.query(Argument).filter(and_(Argument.argument_uid == argument_uid,
                                                                           Argument.is_supportive == False,
                                                                           Argument.issue_uid == self.issue_uid)).all()

        elif attack_type == 'overbid':
            db_arguments = DBDiscussionSession.query(Argument).filter(and_(Argument.argument_uid == argument_uid,
                                                                           Argument.is_supportive == True,
                                                                           Argument.issue_uid == self.issue_uid)).all()

        elif attack_type == 'rebut':
            db_arguments = DBDiscussionSession.query(Argument).filter(and_(Argument.conclusion_uid == db_argument.conclusion_uid,
                                                                           Argument.argument_uid == db_argument.argument_uid,
                                                                           Argument.is_supportive == False,
                                                                           Argument.issue_uid == self.issue_uid)).all()
        elif attack_type == 'support':
            db_arguments = DBDiscussionSession.query(Argument).filter(and_(Argument.conclusion_uid == db_argument.conclusion_uid,
                                                                           Argument.argument_uid == db_argument.argument_uid,
                                                                           Argument.is_supportive == db_argument.is_supportive,
                                                                           Argument.issue_uid == self.issue_uid)).all()

        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)

        if db_arguments:
            for argument in db_arguments:
                # get alles premises in this group
                db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=argument.premisesgroup_uid).all()
                premises_array = []
                for premise in db_premises:
                    text = get_text_for_statement_uid(premise.statement_uid)
                    premises_array.append({'id': premise.statement_uid, 'title': text[0:1].upper() + text[1:]})

                # for each justifying premise, we need a new confrontation: (restriction is based on fix #38)
                is_undermine = 'undermine' if attack_type == 'undermine' else None
                attacking_arg_uids = get_all_attacking_arg_uids_from_history(self.path)

                arg_id_sys, attack = RecommenderSystem.get_attack_for_argument(argument.uid, self.lang, last_attack=is_undermine,
                                                                               restriction_on_arg_uids=attacking_arg_uids, history=self.path)

                url = _um.get_url_for_reaction_on_argument(True, argument.uid, attack, arg_id_sys)
                statements_array.append(self.__create_answer_dict(argument.uid, premises_array, 'justify', url))

        if logged_in:
            if len(statements_array) == 0:
                text = _tn.get(_tn.newPremisesRadioButtonTextAsFirstOne)
            else:
                text = _tn.get(_tn.newPremiseRadioButtonText)
            statements_array.append(self.__create_answer_dict('justify_premise', [{'id': '0', 'title': text}], 'justify', 'add'))
        else:
            # elif len(statements_array) == 1:
            statements_array.append(self.__create_answer_dict('login', [{'id': '0', 'title': _tn.get(_tn.onlyOneItem)}], 'justify', 'login'))

        return statements_array

    def get_array_for_dont_know_reaction(self, argument_uid, is_supportive):
        """
        Prepares the dict with all items for the third step, where an suppotive argument will be presented.

        :param argument_uid: Argument.uid
        :param is_supportive: Boolean
        :return:
        """
        logger('ItemDictHelper', 'get_array_for_dont_know_reaction', 'def')
        _tg = TextGenerator(self.lang)
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()
        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)
        statements_array = []

        db_argument  = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid).first()
        if not db_argument:
            return statements_array

        rel_dict     = _tg.get_relation_text_dict(False, False, False, is_dont_know=True)
        mode         = 't' if is_supportive else 't'
        counter_mode = 'f' if is_supportive else 't'

        # relations = ['undermine', 'support', 'undercut', 'overbid', 'rebut'] # TODO 'overbid'
        relations = ['undermine', 'support', 'undercut', 'rebut']
        for relation in relations:
            if relation == 'support':
                arg_id_sys, sys_attack = RecommenderSystem.get_attack_for_argument(argument_uid, self.lang)
                url = _um.get_url_for_reaction_on_argument(True, argument_uid, sys_attack, arg_id_sys)

            else:
                current_mode = mode if relation == 'overbid' else counter_mode
                url = _um.get_url_for_justifying_argument(True, argument_uid, current_mode, relation)

            statements_array.append(self.__create_answer_dict(relation, [{'title': rel_dict[relation + '_text'], 'id':relation}], relation, url))

        return statements_array

    def get_array_for_reaction(self, argument_uid_sys, argument_uid_user, is_supportive, attack):
        """
        Prepares the dict with all items for the argumentation window.

        :param argument_uid_sys: Argument.uid
        :param argument_uid_user: Argument.uid
        :param is_supportive: Boolean
        :param attack: String
        :return:
        """
        logger('ItemDictHelper', 'get_array_for_reaction', 'def')
        _tg  = TextGenerator(self.lang)
        _tn  = Translator(self.lang)
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()

        db_sys_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid_sys).first()
        db_user_argument = DBDiscussionSession.query(Argument).filter_by(uid=argument_uid_user).first()
        statements_array = []
        if not db_sys_argument or not db_user_argument:
            return statements_array

        rel_dict         = _tg.get_relation_text_dict(False, True, db_user_argument.is_supportive, first_conclusion=_tn.get(_tn.myPosition), attack_type=attack)
        mode             = 't' if is_supportive else 'f'
        _um              = UrlManager(self.application_url, slug, self.for_api, history=self.path)
        _rh              = RecommenderSystem

        # based in the relation, we will fetch different url's for the items
        # relations = ['undermine', 'support', 'undercut', 'overbid', 'rebut'] # TODO overbid
        # TODO COMMA16 Special Case (forbid: undercuts of undercuts)
        # if attack == 'undercut':
        #     relations = ['undermine', 'support', 'rebut']
        # else:
        relations = ['undermine', 'support', 'undercut', 'rebut']
        for relation in relations:
            url = ''

            # special case, when the user selectes the support, because this does not need to be justified!
            if relation == 'support':
                attacking_arg_uids = get_all_attacking_arg_uids_from_history(self.path)
                arg_id_sys, sys_attack = _rh.get_attack_for_argument(argument_uid_sys, self.lang,
                                                                     restriction_on_arg_uids=attacking_arg_uids)
                if sys_attack == 'rebut' and attack == 'undercut':
                    # case: system makes an undercut and the user supports this
                    # new attack can be an rebut, so another undercut for the users argument
                    # therefore now the users opininion is the new undercut (e.g. rebut)
                    # because he supported it!
                    url = _um.get_url_for_reaction_on_argument(True, arg_id_sys, sys_attack, db_sys_argument.argument_uid)
                else:
                    url = _um.get_url_for_reaction_on_argument(True, argument_uid_sys, sys_attack, arg_id_sys)

            # easy cases
            elif relation == 'undermine' or relation == 'undercut':
                url = _um.get_url_for_justifying_argument(True, argument_uid_sys, mode, relation)

            elif relation == 'overbid':
                # if overbid is the 'overbid', it's easy
                #  url = _um.get_url_for_justifying_argument(True, argument_uid_sys, mode, relation)
                # otherwise it will be the attack again
                url = _um.get_url_for_justifying_argument(True, argument_uid_user, mode, attack)

            elif relation == 'rebut':  # if we are having an rebut, everything seems different

                if attack == 'undermine':  # rebutting an undermine will be a support for the initial argument
                    url = _um.get_url_for_justifying_statement(True, db_sys_argument.conclusion_uid, mode)
                # rebutting an undercut will be a overbid for the initial argument
                elif attack == 'undercut':
                    # url = _um.get_url_for_justifying_argument(True, argument_uid_user, mode, 'overbid')
                    if db_user_argument.argument_uid is None:
                        url = _um.get_url_for_justifying_statement(True, db_user_argument.conclusion_uid, mode)
                    else:
                        db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=db_user_argument.premisesgroup_uid).all()
                        db_premise = db_premises[random.randint(0, len(db_premises) - 1)]  # TODO: ELIMINATE RANDOM
                        url = _um.get_url_for_justifying_statement(True, db_premise.statement_uid, mode)

                # rebutting an rebut will be a justify for the initial argument
                elif attack == 'rebut':
                    current_user_argument = db_user_argument
                    conclusion_uid = current_user_argument.conclusion_uid
                    while conclusion_uid is None:
                        current_user_argument = DBDiscussionSession.query(Argument).filter_by(uid=current_user_argument.argument_uid).first()
                        conclusion_uid = current_user_argument.conclusion_uid
                    url = _um.get_url_for_justifying_statement(True, db_user_argument.conclusion_uid if conclusion_uid is None else conclusion_uid, mode)

            else:
                url = _um.get_url_for_justifying_argument(True, argument_uid_sys, mode, relation)

            # TODO PREVENT LOOPING
            # newStepInUrl = url[url.index('/reaction/') if url.index('/reaction/') < url.index('/justify/') else url.index('/justify/'):url.index('?')]
            # additionalText = (' (<em>' + _tn.get(_tn.youUsedThisEarlier) + '<em>)') if newStepInUrl in url[url.index('?'):] else ''

            statements_array.append(self.__create_answer_dict(relation, [{'title': rel_dict[relation + '_text'], 'id':relation}], relation, url))

        # last item is the change attack button or step back, if we have bno other attack
        attacking_arg_uids = get_all_attacking_arg_uids_from_history(self.path)
        attacking_arg_uids.append(argument_uid_sys)
        arg_id_sys, new_attack = _rh.get_attack_for_argument(argument_uid_user, self.lang,
                                                             restriction_on_attacks=attack,
                                                             restriction_on_arg_uids=attacking_arg_uids)

        if new_attack == 'no_other_attack' or new_attack.startswith('end'):
            relation = 'step_back'
            url = 'back' if self.for_api else 'window.history.go(-1)'
        else:
            relation = 'no_opinion'
            url = _um.get_url_for_reaction_on_argument(True, argument_uid_user, new_attack, arg_id_sys)
        statements_array.append(self.__create_answer_dict(relation, [{'title': rel_dict[relation + '_text'], 'id':relation}], relation, url))

        return statements_array

    def get_array_for_choosing(self, argument_or_statement_id, pgroup_ids, is_argument, is_supportive):
        """
        Prepares the dict with all items for the choosing an premise, when the user inserted more than one new premise.

        :param argument_or_statement_id: Argument.uid or Statement.uid
        :param pgroup_ids: PremiseGroups.uid
        :param is_argument: Boolean
        :param is_supportive: Boolean
        :return: dict()
        """
        logger('ItemDictHelper', 'get_array_for_choosing', 'def')
        statements_array = []
        slug = DBDiscussionSession.query(Issue).filter_by(uid=self.issue_uid).first().get_slug()
        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)
        conclusion = argument_or_statement_id if not is_argument else None
        argument = argument_or_statement_id if is_argument else None

        for group_id in pgroup_ids:
            db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=group_id).all()
            premise_array = []
            for premise in db_premises:
                text = get_text_for_statement_uid(premise.statement_uid)
                premise_array.append({'title': text, 'id': premise.statement_uid})

            # get attack for each premise, so the urls will be unique
            logger('ItemDictHelper', 'get_array_for_choosing', 'premisesgroup_uid: ' + str(group_id) +
                   ', conclusion_uid: ' + str(conclusion) +
                   ', argument_uid: ' + str(argument) +
                   ', is_supportive: ' + str(is_supportive))
            db_argument = DBDiscussionSession.query(Argument).filter(and_(Argument.premisesgroup_uid == group_id,
                                                                          Argument.conclusion_uid == conclusion,
                                                                          Argument.argument_uid == argument,
                                                                          Argument.is_supportive == is_supportive)).first()
            if not db_argument:
                return None
            attacking_arg_uids = get_all_attacking_arg_uids_from_history(self.path)
            arg_id_sys, attack = RecommenderSystem.get_attack_for_argument(db_argument.uid, self.lang,
                                                                           restriction_on_arg_uids=attacking_arg_uids)
            url = _um.get_url_for_reaction_on_argument(True, db_argument.uid, attack, arg_id_sys)

            statements_array.append(self.__create_answer_dict(str(db_argument.uid), premise_array, 'choose', url))
        # url = 'back' if self.for_api else 'window.history.go(-1)'
        # text = _t.get(_t.iHaveNoOpinion) + '. ' + _t.get(_t.goStepBack) + '.'
        # statements_array.append(self.__create_answer_dict('no_opinion', text, [{'title': text, 'id': 'no_opinion'}], 'no_opinion', url))
        return statements_array

    def get_array_for_jump(self, arg_uid, slug, for_api):
        """

        :param arg_uid:
        :param slug:
        :param for_api:
        :return:
        """

        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)
        db_argument = DBDiscussionSession.query(Argument).filter_by(uid=arg_uid).first()
        db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=db_argument.premisesgroup_uid).all()
        db_premise = db_premises[random.randint(0, len(db_premises) - 1)]  # TODO: FIX RANDOM FOR PGROUP

        # Array with [Conclusion is (right, wrong), Premise is (right, wrong), Premise does not leads to the conclusion, both hold]
        item_text = TextGenerator(self.lang).get_jump_to_argument_text_list()

        # which part of the argument should be attacked ?
        base = db_argument.argument_uid if db_argument.conclusion_uid is None else arg_uid
        arg_id_sys, sys_attack = RecommenderSystem.get_attack_for_argument(base, self.lang)

        url0 = _um.get_url_for_reaction_on_argument(not for_api, arg_uid, sys_attack, arg_id_sys)
        if db_argument.conclusion_uid is None:  # conclusion is an argument
            url1 = _um.get_url_for_reaction_on_argument(not for_api, db_argument.argument_uid, sys_attack, arg_id_sys)
            url2 = _um.get_url_for_justifying_argument(not for_api, db_argument.argument_uid, 'f', 'undercut')
        else:
            url1 = _um.get_url_for_justifying_statement(not for_api, db_argument.conclusion_uid, 't')
            url2 = _um.get_url_for_justifying_statement(not for_api, db_argument.conclusion_uid, 'f')
        url3 = _um.get_url_for_justifying_statement(not for_api, db_premise.statement_uid, 'f')
        url4 = _um.get_url_for_justifying_argument(not for_api, arg_uid, 't', 'undercut')

        answers = list()
        answers.append({'text': item_text[0], 'url': url0})
        answers.append({'text': item_text[1], 'url': url1})
        answers.append({'text': item_text[2], 'url': url2})
        answers.append({'text': item_text[3], 'url': url3})
        answers.append({'text': item_text[4], 'url': url4})

        return_array = []
        for no in range(0, len(answers)):
            arr = [{'title': answers[no]['text'], 'id': 0}]
            return_array.append(self.__create_answer_dict('jump' + str(no), arr, 'jump', answers[no]['url']))

        return return_array

    def get_array_for_jump_decision(self, arg_uid, slug, for_api):
        """

        :param arg_uid:
        :param slug:
        :param for_api:
        :return:
        """

        _um = UrlManager(self.application_url, slug, self.for_api, history=self.path)
        db_argument = DBDiscussionSession.query(Argument).filter_by(uid=arg_uid).first()
        db_premises = DBDiscussionSession.query(Premise).filter_by(premisesgroup_uid=db_argument.premisesgroup_uid).all()
        premise = db_premises[random.randint(0, len(db_premises) - 1)]  # TODO eliminate random

        item_text = TextGenerator(self.lang).get_jump_to_argument_text_list(True)

        url0 = _um.get_url_for_justifying_statement(not for_api, premise.statement_uid, 'f')
        if db_argument.conclusion_uid is None:  # conclusion is an argument
            url2 = _um.get_url_for_justifying_argument(not for_api, db_argument.argument_uid, 'f', 'undercut')
        else:
            url2 = _um.get_url_for_justifying_statement(not for_api, db_argument.conclusion_uid, 'f')
        url2 = _um.get_url_for_justifying_argument(not for_api, arg_uid, 't', 'undercut')

        answers = list()
        answers.append({'text': item_text[0], 'url': url0})
        answers.append({'text': item_text[1], 'url': url1})
        answers.append({'text': item_text[2], 'url': url2})

        return_array = []
        for no in range(0, len(answers)):
            arr = [{'title': answers[no]['text'], 'id': 0}]
            return_array.append(self.__create_answer_dict('jump' + str(no), arr, 'jump', answers[no]['url']))

        return return_array

    @staticmethod
    def __create_answer_dict(uid, premises, attitude, url, already_used=False, already_used_text=''):
        """
        Return dictionary

        :param uid: Integer
        :param premises: Array of dict with title and id
        :param attitude: String
        :param url: String
        :param already_used: Boolean
        :param already_used_text: String
        :return: dict()
        """
        return {
            'id': 'item_' + str(uid),
            'premises': premises,
            'attitude': attitude,
            'url': url,
            'already_used': already_used,
            'already_used_text': already_used_text}
