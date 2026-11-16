"""Dashboard analitico do WeatherFlow."""

from datetime import date

import pandas as pd
import streamlit as st

from weatherflow.analytics import (
    calculate_summary,
    get_available_cities,
    get_latest_forecasts,
)

st.set_page_config(
    page_title="WeatherFlow | Analytics",
    page_icon="🌤️",
    layout="wide",
)


@st.cache_data(ttl=300)
def load_cities() -> list[str]:
    """Consulta cidades com cache de cinco minutos."""
    return get_available_cities()


@st.cache_data(ttl=300)
def load_forecasts(
    city: str | None,
    start_date: date | None,
    end_date: date | None,
) -> pd.DataFrame:
    """Carrega a previsao mais recente por cidade e data."""
    records = get_latest_forecasts(
        city=city,
        start_date=start_date,
        end_date=end_date,
    )

    df = pd.DataFrame(records)

    if df.empty:
        return df

    numeric_columns = [
        "temperature_max",
        "temperature_min",
        "precipitation_sum",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    return df


def format_metric(value: float | None, unit: str) -> str:
    """Formata indicadores numericos opcionais."""
    if value is None or pd.isna(value):
        return "N/D"

    return f"{value:.1f} {unit}"


def prepare_chart_data(
    df: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Prepara dados para os graficos meteorologicos."""
    chart_df = df[["city", "forecast_date", *columns]].copy()

    chart_df["categoria"] = (
        chart_df["city"]
        + " | "
        + pd.to_datetime(chart_df["forecast_date"]).dt.strftime("%d/%m/%Y")
    )

    return chart_df.set_index("categoria")[columns]


# --------------------------------------------------
# CABECALHO
# --------------------------------------------------

st.title("🌤️ WeatherFlow Analytics")

st.caption(
    "Monitoramento de previsoes meteorologicas com Python, PostgreSQL e Apache Airflow."
)


# --------------------------------------------------
# FILTROS
# --------------------------------------------------

st.sidebar.header("Filtros")

try:
    cities = load_cities()

    selected_city = st.sidebar.selectbox(
        "Cidade",
        options=["Todas", *cities],
    )

    city_filter = None if selected_city == "Todas" else selected_city

    use_date_filter = st.sidebar.checkbox(
        "Filtrar por periodo",
        value=False,
    )

    start_date = None
    end_date = None

    if use_date_filter:
        start_date = st.sidebar.date_input(
            "Data inicial",
            value=date(2026, 11, 15),
            format="DD/MM/YYYY",
        )

        end_date = st.sidebar.date_input(
            "Data final",
            value=date.today(),
            format="DD/MM/YYYY",
        )

        if start_date > end_date:
            st.error("A data inicial nao pode ser posterior a data final.")
            st.stop()

    if st.sidebar.button("Atualizar dados"):
        load_cities.clear()
        load_forecasts.clear()
        st.rerun()

    df = load_forecasts(
        city=city_filter,
        start_date=start_date,
        end_date=end_date,
    )

except Exception:
    st.error(
        "Nao foi possivel consultar o PostgreSQL. "
        "Verifique se o banco esta em execucao "
        "e se a conexao foi configurada."
    )
    st.stop()


# --------------------------------------------------
# VALIDACAO DOS DADOS
# --------------------------------------------------

if df.empty:
    st.warning("Nenhuma previsao encontrada para os filtros selecionados.")
    st.stop()


# --------------------------------------------------
# INDICADORES
# --------------------------------------------------

summary = calculate_summary(df.to_dict("records"))

st.subheader("Indicadores meteorologicos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Previsoes",
        summary["total_forecasts"],
    )

with col2:
    st.metric(
        "Cidades",
        summary["total_cities"],
    )

with col3:
    st.metric(
        "Maior temperatura maxima",
        format_metric(
            summary["max_temperature"],
            "°C",
        ),
    )

with col4:
    st.metric(
        "Menor temperatura minima",
        format_metric(
            summary["min_temperature"],
            "°C",
        ),
    )

st.metric(
    "Soma da precipitacao prevista",
    format_metric(
        summary["total_precipitation"],
        "mm",
    ),
)

st.caption(
    "A precipitacao representa a soma dos acumulados "
    "previstos para as cidades e datas selecionadas. "
    "Nao representa uma medicao de chuva observada."
)

st.divider()


# --------------------------------------------------
# GRAFICO 1 — TEMPERATURAS
# --------------------------------------------------

st.subheader("Temperaturas previstas")

temperature_df = prepare_chart_data(
    df,
    [
        "temperature_max",
        "temperature_min",
    ],
)

temperature_df = temperature_df.rename(
    columns={
        "temperature_max": "Temperatura maxima",
        "temperature_min": "Temperatura minima",
    }
)

st.bar_chart(
    temperature_df,
    x_label="Cidade e data prevista",
    y_label="Temperatura (°C)",
    stack=False,
    height=380,
)

st.caption("Comparacao das temperaturas maxima e minima previstas por cidade e data.")


# --------------------------------------------------
# GRAFICO 2 — PRECIPITACAO
# --------------------------------------------------

st.subheader("Precipitacao prevista")

precipitation_df = prepare_chart_data(
    df,
    ["precipitation_sum"],
)

precipitation_df = precipitation_df.rename(
    columns={
        "precipitation_sum": "Precipitacao (mm)",
    }
)

st.bar_chart(
    precipitation_df,
    x_label="Cidade e data prevista",
    y_label="Precipitacao prevista (mm)",
    height=380,
)

st.caption("Volume de precipitacao previsto para cada cidade e data, em milimetros.")

st.divider()


# --------------------------------------------------
# TABELA DE DADOS
# --------------------------------------------------

st.subheader("Dados detalhados")

display_df = df.copy()

display_df["forecast_date"] = pd.to_datetime(display_df["forecast_date"]).dt.strftime(
    "%d/%m/%Y"
)

display_df["collected_at"] = pd.to_datetime(
    display_df["collected_at"],
    utc=True,
).dt.strftime("%d/%m/%Y %H:%M:%S UTC")

display_df = display_df.rename(
    columns={
        "city": "Cidade",
        "forecast_date": "Data prevista",
        "collected_at": "Coletado em (UTC)",
        "temperature_max": "Temperatura maxima (°C)",
        "temperature_min": "Temperatura minima (°C)",
        "precipitation_sum": "Precipitacao (mm)",
        "source": "Fonte",
    }
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)

# --------------------------------------------------
# EXPORTACAO CSV
# --------------------------------------------------

csv_data = display_df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Exportar dados CSV",
    data=csv_data,
    file_name="weatherflow_forecasts.csv",
    mime="text/csv",
)

st.caption(
    "Cada linha representa a coleta mais recente "
    "de uma cidade para determinada data prevista."
)
