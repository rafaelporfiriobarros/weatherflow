"""Testes da estrutura do DAG WeatherFlow."""

import ast
from pathlib import Path

DAG_FILE = Path(__file__).resolve().parents[1] / "dags" / "weatherflow_dag.py"


def read_dag_source() -> str:
    """Le o codigo-fonte do DAG."""
    return DAG_FILE.read_text(encoding="utf-8")


def test_dag_file_exists() -> None:
    """Verifica se o arquivo do DAG existe."""
    assert DAG_FILE.is_file()


def test_dag_python_syntax() -> None:
    """Verifica se o DAG possui sintaxe Python valida."""
    ast.parse(read_dag_source())


def test_dag_identifier() -> None:
    """Verifica o identificador do DAG."""
    assert 'dag_id="weatherflow_daily"' in read_dag_source()


def test_dag_tasks() -> None:
    """Verifica as tarefas esperadas."""
    source = read_dag_source()

    assert 'task_id="extract_weather"' in source
    assert 'task_id="load_weather"' in source


def test_task_dependency() -> None:
    """Verifica a ordem de execucao."""
    assert "extract_weather >> load_weather" in read_dag_source()


def test_catchup_disabled() -> None:
    """Verifica se o catchup esta desabilitado."""
    assert "catchup=False" in read_dag_source()


def test_retry_configuration() -> None:
    """Verifica a configuracao de tentativas."""
    assert '"retries": 2' in read_dag_source()
