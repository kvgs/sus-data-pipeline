{{ config(materialized='view') }}

SELECT *
FROM {{ ref('sih_internacoes') }}
WHERE
    especialidade = '05'
    OR SUBSTR(cid_principal, 1, 1) = 'F'
