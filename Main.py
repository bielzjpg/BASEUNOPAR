import streamlit as st
import pandas as pd
from io import BytesIO

def encontrar_cpf(cpf_mask, lista_completa):
    if pd.isna(cpf_mask):
        return None
    prefixo = cpf_mask[:3]
    sufixo = cpf_mask[-2:]
    candidatos = [cpf for cpf in lista_completa if cpf.startswith(prefixo) and cpf.endswith(sufixo)]
    if candidatos:
        return ", ".join(candidatos)
    return None

st.title("🔍 Desmascarar CPFs em Planilhas")

arquivo_completa = st.file_uploader("📂 Envie a base completa (com CPFs mascarados)", type=["xlsx", "csv"])
arquivo_cpfs = st.file_uploader("📂 Envie a base de CPFs (coluna única)", type=["xlsx", "csv"])

if arquivo_completa and arquivo_cpfs:
    if arquivo_completa.name.endswith(".csv"):
        df_completa = pd.read_csv(arquivo_completa, dtype=str)
    else:
        df_completa = pd.read_excel(arquivo_completa, dtype=str)

    col_cpf_mask = None
    for col in df_completa.columns:
        if "MASCARADO" in col.upper():
            col_cpf_mask = col
            break

    if not col_cpf_mask:
        st.error("❌ Não foi encontrada nenhuma coluna com 'MASCARADO' no nome.")
    else:
        if arquivo_cpfs.name.endswith(".csv"):
            df_cpfs_raw = pd.read_csv(arquivo_cpfs, header=None, dtype=str)
        else:
            df_cpfs_raw = pd.read_excel(arquivo_cpfs, header=None, dtype=str)

        df_cpfs = df_cpfs_raw[df_cpfs_raw[0].str.match(r"^\d{11}$", na=False)].copy()
        df_cpfs.columns = ["CPF"]
        lista_cpfs = df_cpfs["CPF"].tolist()

        df_completa["CPF_DESMASCARADO"] = df_completa[col_cpf_mask].apply(
            lambda x: encontrar_cpf(x, lista_cpfs)
        )

        st.success("✅ Processamento concluído!")
        st.dataframe(df_completa.head())

        output = BytesIO()
        df_completa.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Baixar resultado",
            data=output,
            file_name="Base_completa_desmascarada.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
