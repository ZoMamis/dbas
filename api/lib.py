"""
Common, pure functions used by the API.

.. codeauthor:: Christian Meter <meter@cs.uni-duesseldorf.de
.. codeauthor:: Tobias Krauthoff <krauthoff@cs.uni-duesseldorf.de
"""

import json
import logging
import warnings
from functools import reduce
from html import escape
from typing import Tuple, List, Optional

from api.models import DataItem, DataBubble


def logger():
    """
    Create a logger.
    """
    return logging.getLogger("api")


def escape_html(evil):
    """
    Replace html tags.

    :param evil:
    :return: escaped string
    :rtype: str
    """
    warnings.warn("There is escape_string() for it", DeprecationWarning)
    return escape(str(evil))


def json_to_dict(col):
    """
    Given a json object as bytes, convert it to a Python dictionary.

    :param col:
    :type col: bytes
    :rtype: dict
    """
    if isinstance(col, dict):
        return col
    elif isinstance(col, bytes):
        col = col.decode("utf-8")
    return json.loads(col)


def flatten(l: List[List[any]]) -> Optional[List[any]]:
    """
    Flattens a list.

    :param l: list of lists
    :return:
    """
    if not l:
        return None
    return reduce(lambda x, y: x + y, l)


def merge_dicts(d1, d2) -> dict:
    """
    Merge two dictionaries.

    :param d1: first dictionary
    :param d2: second dictionary, overwriting existing keys in d1
    :return: merged dictionary
    """
    if isinstance(d1, dict) and isinstance(d2, dict):
        merged = d1.copy()
        merged.update(d2)
        return merged
    return None


def extract_items_and_bubbles(prepared_discussion: dict) -> Tuple[list, list]:
    """
    The prepared discussion is the result of the core functions from dbas.discussion.core. We need only few data for
    the API, so we extract the data in this function and append it to lists.

    :param prepared_discussion:
    :return:
    """
    items = [DataItem([premise['title'] for premise in item['premises']], item['url'])
             for item in prepared_discussion['items']['elements']]
    bubbles = [DataBubble(bubble) for bubble in prepared_discussion['discussion']['bubbles']]
    return bubbles, items
