{{ config(materialized='view') }}

SELECT
    CONTADOR                                        AS id_obito,
    CAUSABAS                                        AS cid_causa,
    SUBSTR(DTOBITO, 5, 4)                           AS ano,
    SUBSTR(DTOBITO, 3, 2)                           AS mes,
    TRIM(CODMUNOCOR)                                AS cod_municipio,
    SEXO                                            AS sexo,
    IDADE                                           AS idade_raw,
    RACACOR                                         AS raca_cor,
    LOCOCOR                                         AS local_obito,
    CIRCOBITO                                       AS circunstancia,
    CASE CAUSABAS
        WHEN 'X600' THEN 'Envenenamento - analgésicos'
        WHEN 'X610' THEN 'Envenenamento - anticonvulsivantes'
        WHEN 'X620' THEN 'Envenenamento - narcóticos'
        WHEN 'X630' THEN 'Envenenamento - outras drogas'
        WHEN 'X640' THEN 'Envenenamento - medicamentos'
        WHEN 'X700' THEN 'Enforcamento'
        WHEN 'X701' THEN 'Enforcamento'
        WHEN 'X709' THEN 'Enforcamento - NE'
        WHEN 'X720' THEN 'Disparo - arma curta'
        WHEN 'X740' THEN 'Disparo - arma longa'
        WHEN 'X780' THEN 'Objeto cortante'
        WHEN 'X800' THEN 'Salto de lugar elevado'
        WHEN 'X804' THEN 'Salto de lugar elevado'
        WHEN 'X840' THEN 'Outros meios'
        ELSE 'Outros'
    END                                             AS metodo_suicidio
FROM {{ source('sus_pipeline', 'sim_obitos') }}
WHERE 
    SUBSTR(CAUSABAS, 1, 1) = 'X'
    AND TRY_CAST(SUBSTR(CAUSABAS, 2, 2) AS INT) BETWEEN 60 AND 84
