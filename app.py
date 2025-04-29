import streamlit as st
import pandas as pd
import plotly.express as px

# Função para carregar os dados
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

# Função para calcular a composição
def calcular_composicao(gravimetria, fluxo):
    col_tipo_unidade = "Tipo de unidade, segundo o município informante"

    # Normaliza os nomes para facilitar o merge
    fluxo[col_tipo_unidade] = fluxo[col_tipo_unidade].str.strip().str.lower()
    gravimetria[col_tipo_unidade] = gravimetria[col_tipo_unidade].str.strip().str.lower()

    # Merge
    fluxo_completo = fluxo.merge(
        gravimetria,
        left_on=col_tipo_unidade,
        right_on=col_tipo_unidade,
        how='left'
    )

    # Materiais (colunas que são frações)
    materiais = gravimetria.columns.drop(col_tipo_unidade)

    # Multiplica as frações pela quantidade total
    for material in materiais:
        fluxo_completo[material] = fluxo_completo[material] * fluxo_completo['Total ']

    return fluxo_completo, materiais

# Função para exibir dados e gráficos
def exibir_dados(fluxo_completo, materiais):
    st.sidebar.header("Filtros")

    ufs = fluxo_completo['UF'].unique()
    tipos_unidade = fluxo_completo['Tipo de unidade, segundo o município informante'].unique()

    uf_selecionada = st.sidebar.selectbox("Selecione a UF", sorted(ufs))
    tipo_unidade_selecionado = st.sidebar.selectbox("Selecione o Tipo de Unidade", sorted(tipos_unidade))

    dados_filtrados = fluxo_completo[
        (fluxo_completo['UF'] == uf_selecionada) &
        (fluxo_completo['Tipo de unidade, segundo o município informante'] == tipo_unidade_selecionado)
    ]

    if dados_filtrados.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    st.subheader(f"Composição de Resíduos - {uf_selecionada} - {tipo_unidade_selecionado.upper()}")

    # Somar os materiais
    soma_materiais = dados_filtrados[materiais].sum()

    # Mostrar tabela
    st.write("Tabela de Composição (toneladas):")
    st.dataframe(soma_materiais.to_frame(name="Toneladas").style.format({"Toneladas": "{:,.2f}"}))

    # Gráfico de pizza
    fig_pizza = px.pie(
        names=soma_materiais.index,
        values=soma_materiais.values,
        title="Distribuição dos Materiais",
    )
    st.plotly_chart(fig_pizza)

    # Gráfico de barras empilhadas
    dados_melt = dados_filtrados.melt(
        id_vars=['Nome da Unidade', 'UF'],
        value_vars=materiais,
        var_name='Material',
        value_name='Toneladas'
    )

    fig_barras = px.bar(
        dados_melt,
        x="Nome da Unidade",
        y="Toneladas",
        color="Material",
        title="Composição por Unidade",
        barmode="stack"
    )
    st.plotly_chart(fig_barras)

    # Download dos dados
    csv = dados_filtrados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados (.csv)",
        data=csv,
        file_name=f"residuos_{uf_selecionada}_{tipo_unidade_selecionado}.csv",
        mime='text/csv'
    )

# Função principal
def main():
    st.set_page_config(page_title="Análise de Resíduos", layout="wide")

    st.title("📊 Análise de Composição de Resíduos por Unidade")

    gravimetria, fluxo = load_data()
    fluxo_completo, materiais = calcular_composicao(gravimetria, fluxo)
    exibir_dados(fluxo_completo, materiais)

if __name__ == "__main__":
    main()
