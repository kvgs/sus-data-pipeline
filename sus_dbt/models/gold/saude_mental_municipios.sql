{{ config(materialized='table') }}

WITH internacoes AS (
    SELECT
        cod_municipio_internacao    AS cod_municipio,
        ano,
        COUNT(*)                   AS total_internacoes,
        SUM(obito)                 AS total_obitos,
        ROUND(AVG(CASE WHEN dias_internacao > 0
            THEN dias_internacao END), 1) AS media_dias_internacao,
        ROUND(AVG(valor_total), 2) AS valor_medio_internacao
    FROM {{ ref('sih_internacoes_psiquiatria') }}
    GROUP BY cod_municipio_internacao, ano
),

atendimentos AS (
    SELECT
        cod_municipio,
        ano,
        SUM(total_atendimentos)    AS total_atendimentos,
        SUM(total_masculino)       AS atend_masculino,
        SUM(total_feminino)        AS atend_feminino,
        SUM(atend_uso_drogas)      AS atend_uso_drogas,
        SUM(total_situacao_rua)    AS atend_situacao_rua
    FROM {{ ref('atendimentos_por_ano') }}
    GROUP BY cod_municipio, ano
),

suicidios AS (
    SELECT
        cod_municipio,
        ano,
        SUM(total_suicidios)       AS total_suicidios,
        SUM(total_masculino)       AS suicidios_masculino,
        SUM(total_feminino)        AS suicidios_feminino
    FROM {{ ref('suicidios_por_ano') }}
    GROUP BY cod_municipio, ano
),

caps AS (
    SELECT
        cod_municipio,
        ano,
        SUM(total_caps)            AS total_caps,
        SUM(total_hospitais)       AS total_hospitais,
        SUM(total_equipamentos)    AS total_equipamentos
    FROM {{ ref('caps_vs_internacoes') }}
    GROUP BY cod_municipio, ano
)

SELECT
    i.cod_municipio,
    i.ano,
    i.total_internacoes,
    i.total_obitos,
    i.media_dias_internacao,
    i.valor_medio_internacao,
    COALESCE(a.total_atendimentos, 0)       AS total_atendimentos_caps,
    COALESCE(a.atend_uso_drogas, 0)         AS atend_uso_drogas,
    COALESCE(a.atend_situacao_rua, 0)       AS atend_situacao_rua,
    COALESCE(s.total_suicidios, 0)          AS total_suicidios,
    COALESCE(s.suicidios_masculino, 0)      AS suicidios_masculino,
    COALESCE(s.suicidios_feminino, 0)       AS suicidios_feminino,
    COALESCE(c.total_caps, 0)               AS total_caps,
    COALESCE(c.total_hospitais, 0)          AS total_hospitais,
    COALESCE(c.total_equipamentos, 0)       AS total_equipamentos,
    -- população por ano (estimativas IBGE)
    pop.municipio,
    COALESCE(pop.populacao, 0)              AS populacao_total,
    -- favelas do censo 2022
    COALESCE(ce.domicilios_favelas, 0)      AS domicilios_favelas,
    COALESCE(ce.pct_domicilios_favelas, 0)  AS pct_domicilios_favelas,
    -- taxas normalizadas por 100k habitantes
    ROUND(
        i.total_internacoes * 100000.0 / NULLIF(pop.populacao, 0), 2
    )                                       AS taxa_internacao_100k,
    ROUND(
        COALESCE(s.total_suicidios, 0) * 100000.0 / NULLIF(pop.populacao, 0), 2
    )                                       AS taxa_suicidio_100k,
    ROUND(
        COALESCE(c.total_caps, 0) * 100000.0 / NULLIF(pop.populacao, 0), 2
    )                                       AS taxa_caps_100k
FROM internacoes i
LEFT JOIN atendimentos a
    ON i.cod_municipio = a.cod_municipio AND i.ano = a.ano
LEFT JOIN suicidios s
    ON i.cod_municipio = s.cod_municipio AND i.ano = s.ano
LEFT JOIN caps c
    ON i.cod_municipio = c.cod_municipio AND i.ano = c.ano
LEFT JOIN {{ ref('ibge_populacao') }} pop
    ON i.cod_municipio = pop.cod_municipio AND i.ano = pop.ano
LEFT JOIN {{ ref('censo_municipios') }} ce
    ON i.cod_municipio = SUBSTR(ce.cod_municipio, 1, 6)
ORDER BY i.ano, i.total_internacoes DESC