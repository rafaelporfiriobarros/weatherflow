"""Testes automatizados do dashboard WeatherFlow."""

from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "dashboard" / "app.py"

SAMPLE_FORECASTS = [
    {
        "city": "Curitiba",
        "forecast_date": date(2026, 11, 16),
        "collected_at": datetime(2026, 11, 16, 16, 0, tzinfo=UTC),
        "temperature_max": 24.9,
        "temperature_min": 13.9,
        "precipitation_sum": 0.2,
        "source": "open-meteo",
    },
    {
        "city": "Sao Paulo",
        "forecast_date": date(2026, 11, 16),
        "collected_at": datetime(2026, 11, 16, 16, 0, tzinfo=UTC),
        "temperature_max": 28.7,
        "temperature_min": 18.4,
        "precipitation_sum": 6.9,
        "source": "open-meteo",
    },
]


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Evita interferencia do cache entre os testes."""
    st.cache_data.clear()
    yield
    st.cache_data.clear()


def run_dashboard(
    records=None,
    cities=None,
    database_error=False,
):
    """Executa o dashboard com dependencias simuladas."""
    if records is None:
        records = SAMPLE_FORECASTS

    if cities is None:
        cities = ["Curitiba", "Sao Paulo"]

    def fake_get_latest_forecasts(
        city=None,
        start_date=None,
        end_date=None,
    ):
        """Simula os filtros aplicados pela consulta SQL."""
        filtered = records

        if city is not None:
            filtered = [row for row in filtered if row["city"] == city]

        if start_date is not None:
            filtered = [row for row in filtered if row["forecast_date"] >= start_date]

        if end_date is not None:
            filtered = [row for row in filtered if row["forecast_date"] <= end_date]

        return filtered

    if database_error:
        cities_patch = patch(
            "weatherflow.analytics.get_available_cities",
            side_effect=ConnectionError("Banco indisponivel"),
        )
    else:
        cities_patch = patch(
            "weatherflow.analytics.get_available_cities",
            return_value=cities,
        )

    with (
        cities_patch,
        patch(
            "weatherflow.analytics.get_latest_forecasts",
            side_effect=fake_get_latest_forecasts,
        ),
    ):
        app = AppTest.from_file(
            APP_PATH,
            default_timeout=10,
        )

        app.run()

    return app


def test_dashboard_runs_without_errors():
    """Verifica se o dashboard inicia sem excecoes."""
    app = run_dashboard()

    assert len(app.exception) == 0


def test_dashboard_title():
    """Verifica o titulo principal da aplicacao."""
    app = run_dashboard()

    assert len(app.title) >= 1
    assert "WeatherFlow Analytics" in app.title[0].value


def test_dashboard_metrics():
    """Verifica os indicadores meteorologicos."""
    app = run_dashboard()

    metrics = {metric.label: str(metric.value) for metric in app.metric}

    assert metrics["Previsoes"] == "2"
    assert metrics["Cidades"] == "2"
    assert metrics["Maior temperatura maxima"] == "28.7 °C"
    assert metrics["Menor temperatura minima"] == "13.9 °C"
    assert metrics["Soma da precipitacao prevista"] == "7.1 mm"


def test_dashboard_city_filter():
    """Verifica se selecionar uma cidade altera os dados."""

    def fake_get_latest_forecasts(
        city=None,
        start_date=None,
        end_date=None,
    ):
        records = SAMPLE_FORECASTS

        if city is not None:
            records = [row for row in records if row["city"] == city]

        if start_date is not None:
            records = [row for row in records if row["forecast_date"] >= start_date]

        if end_date is not None:
            records = [row for row in records if row["forecast_date"] <= end_date]

        return records

    with (
        patch(
            "weatherflow.analytics.get_available_cities",
            return_value=["Curitiba", "Sao Paulo"],
        ),
        patch(
            "weatherflow.analytics.get_latest_forecasts",
            side_effect=fake_get_latest_forecasts,
        ),
    ):
        app = AppTest.from_file(
            APP_PATH,
            default_timeout=10,
        )

        app.run()

        assert len(app.exception) == 0

        app.selectbox[0].set_value("Curitiba").run()

        assert len(app.exception) == 0

        metrics = {metric.label: str(metric.value) for metric in app.metric}

        assert metrics["Previsoes"] == "1"
        assert metrics["Cidades"] == "1"


def test_dashboard_date_filter_exists():
    """Verifica se o filtro por periodo esta disponivel."""
    app = run_dashboard()

    assert len(app.checkbox) >= 1
    assert app.checkbox[0].label == "Filtrar por periodo"


def test_dashboard_empty_data():
    """Verifica a mensagem para consultas sem resultados."""
    app = run_dashboard(records=[])

    assert len(app.warning) >= 1
    assert "Nenhuma previsao" in app.warning[0].value


def test_dashboard_database_error():
    """Verifica o tratamento de erros de conexao."""
    app = run_dashboard(database_error=True)

    assert len(app.error) >= 1
    assert "PostgreSQL" in app.error[0].value


def test_dashboard_city_filter_exists():
    """Verifica se o seletor apresenta as cidades esperadas."""
    app = run_dashboard()

    assert len(app.exception) == 0
    assert len(app.selectbox) == 1

    options = list(app.selectbox[0].options)

    assert "Todas" in options
    assert "Curitiba" in options
    assert "Sao Paulo" in options
