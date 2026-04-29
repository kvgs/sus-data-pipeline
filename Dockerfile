FROM apache/airflow:2.8.1-python3.10

USER root

RUN apt-get update && \
    apt-get install -y gcc build-essential && \
    apt-get clean

USER airflow

RUN pip install --no-cache-dir \
    "numpy<2" \
    "pyarrow<13" \
    pysus==1.0.1 \
    boto3 \
    awswrangler \
    pandas