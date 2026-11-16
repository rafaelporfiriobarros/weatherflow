"""Testes da camada de persistencia."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from weatherflow.load import load_records
from weatherflow.transform import WeatherRecord


def make_record():
    return WeatherRecord(
        city="Sao Paulo",
        forecast_date=date(2026, 11, 16),
        collected_at=datetime.fromisoformat("2026-11-16T11:00:00-03:00"),
        temperature_max=Decimal("28.5"),
        temperature_min=Decimal("18.2"),
        precipitation_sum=Decimal("5.3"),
        source="open-meteo",
    )


def test_empty_records_do_not_connect():
    with patch("weatherflow.load.psycopg.connect") as connect:
        assert load_records([], database_url="postgresql://example") == 0

    connect.assert_not_called()


def test_load_records_counts_insertions():
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    cursor.rowcount = 1

    with patch(
        "weatherflow.load.psycopg.connect",
        return_value=connection,
    ) as connect:
        inserted = load_records(
            [make_record()],
            database_url="postgresql://example",
        )

    assert inserted == 1
    connect.assert_called_once()
    cursor.execute.assert_called_once()


def test_conflict_does_not_count_as_insertion():
    connection = MagicMock()
    cursor = MagicMock()

    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value = cursor
    cursor.rowcount = 0

    with patch(
        "weatherflow.load.psycopg.connect",
        return_value=connection,
    ):
        inserted = load_records(
            [make_record()],
            database_url="postgresql://example",
        )

    assert inserted == 0
