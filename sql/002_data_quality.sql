
-- WeatherFlow
-- Relatorio de qualidade dos dados meteorologicos

WITH duplicados AS (
    SELECT COUNT(*) AS total
    FROM (
        SELECT city, forecast_date, collected_at
        FROM weather_forecasts
        GROUP BY city, forecast_date, collected_at
        HAVING COUNT(*) > 1
    ) AS grupos_duplicados
),
qualidade AS (
    SELECT
        COUNT(*) AS total_registros,
        COUNT(DISTINCT city) AS cidades_monitoradas,
        COUNT(*) FILTER (
            WHERE city IS NULL
               OR forecast_date IS NULL
               OR collected_at IS NULL
        ) AS registros_incompletos
    FROM weather_forecasts
)
SELECT
    q.total_registros,
    q.cidades_monitoradas,
    d.total AS chaves_duplicadas,
    q.registros_incompletos
FROM qualidade q
CROSS JOIN duplicados d;
