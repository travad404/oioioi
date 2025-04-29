import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Gestão de Resíduos Sólidos Urbanos", layout="wide")
st.title("📊 Gestão de Resíduos Sólidos Urbanos")
st.sidebar.header("📂 Configurações de Entrada")

@st.cache_data
def carregar_tabelas(tabela1_path, tabela2_path):
    gravimetria_data = pd.read_excel(tabela1_path)
    resumo_fluxo_data = pd.read_excel(tabela2_path)
    gravimetria_data.columns = gravimetria_data.columns.str.strip()
    resumo_fluxo_data.columns = resumo_fluxo_data.columns.str.strip()
    return gravimetria_data, resumo_fluxo_data

percentuais_entulho = {
    "Concreto": 0.0677, "Argamassa": 0.1065, "Tijolo": 0.078, "Madeira": 0.0067,
    "Papel": 0.0023, "Plástico": 0.0034, "Metal": 0.0029, "Material agregado": 0.0484,
    "Terra bruta": 0.0931, "Pedra": 0.00192, "Caliça Retida": 0.3492,
    "Caliça Peneirada": 0.2, "Cerâmica": 0.0161, "Material orgânico e galhos": 0.0087,
    "Outros": 0
}

def calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data):
    fluxo_ajustado = []
    for _, row in resumo_fluxo_data.iterrows():
        uf = row["UF"]
        unidade = row["Tipo de unidade, segundo o município informante"]
        ajuste_residuos = {"UF": uf, "Unidade": unidade}

        for residuo in ["Dom+Pub", "Entulho", "Podas", "Saúde", "Outros"]:
            if residuo in resumo_fluxo_data.columns:
                gravimetricos = gravimetria_data[
                    gravimetria_data["Tipo de unidade, segundo o município informante"] == unidade
                ]
                if not gravimetricos.empty:
                    gravimetricos = gravimetricos.iloc[0]

                    if residuo == "Dom+Pub":
                        ajuste_residuos.update({
                            "Papel/Papelão": row[residuo] * gravimetricos.get("Papel/Papelão", 0),
                            "Plásticos": row[residuo] * gravimetricos.get("Plásticos", 0),
                            "Vidros": row[residuo] * gravimetricos.get("Vidros", 0),
                            "Metais": row[residuo] * gravimetricos.get("Metais", 0),
                            "Orgânicos": row[residuo] * gravimetricos.get("Orgânicos", 0),
                            "Redução Peso Seco com Dom+Pub": row[residuo] * gravimetricos.get(
                                "Redução de peso seco com Dom + Pub", 0
                            ),
                            "Redução Peso Líquido com Dom+Pub": row[residuo] * gravimetricos.get(
                                "Redução de peso Líquido com Dom + Pub", 0
                            ),
                        })
                    elif residuo == "Entulho":
                        for material, percentual in percentuais_entulho.items():
                            ajuste_residuos[material] = row[residuo] * percentual
                    elif residuo == "Podas":
                        ajuste_residuos.update({
                            "Redução Peso Seco com Podas": row[residuo] * gravimetricos.get(
                                "Redução de peso seco com Podas", 0
                            ),
                            "Redução Peso Líquido com Podas": row[residuo] * gravimetricos.get(
                                "Redução de peso Líquido com Podas", 0
                            ),
                        })
                    elif residuo == "Saúde":
                        ajuste_residuos.update({
                            "Valor energético (MJ/ton)": row[residuo] * gravimetricos.get(
                                "Valor energético p/Incineração", 0
                            ),
                            "Valor energético p/Coprocessamento": row[residuo] * gravimetricos.get(
                                "Valor energético p/Coprocessamento", 0
                            ),
                        })
                    elif residuo == "Outros":
                        ajuste_residuos["Outros Processados"] = row[residuo] * gravimetricos.get("Outros", 0)
        fluxo_ajustado.append(ajuste_residuos)
    return pd.DataFrame(fluxo_ajustado)

# Interface para upload de arquivos
tabela1_path = st.sidebar.file_uploader("📄 Carregue a Tabela 1 (Gravimetria por Tipo de Unidade)", type=["xlsx"])
tabela2_path = st.sidebar.file_uploader("📄 Carregue a Tabela 2 (Resumo por Unidade e UF)", type=["xlsx"])

if tabela1_path and tabela2_path:
    gravimetria_data, resumo_fluxo_data = carregar_tabelas(tabela1_path, tabela2_path)
    st.success("✅ Tabelas carregadas com sucesso!")

    fluxo_ajustado = calcular_fluxo_ajustado(gravimetria_data, resumo_fluxo_data)

    st.header("📋 Resumo Geral")
    resumo_por_uf = fluxo_ajustado.groupby("UF").sum(numeric_only=True).reset_index()
    resumo_por_unidade = fluxo_ajustado.groupby("Unidade").sum(numeric_only=True).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Totais por UF")
        st.dataframe(resumo_por_uf.style.format("{:.2f}"), use_container_width=True)
        st.plotly_chart(px.bar(resumo_por_uf, x="UF", y=fluxo_ajustado.columns[2:], title="Totais por UF"))

    with col2:
        st.subheader("🏢 Totais por Tipo de Unidade")
        st.dataframe(resumo_por_unidade.style.format("{:.2f}"), use_container_width=True)
        st.plotly_chart(px.bar(resumo_por_unidade, x="Unidade", y=fluxo_ajustado.columns[2:], title="Totais por Tipo de Unidade"))

    with st.expander("📈 Estatísticas Descritivas dos Dados"):
        st.dataframe(fluxo_ajustado.describe().style.format("{:.2f}"))

