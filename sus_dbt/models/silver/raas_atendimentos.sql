{{ config(materialized='view') }}

SELECT
    CNES_EXEC                                   AS cnes_estabelecimento,
    UFMUN                                       AS cod_municipio,
    MUNPAC                                      AS cod_municipio_paciente,
    SUBSTR(DT_ATEND, 1, 4)                      AS ano,
    SUBSTR(DT_ATEND, 5, 2)                      AS mes,
    SEXOPAC                                     AS sexo,
    TPIDADEPAC                                  AS tipo_idade,
    TRY_CAST(TRIM(IDADEPAC) AS INT)             AS idade,
    RACACOR                                     AS raca_cor,
    CIDPRI                                      AS cid_principal,
    CIDASSOC                                    AS cid_associado,
    SUBSTR(CIDPRI, 1, 1)                        AS capitulo_cid,
    CATEND                                      AS categoria_atendimento,
    TPUPS                                       AS tipo_estabelecimento,
    TRY_CAST(TRIM(PERMANEN) AS INT)             AS dias_permanencia,
    TRY_CAST(TRIM(QTDATE) AS INT)               AS qtd_atendimentos,
    SIT_RUA                                     AS situacao_rua,
    TP_DROGA                                    AS tipo_droga,
    DESTINOPAC                                  AS destino_paciente,
    ORIGEM_PAC                                  AS origem_paciente
FROM {{ source('sus_pipeline', 'raas_psicossocial') }}
WHERE DT_ATEND IS NOT NULL
