"""
DAG principal do pipeline SUS Saúde Mental SP.

Execução mensal — todo dia 10 de cada mês.
Ordem: ingestão → dbt → testes → notificação
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# argumentos padrão para todas as tasks
DEFAULT_ARGS = {
    'owner': 'kelli',
    'depends_on_past': False,
    'email': ['kelli.vgs@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

PIPELINE_DIR = '/home/kellivgs/sus-data-pipeline'
DBT_DIR = f'{PIPELINE_DIR}/sus_dbt'
VENV = '/home/kellivgs/sus-saude-mental-analytics/.venv/bin/python3'

with DAG(
    dag_id='sus_saude_mental_pipeline',
    default_args=DEFAULT_ARGS,
    description='Pipeline mensal de dados de saúde mental SP',
    schedule_interval='0 6 10 * *',  # todo dia 10 às 6h
    start_date=days_ago(1),
    catchup=False,
    tags=['sus', 'saude_mental', 'sp'],
) as dag:

    # ── INGESTÃO ──────────────────────────────────────────────

    ingest_sih = BashOperator(
        task_id='ingest_sih',
        bash_command=f'{VENV} {PIPELINE_DIR}/ingest_sih_historico.py',
        doc_md="Ingere dados do SIH (internações hospitalares) do DATASUS",
    )

    ingest_populacao = BashOperator(
        task_id='ingest_populacao',
        bash_command=f'{VENV} {PIPELINE_DIR}/ingest_populacao.py',
        doc_md="Ingere estimativas populacionais IBGE por município SP",
    )

    ingest_sinan = BashOperator(
        task_id='ingest_sinan_viol',
        bash_command=f'{VENV} {PIPELINE_DIR}/ingest_sinan_viol.py',
        doc_md="Ingere notificações de violência SINAN SP",
    )

    ingest_pnadc = BashOperator(
        task_id='ingest_pnadc',
        bash_command=f'{VENV} {PIPELINE_DIR}/ingest_pnadc.py',
        doc_md="Ingere microdados PNADC SP via BigQuery/Base dos Dados",
    )

    # ── TRANSFORMAÇÃO (dbt) ────────────────────────────────────

    dbt_run_silver = BashOperator(
        task_id='dbt_run_silver',
        bash_command=f'cd {DBT_DIR} && dbt run --select tag:silver',
        doc_md="Roda modelos silver do dbt (limpeza e padronização)",
    )

    dbt_run_gold = BashOperator(
        task_id='dbt_run_gold',
        bash_command=f'cd {DBT_DIR} && dbt run --select tag:gold',
        doc_md="Roda modelos gold do dbt (agregações analíticas)",
    )

    # ── TESTES ────────────────────────────────────────────────

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'cd {DBT_DIR} && dbt test',
        doc_md="Roda testes de qualidade do dbt",
    )

    # ── DOCUMENTAÇÃO ──────────────────────────────────────────

    dbt_docs = BashOperator(
        task_id='dbt_docs_generate',
        bash_command=f'cd {DBT_DIR} && dbt docs generate',
        doc_md="Atualiza documentação dos modelos dbt",
    )

    # ── DEPENDÊNCIAS ──────────────────────────────────────────
    #
    # ingestões paralelas → silver → gold → testes → docs
    #
    #  ingest_sih ──┐
    #  ingest_pop ──┤
    #  ingest_sinan─┼── dbt_silver ── dbt_gold ── dbt_test ── dbt_docs
    #  ingest_pnadc─┘

    [ingest_sih, ingest_populacao, ingest_sinan, ingest_pnadc] >> \
        dbt_run_silver >> dbt_run_gold >> dbt_test >> dbt_docs