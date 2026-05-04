import requests
import pandas as pd
import os
import time
from ingest_base import IngestBase

class IngestPopulacao(IngestBase):
    """Ingestão de estimativas populacionais IBGE por município SP."""

    def __init__(self):
        super().__init__(nome='ingest_populacao')
        self.ids_municipios = []
        self.df = None
        self.anos = '2015|2016|2017|2018|2019|2020|2021|2022|2023|2024'

    def extrair(self):
        self.logger.info("Buscando municípios de SP na API do IBGE...")
        municipios = requests.get(
            "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"
        ).json()
        self.ids_municipios = [str(m['id']) for m in municipios]
        self.logger.info(f"{len(self.ids_municipios)} municípios encontrados")

    def transformar(self):
        self.logger.info("Buscando estimativas populacionais por ano...")
        resultados = []

        for i in range(0, len(self.ids_municipios), 100):
            lote = ','.join(self.ids_municipios[i:i+100])
            url = (
                f"https://servicodados.ibge.gov.br/api/v3/agregados/6579"
                f"/periodos/{self.anos}/variaveis/9324"
                f"?localidades=N6[{lote}]"
            )
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
            self.logger.info(f"  Lote {i//100 + 1}/{len(self.ids_municipios)//100 + 1} concluído")

        self.df = pd.DataFrame(resultados)
        self.registros_processados = len(self.df)
        self.logger.info(f"{self.registros_processados:,} registros transformados")

    def carregar(self):
        os.makedirs('/tmp/pop_raw', exist_ok=True)
        path = '/tmp/pop_raw/estimativas_populacionais_sp.parquet'
        self.df.to_parquet(path, index=False)
        self.upload_s3(path, 'raw/ibge/populacao/estimativas_populacionais_sp.parquet')


if __name__ == '__main__':
    IngestPopulacao().executar()