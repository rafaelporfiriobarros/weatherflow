
# Observabilidade e Qualidade dos Dados — WeatherFlow

## 1. Objetivo

Documentar as verificações de infraestrutura,
orquestração e qualidade dos dados do WeatherFlow.

## 2. Infraestrutura

| Componente | Resultado |
|---|---|
| PostgreSQL 17 | Healthy |
| Apache Airflow | Em execução |
| Docker Compose | Configuração válida |
| DAG weatherflow_daily | Identificada e ativa |
| Erros de importação | Nenhum |

## 3. Orquestração

DAG: `weatherflow_daily`

Tarefas:

1. `extract_weather`
2. `load_weather`

Dependência:

`extract_weather >> load_weather`

Configurações:

- Agendamento diário
- Catchup desabilitado
- Máximo de uma execução ativa
- Duas retentativas por tarefa
- Intervalo de dois minutos entre retentativas

A DAG foi identificada pelo Airflow sem erros
de importação.

A execução mais recente ainda precisa ser
consultada separadamente.

## 4. Qualidade dos dados

| Indicador | Resultado |
|---|---|
| Total de registros | 15 |
| Cidades monitoradas | 3 |
| Curitiba | 5 registros |
| Rio de Janeiro | 5 registros |
| Sao Paulo | 5 registros |
| Chaves duplicadas | 0 |
| Identificações incompletas | 0 |

## 5. Verificações SQL

### Total de registros

```sql
SELECT COUNT(*) AS total_registros
FROM weather_forecasts;
```

Resultado: 15.

### Distribuição por cidade

```sql
SELECT city, COUNT(*) AS total
FROM weather_forecasts
GROUP BY city
ORDER BY city;
```

Resultado:

- Curitiba: 5
- Rio de Janeiro: 5
- Sao Paulo: 5

### Chaves duplicadas

```sql
SELECT
    city,
    forecast_date,
    collected_at,
    COUNT(*) AS quantidade
FROM weather_forecasts
GROUP BY
    city,
    forecast_date,
    collected_at
HAVING COUNT(*) > 1;
```

Resultado: nenhuma linha retornada.

### Identificações incompletas

```sql
SELECT COUNT(*) AS registros_incompletos
FROM weather_forecasts
WHERE city IS NULL
   OR forecast_date IS NULL
   OR collected_at IS NULL;
```

Resultado: 0.

## 6. Qualidade de software

Última validação:

- Pytest: 63 testes aprovados
- Ruff: sem erros
- Docker Compose: configuração válida
- Sintaxe da DAG: aprovada
- Importação da DAG: sem erros

## 7. Limitações

As verificações foram executadas manualmente.

Não há monitoramento contínuo de disponibilidade,
alertas automáticos ou armazenamento histórico
das métricas de qualidade.

Os testes realizados não substituem a validação
dos valores meteorológicos nem a verificação
do sucesso da execução mais recente do Airflow.

## 8. Conclusão

O WeatherFlow possui verificações básicas de
disponibilidade, orquestração e integridade
dos dados.

Os resultados demonstram que a base consultada
não apresenta duplicações da chave composta
nem identificações incompletas.


## 9. Histórico de execuções do Apache Airflow

DAG: `weatherflow_daily`

Consulta realizada em 16/11/2026.

| Tipo | Data lógica (UTC) | Estado |
|---|---|---|
| Manual | 2026-11-16 16:01:42 | success |
| Agendada | 2026-11-15 00:00:00 | success |

### Indicadores de execução

- Total de execuções registradas: 2
- Execuções bem-sucedidas: 2
- Execuções com falha: 0
- Taxa de sucesso observada: 100%

### Duração aproximada

- Execução manual: 12,6 segundos
- Execução agendada: 13,9 segundos

A duração foi calculada pela diferença entre
`start_date` e `end_date`.

### Interpretação

O histórico confirma a conclusão bem-sucedida
de uma execução manual e uma execução agendada.

A data lógica da execução agendada não deve ser
confundida com o horário real de início.

Os resultados representam o histórico consultado,
não uma garantia de disponibilidade futura.
