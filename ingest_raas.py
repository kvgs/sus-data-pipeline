import pysus
import boto3
import glob
import os

BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/tmp/raas_raw'

os.makedirs(DATA_DIR, exist_ok=True)

print("Buscando arquivos RAAS Psicossocial SP (2018-2025)...")
sia = pysus.SIA()
sia.load()
files = sia.get_files(group='PS', uf='SP', year=list(range(2018, 2026)))
print(f"{len(files)} arquivos encontrados. Baixando...")

sia.download(files, local_dir=DATA_DIR)

print("Enviando para S3...")
s3 = boto3.client('s3')

for arquivo in glob.glob(f'{DATA_DIR}/**/*-0.parquet', recursive=True):
    nome_pasta = os.path.basename(os.path.dirname(arquivo))
    nome_arquivo = os.path.basename(arquivo)
    chave = f'raw/raas/{nome_pasta}/{nome_arquivo}'
    s3.upload_file(arquivo, BUCKET, chave)
    print(f"Enviado: {chave}")

print("Concluído!")
