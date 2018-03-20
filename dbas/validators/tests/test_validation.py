"""
Unit tests for our validators

.. codeauthor:: Christian Meter <meter@cs.uni-duesseldorf.de>
.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de>
"""

from dbas.database.discussion_model import ReviewDelete
from dbas.tests.utils import TestCaseWithConfig, construct_dummy_request
from dbas.validators.core import has_keywords
from dbas.validators.reviews import valid_not_executed_review


class TestHasKeywords(TestCaseWithConfig):
    def test_has_one_keyword(self):
        request = construct_dummy_request({'string': 'foo'})
        response = has_keywords(('string', str))(request)
        self.assertTrue(response)
        self.assertIn('string', request.validated)

    def test_has_multiple_keywords(self):
        request = construct_dummy_request({
            'string': 'foo',
            'bool': True
        })
        response = has_keywords(('string', str), ('bool', bool))(request)
        self.assertTrue(response)
        self.assertIn('string', request.validated)
        self.assertIn('bool', request.validated)

    def test_has_number_keywords(self):
        request = construct_dummy_request({
            'int': 4,
            'float': 4.0
        })
        response = has_keywords(('int', int), ('float', float))(request)
        self.assertTrue(response)
        self.assertIn('int', request.validated)
        self.assertIn('float', request.validated)

    def test_has_list_keywords(self):
        request = construct_dummy_request({'list': ['<:)']})
        response = has_keywords(('list', list))(request)
        self.assertTrue(response)
        self.assertIn('list', request.validated)

    def test_has_keywords_with_wrong_type(self):
        request = construct_dummy_request({'int': 4})
        response = has_keywords(('int', float))(request)
        self.assertFalse(response)
        self.assertNotIn('int', request.validated)

    def test_has_keywords_without_keyword(self):
        request = construct_dummy_request({'foo': 42})
        response = has_keywords(('bar', int))(request)
        self.assertFalse(response)
        self.assertNotIn('bar', request.validated)


class TestExecutedReviews(TestCaseWithConfig):
    def test_valid_not_executed_review(self):
        request = construct_dummy_request({'ruid': 4})
        response = valid_not_executed_review('ruid', ReviewDelete)(request)
        self.assertTrue(response)

    def test_valid_not_executed_review_error(self):
        request = construct_dummy_request({'ruid': 1})
        response = valid_not_executed_review('ruid', ReviewDelete)(request)
        self.assertFalse(response)
