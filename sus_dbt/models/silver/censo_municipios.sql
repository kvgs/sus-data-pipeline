{{ config(materialized='view') }}

WITH populacao AS (
    SELECT
        cod_municipio,
        REGEXP_REPLACE(municipio, ' \(SP\)$', '')   AS municipio,
        TRY_CAST(valor AS INT)                       AS populacao_total
    FROM {{ source('sus_pipeline', 'censo_populacao') }}
),

favelas AS (
    SELECT
        cod_municipio,
        TRY_CAST(valor AS INT)                       AS domicilios_favelas
    FROM {{ source('sus_pipeline', 'censo_favelas') }}
    WHERE cat_existencia_de_banheiro_ou_sani = 'Total'
    AND cat_tipo_de_esgotamento_sanitario = 'Total'
)

SELECT
    p.cod_municipio,
    p.municipio,
    p.populacao_total,
    COALESCE(f.domicilios_favelas, 0)                               AS domicilios_favelas,
    ROUND(
        f.domicilios_favelas * 100.0 / NULLIF(p.populacao_total, 0), 2
    )                                                               AS pct_domicilios_favelas
FROM populacao p
LEFT JOIN favelas f ON p.cod_municipio = f.cod_municipio