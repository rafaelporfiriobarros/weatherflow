"""Execucao da extracao meteorologica."""

import logging
from pathlib import Path

from weatherflow.config import get_cities, validate_cities
from weatherflow.extract import ExtractionError, fetch_weather, save_raw

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def main() -> None:
    """Executa a coleta das cidades configuradas."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    cities = get_cities()

    if not validate_cities(cities):
        raise ValueError("Configuracao de cidades invalida")

    failures = []

    for city in cities:
        try:
            record = fetch_weather(city)
            path = save_raw(record, RAW_DIR)

            logger.info(
                "Cidade %s salva em %s",
                city.name,
                path,
            )

        except (ExtractionError, OSError) as exc:
            logger.error(
                "Falha na cidade %s: %s",
                city.name,
                exc,
            )
            failures.append(city.name)

    if failures:
        raise RuntimeError(
            "Extracao incompleta. Cidades com falha: " + ", ".join(failures)
        )

    logger.info("Todas as cidades foram processadas.")


if __name__ == "__main__":
    main()
