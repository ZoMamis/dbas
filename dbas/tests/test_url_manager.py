import unittest

from dbas.lib import Relations, Attitudes


class UrlManagerTests(unittest.TestCase):
    @staticmethod
    def __get_target_class():
        from dbas.helper.url import UrlManager
        return UrlManager

    def __make_one(self, *args, **kw):
        return self.__get_target_class()(*args, **kw)

    def test_init(self):
        url1 = self.__make_one(slug='', history='')
        url2 = self.__make_one(slug='cat-or-dog', history='attitude/35')
        # Test empty string.
        self.assertEqual(url1.slug, '')
        # Test string.
        self.assertEqual(url2.slug, 'cat-or-dog')

        # Test empty string.
        self.assertEqual(url1.history, '')
        # Test string.
        self.assertEqual(url2.history, 'attitude/35')

        # Test whether 'None' is returned.
        self.assertEqual(url1.__init__(), None)

    def test_get_url_for_statement_attitude(self):
        url = self.__make_one(slug='cat-or-dog')

        response_string_true = url.get_url_for_statement_attitude(statement_uid=123)
        # Verify that, if 'as_location_href' is 'True' and 'statement_uid' is not empty,
        # '{discussion_url}/{slug}/attitude/{statement_uid}' with 'location.href=' as prefix is returned.
        self.assertEqual(response_string_true, '/cat-or-dog/attitude/123')

        response_empty_string_false = url.get_url_for_statement_attitude(statement_uid='')
        # Verify that, if 'as_location_href' is 'False' and 'statement_uid' is empty,
        # '{discussion_url}/{slug}/attitude/' is returned.
        self.assertEqual(response_empty_string_false, '/cat-or-dog/attitude/')

        response_negative_uid_true = url.get_url_for_statement_attitude(statement_uid=-123)
        self.assertEqual(response_negative_uid_true, '/cat-or-dog/attitude/-123')

    def test_get_url_for_justifying_statement(self):
        url = self.__make_one(slug='cat-or-dog')

        response_string_true = url.get_url_for_justifying_statement(statement_uid=123,
                                                                    attitude=Attitudes.AGREE)
        # Verify that, if 'as_location_href' is 'True', 'statement_uid' and 'mode' are not empty,
        # '{discussion_url}/{slug}/justify/{statement_or_arg_id}/{mode}' is returned.
        self.assertEqual(response_string_true, '/cat-or-dog/justify/123/agree')

    def test_get_url_for_justifying_argument(self):
        url = self.__make_one(slug='cat-or-dog')

        response_no_additional_id_true = url.get_url_for_justifying_argument(argument_uid=123,
                                                                             attitude=Attitudes.AGREE,
                                                                             relation=Relations.SUPPORT,
                                                                             additional_id=-1)
        # Verify that, if 'additional_id' is '-1' and 'as_location_href' is 'True',
        # '{discussion_url}/{slug}/justify/{argument_uid}/{mode}/{attitude}' is returned.
        self.assertEqual(response_no_additional_id_true, '/cat-or-dog/justify/123/agree/support')

        response_additional_id_false = url.get_url_for_justifying_argument(argument_uid=123,
                                                                           attitude=Attitudes.AGREE,
                                                                           relation=Relations.SUPPORT,
                                                                           additional_id=30)
        # Verify that, if 'additional_id' is not equal '-1' and 'as_location_href' is 'False',
        # '{discussion_url}/{slug}/justify/{argument_uid}/{mode}/{attitude}/{attitude_uid}' is returned.
        self.assertEqual(response_additional_id_false, '/cat-or-dog/justify/123/agree/support/30')

    def test_get_url_for_reaction_on_argument(self):
        url = self.__make_one(slug='cat-or-dog')

        response_as_location_href_true = url.get_url_for_reaction_on_argument(argument_uid=123,
                                                                              relation=Relations.REBUT,
                                                                              confrontation_argument=35)
        # Verify that, if 'as_location_href' is 'True',
        # '{discussion_url}/{slug}/reaction/{argument_uid}/{mode}/{confrontation_argument}' is returned.
        self.assertEqual(response_as_location_href_true,
                         '/cat-or-dog/reaction/123/rebut/35')

        response_as_location_href_false = url.get_url_for_reaction_on_argument(argument_uid=0,
                                                                               relation=Relations.UNDERCUT,
                                                                               confrontation_argument=0)
        # Verify that, if 'as_location_href' is 'False',
        # '{discussion_url}/{slug}/reaction/{argument_uid}/{mode}/{confrontation_argument}' is returned.
        self.assertEqual(response_as_location_href_false, '/cat-or-dog/finish/0')

    def test_get_url_for_choosing_premisegroup(self):
        url = self.__make_one(slug='cat-or-dog')

        response_true = url.get_url_for_choosing_premisegroup(is_argument=True,
                                                              is_supportive=True,
                                                              statement_or_argument_id=20,
                                                              pgroup_id_list=[1, 2, 3])
        # Verify that, if 'as_location_href', 'is_argument', 'is_supportive' are 'True' and length of array
        # 'pgroup_id_list' is greater than 0, the url '{discussion-url}/{slug}/choose/{is_argument}/{
        # is_supportive}/{statement_or_argument_id}' and the elements of array 'pgroup_id_list' are put together,
        # separated with backslash, and are attached in url.
        self.assertEqual(response_true, '/cat-or-dog/choose/true/true/20/1/2/3')

        response_false = url.get_url_for_choosing_premisegroup(is_argument=False,
                                                               is_supportive=False,
                                                               statement_or_argument_id=20,
                                                               pgroup_id_list='')
        # Verify that, if 'as_location_href', 'is_argument', 'is_supportive' are 'False' and length of array
        # 'pgroup_id_list' is equal 0, '{discussion-url}/{slug}/choose/{is_argument}/{is_supportive}/{
        # statement_or_argument_id}' is returned.
        self.assertEqual(response_false, '/cat-or-dog/choose/false/false/20')

    def test_get_url_for_new_argument(self):
        url = self.__make_one(slug='cat-or-dog', history='attitude/4')
        res = '/cat-or-dog/finish/10?history=attitude/4'
        self.assertEqual(res, url.get_url_for_new_argument([10]))
