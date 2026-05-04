import pysus
import pandas as pd
import boto3
import glob
import os
from ingest_base import IngestBase

class IngestSIHHistorico(IngestBase):
    """Ingestão histórica do SIH SP 2015-2017."""

    ANOS = list(range(2015, 2018))
    DATA_DIR = '/tmp/sih_historico_new'

    def __init__(self):
        super().__init__(nome='ingest_sih_historico')
        self.files = []

    def extrair(self):
        self.logger.info(f"Buscando arquivos SIH SP {min(self.ANOS)}-{max(self.ANOS)}...")
        sih = pysus.SIH()
        sih.load()
        self.files = sih.get_files(group='RD', uf='SP', year=self.ANOS)
        self.logger.info(f"{len(self.files)} arquivos encontrados. Baixando...")
        os.makedirs(self.DATA_DIR, exist_ok=True)
        sih.download(self.files, local_dir=self.DATA_DIR)
        self.logger.info("Download concluído")

    def transformar(self):
        self.logger.info("Arquivos prontos para upload")

    def carregar(self):
        arquivos = glob.glob(f'{self.DATA_DIR}/**/*-0.parquet', recursive=True)
        self.logger.info(f"{len(arquivos)} arquivos para enviar ao S3")

        for arquivo in arquivos:
            nome_pasta = os.path.basename(os.path.dirname(arquivo))
            nome_arquivo = os.path.basename(arquivo)
            chave = f'raw/sih/{nome_pasta}/{nome_arquivo}'
            try:
                df = pd.read_parquet(arquivo)
                self.registros_processados += len(df)
                self.upload_s3(arquivo, chave)
            except Exception as e:
                self.logger.error(f"Erro em {arquivo}: {e}")


if __name__ == '__main__':
    IngestSIHHistorico().executar()