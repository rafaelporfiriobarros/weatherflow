"""Testes da transformacao dos dados meteorologicos."""

from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from weatherflow.transform import (
    TransformationError,
    parse_number,
    transform_record,
)


@pytest.fixture
def valid_raw():
    return {
        "city": "Sao Paulo",
        "source": "open-meteo",
        "data_type": "forecast",
        "collected_at": "2026-11-16T11:00:00-03:00",
        "payload": {
            "daily": {
                "time": ["2026-11-16"],
                "temperature_2m_max": [28.5],
                "temperature_2m_min": [18.2],
                "precipitation_sum": [5.3],
            }
        },
    }


def test_transform_valid_record(valid_raw):
    record = transform_record(valid_raw)

    assert record.city == "Sao Paulo"
    assert record.forecast_date == date(2026, 11, 16)
    assert record.temperature_max == Decimal("28.5")
    assert record.temperature_min == Decimal("18.2")
    assert record.precipitation_sum == Decimal("5.3")


def test_missing_city(valid_raw):
    raw = deepcopy(valid_raw)
    raw["city"] = ""

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_invalid_data_type(valid_raw):
    raw = deepcopy(valid_raw)
    raw["data_type"] = "historical"

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_missing_timezone(valid_raw):
    raw = deepcopy(valid_raw)
    raw["collected_at"] = "2026-11-16T11:00:00"

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_minimum_above_maximum(valid_raw):
    raw = deepcopy(valid_raw)
    raw["payload"]["daily"]["temperature_2m_min"] = [30.0]

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_negative_precipitation(valid_raw):
    raw = deepcopy(valid_raw)
    raw["payload"]["daily"]["precipitation_sum"] = [-1.0]

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_missing_daily_field(valid_raw):
    raw = deepcopy(valid_raw)
    del raw["payload"]["daily"]["temperature_2m_max"]

    with pytest.raises(TransformationError):
        transform_record(raw)


def test_multiple_dates_not_supported(valid_raw):
    raw = deepcopy(valid_raw)
    raw["payload"]["daily"]["time"] = [
        "2026-11-16",
        "2026-11-17",
    ]

    with pytest.raises(TransformationError):
        transform_record(raw)


@pytest.mark.parametrize("value", [True, "12.5", float("nan"), float("inf")])
def test_invalid_numbers(value):
    with pytest.raises(TransformationError):
        parse_number(value)


def test_null_number():
    assert parse_number(None) is None


def test_number_with_excessive_precision():
    with pytest.raises(TransformationError):
        parse_number(12.345)
