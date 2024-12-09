import os
import pytest

from src.util.query_result_parser import QueryResultParser
from src.services.config_service import ConfigService

# pytest -v tests/test_query_result_parser.py


def test_non_tuples_tuple():
    for value in [None, 1, 3.14, "hello", [], {}]:
        qrp = QueryResultParser()
        result = qrp.parse(value)
        assert result == None


def test_parse_count_tuple():
    qrp = QueryResultParser()
    result = qrp.parse((10761,))
    assert result == 10761


def test_parse_two_numeric_tuple():
    qrp = QueryResultParser()
    result = qrp.parse(
        (
            0,
            1,
            1,
            2,
            3,
            5,
            8,
            13,
            21,
            34,
        )
    )
    assert result == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_parse_two_str_tuple():
    qrp = QueryResultParser()
    result = qrp.parse(
        (
            "Azure Cosmos DB",
            "Azure PostgreSQL",
        )
    )
    assert result == ["Azure Cosmos DB", "Azure PostgreSQL"]


def test_parse_mixed_tuple():
    qrp = QueryResultParser()
    loc = {"lat": 35.50988920032978, "lon": -80.83487017080188}
    result = qrp.parse((28036, "Davidson", "NC", loc))
    assert result == [28036, "Davidson", "NC", loc]


def test_parse_simple_str_one_tuple():
    qrp = QueryResultParser()
    result = qrp.parse(("Azure PostgreSQL",))
    assert result == "Azure PostgreSQL"


def test_parse_single_result_vertex():
    qrp = QueryResultParser()
    arg = (
        '{"id": 844424930131969, "label": "Developer", "properties": {"name": "info@2captcha.com"}}::vertex',
    )
    result = qrp.parse(arg)
    print("test result: {}".format(result))
    assert result["id"] == 844424930131969
    assert result["label"] == "Developer"
    assert result["properties"]["name"] == "info@2captcha.com"
