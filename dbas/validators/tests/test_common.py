# -*- coding: utf-8 -*-

import hypothesis.strategies as st
from hypothesis import given
from pyramid.httpexceptions import HTTPFound

from dbas.tests.utils import TestCaseWithConfig, construct_dummy_request
from dbas.validators.common import valid_lang_cookie_fallback, valid_language, check_authentication, \
    valid_fuzzy_search_mode


class ValidLanguageTest(TestCaseWithConfig):
    @given(lang=st.text())
    def test_invalid_language(self, lang: str):
        lang = lang.replace('\x00', '')
        if lang == 'en' or lang == 'de':
            return

        request = construct_dummy_request({'lang': lang})
        self.assertFalse(valid_language(request))
        self.assertNotIn('lang', request.validated)

    def test_valid_german_language(self):
        request = construct_dummy_request({'lang': 'de'})
        self.assertTrue(valid_language(request))
        self.assertIn('lang', request.validated)
        self.assertEqual('de', request.validated['lang'].ui_locales)

    def test_valid_english_language(self):
        request = construct_dummy_request({'lang': 'en'})
        self.assertTrue(valid_language(request))
        self.assertIn('lang', request.validated)
        self.assertEqual('en', request.validated['lang'].ui_locales)


class ValidLangCookieFallbackTest(TestCaseWithConfig):
    @given(lang=st.text())
    def test_valid_lang_cookie_fallback(self, lang: str):
        lang = lang.replace('\x00', '')
        request = construct_dummy_request({'lang': lang})
        valid_lang_cookie_fallback(request)
        self.assertIn('lang', request.validated)


class CheckAuthenticationTest(TestCaseWithConfig):
    def test_check_authentication_not_logged_in(self):
        request = construct_dummy_request({'lang': 'en'})
        self.assertIsNone(check_authentication(request))

    def test_check_authentication_logged_in(self):
        self.config.testing_securitypolicy(userid='Alwin', permissive=True)
        request = construct_dummy_request({'lang': 'en'})
        with self.assertRaises(HTTPFound):
            check_authentication(request)


class TestFuzzySearch(TestCaseWithConfig):
    def test_none_type_is_false(self):
        request = construct_dummy_request({'type': None})
        response = valid_fuzzy_search_mode(request)
        self.assertFalse(response)
        self.assertIsInstance(response, bool)

    def test_empty_type_is_false(self):
        request = construct_dummy_request({'type': ''})
        response = valid_fuzzy_search_mode(request)
        self.assertFalse(response)
        self.assertIsInstance(response, bool)

    def test_invalid_mode_number_is_false(self):
        request = construct_dummy_request({'type': -1})
        response = valid_fuzzy_search_mode(request)
        self.assertFalse(response)
        self.assertIsInstance(response, bool)

    def test_valid_modes_returns_true(self):
        for mode in [0, 1, 2, 3, 4, 8, 9]:
            request = construct_dummy_request({'type': mode})
            response = valid_fuzzy_search_mode(request)
            self.assertTrue(response)
            self.assertIsInstance(response, bool)

    def test_valid_mode_5_returns_true(self):
        request = construct_dummy_request({'type': 5})
        response = valid_fuzzy_search_mode(request)
        self.assertTrue(response)
        self.assertIsInstance(response, bool)
