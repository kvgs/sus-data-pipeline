{{ config(materialized='view') }}

SELECT
    N_AIH                                    AS numero_aih,
    ESPEC                                    AS especialidade,
    ANO_CMPT                                 AS ano,
    MES_CMPT                                 AS mes,
    CNES                                     AS cnes_hospital,
    MUNIC_RES                                AS cod_municipio_residencia,
    MUNIC_MOV                                AS cod_municipio_internacao,
    SEXO                                     AS sexo,
    TRY_CAST(IDADE AS INT)                   AS idade,
    COD_IDADE                                AS tipo_idade,
    DIAG_PRINC                               AS cid_principal,
    DIAG_SECUN                               AS cid_secundario,
    CID_MORTE                                AS cid_morte,
    PROC_REA                                 AS procedimento_realizado,
    TRY_CAST(DIAS_PERM AS INT)               AS dias_internacao,
    TRY_CAST(MORTE AS INT)                   AS obito,
    TRY_CAST(VAL_TOT AS DOUBLE)              AS valor_total,
    TRY_CAST(VAL_SH AS DOUBLE)               AS valor_servicos_hospitalares,
    TRY_CAST(VAL_SP AS DOUBLE)               AS valor_servicos_profissionais,
    TRY_CAST(UTI_MES_TO AS INT)              AS dias_uti,
    NATUREZA                                 AS natureza_juridica,
    FINANC                                   AS modalidade_financiamento,
    RACA_COR                                 AS raca_cor,
    COMPLEX                                  AS complexidade
FROM {{ source('sus_pipeline', 'sih_sp') }}
WHERE ANO_CMPT IS NOT NULL
