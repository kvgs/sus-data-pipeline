{{ config(materialized='table') }}

SELECT
    ano,
    cod_municipio,
    COUNT(*)                                                        AS total_suicidios,
    COUNT(CASE WHEN sexo = '1' THEN 1 END)                         AS total_masculino,
    COUNT(CASE WHEN sexo = '2' THEN 1 END)                         AS total_feminino,
    COUNT(CASE WHEN metodo_suicidio = 'Enforcamento' THEN 1 END)   AS por_enforcamento,
    COUNT(CASE WHEN metodo_suicidio LIKE 'Disparo%' THEN 1 END)    AS por_arma_fogo,
    COUNT(CASE WHEN metodo_suicidio LIKE 'Envenenamento%' THEN 1 END) AS por_envenenamento,
    COUNT(CASE WHEN metodo_suicidio = 'Salto de lugar elevado' THEN 1 END) AS por_salto
FROM {{ ref('sim_suicidios') }}
WHERE ano IS NOT NULL
GROUP BY ano, cod_municipio
ORDER BY ano, total_suicidios DESC
