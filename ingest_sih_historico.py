import pysus
import boto3
import glob
import os

BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/tmp/sih_historico'

os.makedirs(DATA_DIR, exist_ok=True)

print("Buscando arquivos SIH SP 2015-2017...")
sih = pysus.SIH()
sih.load()
files = sih.get_files(group='RD', uf='SP', year=list(range(2015, 2018)))
print(f"{len(files)} arquivos encontrados. Baixando...")

sih.download(files, local_dir=DATA_DIR)

print("Enviando para S3...")
s3 = boto3.client('s3')

for arquivo in glob.glob(f'{DATA_DIR}/**/*-0.parquet', recursive=True):
    nome_pasta = os.path.basename(os.path.dirname(arquivo))
    nome_arquivo = os.path.basename(arquivo)
    chave = f'raw/sih/{nome_pasta}/{nome_arquivo}'
    s3.upload_file(arquivo, BUCKET, chave)
    print(f"Enviado: {chave}")

print("Concluído!")