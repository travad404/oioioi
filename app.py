import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Análise Avançada de Resíduos com Gravimetria por Tipo de Unidade")

@st.cache_data
def load_data(grav_path, fluxo_path):
    grav = pd.read_excel(grav_path)
    fluxo = pd.read_excel(fluxo_path)
    return grav, fluxo

grav_file = st.file_uploader("Carregue a planilha de Gravimetria", type="xlsx")
flux_file = st.file_uploader("Carregue a planilha de Fluxo", type="xlsx")

if grav_file and flux_file:
    grav, fluxo = load_data(grav_file, flux_file)

    col_tipo_unidade = "Tipo de unidade, segundo o município informante"
    fluxo[col_tipo_unidade] = fluxo[col_tipo_unidade].str.strip()
    grav[col_tipo_unidade] = grav[col_tipo_unidade].str.strip()

    ufs = sorted(fluxo["UF"].dropna().unique())
    tipos_unidade = sorted(fluxo[col_tipo_unidade].dropna().unique())

    uf_sel = st.selectbox("Selecione a UF", ufs)
    tipo_sel = st.selectbox("Selecione o Tipo de Unidade", tipos_unidade)

    fluxo_filtrado = fluxo[(fluxo["UF"] == uf_sel) & (fluxo[col_tipo_unidade] == tipo_sel)]
    grav_filtro = grav[grav[col_tipo_unidade] == tipo_sel]

    if fluxo_filtrado.empty or grav_filtro.empty:
        st.warning("Sem dados suficientes para análise.")
    else:
        grav_row = grav_filtro.iloc[0]
        composicao_final = {}
        
        total_geral = 0

        # 1. DOM+PUB
        if "Dom+Pub" in fluxo_filtrado.columns and "Dom+Pub" in grav_row:
            dompub_total = fluxo_filtrado["Dom+Pub"].sum()
            total_geral += dompub_total

            for material, frac in grav_row.items():
                if material in ["Dom+Pub", col_tipo_unidade] or pd.isna(frac): continue
                if grav_row["Dom+Pub"] > 0:
                    composicao_final[material] = composicao_final.get(material, 0) + dompub_total * frac

        # 2. ENTULHO, SAUDE, PODAS, OUTROS diretamente
        residuos_diretos = ["Entulho", "Saúde", "Podas", "Outros"]
        for res in residuos_diretos:
            if res in fluxo_filtrado.columns and res in grav_row:
                valor = fluxo_filtrado[res].sum()
                total_geral += valor
                composicao_final[res] = composicao_final.get(res, 0) + valor

        # Exibir resultados
        st.subheader(f"Composição estimada dos resíduos em {uf_sel} para {tipo_sel}")
        df_resultado = pd.DataFrame({
            "Material": list(composicao_final.keys()),
            "Quantidade (t)": list(composicao_final.values())
        }).sort_values("Quantidade (t)", ascending=False)

        st.dataframe(df_resultado, use_container_width=True)

        st.subheader("Gráfico de Barras")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(df_resultado["Material"], df_resultado["Quantidade (t)"], color="seagreen")
        ax.set_xlabel("Toneladas")
        ax.invert_yaxis()
        st.pyplot(fig)
