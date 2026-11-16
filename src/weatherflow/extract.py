"""Extracao de dados meteorologicos da Open-Meteo."""

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

from weatherflow.config import City

logger = logging.getLogger(__name__)

API_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARIABLES = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
)


class ExtractionError(Exception):
    """Erro controlado durante a extracao."""


def fetch_weather(
    city: City,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Consulta dados diarios de uma cidade."""

    params = {
        "latitude": city.latitude,
        "longitude": city.longitude,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "America/Sao_Paulo",
        "forecast_days": 1,
    }

    client = session if session is not None else requests

    try:
        response = client.get(
            API_URL,
            params=params,
            timeout=(5, 20),
        )

        response.raise_for_status()
        payload = response.json()

    except requests.Timeout as exc:
        raise ExtractionError(f"Timeout ao consultar {city.name}") from exc

    except requests.HTTPError as exc:
        status = (
            exc.response.status_code if exc.response is not None else "desconhecido"
        )
        raise ExtractionError(f"Erro HTTP {status} para {city.name}") from exc

    except requests.RequestException as exc:
        raise ExtractionError(f"Falha de conexao para {city.name}") from exc

    except ValueError as exc:
        raise ExtractionError(f"JSON invalido para {city.name}") from exc

    if not isinstance(payload, dict):
        raise ExtractionError(f"Resposta inesperada para {city.name}")

    daily = payload.get("daily")

    if not isinstance(daily, dict):
        raise ExtractionError(f"Campo daily ausente ou invalido: {city.name}")

    required_fields = ("time", *DAILY_VARIABLES)

    for field in required_fields:
        if not isinstance(daily.get(field), list):
            raise ExtractionError(f"Campo {field} ausente ou invalido: {city.name}")

    lengths = {len(daily[field]) for field in required_fields}

    if lengths != {1}:
        raise ExtractionError(f"Series diarias inconsistentes: {city.name}")

    logger.info("Extracao concluida: %s", city.name)

    return {
        "city": city.name,
        "collected_at": datetime.now(UTC).isoformat(),
        "source": "open-meteo",
        "data_type": "forecast",
        "payload": payload,
    }


def save_raw(
    record: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Grava uma coleta JSON sem sobrescrever outra."""

    city = record["city"]

    safe_city = "".join(
        char.lower() if char.isalnum() and char.isascii() else "_" for char in city
    ).strip("_")

    if not safe_city:
        raise ValueError("Nome de cidade invalido")

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")

    filename = f"{safe_city}_{timestamp}_{uuid.uuid4().hex[:8]}.json"

    path = output_dir / filename

    content = json.dumps(
        record,
        ensure_ascii=False,
        indent=2,
    )

    with path.open("x", encoding="utf-8") as file:
        file.write(content)

    logger.info("Arquivo salvo: %s", path)

    return path
