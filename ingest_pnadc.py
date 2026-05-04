import os
import boto3
from google.cloud import bigquery
from ingest_base import IngestBase

class IngestPNADC(IngestBase):
    """Ingestão de microdados PNADC SP 2015-2023 via BigQuery/Base dos Dados."""

    DATA_DIR = '/tmp/pnadc'
    ANOS = '2015 AND 2023'

    def __init__(self):
        super().__init__(nome='ingest_pnadc')
        self.client = bigquery.Client(project='sus-saude-mental')
        self.df = None

    def extrair(self):
        self.logger.info("Consultando microdados PNADC SP no BigQuery...")
        query = f"""
            SELECT
                ano, trimestre, sigla_uf,
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
            AND ano BETWEEN {self.ANOS}
            AND trimestre = 1
        """
        self.df = self.client.query(query).to_dataframe()
        self.registros_processados = len(self.df)
        self.logger.info(f"{self.registros_processados:,} registros extraídos")

    def transformar(self):
        self.logger.info("Dados prontos — sem transformações adicionais")

    def carregar(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)
        path = f'{self.DATA_DIR}/pnadc_sp_2015_2023.parquet'
        self.df.to_parquet(path, index=False)
        self.upload_s3(path, 'raw/pnadc/pnadc_sp_2015_2023.parquet')


if __name__ == '__main__':
    IngestPNADC().executar()