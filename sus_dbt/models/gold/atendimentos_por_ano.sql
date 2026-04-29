{{ config(materialized='table') }}

SELECT
    ano,
    cod_municipio,
    COUNT(*)                                            AS total_atendimentos,
    COUNT(DISTINCT cnes_estabelecimento)                AS total_estabelecimentos,
    COUNT(CASE WHEN sexo = 'M' THEN 1 END)             AS total_masculino,
    COUNT(CASE WHEN sexo = 'F' THEN 1 END)             AS total_feminino,
    COUNT(CASE WHEN TRIM(situacao_rua) = 'S' THEN 1 END)        AS total_situacao_rua,
    COUNT(CASE WHEN capitulo_cid = 'F' THEN 1 END)     AS atend_transtorno_mental,
    COUNT(CASE WHEN capitulo_cid = 'Z' THEN 1 END)     AS atend_fatores_sociais,
    COUNT(CASE WHEN TRIM(tipo_droga) != '' 
               AND tipo_droga IS NOT NULL THEN 1 END)           AS atend_uso_drogas
FROM {{ ref('raas_atendimentos') }}
WHERE ano IS NOT NULL
GROUP BY ano, cod_municipio
ORDER BY ano, total_atendimentos DESC
