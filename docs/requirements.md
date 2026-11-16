
# WeatherFlow - Requisitos

## 1. Contexto

O WeatherFlow automatiza a coleta e a persistencia de
dados meteorologicos para consultas analiticas.

## 2. Escopo

Cidades iniciais:
- Sao Paulo
- Rio de Janeiro
- Curitiba

Fonte planejada:
- Open-Meteo API

## 3. Requisitos funcionais

- RF01: Consultar dados de uma API publica.
- RF02: Validar e transformar os registros.
- RF03: Armazenar dados no PostgreSQL.
- RF04: Orquestrar o pipeline com Airflow.
- RF05: Disponibilizar consultas SQL analiticas.

## 4. Requisitos nao funcionais

- RNF01: Python 3.12.
- RNF02: Codigo modular e testavel.
- RNF03: Segredos fora do Git.
- RNF04: Carga sem duplicacoes.
- RNF05: Logs de execucao e erros.
- RNF06: Testes e analise estatica automatizados.
- RNF07: Documentacao de instalacao e uso.

## 5. Fora do escopo

- Kafka e processamento em tempo real.
- Spark e processamento distribuido.
- Kubernetes.
- Infraestrutura cloud.
- Dashboard web.
- Machine Learning.

## 6. Criterios de aceite da Etapa 1

- Projeto Python inicializado com UV.
- Configuracao de cidades implementada.
- Nove testes automatizados aprovados.
- Ruff sem erros.
- Documentacao inicial criada.
- Repositorio Git inicializado.
