from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# =============================================
# CONFIGURAÇÕES DA DAG
# =============================================
default_args = {
    'owner': 'kelli',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# =============================================
# FUNÇÕES — o que cada tarefa vai fazer
# =============================================
def baixar_dados():
    print("Baixando dados do DATASUS...")
    # aqui vai o código do PySUS
    print("Download concluído!")

def validar_dados():
    print("Validando dados...")
    # aqui vão as verificações de qualidade
    print("Validação concluída!")

def salvar_no_s3():
    print("Salvando no S3...")
    # aqui vai o código do boto3
    print("Dados salvos no S3!")

# =============================================
# DEFINIÇÃO DA DAG
# =============================================
with DAG(
    dag_id='sus_pipeline',
    description='Pipeline de dados do SUS — DATASUS para S3',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval='@monthly',
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

    # define a ordem de execução
    tarefa_download >> tarefa_validacao >> tarefa_s3