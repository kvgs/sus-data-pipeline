# 🧠 Pipeline de Dados em Saúde Mental — SUS/SP

Pipeline completo de engenharia de dados para análise de saúde mental no estado de São Paulo, integrando quatro fontes do DATASUS em uma arquitetura moderna com AWS e dbt.

## 🏗️ Arquitetura

```
DATASUS (SIH + CNES + SIM + RAAS)
           ↓
     Python + PySUS
    (ingestão automatizada)
           ↓
     AWS S3 (data lake)
    raw/sih/ | raw/cnes/ | raw/sim/ | raw/raas/
           ↓
     AWS Athena
    (tabelas externas sobre parquet)
           ↓
     dbt (transformação)
    silver: limpeza e padronização
    gold: agregações e cruzamentos
```

## 📊 Fontes de Dados

| Dataset | Descrição | Período | Volume |
|---------|-----------|---------|--------|
| **SIH/DATASUS** | Internações hospitalares psiquiátricas | 2018–2026 | ~830k internações |
| **CNES** | Estabelecimentos de saúde mental (CAPS, hospitais) | 2018–2025 | snapshot anual |
| **SIM** | Óbitos por suicídio (CID X60–X84) | 2018–2024 | ~18k óbitos |
| **RAAS Psicossocial** | Atendimentos ambulatoriais nos CAPS | 2018–2025 | ~33M atendimentos |

## 🗂️ Modelos dbt

### Silver (limpeza e padronização)
- `sih_internacoes` — internações hospitalares SP (todas)
- `sih_internacoes_psiquiatria` — filtrado por ESPEC=05 ou CID F
- `cnes_saude_mental` — estabelecimentos de saúde mental categorizados
- `sim_suicidios` — óbitos por suicídio com método classificado
- `raas_atendimentos` — atendimentos ambulatoriais psicossociais

### Gold (tabelas analíticas)
- `internacoes_por_ano` — internações psiquiátricas agregadas por ano
- `internacoes_por_cid` — internações por diagnóstico e ano
- `atendimentos_por_ano` — atendimentos CAPS por município e ano
- `suicidios_por_ano` — óbitos por suicídio por município e ano
- `caps_vs_internacoes` — infraestrutura vs volume de internações
- `saude_mental_municipios` — **cruzamento completo** dos 4 datasets por município e ano

## 🔍 Principais Achados

- **Queda de 28% nas internações em 2020** — serviços fecharam durante a pandemia
- **2021: pico de óbitos** com 183k mortes — o pior ano da pandemia
- **Média de internação psiquiátrica caiu** de 18.9 para 14.7 dias (2018–2026) — tendência de desinstitucionalização
- **33M atendimentos ambulatoriais** em 2018–2025, com crescimento de 35% no período
- **~4% dos atendimentos nos CAPS** são de pessoas em situação de rua
- **Suicídio cresceu 32%** entre 2018 e 2022, com pico pós-pandemia

## 🛠️ Stack Tecnológica

- **Linguagem:** Python (PySUS, boto3, pandas)
- **Cloud:** AWS (S3, Athena, IAM)
- **Transformação:** dbt-athena
- **Orquestração:** Apache Airflow (Docker)
- **Versionamento:** Git/GitHub

## 🚀 Como Reproduzir

### Pré-requisitos
- Python 3.12+
- AWS CLI configurado
- Conta AWS com acesso a S3 e Athena
- WSL2 (Windows) ou Linux

### Instalação

```bash
git clone https://github.com/kvgs/sus-data-pipeline
cd sus-data-pipeline
pip install pysus boto3 pandas dbt-athena-community
```

### Ingestão

```bash
python3 ingest_sih.py    # SIH - internações
python3 ingest_cnes.py   # CNES - estabelecimentos
python3 ingest_sim.py    # SIM - óbitos
python3 ingest_raas.py   # RAAS - atendimentos
```

### Transformação

```bash
cd sus_dbt
dbt run
```

## 📁 Estrutura do Projeto

```
sus-data-pipeline/
├── dags/                    # DAGs do Airflow
├── sus_dbt/                 # Projeto dbt
│   ├── models/
│   │   ├── silver/          # Limpeza e padronização
│   │   └── gold/            # Tabelas analíticas
├── ingest_sih.py
├── ingest_cnes.py
├── ingest_sim.py
├── ingest_raas.py
└── README.md
```