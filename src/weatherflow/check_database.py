"""Verifica a quantidade de registros no PostgreSQL."""

import psycopg

from weatherflow.load import get_database_url


def main() -> None:
    """Consulta a quantidade de previsoes armazenadas."""

    with psycopg.connect(get_database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM weather_forecasts")

            total = cursor.fetchone()[0]

            print(f"Registros no PostgreSQL: {total}")


if __name__ == "__main__":
    main()
