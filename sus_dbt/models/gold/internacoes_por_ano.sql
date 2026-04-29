{{ config(materialized='table') }}

SELECT
    ano,
    COUNT(*)                                        AS total_internacoes,
    SUM(obito)                                      AS total_obitos,
    ROUND(
        SUM(obito) * 100.0 / COUNT(*), 2
    )                                               AS taxa_obito_pct,
    ROUND(AVG(
        CASE WHEN dias_internacao > 0 
        THEN dias_internacao END), 1
    )                                               AS media_dias_internacao,
    ROUND(AVG(valor_total), 2)                      AS valor_medio_internacao,
    ROUND(SUM(valor_total), 2)                      AS valor_total_internacoes,
    SUM(dias_uti)                                   AS total_dias_uti,
    COUNT(CASE WHEN sexo = '1' THEN 1 END)          AS total_masculino,
    COUNT(CASE WHEN sexo = '3' THEN 1 END)          AS total_feminino
FROM {{ ref('sih_internacoes') }}
GROUP BY ano
ORDER BY ano