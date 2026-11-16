
# Guia de Execução — WeatherFlow

## 1. Objetivo

Este documento apresenta os procedimentos para
configurar, executar e validar o WeatherFlow localmente.

O ambiente utiliza Python, UV, Docker Compose,
PostgreSQL, Apache Airflow e Streamlit.

## 2. Pré-requisitos

- Windows com PowerShell
- Python 3.12
- UV
- Git
- Docker Desktop
- VS Code (recomendado)

Verificar as ferramentas:

```powershell
python --version
uv --version
docker --version
docker compose version
git --version
```

## 3. Clonar o repositório

```powershell
git clone https://github.com/rafaelporfiriobarros/weatherflow.git
cd weatherflow
```

## 4. Instalar dependências Python

```powershell
uv sync --locked
```

Verificar:

```powershell
uv run python --version
```

## 5. Configurar variáveis de ambiente

Criar o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Editar o `.env` e configurar:

- `APP_ENV`
- `LOG_LEVEL`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`

A senha definida em `POSTGRES_PASSWORD` deve
corresponder à senha utilizada em `DATABASE_URL`.

Exemplo de estrutura:

```dotenv
APP_ENV=development
LOG_LEVEL=INFO

POSTGRES_PASSWORD=SENHA_LOCAL_ESCOLHIDA
DATABASE_URL=postgresql://weatherflow:SENHA_LOCAL_ESCOLHIDA@127.0.0.1:55435/weatherflow
```

Não utilizar literalmente a senha de exemplo.

O arquivo `.env` não deve ser publicado no GitHub.

Se a senha contiver caracteres especiais,
a parte correspondente da URL deve ser
codificada adequadamente.

## 6. Iniciar PostgreSQL

Iniciar o serviço:

```powershell
docker compose up -d postgres
```

Verificar o estado:

```powershell
docker compose ps
```

Verificar a disponibilidade:

```powershell
docker exec weatherflow-postgres `
    pg_isready -U weatherflow -d weatherflow
```

O PostgreSQL utiliza:

- Banco: `weatherflow`
- Usuário: `weatherflow`
- Porta local: `55435`
- Porta interna: `5432`

O script `sql/001_schema.sql` é montado no
diretório de inicialização do PostgreSQL.

Esse script é executado automaticamente apenas
quando o diretório de dados do banco é inicializado
pela primeira vez.

## 7. Executar extração

```powershell
uv run python -m weatherflow.main
```

Os arquivos JSON são gravados em:

```text
data/raw/
```

Listar arquivos:

```powershell
Get-ChildItem .\data\raw\ -Filter *.json
```

## 8. Executar ETL

Com PostgreSQL disponível e arquivos de
entrada preparados:

```powershell
uv run python -m weatherflow.etl
```

O processo transforma os registros e realiza
o carregamento no PostgreSQL.

## 9. Iniciar Apache Airflow

Construir e iniciar o serviço:

```powershell
docker compose up -d --build airflow
```

Verificar:

```powershell
docker compose ps
```

Acessar:

http://localhost:8080

O Airflow utiliza a DAG:

`weatherflow_daily`

As tarefas são:

1. `extract_weather`
2. `load_weather`

Dependência:

`extract_weather >> load_weather`

O agendamento é diário.

A DAG possui:

- `catchup=False`
- `max_active_runs=1`
- 2 retentativas por tarefa
- Intervalo de 2 minutos entre retentativas

A criação da DAG utiliza pausa inicial.
É necessário habilitá-la na interface
para permitir execuções agendadas.

O comando `standalone` do Airflow pode gerar
credenciais administrativas nos logs do contêiner.
Consulte-as localmente e não as publique.

## 10. Consultar logs

Logs do PostgreSQL:

```powershell
docker compose logs --tail=100 postgres
```

Logs do Airflow:

```powershell
docker compose logs --tail=100 airflow
```

Acompanhar logs do Airflow:

```powershell
docker compose logs -f airflow
```

## 11. Consultar dados no PostgreSQL

Executar:

```powershell
docker exec weatherflow-postgres `
    psql -U weatherflow -d weatherflow `
    -c "SELECT COUNT(*) FROM weather_forecasts;"
```

Consultar a distribuição por cidade:

```powershell
docker exec weatherflow-postgres `
    psql -U weatherflow -d weatherflow `
    -c "SELECT city, COUNT(*) FROM weather_forecasts GROUP BY city ORDER BY city;"
```

## 12. Executar Streamlit

Com PostgreSQL disponível:

```powershell
uv run streamlit run dashboard/app.py
```

Acessar:

http://localhost:8501

O dashboard permite consultar:

- Previsões meteorológicas
- Cidades monitoradas
- Temperaturas
- Precipitação
- Gráficos e tabelas
- Exportação CSV

## 13. Testes automatizados

Executar:

```powershell
uv run pytest -q
```

Resultado validado na Etapa 5:

63 testes aprovados.

## 14. Qualidade de código

```powershell
uv run ruff check .
uv run ruff format --check .
```

## 15. Encerrar os serviços

```powershell
docker compose down
```

Esse comando encerra os serviços sem remover
o volume persistente do PostgreSQL.

Atenção: não utilizar `docker compose down -v`
sem intenção explícita de apagar os dados
armazenados nos volumes.

## 16. Solução de problemas

### PostgreSQL indisponível

Verificar:

```powershell
docker compose ps
docker compose logs postgres
```

### Airflow não inicia

Verificar:

```powershell
docker compose logs airflow
```

### Dashboard sem dados

Confirmar que o PostgreSQL está disponível
e que o ETL foi executado.

### Erros de configuração

Verificar se as variáveis do `.env`
estão preenchidas corretamente.

Não imprimir senhas ou URLs com credenciais
em logs públicos ou capturas de tela.

### Testes com falhas

Executar:

```powershell
uv run pytest -v --tb=short
```

Investigar o erro antes de alterar o código.
