import pandas as pd
import streamlit as st

@st.cache_data
def load_data(grav_file, fluxo_file):
    # Lendo os arquivos
    fluxo_df = pd.read_csv(fluxo_file)
    grav_df = pd.read_csv(grav_file)

    # Corrigir problemas comuns de cabeçalho (remover espaços extras)
    fluxo_df.columns = fluxo_df.columns.str.strip()
    grav_df.columns = grav_df.columns.str.strip()

    # Nome da chave para fazer o merge
    MERGE_KEY = 'Tipo de unidade, segundo o município informante'

    # Verificar se a coluna chave existe
    if MERGE_KEY not in fluxo_df.columns:
        st.error(f"❌ A coluna '{MERGE_KEY}' não foi encontrada no arquivo de fluxo.\n\nColunas disponíveis: {list(fluxo_df.columns)}")
        st.stop()

    if MERGE_KEY not in grav_df.columns:
        st.error(f"❌ A coluna '{MERGE_KEY}' não foi encontrada no arquivo de gravimetria.\n\nColunas disponíveis: {list(grav_df.columns)}")
        st.stop()

    # Fazendo o merge
    merged = pd.merge(
        fluxo_df,
        grav_df,
        on=MERGE_KEY,
        how='left'
    )

    # Preenche pesos faltantes com 1.0
    peso_col = 'Peso'
    if peso_col not in merged.columns:
        merged[peso_col] = 1.0
    else:
        merged[peso_col] = merged[peso_col].fillna(1.0)

    return merged
