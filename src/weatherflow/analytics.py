"""Consultas analiticas para o WeatherFlow."""

from datetime import date
from typing import Any

import psycopg
from psycopg.rows import dict_row

from weatherflow.load import get_database_url

LATEST_FORECASTS_SQL = """
WITH ranked AS (
    SELECT
        id,
        city,
        forecast_date,
        collected_at,
        temperature_max,
        temperature_min,
        precipitation_sum,
        source,
        ROW_NUMBER() OVER (
            PARTITION BY city, forecast_date
            ORDER BY collected_at DESC, id DESC
        ) AS rn
    FROM weather_forecasts
)
SELECT
    city,
    forecast_date,
    collected_at,
    temperature_max,
    temperature_min,
    precipitation_sum,
    source
FROM ranked
WHERE rn = 1
  AND (%s::text IS NULL OR city = %s)
  AND (%s::date IS NULL OR forecast_date >= %s)
  AND (%s::date IS NULL OR forecast_date <= %s)
ORDER BY forecast_date, city
"""


def get_latest_forecasts(
    city: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """Consulta a ultima previsao de cada cidade e data."""
    if start_date and end_date and start_date > end_date:
        raise ValueError("A data inicial nao pode ser posterior a data final.")

    params = (
        city,
        city,
        start_date,
        start_date,
        end_date,
        end_date,
    )

    with psycopg.connect(
        get_database_url(),
        row_factory=dict_row,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(LATEST_FORECASTS_SQL, params)
            return list(cursor.fetchall())


def calculate_summary(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calcula indicadores a partir das previsoes selecionadas."""
    if not records:
        return {
            "total_forecasts": 0,
            "total_cities": 0,
            "max_temperature": None,
            "min_temperature": None,
            "total_precipitation": None,
        }

    max_temps = [
        float(row["temperature_max"])
        for row in records
        if row["temperature_max"] is not None
    ]
    min_temps = [
        float(row["temperature_min"])
        for row in records
        if row["temperature_min"] is not None
    ]
    precipitation = [
        float(row["precipitation_sum"])
        for row in records
        if row["precipitation_sum"] is not None
    ]

    return {
        "total_forecasts": len(records),
        "total_cities": len({row["city"] for row in records}),
        "max_temperature": max(max_temps) if max_temps else None,
        "min_temperature": min(min_temps) if min_temps else None,
        "total_precipitation": (sum(precipitation) if precipitation else None),
    }


def get_available_cities() -> list[str]:
    """Retorna as cidades disponiveis no banco."""
    query = """
        SELECT DISTINCT city
        FROM weather_forecasts
        ORDER BY city
    """

    with psycopg.connect(get_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
