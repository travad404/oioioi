import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar os arquivos
def carregar_dados():
    st.sidebar.title("Upload das planilhas")
    gravimetria_file = st.sidebar.file_uploader("Upload da Planilha de Gravimetria", type=["xlsx", "csv"])
    residuos_file = st.sidebar.file_uploader("Upload da Planilha de Resíduos Municipais", type=["xlsx", "csv"])
    
    gravimetria_df = residuos_df = None

    if gravimetria_file:
        gravimetria_df = pd.read_excel(gravimetria_file) if gravimetria_file.name.endswith('xlsx') else pd.read_csv(gravimetria_file)

    if residuos_file:
        residuos_df = pd.read_excel(residuos_file) if residuos_file.name.endswith('xlsx') else pd.read_csv(residuos_file)

    return gravimetria_df, residuos_df

# Função para calcular os volumes ajustados
def calcular_volumes(gravimetria_df, residuos_df):
    # Vamos assumir que ambas as tabelas têm colunas de identificação comuns:
    # residuos_df: 'Município', 'Estado', 'Tipo de Unidade', 'Quantidade (t)'
    # gravimetria_df: 'Tipo de Unidade', 'Peso de Ajuste'
    
    # Fazendo o merge
    merged_df = pd.merge(residuos_df, gravimetria_df, on="Tipo de Unidade", how="left")
    
    # Aplicar o peso de ajuste
    merged_df["Volume Ajustado (t)"] = merged_df["Quantidade (t)"] * merged_df["Peso de Ajuste"]
    
    return merged_df

# Função para visualizar os dados
def visualizar_dados(merged_df):
    st.title("Análise de Resíduos com Gravimetria Ajustada")
    
    nivel = st.selectbox("Escolha o nível de visualização", ["Estadual", "Municipal", "Tipo de Unidade"])
    
    if nivel == "Estadual":
        agrupado = merged_df.groupby("Estado")["Volume Ajustado (t)"].sum().reset_index()
        fig = px.bar(agrupado, x="Estado", y="Volume Ajustado (t)", title="Volume Ajustado por Estado")
        st.plotly_chart(fig)
    
    elif nivel == "Municipal":
        estado_selecionado = st.selectbox("Selecione o Estado", merged_df["Estado"].unique())
        filtrado = merged_df[merged_df["Estado"] == estado_selecionado]
        agrupado = filtrado.groupby("Município")["Volume Ajustado (t)"].sum().reset_index()
        fig = px.bar(agrupado, x="Município", y="Volume Ajustado (t)", title=f"Volume Ajustado nos Municípios de {estado_selecionado}")
        st.plotly_chart(fig)
    
    elif nivel == "Tipo de Unidade":
        agrupado = merged_df.groupby("Tipo de Unidade")["Volume Ajustado (t)"].sum().reset_index()
        fig = px.pie(agrupado, names="Tipo de Unidade", values="Volume Ajustado (t)", title="Distribuição por Tipo de Unidade de Tratamento")
        st.plotly_chart(fig)
    
    st.dataframe(merged_df)

# Código principal
def main():
    gravimetria_df, residuos_df = carregar_dados()

    if gravimetria_df is not None and residuos_df is not None:
        merged_df = calcular_volumes(gravimetria_df, residuos_df)
        visualizar_dados(merged_df)
    else:
        st.info("Por favor, faça o upload das duas planilhas para começar.")

if __name__ == "__main__":
    main()
