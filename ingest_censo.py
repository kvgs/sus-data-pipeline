import requests
import pandas as pd
import boto3
import time
import os

BUCKET = 'sus-data-pipeline-kvgs'

print("Buscando municípios de SP...")
municipios = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios").json()
ids = [str(m['id']) for m in municipios]
print(f"{len(ids)} municípios encontrados.")

def buscar_tabela(tabela, variavel, descricao):
    print(f"Buscando {descricao}...")
    resultados = []
    for i in range(0, len(ids), 100):
        lote = ','.join(ids[i:i+100])
        url = f"https://servicodados.ibge.gov.br/api/v3/agregados/{tabela}/periodos/2022/variaveis/{variavel}?localidades=N6[{lote}]"
        r = requests.get(url)
        if r.status_code == 200:
            for var in r.json():
                for idx, resultado in enumerate(var.get('resultados', [])):
                    cats = {}
                    for c in resultado.get('classificacoes', []):
                        # nome limpo: sem acentos, espaços viram underscore
                        nome_limpo = c['nome'].lower()
                        nome_limpo = nome_limpo.replace(' ', '_').replace('/', '_').replace('ã', 'a').replace('ç', 'c').replace('é', 'e').replace('ó', 'o').replace('ê', 'e').replace('ú', 'u').replace('á', 'a').replace('í', 'i')
                        nome_limpo = f"cat_{nome_limpo[:30]}"
                        cats[nome_limpo] = list(c['categoria'].values())[0]
                    for serie in resultado.get('series', []):
                        loc = serie['localidade']
                        valor = serie['serie'].get('2022')
                        row = {
                            'cod_municipio': loc['id'],
                            'municipio': loc['nome'],
                            'variavel': descricao,
                            'valor': valor
                        }
                        row.update(cats)
                        resultados.append(row)
        time.sleep(0.3)
    return resultados

pop_raca = buscar_tabela('9605', '93', 'populacao_raca_cor')
instrucao = buscar_tabela('9517', '1641', 'instrucao_14_mais')
favelas = buscar_tabela('9892', '9913', 'domicilios_favelas')

os.makedirs('/tmp/censo_raw', exist_ok=True)
s3 = boto3.client('s3')

for dados, nome in [(pop_raca, 'pop_raca_cor'), (instrucao, 'instrucao'), (favelas, 'favelas')]:
    df = pd.DataFrame(dados)
    print(f"{nome}: {len(df)} registros — colunas: {df.columns.tolist()}")
    path = f'/tmp/censo_raw/censo_{nome}_sp.parquet'
    df.to_parquet(path, index=False)
    s3.upload_file(path, BUCKET, f'raw/censo/{nome}/censo_{nome}_sp.parquet')
    print(f"Enviado: raw/censo/{nome}/censo_{nome}_sp.parquet")

print("Concluído!")