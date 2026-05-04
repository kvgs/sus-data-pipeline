"""
Monitor de qualidade dos dados do pipeline SUS Saúde Mental SP.
Verifica anomalias e inconsistências após cada ingestão.
"""

import boto3
import pandas as pd
from pyathena import connect
from pyathena.pandas.cursor import PandasCursor
from ingest_base import IngestBase

REGION = 'us-east-1'
S3_STAGING = 's3://sus-data-pipeline-kvgs/athena-results/'
DATABASE = 'sus_pipeline'


def query(sql: str) -> pd.DataFrame:
    conn = connect(
        region_name=REGION,
        s3_staging_dir=S3_STAGING,
        schema_name=DATABASE,
        cursor_class=PandasCursor
    )
    return conn.cursor().execute(sql).as_pandas()


class MonitorQualidade:
    """Verifica qualidade e anomalias nos dados do pipeline."""

    def __init__(self):
        self.alertas = []
        self.logger = __import__('logging').getLogger('monitor_qualidade')
        __import__('logging').basicConfig(
            level=__import__('logging').INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )

    def verificar_tudo(self):
        self.logger.info("Iniciando verificação de qualidade...")
        self.verifica_internacoes()
        self.verifica_suicidios()
        self.verifica_violencia()
        self.verifica_populacao()
        self.relatorio()

    def verifica_internacoes(self):
        self.logger.info("Verificando internações...")
        df = query("""
            SELECT ano, total_internacoes
            FROM sus_pipeline.internacoes_por_ano
            ORDER BY ano
        """)

        # verifica se há anos faltando
        anos_esperados = set(str(a) for a in range(2015, 2026))
        anos_presentes = set(df['ano'].astype(str))
        faltando = anos_esperados - anos_presentes
        if faltando:
            self.alertas.append(f"⚠️ INTERNAÇÕES: anos faltando — {sorted(faltando)}")

        # verifica queda brusca (>50% em relação à média)
        media = df['total_internacoes'].astype(float).mean()
        for _, row in df.iterrows():
            if float(row['total_internacoes']) < media * 0.5:
                self.alertas.append(
                    f"⚠️ INTERNAÇÕES: ano {row['ano']} muito abaixo da média "
                    f"({row['total_internacoes']:,} vs média {media:,.0f})"
                )

        self.logger.info(f"  {len(df)} anos verificados")

    def verifica_suicidios(self):
        self.logger.info("Verificando suicídios...")
        df = query("""
            SELECT ano, SUM(total_suicidios) as total
            FROM sus_pipeline.suicidios_por_ano
            GROUP BY ano ORDER BY ano
        """)

        # verifica se total é razoável (entre 1k e 5k por ano)
        for _, row in df.iterrows():
            total = float(row['total'])
            if total < 1000 or total > 5000:
                self.alertas.append(
                    f"⚠️ SUICÍDIOS: ano {row['ano']} fora do intervalo esperado "
                    f"({total:,.0f} — esperado entre 1.000 e 5.000)"
                )

        self.logger.info(f"  {len(df)} anos verificados")

    def verifica_violencia(self):
        self.logger.info("Verificando violência SINAN...")
        df = query("""
            SELECT ano, total_notificacoes
            FROM sus_pipeline.violencia_por_ano
            ORDER BY ano
        """)

        # verifica anos faltando
        anos_esperados = set(str(a) for a in range(2015, 2026))
        anos_presentes = set(df['ano'].astype(str))
        faltando = anos_esperados - anos_presentes
        if faltando:
            self.alertas.append(f"⚠️ VIOLÊNCIA: anos faltando — {sorted(faltando)}")

        self.logger.info(f"  {len(df)} anos verificados")

    def verifica_populacao(self):
        self.logger.info("Verificando população...")
        df = query("""
            SELECT ano, COUNT(DISTINCT cod_municipio) as municipios
            FROM sus_pipeline.ibge_populacao
            GROUP BY ano ORDER BY ano
        """)

        # verifica se todos os anos têm 645 municípios
        for _, row in df.iterrows():
            if int(row['municipios']) < 600:
                self.alertas.append(
                    f"⚠️ POPULAÇÃO: ano {row['ano']} com poucos municípios "
                    f"({row['municipios']} — esperado 645)"
                )

        self.logger.info(f"  {len(df)} anos verificados")

    def relatorio(self):
        print("\n" + "="*60)
        print("RELATÓRIO DE QUALIDADE DOS DADOS")
        print("="*60)
        if not self.alertas:
            print("✅ Nenhuma anomalia detectada — dados OK!")
        else:
            print(f"⚠️ {len(self.alertas)} alertas encontrados:\n")
            for alerta in self.alertas:
                print(f"  {alerta}")
        print("="*60)


if __name__ == '__main__':
    MonitorQualidade().verificar_tudo()