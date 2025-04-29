import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Função para carregar arquivos manualmente
@st.cache_data
def load_data(gravimetria_path, fluxo_path):
    gravimetria = pd.read_excel(gravimetria_path)
    fluxo = pd.read_excel(fluxo_path)
    return gravimetria, fluxo

# Interface para uploads
st.title("Análise de Resíduos por Tipo de Unidade e UF")
grav_file = st.file_uploader("Carregar planilha de Gravimetria", type=["xlsx"])
flux_file = st.file_uploader("Carregar planilha de Fluxo", type=["xlsx"])

if grav_file and flux_file:
    gravimetria, fluxo = load_data(grav_file, flux_file)

    tipo_col = "Tipo de unidade, segundo o município informante"

    # Padronização dos nomes
    gravimetria[tipo_col] = gravimetria[tipo_col].str.strip()
    fluxo[tipo_col] = fluxo[tipo_col].str.strip()

    ufs = sorted(fluxo["UF"].dropna().unique())
    tipos_unidade = sorted(fluxo[tipo_col].dropna().unique())

    uf_sel = st.selectbox("Selecione a UF", ufs)
    tipo_sel = st.selectbox("Selecione o Tipo de Unidade", tipos_unidade)

    fluxo_filtrado = fluxo[(fluxo["UF"] == uf_sel) & (fluxo[tipo_col] == tipo_sel)]

    if not fluxo_filtrado.empty:
        total_por_unidade = fluxo_filtrado.groupby("Nome da unidade")["Total"].sum().reset_index()
        grav_filtro = gravimetria[gravimetria[tipo_col] == tipo_sel]

        if grav_filtro.empty:
            st.error("Não há dados de gravimetria para esse tipo de unidade.")
        else:
            composicao = grav_filtro.iloc[0].drop(tipo_col)

            materiais_validos = []
            composicao_final = {}

            for material, frac in composicao.items():
                if isinstance(frac, (float, int)):
                    valor_total = fluxo_filtrado["Total"].sum() * frac
                    composicao_final[material] = valor_total
                    materiais_validos.append(material)

            df_resultado = pd.DataFrame({
                "Material": list(composicao_final.keys()),
                "Quantidade (t)": list(composicao_final.values())
            }).sort_values("Quantidade (t)", ascending=False)

            st.subheader("Tabela de Composição Estimada dos Resíduos")
            st.dataframe(df_resultado, use_container_width=True)

            st.subheader("Gráfico de Barras")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.barh(df_resultado["Material"], df_resultado["Quantidade (t)"], color="teal")
            ax.invert_yaxis()
            ax.set_xlabel("Toneladas")
            st.pyplot(fig)
    else:
        st.warning("Nenhuma unidade encontrada para os filtros selecionados.")
