{{ config(materialized='view') }}

SELECT
    CNES                                        AS cnes,
    CODUFMUN                                    AS cod_municipio,
    TP_UNID                                     AS tipo_unidade,
    CASE TP_UNID
        WHEN '70' THEN 'CAPS I'
        WHEN '71' THEN 'CAPS II'
        WHEN '72' THEN 'CAPS III'
        WHEN '73' THEN 'CAPS AD'
        WHEN '74' THEN 'CAPS Infantojuvenil'
        WHEN '75' THEN 'CAPS AD III'
        WHEN '77' THEN 'Serviço Saúde Mental'
        WHEN '04' THEN 'Hospital Especializado'
        WHEN '02' THEN 'Hospital Geral'
    END                                         AS descricao_unidade,
    CASE 
        WHEN TP_UNID IN ('70','71','72','73','74','75') THEN 'CAPS'
        WHEN TP_UNID = '77' THEN 'Serviço Mental'
        WHEN TP_UNID IN ('02','04') THEN 'Hospital'
    END                                         AS categoria,
    TPGESTAO                                    AS tipo_gestao,
    ESFERA_A                                    AS esfera_administrativa,
    COMPETEN                                    AS competencia,
    SUBSTR(COMPETEN, 1, 4)                      AS ano,
    SUBSTR(COMPETEN, 5, 2)                      AS mes
FROM {{ source('sus_pipeline', 'cnes_estabelecimentos') }}
WHERE TP_UNID IN ('70','71','72','73','74','75','77','02','04')
