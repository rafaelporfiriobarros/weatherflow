"""Testes da camada analitica do WeatherFlow."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from weatherflow import analytics


@pytest.fixture
def sample_records():
    """Retorna previsoes sinteticas para os testes."""
    return [
        {
            "city": "Curitiba",
            "temperature_max": Decimal("24.9"),
            "temperature_min": Decimal("13.9"),
            "precipitation_sum": Decimal("0.2"),
        },
        {
            "city": "Rio de Janeiro",
            "temperature_max": Decimal("27.3"),
            "temperature_min": Decimal("22.3"),
            "precipitation_sum": Decimal("9.0"),
        },
        {
            "city": "Sao Paulo",
            "temperature_max": Decimal("24.5"),
            "temperature_min": Decimal("18.4"),
            "precipitation_sum": Decimal("6.9"),
        },
    ]


def test_calculate_summary(sample_records):
    result = analytics.calculate_summary(sample_records)

    assert result["total_forecasts"] == 3
    assert result["total_cities"] == 3
    assert result["max_temperature"] == 27.3
    assert result["min_temperature"] == 13.9
    assert result["total_precipitation"] == pytest.approx(16.1)


def test_calculate_summary_empty():
    result = analytics.calculate_summary([])

    assert result["total_forecasts"] == 0
    assert result["total_cities"] == 0
    assert result["max_temperature"] is None
    assert result["total_precipitation"] is None


def test_calculate_summary_with_null_values():
    records = [
        {
            "city": "Curitiba",
            "temperature_max": None,
            "temperature_min": None,
            "precipitation_sum": None,
        }
    ]

    result = analytics.calculate_summary(records)

    assert result["total_forecasts"] == 1
    assert result["max_temperature"] is None
    assert result["min_temperature"] is None
    assert result["total_precipitation"] is None


def test_invalid_date_range():
    with pytest.raises(ValueError):
        analytics.get_latest_forecasts(
            start_date=date(2026, 11, 17),
            end_date=date(2026, 11, 15),
        )


def test_get_latest_forecasts_uses_parameters(monkeypatch):
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        {"city": "Curitiba", "forecast_date": date(2026, 11, 16)}
    ]

    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    connect = MagicMock(return_value=connection)

    monkeypatch.setattr(analytics.psycopg, "connect", connect)
    monkeypatch.setattr(analytics, "get_database_url", lambda: "postgresql://test")

    result = analytics.get_latest_forecasts(
        city="Curitiba",
        start_date=date(2026, 11, 16),
    )

    assert len(result) == 1
    assert result[0]["city"] == "Curitiba"

    cursor.execute.assert_called_once()

    sql, params = cursor.execute.call_args.args

    assert "ROW_NUMBER()" in sql
    assert "PARTITION BY city, forecast_date" in sql
    assert params == (
        "Curitiba",
        "Curitiba",
        date(2026, 11, 16),
        date(2026, 11, 16),
        None,
        None,
    )
    assert "Curitiba" not in sql


def test_get_available_cities(monkeypatch):
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("Curitiba",),
        ("Rio de Janeiro",),
        ("Sao Paulo",),
    ]

    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor

    monkeypatch.setattr(
        analytics.psycopg,
        "connect",
        MagicMock(return_value=connection),
    )
    monkeypatch.setattr(analytics, "get_database_url", lambda: "postgresql://test")

    result = analytics.get_available_cities()

    assert result == ["Curitiba", "Rio de Janeiro", "Sao Paulo"]
