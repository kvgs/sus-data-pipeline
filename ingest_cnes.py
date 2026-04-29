from pysus.online_data import CNES
import boto3
import glob
import os

BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/tmp/cnes_raw'

os.makedirs(DATA_DIR, exist_ok=True)

print("Baixando CNES - Estabelecimentos SP (2018-2025)...")
CNES.download(
    group='ST',
    states='SP',
    years=list(range(2018, 2026)),
    months=[12],
    data_dir=DATA_DIR
)

print("Enviando para S3...")
s3 = boto3.client('s3')

# busca arquivos dentro das subpastas
for arquivo in glob.glob(f'{DATA_DIR}/**/*-0.parquet', recursive=True):
    nome_pasta = os.path.basename(os.path.dirname(arquivo))
    nome_arquivo = os.path.basename(arquivo)
    chave = f'raw/cnes/{nome_pasta}/{nome_arquivo}'
    s3.upload_file(arquivo, BUCKET, chave)
    print(f"Enviado: {chave}")

print("Concluído!")
