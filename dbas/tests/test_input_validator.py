import unittest

from sqlalchemy import engine_from_config
from dbas.database import DBDiscussionSession
from dbas.helper.tests import add_settings_to_appconfig


settings = add_settings_to_appconfig()


class InputValidatorTests(unittest.TestCase):

    @staticmethod
    def _getTargetClass():
        from dbas.input_validator import Validator
        return Validator

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_check_for_integer(self):
        reaction = self._makeOne()

        # conditions_response
        ignore_empty_case_len_zero_true = reaction.check_for_integer(variable='',
                                                                     ignore_empty_case=True)
        self.assertEqual(ignore_empty_case_len_zero_true, True)

        long_string_false = reaction.check_for_integer(variable=',' * 1000 + '30' + '?' * 1000,
                                                       ignore_empty_case=True)
        self.assertEqual(long_string_false, False)

        ignore_empty_case_len_false = reaction.check_for_integer(variable='str',
                                                                 ignore_empty_case=True)
        self.assertEqual(ignore_empty_case_len_false, False)

        not_ignore_empty_case_len_zero_false = reaction.check_for_integer(variable='',
                                                                          ignore_empty_case=False)
        self.assertEqual(not_ignore_empty_case_len_zero_false, False)

        not_ignore_empty_case_len_false = reaction.check_for_integer(variable='str',
                                                                     ignore_empty_case=False)
        self.assertEqual(not_ignore_empty_case_len_false, False)

        ignore_empty_case_int_true = reaction.check_for_integer(variable=123,
                                                                ignore_empty_case=True)
        self.assertEqual(ignore_empty_case_int_true, True)

        not_ignore_empty_case_int_true = reaction.check_for_integer(variable=1,
                                                                    ignore_empty_case=False)
        self.assertEqual(not_ignore_empty_case_int_true, True)

        input_none_false = reaction.check_for_integer(variable=None,
                                                      ignore_empty_case=True)
        self.assertEqual(input_none_false, False)

        input_array_false = reaction.check_for_integer(variable=[1, 2, 3, 'str'],
                                                       ignore_empty_case=True)
        self.assertEqual(input_array_false, False)

    def test_check_reaction(self):
        reaction = self._makeOne()

        DBDiscussionSession.configure(bind=engine_from_config(settings, 'sqlalchemy-discussion.'))

        # undermine
        undermine_true = reaction.check_reaction(attacked_arg_uid=2,
                                                 attacking_arg_uid=19,
                                                 relation='undermine',
                                                 is_history=False)
        self.assertEqual(undermine_true, True)

        undermine_uid_array_false = reaction.check_reaction(attacked_arg_uid=[1, 2, 3],
                                                            attacking_arg_uid=[1, 2, 3],
                                                            relation='undermine',
                                                            is_history=False)
        self.assertEqual(undermine_uid_array_false, False)

        undermine_negative_uid_false = reaction.check_reaction(attacked_arg_uid=-2,
                                                               attacking_arg_uid=-19,
                                                               relation='undermine',
                                                               is_history=False)
        self.assertEqual(undermine_negative_uid_false, False)

        # relation_conditions_response
        undermine_not_db_attacking_arg_false = reaction.check_reaction(attacked_arg_uid=2,
                                                                       attacking_arg_uid=1,
                                                                       relation='undermine',
                                                                       is_history=False)
        self.assertEqual(undermine_not_db_attacking_arg_false, False)

        undermine_db_attacked_arg_false = reaction.check_reaction(attacked_arg_uid=1,
                                                                  attacking_arg_uid=19,
                                                                  relation='undermine',
                                                                  is_history=False)
        self.assertEqual(undermine_db_attacked_arg_false, False)

        undermine_false = reaction.check_reaction(attacked_arg_uid=0,
                                                  attacking_arg_uid=0,
                                                  relation='undermine',
                                                  is_history=False)
        self.assertEqual(undermine_false, False)

        undermine_empty_string_false = reaction.check_reaction(attacked_arg_uid='',
                                                               attacking_arg_uid='',
                                                               relation='undermine',
                                                               is_history=False)
        self.assertEqual(undermine_empty_string_false, False)

        undermine_string_false = reaction.check_reaction(attacked_arg_uid='2str/',
                                                         attacking_arg_uid='19str',
                                                         relation='undermine',
                                                         is_history=True)
        self.assertEqual(undermine_string_false, False)

        # undercut
        undercut_true = reaction.check_reaction(attacked_arg_uid=1,
                                                attacking_arg_uid=17,
                                                relation='undercut',
                                                is_history=False)
        self.assertEqual(undercut_true, True)

        undercut_false = reaction.check_reaction(attacked_arg_uid=0,
                                                 attacking_arg_uid=0,
                                                 relation='undercut',
                                                 is_history=False)
        self.assertEqual(undercut_false, False)

        undercut_empty_string_false = reaction.check_reaction(attacked_arg_uid='',
                                                              attacking_arg_uid='',
                                                              relation='undercut',
                                                              is_history=False)
        self.assertEqual(undercut_empty_string_false, False)

        undercut_string_false = reaction.check_reaction(attacked_arg_uid='1str/',
                                                        attacking_arg_uid='17str',
                                                        relation='undercut',
                                                        is_history=True)
        self.assertEqual(undercut_string_false, False)

        # rebut
        rebut_true = reaction.check_reaction(attacked_arg_uid=31,
                                             attacking_arg_uid=35,
                                             relation='rebut',
                                             is_history=False)
        self.assertEqual(rebut_true, True)

        rebut_not_db_attacked_arg_false = reaction.check_reaction(attacked_arg_uid=1,
                                                                  attacking_arg_uid=35,
                                                                  relation='rebut',
                                                                  is_history=False)
        self.assertEqual(rebut_not_db_attacked_arg_false, False)

        rebut_not_db_attacking_arg_false = reaction.check_reaction(attacked_arg_uid=31,
                                                                   attacking_arg_uid=1,
                                                                   relation='rebut',
                                                                   is_history=False)
        self.assertEqual(rebut_not_db_attacking_arg_false, False)

        rebut_not_db_attacked_arg_false = reaction.check_reaction(attacked_arg_uid=1,
                                                                  attacking_arg_uid=35,
                                                                  relation='rebut',
                                                                  is_history=False)
        self.assertEqual(rebut_not_db_attacked_arg_false, False)

        # db_attacked_arg and db_attacking_arg are False
        rebut_false = reaction.check_reaction(attacked_arg_uid=0,
                                              attacking_arg_uid=0,
                                              relation='rebut',
                                              is_history=False)
        self.assertEqual(rebut_false, False)

        rebut_empty_string_false = reaction.check_reaction(attacked_arg_uid='',
                                                           attacking_arg_uid='',
                                                           relation='rebut',
                                                           is_history=False)
        self.assertEqual(rebut_empty_string_false, False)

        rebut_string_false = reaction.check_reaction(attacked_arg_uid='31str/',
                                                     attacking_arg_uid='35str',
                                                     relation='rebut',
                                                     is_history=True)
        self.assertEqual(rebut_string_false, False)

        # end
        end_attacking_arg_uid_not_zero_true = reaction.check_reaction(attacked_arg_uid=1,
                                                                      attacking_arg_uid=0,
                                                                      relation='end',
                                                                      is_history=False)
        self.assertEqual(end_attacking_arg_uid_not_zero_true, True)

        end_attacking_arg_uid_not_zero_false = reaction.check_reaction(attacked_arg_uid=1,
                                                                       attacking_arg_uid=1,
                                                                       relation='end',
                                                                       is_history=False)
        self.assertEqual(end_attacking_arg_uid_not_zero_false, False)

        end_not_is_history_false = reaction.check_reaction(attacked_arg_uid=1,
                                                           attacking_arg_uid=0,
                                                           relation='end',
                                                           is_history=True)
        self.assertEqual(end_not_is_history_false, False)

        end_empty_string_false = reaction.check_reaction(attacked_arg_uid='',
                                                         attacking_arg_uid='',
                                                         relation='end',
                                                         is_history=False)
        self.assertEqual(end_empty_string_false, False)

        end_string_false = reaction.check_reaction(attacked_arg_uid='1str/',
                                                   attacking_arg_uid='str',
                                                   relation='end',
                                                   is_history=False)
        self.assertEqual(end_string_false, False)

        end_string_long_false = reaction.check_reaction(attacked_arg_uid=',' * 1000 + '30' + 'str' * 1000,
                                                        attacking_arg_uid=',' * 1000 + '30' + 'str' * 1000,
                                                        relation='end',
                                                        is_history=False)
        self.assertEqual(end_string_long_false, False)

        # no relation
        no_relation_false = reaction.check_reaction(attacked_arg_uid='',
                                                    attacking_arg_uid='3',
                                                    relation='',
                                                    is_history=False)
        self.assertEqual(no_relation_false, False)

        no_relation_uid_none_false = reaction.check_reaction(attacked_arg_uid=None,
                                                             attacking_arg_uid=None,
                                                             relation='',
                                                             is_history=False)
        self.assertEqual(no_relation_uid_none_false, False)
