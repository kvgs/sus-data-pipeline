# 🧠 Pipeline de Dados em Saúde Mental — SUS/SP

Pipeline completo de engenharia de dados para análise de saúde mental no estado de São Paulo, integrando nove fontes de dados públicos em uma arquitetura moderna com AWS S3, Athena e dbt.

> **Repositório de análise:** [sus-saude-mental-analytics](https://github.com/kvgs/sus-saude-mental-analytics) — notebooks de análise exploratória, estatística e equidade que consomem os dados deste pipeline.

## 🏗️ Arquitetura
```
DATASUS + IBGE + SINAN + BigQuery/Base dos Dados
↓
Python (PySUS, requests, google-cloud-bigquery)
scripts de ingestão padronizados com IngestBase
↓
AWS S3 (data lake)
raw/sih/ · raw/cnes/ · raw/sim/ · raw/raas/
raw/censo/ · raw/ibge/ · raw/sinan/ · raw/pnadc/
↓
AWS Athena (tabelas externas sobre parquet)
↓
dbt (transformação em camadas)
silver: limpeza, padronização e enriquecimento
gold:   agregações, cruzamentos e taxas normalizadas
↓
Apache Airflow (orquestração mensal)
```

## 📊 Fontes de Dados

| Dataset | Descrição | Período | Volume |
|---------|-----------|---------|--------|
| **SIH/DATASUS** | Internações psiquiátricas (ESPEC=05 ou CID F*) | 2015–2025 | ~1.1M internações |
| **CNES** | Estabelecimentos de saúde mental (CAPS, hospitais) | 2018–2025 | snapshot anual |
| **SIM** | Óbitos por suicídio (CID X60–X84) | 2018–2024 | ~18k óbitos |
| **RAAS** | Atendimentos ambulatoriais nos CAPS | 2018–2025 | ~33M atendimentos |
| **Censo 2022 (IBGE)** | População, favelas e demografia por município | 2022 | 645 municípios SP |
| **Estimativas Pop. IBGE** | População estimada por município por ano | 2015–2025 | 5.160 registros |
| **SINAN Violência** | Notificações de violência doméstica e autoprovocada | 2015–2025 | ~1.18M notificações |
| **PNADC (Base dos Dados)** | Microdados de renda, emprego e escolaridade SP | 2015–2023 | 358k registros |
| **Censo 2022 Demográfico** | População por município, idade, sexo e raça | 2022 | 270k registros |

## 🗂️ Modelos dbt

### Silver (views — limpeza e padronização)
| Modelo | Descrição |
|--------|-----------|
| `sih_internacoes_psiquiatria` | Internações filtradas por especialidade/CID psiquiátrico |
| `cnes_saude_mental` | CAPS, hospitais e serviços categorizados |
| `sim_suicidios` | Óbitos por suicídio com método classificado |
| `raas_atendimentos` | Atendimentos CAPS com campos padronizados |
| `censo_municipios` | População e % domicílios em favelas |
| `ibge_populacao` | Estimativas populacionais + Censo 2022 + interpolação 2023 |
| `sinan_violencia_silver` | Notificações com ano extraído de DT_NOTIFIC |
| `pnadc_sp_silver` | Microdados PNADC com campos decodificados |
| `censo_2022_demografico` | População por município, idade, sexo e raça |

### Gold (tables — tabelas analíticas)
| Modelo | Descrição |
|--------|-----------|
| `internacoes_por_ano` | Internações psiquiátricas por ano (2015–2025) |
| `internacoes_por_cid` | Internações por diagnóstico e ano |
| `atendimentos_por_ano` | Atendimentos CAPS por município e ano |
| `suicidios_por_ano` | Óbitos por suicídio por município e ano |
| `caps_vs_internacoes` | Infraestrutura vs volume de internações |
| `violencia_por_ano` | Notificações de violência por ano |
| `saude_mental_municipios` | **Modelo principal** — cruzamento completo com taxas por 100k hab normalizadas por população do ano correto |

## ✅ Qualidade de Dados

- **32 testes dbt** cobrindo modelos silver e gold (`not_null`, `unique`, `accepted_values`)
- **Monitor de anomalias** — `monitor_qualidade.py` verifica inconsistências após cada ingestão
- **Filtro de anos incompletos** — 2026 excluído automaticamente dos modelos gold
- **Documentação automática** — `dbt docs generate` gera site com lineage graph

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.12 (PySUS, boto3, pandas, requests, google-cloud-bigquery)
- **Cloud:** AWS (S3, Athena, IAM) + Google Cloud (BigQuery)
- **Transformação:** dbt-athena 1.10
- **Orquestração:** Apache Airflow (DAG mensal)
- **Versionamento:** Git/GitHub

## 🚀 Como Reproduzir

### Pré-requisitos
- Python 3.12+
- AWS CLI configurado com acesso a S3 e Athena
- Google Cloud SDK com projeto configurado (para PNADC via Base dos Dados)
- WSL2 (Windows) ou Linux

### Instalação

```bash
git clone https://github.com/kvgs/sus-data-pipeline
cd sus-data-pipeline
pip install -r requirements.txt
cp .env.example .env  # configure suas credenciais
```

### Ingestão

```bash
python3 ingest_sih_historico.py       # SIH 2015-2017
python3 ingest_populacao.py           # Estimativas populacionais IBGE
python3 ingest_sinan_viol.py          # SINAN violência
python3 ingest_pnadc.py               # PNADC via BigQuery
python3 ingest_censo_demografico.py   # Censo 2022 demográfico
```

### Transformação

```bash
cd sus_dbt
dbt run        # roda todos os modelos
dbt test       # roda os testes de qualidade
dbt docs generate && dbt docs serve  # documentação
```

### Monitoramento

```bash
python3 monitor_qualidade.py  # verifica anomalias nos dados
```

## 📁 Estrutura do Projeto
```
sus-data-pipeline/
├── dags/
│   └── sus_pipeline_dag.py       # DAG Airflow — orquestração mensal
├── sus_dbt/
│   ├── models/
│   │   ├── silver/               # Limpeza e padronização
│   │   │   ├── schema.yml        # Testes e documentação
│   │   │   └── *.sql
│   │   └── gold/                 # Tabelas analíticas
│   │       ├── schema.yml        # Testes e documentação
│   │       └── *.sql
│   └── dbt_project.yml
├── ingest_base.py                # Classe base para ingestão
├── ingest_sih_historico.py
├── ingest_populacao.py
├── ingest_sinan_viol.py
├── ingest_pnadc.py
├── ingest_censo_demografico.py
├── monitor_qualidade.py          # Monitor de anomalias
├── .env.example                  # Template de variáveis de ambiente
└── README.md
```
