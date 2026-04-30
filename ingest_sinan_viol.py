import pysus
import pandas as pd
import boto3
import glob
import os

BUCKET = 'sus-data-pipeline-kvgs'
DATA_DIR = '/tmp/sinan_viol'
os.makedirs(DATA_DIR, exist_ok=True)

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

print("Buscando arquivos SINAN VIOL 2015-2025...")
sinan = pysus.SINAN()
sinan.load()
files = sinan.get_files(dis_code='VIOL', year=list(range(2015, 2026)))
print(f"{len(files)} arquivos encontrados. Baixando...")

sinan.download(files, local_dir=DATA_DIR)

print("Filtrando SP e enviando para S3...")
s3 = boto3.client('s3')

for arquivo in glob.glob(f'{DATA_DIR}/**/*-0.parquet', recursive=True):
    nome_pasta = os.path.basename(os.path.dirname(arquivo))
    
    df = pd.read_parquet(arquivo)
    
    # filtra SP
    df_sp = df[df['SG_UF_NOT'] == '35'].copy()
    
    # seleciona colunas disponíveis
    cols_disp = [c for c in COLUNAS if c in df_sp.columns]
    df_sp = df_sp[cols_disp]
    
    if len(df_sp) == 0:
        print(f"  {nome_pasta}: sem dados SP")
        continue
    
    # salva e envia
    path_out = f'/tmp/sinan_viol_sp/{nome_pasta}'
    os.makedirs(path_out, exist_ok=True)
    nome_arquivo = os.path.basename(arquivo)
    path_parquet = f'{path_out}/{nome_arquivo}'
    df_sp.to_parquet(path_parquet, index=False)
    
    chave = f'raw/sinan/viol/{nome_pasta}/{nome_arquivo}'
    s3.upload_file(path_parquet, BUCKET, chave)
    print(f"  Enviado: {chave} ({len(df_sp):,} registros SP)")

print("Concluído!")