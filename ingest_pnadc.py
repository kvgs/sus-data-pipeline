import os
from google.cloud import bigquery
import pandas as pd
import boto3

BUCKET = 'sus-data-pipeline-kvgs'

client = bigquery.Client(project='sus-saude-mental')

print("Baixando microdados PNADC SP 2015-2023...")

query = """
    SELECT
        ano,
        trimestre,
        sigla_uf,
        V2007    AS sexo,
        V2009    AS idade,
        V2010    AS raca_cor,
        VD3004   AS nivel_instrucao,
        VD3005   AS anos_estudo,
        VD4001   AS condicao_forca_trabalho,
        VD4002   AS condicao_ocupacao,
        VD4016   AS renda_trabalho_principal,
        VD4019   AS renda_todos_trabalhos,
        V1022    AS situacao_domicilio,
        V1028    AS peso_amostral
    FROM basedosdados.br_ibge_pnadc.microdados
    WHERE sigla_uf = 'SP'
    AND ano BETWEEN 2015 AND 2023
    AND trimestre = 1
"""

print("Rodando query no BigQuery...")
df = client.query(query).to_dataframe()
print(f"✅ {len(df):,} registros baixados")
print(df.head())

os.makedirs('/tmp/pnadc', exist_ok=True)
path = '/tmp/pnadc/pnadc_sp_2015_2023.parquet'
df.to_parquet(path, index=False)

s3 = boto3.client('s3')
s3.upload_file(path, BUCKET, 'raw/pnadc/pnadc_sp_2015_2023.parquet')
print("✅ Enviado para S3!")