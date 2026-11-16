"""Persistencia de previsoes meteorologicas no PostgreSQL."""

import os
from collections.abc import Sequence

import psycopg
from dotenv import load_dotenv

from weatherflow.transform import WeatherRecord

INSERT_SQL = """
INSERT INTO weather_forecasts (
    city,
    forecast_date,
    collected_at,
    temperature_max,
    temperature_min,
    precipitation_sum,
    source
)
VALUES (
    %(city)s,
    %(forecast_date)s,
    %(collected_at)s,
    %(temperature_max)s,
    %(temperature_min)s,
    %(precipitation_sum)s,
    %(source)s
)
ON CONFLICT (city, forecast_date, collected_at)
DO NOTHING
"""


def get_database_url() -> str:
    """Recupera a URL de conexao do ambiente."""

    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL nao configurada")

    return database_url


def load_records(
    records: Sequence[WeatherRecord],
    database_url: str | None = None,
) -> int:
    """Insere registros de maneira transacional e idempotente."""

    if not records:
        return 0

    connection_url = database_url if database_url is not None else get_database_url()

    inserted = 0

    with psycopg.connect(
        connection_url,
        connect_timeout=5,
    ) as connection:
        with connection.cursor() as cursor:
            for record in records:
                params = {
                    "city": record.city,
                    "forecast_date": record.forecast_date,
                    "collected_at": record.collected_at,
                    "temperature_max": record.temperature_max,
                    "temperature_min": record.temperature_min,
                    "precipitation_sum": record.precipitation_sum,
                    "source": record.source,
                }

                cursor.execute(INSERT_SQL, params)
                inserted += cursor.rowcount

    return inserted
