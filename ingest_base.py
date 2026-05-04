import boto3
import logging
import os
import time
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

BUCKET_DEFAULT = os.getenv('AWS_S3_BUCKET', 'sus-data-pipeline-kvgs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class IngestBase(ABC):
    """Classe base para scripts de ingestão do pipeline SUS."""

    def __init__(self, nome: str, bucket: str = BUCKET_DEFAULT):
        self.nome = nome
        self.bucket = bucket
        self.s3 = boto3.client('s3')
        self.logger = logging.getLogger(nome)
        self.inicio = None
        self.registros_processados = 0
        self.arquivos_enviados = 0

    def executar(self):
        """Método principal — executa o pipeline completo."""
        self.inicio = time.time()
        self.logger.info(f"Iniciando ingestão: {self.nome}")
        try:
            self.extrair()
            self.transformar()
            self.carregar()
            self._resumo()
        except Exception as e:
            self.logger.error(f"Erro na ingestão: {e}", exc_info=True)
            raise

    @abstractmethod
    def extrair(self):
        pass

    @abstractmethod
    def transformar(self):
        pass

    @abstractmethod
    def carregar(self):
        pass

    def upload_s3(self, path_local: str, chave_s3: str):
        """Envia arquivo para o S3 com retry automático."""
        for tentativa in range(3):
            try:
                self.s3.upload_file(path_local, self.bucket, chave_s3)
                tamanho = os.path.getsize(path_local) / 1024 / 1024
                self.logger.info(
                    f"Enviado: s3://{self.bucket}/{chave_s3} ({tamanho:.1f} MB)"
                )
                self.arquivos_enviados += 1
                return
            except Exception as e:
                if tentativa < 2:
                    self.logger.warning(
                        f"Tentativa {tentativa+1} falhou: {e}. Retentando em 5s..."
                    )
                    time.sleep(5)
                else:
                    self.logger.error(f"Falha após 3 tentativas: {chave_s3}")
                    raise

    def _resumo(self):
        duracao = time.time() - self.inicio
        self.logger.info(
            f"Ingestão concluída | "
            f"registros={self.registros_processados:,} | "
            f"arquivos={self.arquivos_enviados} | "
            f"duração={duracao:.1f}s"
        )