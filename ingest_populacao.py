import requests
import pandas as pd
import boto3
import time
import os

BUCKET = 'sus-data-pipeline-kvgs'

print("Buscando municípios de SP...")
municipios = requests.get(
    "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"
).json()
ids = [str(m['id']) for m in municipios]
print(f"{len(ids)} municípios encontrados.")

anos = '2015|2016|2017|2018|2019|2020|2021|2022|2023|2024'
resultados = []

print("Buscando estimativas populacionais por ano...")
for i in range(0, len(ids), 100):
    lote = ','.join(ids[i:i+100])
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/{anos}/variaveis/9324?localidades=N6[{lote}]"
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        for var in r.json():
            for resultado in var.get('resultados', []):
                for serie in resultado.get('series', []):
                    loc = serie['localidade']
                    for ano, pop in serie['serie'].items():
                        if pop:
                            resultados.append({
                                'cod_municipio': loc['id'],
                                'municipio': loc['nome'].replace(' (SP)', ''),
                                'ano': ano,
                                'populacao_estimada': pop
                            })
    time.sleep(0.3)
    print(f"  Lote {i//100 + 1}/{len(ids)//100 + 1} concluído...")

df = pd.DataFrame(resultados)
print(f"\nTotal: {len(df)} registros")
print(df.head())

os.makedirs('/tmp/pop_raw', exist_ok=True)
path = '/tmp/pop_raw/estimativas_populacionais_sp.parquet'
df.to_parquet(path, index=False)

s3 = boto3.client('s3')
s3.upload_file(path, BUCKET, 'raw/ibge/populacao/estimativas_populacionais_sp.parquet')
print("✅ Enviado para S3!")