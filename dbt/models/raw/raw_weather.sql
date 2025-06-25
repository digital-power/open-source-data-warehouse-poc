{{ config(
    materialized='table',
    engine='MergeTree()',
    order_by='loaded_at'
) }}

SELECT
    content as json_content,
    now() as loaded_at
FROM s3(
        'https://weather-data-{{ env_var("ENVIRONMENT") }}.s3.fr-par.scw.cloud/weather-data-{{ env_var("ENVIRONMENT")}}/weather/*/*.json',
        '{{ env_var("S3_ACCESS_KEY") }}',
        '{{ env_var("S3_SECRET_KEY") }}',
        'RawBLOB',
        'content String'
     )
WHERE length(content) > 0