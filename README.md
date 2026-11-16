# WeatherFlow — Pipeline de Engenharia de Dados Meteorológicos

Pipeline de Engenharia de Dados desenvolvido com **Python, Open-Meteo API, PostgreSQL, Apache Airflow e Docker**, com foco na automação da coleta, validação, transformação e disponibilização de dados meteorológicos.

O projeto foi estruturado para aplicar, de maneira prática e progressiva, fundamentos de **Engenharia de Software e Engenharia de Dados**, incluindo integração com APIs REST, processamento ETL, modelagem de dados, orquestração, testes automatizados, versionamento e documentação técnica.

> **Status:** Etapa 2 — Extração de dados meteorológicos em desenvolvimento e validação.

---

## 1. Visão geral

O WeatherFlow simula uma solução de dados para uma empresa que precisa acompanhar indicadores meteorológicos de diferentes cidades brasileiras.

A proposta é substituir consultas manuais por um pipeline automatizado, reproduzível e preparado para análises.

O sistema utiliza a **Open-Meteo Forecast API** como fonte de dados, permitindo consultar informações meteorológicas por meio de requisições HTTP.

### Cidades monitoradas

- São Paulo — SP
- Rio de Janeiro — RJ
- Curitiba — PR

### Indicadores meteorológicos

- Temperatura máxima diária (°C)
- Temperatura mínima diária (°C)
- Precipitação diária (mm)
- Data de referência da previsão
- Data e horário da coleta

**Observação:** os dados obtidos pela Forecast API representam previsões meteorológicas, que podem ser atualizadas ao longo do dia. Não devem ser interpretados automaticamente como medições históricas consolidadas.

---

## 2. Problema de negócio

Uma empresa com operações em diferentes cidades brasileiras precisa acompanhar condições meteorológicas para apoiar decisões operacionais.

Atualmente, essas informações são consultadas manualmente em sites externos, dificultando a padronização, o armazenamento e a análise dos dados.

Esse processo apresenta alguns desafios:

- Dependência de consultas manuais.
- Ausência de uma base centralizada.
- Dificuldade para comparar informações entre cidades.
- Falta de rastreabilidade das coletas.
- Possibilidade de inconsistências na organização dos dados.

### Solução proposta

Desenvolver um pipeline de Engenharia de Dados capaz de:

1. Consultar automaticamente uma API meteorológica pública.
2. Extrair dados de diferentes cidades.
3. Preservar as respostas originais em arquivos JSON.
4. Validar e transformar os dados coletados.
5. Armazenar os registros em um banco PostgreSQL.
6. Automatizar a execução com Apache Airflow.
7. Disponibilizar consultas SQL para análise dos indicadores.

O desenvolvimento será incremental, permitindo validar cada componente antes da implementação das próximas funcionalidades.

---

## 3. Tecnologias utilizadas

| Tecnologia | Finalidade | Situação |
|---|---|---|
| Python 3.12 | Desenvolvimento do pipeline | Implementado |
| UV | Gerenciamento de dependências | Implementado |
| Requests | Consumo da API REST | Etapa 2 |
| Open-Meteo API | Fonte de dados meteorológicos | Etapa 2 |
| JSON | Armazenamento inicial dos dados brutos | Etapa 2 |
| Pytest | Testes automatizados | Implementado |
| unittest.mock | Simulação de respostas HTTP | Etapa 2 |
| Ruff | Análise estática e formatação | Implementado |
| Git e GitHub | Versionamento do código | Implementado |
| PostgreSQL | Armazenamento estruturado | Planejado |
| Docker Compose | Infraestrutura local | Planejado |
| Apache Airflow | Orquestração do pipeline | Planejado |
| GitHub Actions | Integração contínua | Planejado |

O projeto utiliza uma arquitetura simples, adequada ao volume de dados e ao objetivo educacional.

Não serão utilizados Kafka, Spark ou Kubernetes nesta versão.

---

## 4. Arquitetura de dados

### Arquitetura planejada

```text
              Open-Meteo API
                    |
                    | HTTP GET
                    v
           +------------------+
           |  Extract         |
           |  Python/Requests |
           +------------------+
                    |
                    | JSON
                    v
           +------------------+
           |  Raw / Bronze    |
           |  Arquivos JSON   |
           +------------------+
                    |
                    v
           +------------------+
           |  Transform       |
           |  Python          |
           +------------------+
                    |
                    v
           +------------------+
           |  Load            |
           |  PostgreSQL      |
           +------------------+
                    |
                    v
           +------------------+
           |  SQL Analytics   |
           |  Indicadores     |
           +------------------+

       Apache Airflow (planejado)
       Orquestracao e agendamento

       GitHub Actions (planejado)
       Testes e qualidade do codigo
```

### Estratégia de processamento

O pipeline seguirá o modelo **ETL — Extract, Transform, Load**.

**Extract — Extração**

Responsável por consultar a Open-Meteo API, receber respostas JSON e registrar metadados da coleta.

**Transform — Transformação**

Responsável por validar campos, tratar inconsistências, padronizar tipos e organizar os registros em formato tabular.

**Load — Carga**

Responsável por persistir os dados no PostgreSQL, aplicando regras para evitar duplicações.

**Analytics — Análise**

Responsável por disponibilizar consultas SQL e indicadores meteorológicos.

A orquestração com Apache Airflow será implementada posteriormente, mantendo a lógica de negócio separada das DAGs.

---

## 5. Estrutura do projeto

```text
weatherflow/
|
|-- src/
|   `-- weatherflow/
|       |-- __init__.py
|       |-- config.py
|       |-- extract.py
|       `-- main.py
|
|-- tests/
|   |-- test_config.py
|   `-- test_extract.py
|
|-- data/
|   `-- raw/
|
|-- dags/
|
|-- sql/
|
|-- docs/
|   `-- requirements.md
|
|-- .github/
|   `-- workflows/
|
|-- .env.example
|-- .gitignore
|-- .python-version
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

### Responsabilidades dos diretórios

| Diretório ou arquivo | Responsabilidade |
|---|---|
| `src/weatherflow/` | Código-fonte da aplicação |
| `config.py` | Configuração das cidades monitoradas |
| `extract.py` | Comunicação com a API e gravação dos dados |
| `main.py` | Ponto de entrada da extração |
| `tests/` | Testes automatizados |
| `data/raw/` | Armazenamento local dos dados brutos |
| `dags/` | DAGs do Airflow, futuramente |
| `sql/` | Scripts SQL e consultas analíticas, futuramente |
| `docs/` | Documentação técnica |
| `.github/workflows/` | Workflows de CI, futuramente |
| `pyproject.toml` | Configuração do projeto Python |
| `uv.lock` | Controle das versões das dependências |

O diretório `data/raw/` é criado durante a execução e não deve ser versionado.

Algumas pastas da arquitetura futura poderão não aparecer no GitHub enquanto estiverem vazias.

---

## 6. Etapa 1 — Fundação do projeto

**Situação: concluída e validada.**

A primeira etapa estabeleceu os fundamentos de Engenharia de Software necessários para o desenvolvimento do pipeline.

### Funcionalidades implementadas

- Inicialização do projeto com UV.
- Configuração do Python 3.12.
- Organização modular do código.
- Configuração inicial das cidades.
- Validação de nomes e coordenadas geográficas.
- Configuração do Pytest.
- Configuração do Ruff.
- Criação do `.gitignore`.
- Documentação dos requisitos.
- Inicialização e publicação do repositório Git.

### Evidências de validação

| Verificação | Resultado |
|---|---|
| Python | 3.12.14 |
| Pytest | 9 testes aprovados |
| Ruff lint | Aprovado |
| Ruff format | Aprovado |
| Git | Branch `main` sincronizada |
| Working tree | Sem alterações pendentes |

A Etapa 1 foi validada antes do início da integração com a API.

---

## 7. Etapa 2 — Extração de dados meteorológicos

**Situação: implementação e validação em andamento.**

Esta etapa introduz a integração com uma API REST externa.

### Funcionalidades desenvolvidas para validação

- Requisições HTTP GET com Requests.
- Consulta da Open-Meteo Forecast API.
- Configuração de coordenadas por cidade.
- Solicitação de variáveis meteorológicas diárias.
- Definição de timeout.
- Tratamento de erros HTTP.
- Tratamento de falhas de conexão.
- Tratamento de respostas JSON inválidas.
- Validação inicial da estrutura recebida.
- Inclusão de metadados de coleta.
- Armazenamento dos dados brutos em JSON.
- Testes automatizados utilizando mocks.

### Endpoint utilizado

```text
https://api.open-meteo.com/v1/forecast
```

### Parâmetros da requisição

| Parâmetro | Valor |
|---|---|
| `latitude` | Latitude da cidade |
| `longitude` | Longitude da cidade |
| `daily` | Variáveis meteorológicas |
| `timezone` | America/Sao_Paulo |
| `forecast_days` | 1 |

### Variáveis solicitadas

```text
temperature_2m_max
temperature_2m_min
precipitation_sum
```

A consulta utiliza o horizonte de previsão de um dia.

### Armazenamento Raw

Os dados são armazenados em:

```text
data/raw/
```

Cada arquivo contém a resposta original da API e os seguintes metadados:

| Campo | Descrição |
|---|---|
| `city` | Cidade consultada |
| `collected_at` | Data e horário UTC da coleta |
| `source` | Identificação da fonte |
| `data_type` | Tipo de dado: forecast |
| `payload` | Resposta JSON da API |

Os arquivos recebem nomes únicos para preservar diferentes execuções.

A estratégia atual não elimina registros equivalentes entre coletas. A deduplicação será tratada na etapa de persistência.

---

## 8. Instalação e configuração

### Pré-requisitos

- Windows com PowerShell.
- Python 3.12.
- UV instalado.
- Git instalado.
- VS Code, recomendado.
- Acesso à internet para a consulta real à API.

### Clonar o repositório

```powershell
git clone https://github.com/SEU-USUARIO/weatherflow.git

cd weatherflow
```

Substitua `SEU-USUARIO` pelo seu usuário do GitHub.

### Instalar dependências

```powershell
uv sync --locked
```

O comando instala as dependências conforme o arquivo `uv.lock`.

### Verificar a versão do Python

```powershell
uv run python --version
```

Resultado esperado:

```text
Python 3.12.x
```

---

## 9. Executando o pipeline de extração

Para executar a coleta meteorológica:

```powershell
uv run python -m weatherflow.main
```

O processo realiza uma consulta para cada cidade configurada.

Em caso de sucesso, os arquivos JSON são gravados em `data/raw/`.

### Listar arquivos gerados

```powershell
Get-ChildItem .\data\raw\ -Filter *.json
```

### Contar arquivos

```powershell
(Get-ChildItem .\data\raw\ -Filter *.json).Count
```

Uma primeira execução totalmente bem-sucedida deverá gerar três arquivos, considerando o diretório inicialmente vazio.

### Inspecionar os dados

```powershell
$file = Get-ChildItem .\data\raw\*.json |
    Select-Object -First 1

$data = Get-Content $file.FullName -Raw |
    ConvertFrom-Json

$data.city
$data.source
$data.collected_at
$data.payload.daily
```

Esses comandos permitem verificar a estrutura e os valores recebidos.

---

## 10. Testes automatizados

O projeto utiliza Pytest para validar o comportamento das funções.

### Executar todos os testes

```powershell
uv run pytest -v
```

### Executar somente os testes de configuração

```powershell
uv run pytest tests/test_config.py -v
```

### Executar somente os testes de extração

```powershell
uv run pytest tests/test_extract.py -v
```

### Estratégia de testes

Os testes de extração utilizam mocks para simular respostas da API sem depender de conexão com a internet.

Entre os cenários previstos estão:

- Requisição bem-sucedida.
- Timeout.
- Erro HTTP.
- Falha de conexão.
- JSON inválido.
- Campo obrigatório ausente.
- Estrutura de resposta inesperada.
- Listas com tamanhos inconsistentes.
- Gravação de arquivos JSON.
- Preservação de coletas anteriores.

**Meta de validação da Etapa 2:** 21 testes aprovados, considerando os nove testes da Etapa 1 e os 12 testes adicionados à extração.

Esse resultado ainda depende da execução e validação no ambiente local.

---

## 11. Qualidade de código

O Ruff é utilizado para análise estática, organização de imports e padronização do código.

### Verificar problemas

```powershell
uv run ruff check .
```

### Verificar formatação

```powershell
uv run ruff format --check .
```

### Aplicar formatação

```powershell
uv run ruff format .
```

### Executar todas as verificações

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
```

O objetivo é manter o projeto organizado, legível e fácil de manter.

---

## 12. Segurança e confiabilidade

O WeatherFlow adota boas práticas de desenvolvimento desde as primeiras etapas.

### Segurança

- Comunicação HTTPS com a API.
- Ausência de credenciais no código-fonte.
- Arquivos `.env` ignorados pelo Git.
- Diretório de dados locais fora do versionamento.
- Separação entre configuração e lógica de negócio.
- Dependências gerenciadas com UV.

### Confiabilidade

- Timeout nas requisições HTTP.
- Tratamento de exceções.
- Validação inicial da resposta JSON.
- Registro de logs.
- Testes automatizados.
- Identificação de falhas por cidade.
- Preservação das respostas originais.

Essas medidas reduzem riscos, mas não substituem monitoramento operacional, controle de acesso ou validações completas de qualidade de dados.

---

## 13. Limitações atuais

O projeto foi propositalmente desenvolvido com escopo reduzido.

Na Etapa 2, as principais limitações são:

- Coleta sequencial de três cidades.
- Uma requisição por cidade.
- Ausência de retentativas automáticas.
- Dados armazenados apenas em arquivos JSON.
- Ausência de persistência em banco de dados.
- Ausência de orquestração com Airflow.
- Ausência de deduplicação entre coletas.
- Ausência de dashboard.
- Validação ainda limitada da estrutura e dos tipos de dados.

Essas funcionalidades serão incorporadas progressivamente, conforme o roadmap.

---

## 14. Roadmap

| Etapa | Descrição | Status |
|---|---|---|
| 1 | Fundação e Engenharia de Software | Concluída |
| 2 | Extração de dados da Open-Meteo API | Em validação |
| 3 | Transformação e persistência no PostgreSQL | Pendente |
| 4 | Orquestração com Apache Airflow | Pendente |
| 5 | Testes avançados e GitHub Actions | Pendente |
| 6 | Analytics e documentação final | Pendente |

### Etapa 3 — Transformação e PostgreSQL

Implementar:

- Tratamento e padronização dos dados.
- Validação de tipos e valores ausentes.
- Modelagem relacional.
- Criação de tabelas SQL.
- Persistência no PostgreSQL.
- Regras de deduplicação e idempotência.

### Etapa 4 — Apache Airflow

Implementar:

- Ambiente Docker Compose.
- DAG de extração e carga.
- Dependências entre tarefas.
- Agendamento diário.
- Logs e tratamento de falhas.
- Retentativas controladas.

### Etapa 5 — Qualidade e integração contínua

Implementar:

- Testes adicionais.
- Validações de qualidade dos dados.
- GitHub Actions.
- Execução automatizada de Pytest e Ruff.
- Documentação das evidências.

### Etapa 6 — Analytics e documentação final

Implementar:

- Consultas SQL analíticas.
- Indicadores meteorológicos.
- Análises comparativas entre cidades.
- Documentação da arquitetura final.
- Evidências de execução.
- README final para portfólio.

---

## 15. Aprendizados técnicos

O desenvolvimento do WeatherFlow permite aplicar conceitos fundamentais de duas áreas complementares.

### Engenharia de Software

- Levantamento de requisitos.
- Organização de projetos Python.
- Separação de responsabilidades.
- Modularização.
- Gerenciamento de dependências.
- Tratamento de exceções.
- Testes unitários e mocks.
- Análise estática e formatação.
- Git, branches e Pull Requests.
- Documentação técnica.

### Engenharia de Dados

- Integração com APIs REST.
- Extração de dados JSON.
- Validação inicial de estruturas.
- Armazenamento de dados brutos.
- Metadados e rastreabilidade.
- Processamento ETL.
- Modelagem relacional.
- Persistência em PostgreSQL.
- Orquestração de pipelines.
- Qualidade e análise de dados.

Os tópicos relacionados a PostgreSQL, Airflow e Analytics serão desenvolvidos nas próximas etapas.

---

## 16. Referências

- [Open-Meteo — Documentação oficial](https://open-meteo.com/en/docs)
- [Python — Documentação oficial](https://docs.python.org/3.12/)
- [Requests — Documentação](https://requests.readthedocs.io/)
- [UV — Documentação](https://docs.astral.sh/uv/)
- [Pytest — Documentação](https://docs.pytest.org/)
- [Ruff — Documentação](https://docs.astral.sh/ruff/)
- [Apache Airflow — Documentação](https://airflow.apache.org/docs/)
- [PostgreSQL — Documentação](https://www.postgresql.org/docs/)
- [GitHub Actions — Documentação](https://docs.github.com/en/actions)

---

## 17. Conclusão

O WeatherFlow demonstra como desenvolver um projeto de Engenharia de Dados de maneira incremental, combinando fundamentos de Engenharia de Software com práticas de construção de pipelines.

A primeira etapa estabeleceu uma base técnica organizada, testada e versionada. A segunda etapa introduz a integração com uma fonte externa de dados, o tratamento de respostas HTTP, a preservação de dados brutos e os testes automatizados com mocks.

As próximas etapas ampliarão a solução com transformação, persistência, orquestração e análises SQL.

**O principal objetivo do projeto não é utilizar o maior número possível de ferramentas, mas compreender como construir um pipeline simples, confiável, testável e sustentável.**

---

## Licença

Licença ainda não definida.