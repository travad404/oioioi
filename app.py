import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Funções auxiliares
# Funções auxiliares
def load_data():
    st.sidebar.header("Upload dos Arquivos")
    gravimetria_file = st.sidebar.file_uploader("Upload da Planilha de Gravimetria", type=["xlsx"])
    fluxo_file = st.sidebar.file_uploader("Upload da Planilha de Fluxo", type=["xlsx"])

    if gravimetria_file and fluxo_file:
        gravimetria = pd.read_excel(gravimetria_file)
        fluxo = pd.read_excel(fluxo_file)
        return gravimetria, fluxo
    else:
        st.warning("Por favor, faça o upload das duas planilhas para continuar.")
        st.stop()

def calcular_composicao(gravimetria, fluxo):
    # Padronizar nomes
    fluxo['Tipo de Unidade'] = fluxo['Tipo de Unidade'].str.strip().str.lower()
    gravimetria['Tipo de Unidade'] = gravimetria['Tipo de Unidade'].str.strip().str.lower()

    # Juntar gravimetria ao fluxo
    fluxo_completo = fluxo.merge(gravimetria, on='Tipo de Unidade', how='left')

    # Multiplicar as frações pelo total recebido
    materiais = gravimetria.columns.drop('Tipo de Unidade')
    for material in materiais:
        fluxo_completo[material] = fluxo_completo[material] * fluxo_completo['Total (t)']

    return fluxo_completo, materiais

def gerar_download_link(df, filename):
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button(
        label=f"📎 Baixar {filename}",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def plot_graficos(df, materiais):
    total_materiais = df[materiais].sum().sort_values(ascending=False)

    st.subheader("Composição Total dos Resíduos")

    # Pizza
    fig_pie = px.pie(
        values=total_materiais.values,
        names=total_materiais.index,
        title="Distribuição Percentual dos Materiais"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Barras empilhadas
    st.subheader("Composição por Unidade")
    df_plot = df.groupby('Nome da Unidade')[materiais].sum()
    df_plot = df_plot.reset_index()
    fig_bar = px.bar(
        df_plot,
        x='Nome da Unidade',
        y=materiais,
        title="Materiais Recebidos por Unidade",
        labels={"value": "Toneladas", "variable": "Material"},
        height=600
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Streamlit App
st.set_page_config(page_title="Análise Gravimetria e Fluxo", layout="wide")
st.title("📊 Análise de Resíduos por Tipo de Unidade e UF")

# Carregar dados
gravimetria, fluxo = load_data()

# Calcular composição
fluxo_completo, materiais = calcular_composicao(gravimetria, fluxo)

# Filtros
ufs = fluxo_completo['UF'].dropna().unique()
tipos = fluxo_completo['Tipo de Unidade'].dropna().unique()

col1, col2 = st.columns(2)

with col1:
    uf_escolhida = st.selectbox("Escolha a UF:", options=["Todas"] + list(ufs))

with col2:
    tipo_escolhido = st.selectbox("Escolha o Tipo de Unidade:", options=["Todas"] + list(tipos))

# Aplicar filtros
filtro = fluxo_completo.copy()
if uf_escolhida != "Todas":
    filtro = filtro[filtro['UF'] == uf_escolhida]
if tipo_escolhido != "Todas":
    filtro = filtro[filtro['Tipo de Unidade'] == tipo_escolhido]

# Mostrar tabela
st.subheader("Tabela de Composição Calculada")
st.dataframe(filtro[['Nome da Unidade', 'Tipo de Unidade', 'UF'] + list(materiais)], use_container_width=True)

# Botão de download
gerar_download_link(filtro[['Nome da Unidade', 'Tipo de Unidade', 'UF'] + list(materiais)], "composicao_residuos.xlsx")

# Mostrar graficos
plot_graficos(filtro, materiais)

