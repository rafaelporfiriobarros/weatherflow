"""Transformacao e validacao de dados meteorologicos."""

import json
import math
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class TransformationError(ValueError):
    """Erro de validacao ou transformacao."""


@dataclass(frozen=True)
class WeatherRecord:
    """Representa uma previsao meteorologica validada."""

    city: str
    forecast_date: date
    collected_at: datetime
    temperature_max: Decimal | None
    temperature_min: Decimal | None
    precipitation_sum: Decimal | None
    source: str


def parse_number(value: Any) -> Decimal | None:
    """Converte valores numericos para Decimal."""

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise TransformationError("Valor numerico invalido")

    if isinstance(value, float) and not math.isfinite(value):
        raise TransformationError("Numero nao finito")

    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise TransformationError("Numero invalido") from exc

    if not number.is_finite():
        raise TransformationError("Numero nao finito")

    if number.as_tuple().exponent < -2:
        raise TransformationError("Precisao superior a duas casas decimais")

    return number


def transform_record(raw: dict[str, Any]) -> WeatherRecord:
    """Valida e transforma um registro JSON."""

    if not isinstance(raw, dict):
        raise TransformationError("Registro Raw invalido")

    city = raw.get("city")
    source = raw.get("source")
    collected_at_raw = raw.get("collected_at")

    if not isinstance(city, str) or not city.strip():
        raise TransformationError("Cidade invalida")

    if len(city) > 100:
        raise TransformationError("Nome de cidade muito longo")

    if not isinstance(source, str) or not source.strip():
        raise TransformationError("Fonte invalida")

    if len(source) > 50:
        raise TransformationError("Nome de fonte muito longo")

    if not isinstance(collected_at_raw, str):
        raise TransformationError("Data de coleta ausente")

    try:
        collected_at = datetime.fromisoformat(collected_at_raw)
    except ValueError as exc:
        raise TransformationError("Data de coleta invalida") from exc

    if collected_at.tzinfo is None:
        raise TransformationError("Data de coleta sem fuso horario")

    if raw.get("data_type") != "forecast":
        raise TransformationError("Tipo de dado nao suportado")

    payload = raw.get("payload")

    if not isinstance(payload, dict):
        raise TransformationError("Payload invalido")

    daily = payload.get("daily")

    if not isinstance(daily, dict):
        raise TransformationError("Campo daily invalido")

    fields = (
        "time",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
    )

    for field in fields:
        values = daily.get(field)

        if not isinstance(values, list) or len(values) != 1:
            raise TransformationError(f"Campo diario invalido: {field}")

    try:
        forecast_date = date.fromisoformat(daily["time"][0])
    except (TypeError, ValueError) as exc:
        raise TransformationError("Data da previsao invalida") from exc

    maximum = parse_number(daily["temperature_2m_max"][0])
    minimum = parse_number(daily["temperature_2m_min"][0])
    precipitation = parse_number(daily["precipitation_sum"][0])

    if maximum is not None and minimum is not None and minimum > maximum:
        raise TransformationError("Temperatura minima maior que maxima")

    if precipitation is not None and precipitation < 0:
        raise TransformationError("Precipitacao negativa")

    for temperature in (minimum, maximum):
        if temperature is not None and not -100 <= temperature <= 100:
            raise TransformationError("Temperatura fora do intervalo permitido")

    return WeatherRecord(
        city=city.strip(),
        forecast_date=forecast_date,
        collected_at=collected_at,
        temperature_max=maximum,
        temperature_min=minimum,
        precipitation_sum=precipitation,
        source=source.strip(),
    )


def transform_file(path: Path) -> WeatherRecord:
    """Le um arquivo JSON e retorna um registro validado."""

    try:
        with path.open(encoding="utf-8") as file:
            raw = json.load(file)
    except (OSError, ValueError) as exc:
        raise TransformationError(f"Falha ao ler JSON: {path.name}") from exc

    return transform_record(raw)
