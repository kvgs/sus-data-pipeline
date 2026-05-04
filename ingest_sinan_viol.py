import pysus
import pandas as pd
import boto3
import glob
import os
from ingest_base import IngestBase

class IngestSinanViol(IngestBase):
    """Ingestão de notificações de violência SINAN SP 2015-2025."""

    COLUNAS = [
        'NU_ANO', 'DT_NOTIFIC', 'SG_UF_NOT', 'ID_MUNICIP',
        'ID_MN_RESI', 'SG_UF', 'DT_OCOR',
        'CS_SEXO', 'CS_RACA', 'NU_IDADE_N', 'CS_GESTANT',
        'VIOL_FISIC', 'VIOL_PSICO', 'VIOL_SEXU', 'VIOL_TORT',
        'VIOL_NEGLI', 'VIOL_OUTR', 'LES_AUTOP',
        'CONS_SUIC', 'CONS_MENT', 'CIRC_LESAO',
        'AUTOR_SEXO', 'AUTOR_ALCO',
        'REL_CONJ', 'REL_EXCON', 'REL_PAI', 'REL_MAE',
        'LOCAL_OCOR', 'OUT_VEZES',
        'EVOLUCAO', 'CLASSI_FIN',
        'ORIENT_SEX', 'IDENT_GEN', 'VIOL_MOTIV'
    ]
    ANOS = list(range(2015, 2026))
    DATA_DIR = '/tmp/sinan_viol_new'

    def __init__(self):
        super().__init__(nome='ingest_sinan_viol')
        self.files = []

    def extrair(self):
        self.logger.info(f"Buscando arquivos SINAN VIOL {min(self.ANOS)}-{max(self.ANOS)}...")
        sinan = pysus.SINAN()
        sinan.load()
        self.files = sinan.get_files(dis_code='VIOL', year=self.ANOS)
        self.logger.info(f"{len(self.files)} arquivos encontrados. Baixando...")
        os.makedirs(self.DATA_DIR, exist_ok=True)
        sinan.download(self.files, local_dir=self.DATA_DIR)
        self.logger.info("Download concluído")

    def transformar(self):
        self.logger.info("Filtrando SP e preparando arquivos...")

    def carregar(self):
        arquivos = glob.glob(f'{self.DATA_DIR}/**/*-0.parquet', recursive=True)
        self.logger.info(f"{len(arquivos)} arquivos para processar")

        for arquivo in arquivos:
            nome_pasta = os.path.basename(os.path.dirname(arquivo))
            try:
                df = pd.read_parquet(arquivo)
                df_sp = df[df['SG_UF_NOT'] == '35'].copy()
                cols_disp = [c for c in self.COLUNAS if c in df_sp.columns]
                df_sp = df_sp[cols_disp]

                if len(df_sp) == 0:
                    continue

                path_out = f'/tmp/sinan_viol_sp_new/{nome_pasta}'
                os.makedirs(path_out, exist_ok=True)
                nome_arquivo = os.path.basename(arquivo)
                path_parquet = f'{path_out}/{nome_arquivo}'
                df_sp.to_parquet(path_parquet, index=False)

                chave = f'raw/sinan/viol/{nome_pasta}/{nome_arquivo}'
                self.upload_s3(path_parquet, chave)
                self.registros_processados += len(df_sp)

            except Exception as e:
                self.logger.error(f"Erro em {arquivo}: {e}")


if __name__ == '__main__':
    IngestSinanViol().executar()