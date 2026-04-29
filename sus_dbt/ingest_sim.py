from pysus.online_data import SIM
import boto3
import glob
import os

BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/tmp/sim_raw'

os.makedirs(DATA_DIR, exist_ok=True)

print("Baixando SIM - Óbitos SP (2018-2024)...")
SIM.download(
    groups='CID10',
    states='SP',
    years=list(range(2018, 2025)),
    data_dir=DATA_DIR
)

print("Enviando para S3...")
s3 = boto3.client('s3')

for arquivo in glob.glob(f'{DATA_DIR}/**/*-0.parquet', recursive=True):
    nome_pasta = os.path.basename(os.path.dirname(arquivo))
    nome_arquivo = os.path.basename(arquivo)
    chave = f'raw/sim/{nome_pasta}/{nome_arquivo}'
    s3.upload_file(arquivo, BUCKET, chave)
    print(f"Enviado: {chave}")

print("Concluído!")
