{{ config(
    materialized='table',
    engine='SummingMergeTree()',
    order_by=['city_name', 'weather_date'],
    partition_by='toYYYYMM(weather_date)'
) }}

WITH source_data AS (
    SELECT
        city_name,
        weather_date,
        temperature_celsius,
        wind_speed_ms,
        precipitation_mm
    FROM {{ ref('stg_weather') }}
)

SELECT
    city_name,
    weather_date,

    -- Temperature statistics
    min(temperature_celsius) AS min_temperature,
    max(temperature_celsius) AS max_temperature,
    avg(temperature_celsius) AS avg_temperature,

    -- Wind speed statistics
    min(wind_speed_ms) AS min_wind_speed,
    max(wind_speed_ms) AS max_wind_speed,
    avg(wind_speed_ms) AS avg_wind_speed,

    -- Precipitation statistics
    sum(precipitation_mm) AS total_precipitation,
    avg(precipitation_mm) AS avg_precipitation

FROM source_data
GROUP BY
    city_name,
    weather_date
