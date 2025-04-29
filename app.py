import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# CONFIGURAÇÃO DE AMBIENTE
# =============================
# Requisitos (requirements.txt):
#   streamlit
#   pandas
#   plotly
#   openpyxl

# Definição das categorias compostas e suas colunas originais
COMPOSITE_MAPPING = {
    'Dom+Pub': [
        'Papel/Papelão', 'Plásticos', 'Vidros', 'Metais', 'Orgânicos',
        'Podas Municipais e Domiciliares', 'Inertes', 'Dom+Pub'
    ],
    'Entulho': [
        'Concreto', 'Argamassa', 'Tijolo', 'Madeira', 'Papel', 'Plástico',
        'Metal', 'Material agregado', 'Terra bruta', 'Pedra',
        'Caliça Retida', 'Caliça Peneirada', 'Cerâmica', 'Material orgânico e galhos',
        'Entulho'
    ],
    'Saúde': [
        'Valor energético p/Coprocessamento', 'Valor energético p/Inciner ação', 'Saude'
    ],
    'Podas': [
        'Redução de peso seco com Dom + Pub', 'Redução de peso Líquido com Dom + Pub',
        'Redução de peso seco com Podas', 'Redução de peso Líquido com Podas', 'Podas'
    ],
    'Outros': ['Outros']
}

FRACTIONS = list(COMPOSITE_MAPPING.keys())
MERGE_KEY = 'Tipo de unidade, segundo o município informante'

@st.cache_data
def load_data(grav_file, fluxo_file):
    # Leitura e padronização de colunas
    grav_df = pd.read_excel(grav_file)
    fluxo_df = pd.read_excel(fluxo_file)
    grav_df.columns = grav_df.columns.str.strip()
    fluxo_df.columns = fluxo_df.columns.str.strip()

    # Calcula frações compostas a partir das colunas originais
    for frac, cols in COMPOSITE_MAPPING.items():
        valid = [c for c in cols if c in fluxo_df.columns]
        fluxo_df[frac] = fluxo_df[valid].fillna(0).sum(axis=1)

    # Renomeia colunas de peso na gravimetria para '{frac}_peso'
    for frac in FRACTIONS:
        if frac in grav_df.columns:
            grav_df.rename(columns={frac: f"{frac}_peso"}, inplace=True)
        # trata 'Saude' sem acento
        elif frac == 'Saúde' and 'Saude' in grav_df.columns:
            grav_df.rename(columns={'Saude': 'Saúde_peso'}, inplace=True)

    # Merge pelo tipo de unidade
    merged = pd.merge(
        fluxo_df,
        grav_df,
        on=MERGE_KEY,
        how='left'
    )

    # Preenche pesos ausentes com 1
    for frac in FRACTIONS:
        peso_col = f"{frac}_peso"
        merged[peso_col] = merged.get(peso_col, pd.Series(1.0, index=merged.index)).fillna(1.0)

    # Cálculo do volume ajustado (soma ponderada)
    merged['Volume Ajustado (t)'] = 0.0
    for frac in FRACTIONS:
        merged['Volume Ajustado (t)'] += merged[frac] * merged[f"{frac}_peso"]

    return merged

# Função principal do Streamlit
def main():
    st.sidebar.title("Upload das Planilhas")
    grav_file = st.sidebar.file_uploader("Gravimetria (pesos)", type=['xlsx','csv'])
    fluxo_file = st.sidebar.file_uploader("Fluxo Municipal (dados)", type=['xlsx','csv'])

    if grav_file and fluxo_file:
        df = load_data(grav_file, fluxo_file)
        st.title("Volume de Resíduos Ajustado por Gravimetria")

        nivel = st.selectbox("Nível de Visualização", ['Estadual', 'Municipal', 'Tipo de Unidade'])

        if nivel == 'Estadual':
            agr = df.groupby('UF')['Volume Ajustado (t)'].sum().reset_index()
            fig = px.bar(agr, x='UF', y='Volume Ajustado (t)', title='Por Estado')
            st.plotly_chart(fig)

        elif nivel == 'Municipal':
            estado_sel = st.selectbox('Selecione Estado', sorted(df['UF'].dropna().unique()))
            filt = df[df['UF'] == estado_sel]
            agr = filt.groupby('Município de origem dos resíduos')['Volume Ajustado (t)'].sum().reset_index()
            fig = px.bar(
                agr,
                x='Município de origem dos resíduos',
                y='Volume Ajustado (t)',
                title=f'Municípios de {estado_sel}'
            )
            st.plotly_chart(fig)

        else:  # Tipo de Unidade
            agr = df.groupby(MERGE_KEY)['Volume Ajustado (t)'].sum().reset_index()
            fig = px.pie(
                agr,
                names=MERGE_KEY,
                values='Volume Ajustado (t)',
                title='Por Tipo de Unidade'
            )
            st.plotly_chart(fig)

        # Exibição da tabela completa
        st.dataframe(df)
    else:
        st.info("Faça upload das duas planilhas para iniciar.")

if __name__ == '__main__':
    main()
