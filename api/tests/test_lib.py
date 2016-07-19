"""
Unit tests for lib.py

.. codeauthor:: Christian Meter <meter@cs.uni-duesseldorf.de
"""

from api.lib import flatten, merge_dicts, as_json


def test_flatten():
    l1 = [[1]]
    l2 = [[1, 2]]
    l3 = [[1, 2], [3]]
    l4 = [[1, 2], [3, 4]]
    l5 = [[1, 2], [3], [4]]
    l6 = []
    assert flatten(l1) == [1]
    assert flatten(l2) == [1, 2]
    assert flatten(l3) == [1, 2, 3]
    assert flatten(l4) == [1, 2, 3, 4]
    assert flatten(l5) == [1, 2, 3, 4]
    assert flatten(l6) is None


def test_merge_dicts():
    a = {"foo": "foo"}
    b = {"bar": "bar"}
    c = {"foo": "foo",
         "bar": "bar"}
    assert merge_dicts(a, {}) == a
    assert merge_dicts({}, a) == a
    assert merge_dicts(a, a) == a
    assert merge_dicts(a, None) is None
    assert merge_dicts(a, b) == c


def test_as_json():
    correct = {"foo": "bar"}
    broken_input = as_json(None)
    assert as_json(correct) == '{"foo": "bar"}'
    assert "status" in broken_input and "error" in broken_input
    assert as_json(1) == "1"
