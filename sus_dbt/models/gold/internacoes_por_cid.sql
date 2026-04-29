{{ config(materialized='table') }}

SELECT
    cid_principal,
    ano,
    COUNT(*)                                    AS total_internacoes,
    SUM(obito)                                  AS total_obitos,
    ROUND(SUM(obito) * 100.0 / COUNT(*), 2)    AS taxa_obito_pct,
    ROUND(AVG(valor_total), 2)                  AS valor_medio_internacao,
    ROUND(AVG(
        CASE WHEN dias_internacao > 0 
        THEN dias_internacao END), 1
    )                                           AS media_dias_internacao
FROM {{ ref('sih_internacoes_psiquiatria') }}
WHERE cid_principal IS NOT NULL
GROUP BY cid_principal, ano
ORDER BY total_internacoes DESC
