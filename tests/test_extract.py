"""Testes automatizados da extracao meteorologica."""

import json
from unittest.mock import Mock

import pytest
import requests

from weatherflow.config import City
from weatherflow.extract import (
    API_URL,
    ExtractionError,
    fetch_weather,
    save_raw,
)

CITY = City("Sao Paulo", -23.5505, -46.6333)


@pytest.fixture
def valid_payload():
    return {
        "latitude": -23.55,
        "longitude": -46.63,
        "daily": {
            "time": ["2026-11-15"],
            "temperature_2m_max": [28.5],
            "temperature_2m_min": [19.2],
            "precipitation_sum": [4.8],
        },
    }


def make_session(payload, status_code=200):
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.json.return_value = payload

    if status_code >= 400:
        error = requests.HTTPError("HTTP error")
        error.response = response
        response.raise_for_status.side_effect = error

    session = Mock(spec=requests.Session)
    session.get.return_value = response

    return session


def test_fetch_weather_success(valid_payload):
    session = make_session(valid_payload)

    result = fetch_weather(CITY, session=session)

    assert result["city"] == "Sao Paulo"
    assert result["source"] == "open-meteo"
    assert result["data_type"] == "forecast"
    assert result["payload"] == valid_payload
    assert "collected_at" in result

    session.get.assert_called_once()

    args, kwargs = session.get.call_args

    assert args[0] == API_URL
    assert kwargs["timeout"] == (5, 20)
    assert kwargs["params"]["forecast_days"] == 1


def test_fetch_weather_timeout():
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.Timeout()

    with pytest.raises(ExtractionError, match="Timeout"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_http_error(valid_payload):
    session = make_session(valid_payload, status_code=503)

    with pytest.raises(ExtractionError, match="HTTP 503"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_connection_error():
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.ConnectionError()

    with pytest.raises(ExtractionError, match="conexao"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_invalid_json():
    session = make_session({})
    session.get.return_value.json.side_effect = ValueError("Invalid JSON")

    with pytest.raises(ExtractionError, match="JSON invalido"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_missing_daily():
    session = make_session({"latitude": -23.55})

    with pytest.raises(ExtractionError, match="daily"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_invalid_root():
    session = make_session([])

    with pytest.raises(ExtractionError, match="Resposta inesperada"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_missing_variable(valid_payload):
    del valid_payload["daily"]["precipitation_sum"]
    session = make_session(valid_payload)

    with pytest.raises(ExtractionError, match="precipitation_sum"):
        fetch_weather(CITY, session=session)


def test_fetch_weather_inconsistent_lengths(valid_payload):
    valid_payload["daily"]["time"].append("2026-11-16")
    session = make_session(valid_payload)

    with pytest.raises(ExtractionError, match="inconsistentes"):
        fetch_weather(CITY, session=session)


def test_save_raw_creates_json(tmp_path, valid_payload):
    record = {
        "city": "Sao Paulo",
        "collected_at": "2026-11-15T12:00:00+00:00",
        "source": "open-meteo",
        "data_type": "forecast",
        "payload": valid_payload,
    }

    path = save_raw(record, tmp_path)

    assert path.exists()
    assert path.suffix == ".json"

    with path.open(encoding="utf-8") as file:
        saved = json.load(file)

    assert saved == record


def test_save_raw_does_not_overwrite(tmp_path, valid_payload):
    record = {
        "city": "Sao Paulo",
        "payload": valid_payload,
    }

    first = save_raw(record, tmp_path)
    second = save_raw(record, tmp_path)

    assert first != second
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_save_raw_invalid_city(tmp_path):
    with pytest.raises(ValueError, match="Nome de cidade"):
        save_raw({"city": "   "}, tmp_path)
