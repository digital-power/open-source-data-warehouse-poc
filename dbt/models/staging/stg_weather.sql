{{ config(
    materialized='incremental',
    engine='MergeTree()',
    order_by='weather_date',
    partition_by='toYYYYMM(weather_date)'
) }}

WITH source_data AS (
    SELECT
        json_content,
        loaded_at
    FROM {{ ref('raw_weather') }}
    {% if is_incremental() %}
    WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})
    {% endif %}
)

SELECT
    JSONExtractString(json_content, 'location', 'city') AS city_name,
    JSONExtractFloat(json_content, 'location', 'coordinates', 'lat') AS latitude,
    JSONExtractFloat(json_content, 'location', 'coordinates', 'lon') AS longitude,
    parseDateTimeBestEffort(JSONExtractString(json_content, 'weather_data', 'hourly', 'time', 1)) AS weather_datetime,
    toDate(parseDateTimeBestEffort(JSONExtractString(json_content, 'weather_data', 'hourly', 'time', 1))) AS weather_date,
    toHour(parseDateTimeBestEffort(JSONExtractString(json_content, 'weather_data', 'hourly', 'time', 1))) AS weather_hour,
    JSONExtractFloat(json_content, 'weather_data', 'hourly', 'temperature_2m', 1) AS temperature_celsius,
    JSONExtractFloat(json_content, 'weather_data', 'hourly', 'precipitation', 1) AS precipitation_mm,
    JSONExtractFloat(json_content, 'weather_data', 'hourly', 'windspeed_10m', 1) AS wind_speed_ms,
    loaded_at
FROM source_data
