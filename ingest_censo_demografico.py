import os
import boto3
from google.cloud import bigquery
from ingest_base import IngestBase

class IngestCensoDemografico(IngestBase):
    """Ingestão do Censo 2022 - população por município, idade, sexo e raça SP."""

    DATA_DIR = '/tmp/censo2022'

    def __init__(self):
        super().__init__(nome='ingest_censo_demografico')
        self.client = bigquery.Client(project='sus-saude-mental')
        self.df = None

    def extrair(self):
        self.logger.info("Consultando Censo 2022 no BigQuery...")
        query = """
            SELECT
                ano,
                id_municipio,
                grupo_idade,
                sexo,
                cor_raca,
                populacao
            FROM basedosdados.br_ibge_censo_2022.populacao_grupo_idade_sexo_raca
            WHERE LEFT(id_municipio, 2) = '35'
        """
        self.df = self.client.query(query).to_dataframe()
        self.registros_processados = len(self.df)
        self.logger.info(f"{self.registros_processados:,} registros extraídos")

    def transformar(self):
        self.logger.info("Dados prontos — sem transformações adicionais")

    def carregar(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        path = f'{self.DATA_DIR}/populacao_grupo_idade_sexo_raca_sp.parquet'
        self.df.to_parquet(path, index=False)
        self.upload_s3(
            path,
            'raw/censo/populacao_grupo_idade_sexo_raca_sp.parquet'
        )


if __name__ == '__main__':
    IngestCensoDemografico().executar()