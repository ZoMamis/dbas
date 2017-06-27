from nose.tools import assert_true, assert_is_not_none

from api.v2.graphql.tests.lib import graphql_query


def test_list_of_issues():
    query = """
        query {
            issues {
                uid
            }
        }
    """
    content = graphql_query(query)
    assert_true(len(content.get("issues")) > 1)


def test_query_single_issue():
    query = """
        query {
            issue (uid: 1) {
                uid
            }
        }
    """
    content = graphql_query(query)
    issue = content.get("issue")
    assert_is_not_none(issue)
    assert_is_not_none(issue.get("uid"))


def test_query_single_issue_by_slug():
    query = """
        query {
            issue (slug: "cat-or-dog") {
                uid
            }
        }
    """
    content = graphql_query(query)
    issue = content.get("issue")
    assert_is_not_none(issue)
    assert_is_not_none(issue.get("uid"))


def test_query_single_issue_by_title():
    query = """
        query {
            issue (title: "Cat or Dog") {
                uid
            }
        }
    """
    content = graphql_query(query)
    issue = content.get("issue")
    assert_is_not_none(issue)
    assert_is_not_none(issue.get("uid"))


def test_query_single_issue_by_title_and_slug():
    query = """
        query {
            issue (slug: "cat-or-dog", title: "Cat or Dog") {
                uid
            }
        }
    """
    content = graphql_query(query)
    issue = content.get("issue")
    assert_is_not_none(issue)
    assert_is_not_none(issue.get("uid"))
