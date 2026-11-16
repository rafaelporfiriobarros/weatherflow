
-- WeatherFlow
-- Estrutura inicial para previsoes meteorologicas.

CREATE TABLE IF NOT EXISTS weather_forecasts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    city VARCHAR(100) NOT NULL,

    forecast_date DATE NOT NULL,

    collected_at TIMESTAMPTZ NOT NULL,

    temperature_max NUMERIC(6, 2),

    temperature_min NUMERIC(6, 2),

    precipitation_sum NUMERIC(10, 2),

    source VARCHAR(50) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_weather_forecast
        UNIQUE (city, forecast_date, collected_at),

    CONSTRAINT chk_city_not_empty
        CHECK (LENGTH(TRIM(city)) > 0),

    CONSTRAINT chk_temperature_range
        CHECK (
            temperature_min IS NULL
            OR temperature_max IS NULL
            OR temperature_min <= temperature_max
        ),

    CONSTRAINT chk_precipitation_nonnegative
        CHECK (
            precipitation_sum IS NULL
            OR precipitation_sum >= 0
        )
);

CREATE INDEX IF NOT EXISTS idx_weather_city_date
ON weather_forecasts (city, forecast_date);
