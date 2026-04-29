{{ config(materialized='table') }}

WITH caps_por_municipio AS (
    SELECT
        cod_municipio,
        ano,
        COUNT(CASE WHEN categoria = 'CAPS' THEN 1 END)           AS total_caps,
        COUNT(CASE WHEN categoria = 'Hospital' THEN 1 END)        AS total_hospitais,
        COUNT(CASE WHEN categoria = 'Serviço Mental' THEN 1 END)  AS total_servicos_mental,
        COUNT(*)                                                   AS total_equipamentos
    FROM {{ ref('cnes_saude_mental') }}
    WHERE mes = '12'
    GROUP BY cod_municipio, ano
),

internacoes_por_municipio AS (
    SELECT
        cod_municipio_internacao                                   AS cod_municipio,
        ano,
        COUNT(*)                                                   AS total_internacoes,
        SUM(obito)                                                 AS total_obitos,
        ROUND(AVG(
            CASE WHEN dias_internacao > 0 
            THEN dias_internacao END), 1
        )                                                          AS media_dias_internacao,
        ROUND(AVG(valor_total), 2)                                 AS valor_medio_internacao
    FROM {{ ref('sih_internacoes_psiquiatria') }}
    GROUP BY cod_municipio_internacao, ano
)

SELECT
    i.cod_municipio,
    i.ano,
    i.total_internacoes,
    i.total_obitos,
    i.media_dias_internacao,
    i.valor_medio_internacao,
    COALESCE(c.total_caps, 0)               AS total_caps,
    COALESCE(c.total_hospitais, 0)          AS total_hospitais,
    COALESCE(c.total_servicos_mental, 0)    AS total_servicos_mental,
    COALESCE(c.total_equipamentos, 0)       AS total_equipamentos
FROM internacoes_por_municipio i
LEFT JOIN caps_por_municipio c
    ON i.cod_municipio = c.cod_municipio
    AND i.ano = c.ano
ORDER BY i.total_internacoes DESC
