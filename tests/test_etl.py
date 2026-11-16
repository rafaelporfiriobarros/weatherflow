"""Testes do processo ETL."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from weatherflow.etl import prepare_records
from weatherflow.transform import TransformationError


def make_payload():
    return {
        "city": "Curitiba",
        "source": "open-meteo",
        "data_type": "forecast",
        "collected_at": "2026-11-16T11:00:00-03:00",
        "payload": {
            "daily": {
                "time": ["2026-11-16"],
                "temperature_2m_max": [24.9],
                "temperature_2m_min": [13.9],
                "precipitation_sum": [0.2],
            }
        },
    }


def test_prepare_records_reads_json(tmp_path: Path):
    file = tmp_path / "curitiba.json"
    file.write_text(
        json.dumps(make_payload()),
        encoding="utf-8",
    )

    records = prepare_records(tmp_path)

    assert len(records) == 1
    assert records[0].city == "Curitiba"


def test_prepare_records_rejects_empty_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        prepare_records(tmp_path)


def test_prepare_records_rejects_invalid_json(tmp_path: Path):
    file = tmp_path / "invalid.json"
    file.write_text("{invalid", encoding="utf-8")

    with pytest.raises(TransformationError):
        prepare_records(tmp_path)


def test_invalid_batch_does_not_load(tmp_path: Path):
    valid_file = tmp_path / "valid.json"
    invalid_file = tmp_path / "invalid.json"

    valid_file.write_text(
        json.dumps(make_payload()),
        encoding="utf-8",
    )
    invalid_file.write_text("{invalid", encoding="utf-8")

    with patch("weatherflow.etl.load_records") as load:
        with pytest.raises(TransformationError):
            records = prepare_records(tmp_path)
            load(records)

    load.assert_not_called()
