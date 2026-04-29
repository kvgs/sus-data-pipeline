from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from pysus.online_data.SIH import download, SIH
import glob
import os

# =============================================
# CONFIGURAÇÕES
# =============================================
BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/opt/airflow/data/raw'

default_args = {
    'owner': 'kelli',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# =============================================
# FUNÇÕES
# =============================================
def baixar_dados(**context):
    anos = list(range(2018, 2026))  # 2018 a 2025
    print(f"Baixando dados do DATASUS para os anos {anos}...")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    arquivos = download(
        states='SP',
        years=anos,
        months=list(range(1, 13)),
        groups='RD',
        data_dir=DATA_DIR
    )
    
    print(f"Download concluído! {len(arquivos)} arquivos baixados.")
    return len(arquivos)

def validar_dados(**context):
    print("Validando dados...")
    
    arquivos = glob.glob(f'{DATA_DIR}/*.parquet')
    
    if not arquivos:
        raise ValueError("Nenhum arquivo encontrado para validação!")
    
    total_registros = 0
    for arquivo in arquivos:
        df = pd.read_parquet(arquivo)
        assert len(df) > 0, f"Arquivo vazio: {arquivo}"
        assert 'DIAG_PRINC' in df.columns, f"Coluna DIAG_PRINC ausente em {arquivo}"
        total_registros += len(df)
    
    print(f"Validação concluída! {total_registros:,} registros válidos em {len(arquivos)} arquivos.")
    return total_registros

def salvar_no_s3(**context):
    import boto3
    from airflow.models import Variable
    
    print("Enviando dados para o S3...")
    
    s3 = boto3.client(
        's3',
        aws_access_key_id=Variable.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=Variable.get('AWS_SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    
    enviados = 0
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith('.parquet'):
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, DATA_DIR)
                chave = f'raw/sih/{caminho_relativo}'
                
                s3.upload_file(caminho_completo, BUCKET, chave)
                print(f"Enviado: {chave}")
                enviados += 1
    
    print(f"Concluído! {enviados} arquivos enviados para s3://{BUCKET}/raw/sih/")

# =============================================
# DAG
# =============================================
with DAG(
    dag_id='sus_pipeline',
    description='Pipeline de dados do SUS — DATASUS para S3',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@monthly',
    catchup=False,
    tags=['sus', 'saude', 'datasus'],
) as dag:

    tarefa_download = PythonOperator(
        task_id='baixar_dados_datasus',
        python_callable=baixar_dados,
    )

    tarefa_validacao = PythonOperator(
        task_id='validar_dados',
        python_callable=validar_dados,
    )

    tarefa_s3 = PythonOperator(
        task_id='salvar_no_s3',
        python_callable=salvar_no_s3,
    )

    tarefa_download >> tarefa_validacao >> tarefa_s3