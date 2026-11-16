
# WeatherFlow

Pipeline de Engenharia de Dados meteorologicos desenvolvido
com Python, PostgreSQL, Apache Airflow e Docker.

## Objetivo

Automatizar a coleta, validacao, transformacao e
armazenamento de dados meteorologicos de cidades brasileiras.

## Problema de negocio

Uma empresa precisa acompanhar indicadores meteorologicos
sem depender de consultas manuais a sites externos.

## Tecnologias

- Python 3.12
- UV
- PostgreSQL (planejado)
- Apache Airflow (planejado)
- Docker Compose (planejado)
- Pytest
- Ruff
- Git e GitHub

## Arquitetura planejada

Open-Meteo API
    |
    v
Extract (Python)
    |
    v
Transform (Python)
    |
    v
Load (PostgreSQL)
    |
    v
SQL Analytics

O Apache Airflow sera responsavel pela orquestracao.

## Status

Etapa 1 - Fundacao do projeto.

## Instalacao

Requisitos:
- Python 3.12
- UV

Clone o repositorio:

```bash
git clone https://github.com/SEU-USUARIO/weatherflow.git
cd weatherflow
```

Instale as dependencias:

```bash
uv sync --locked
```

## Testes

```bash
uv run pytest -v
```

## Qualidade

```bash
uv run ruff check .
uv run ruff format --check .
```

## Estrutura

- src/weatherflow: codigo da aplicacao
- tests: testes automatizados
- dags: orquestracao futura
- sql: scripts SQL futuros
- docs: documentacao tecnica

## Roadmap

- [x] Etapa 1: Fundacao do projeto
- [ ] Etapa 2: Consumo da API
- [ ] Etapa 3: Transformacao e PostgreSQL
- [ ] Etapa 4: Apache Airflow
- [ ] Etapa 5: Qualidade e GitHub Actions
- [ ] Etapa 6: Analytics e documentacao final

## Seguranca

Nao versionar credenciais, arquivos .env ou dados sensiveis.

## Licenca

Ainda nao definida.
