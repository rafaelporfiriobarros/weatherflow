"""Executa a transformacao e a carga dos arquivos JSON."""

import logging
from pathlib import Path

from weatherflow.load import load_records
from weatherflow.transform import WeatherRecord, transform_file

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def prepare_records(
    raw_dir: Path = RAW_DIR,
) -> list[WeatherRecord]:
    """Le e valida os arquivos antes de iniciar a carga."""

    files = sorted(raw_dir.glob("*.json"))

    if not files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em {raw_dir}")

    records = []

    for file in files:
        record = transform_file(file)
        records.append(record)

    return records


def main() -> None:
    """Executa o processo ETL."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logger.info("Iniciando ETL WeatherFlow")

    records = prepare_records()

    logger.info("Registros validados: %s", len(records))

    inserted = load_records(records)

    logger.info("Registros inseridos: %s", inserted)
    logger.info("Registros ignorados por conflito: %s", len(records) - inserted)
    logger.info("ETL finalizado com sucesso")


if __name__ == "__main__":
    main()
