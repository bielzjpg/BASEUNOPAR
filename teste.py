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

st.title("🔍 Desmascarar CPFs e Remover Linhas Duplicadas")

# Upload das planilhas
arquivo_completa = st.file_uploader("📂 Envie a base completa (com CPFs mascarados)", type=["xlsx", "csv"])
arquivo_cpfs = st.file_uploader("📂 Envie a base de CPFs (coluna única)", type=["xlsx", "csv"])

if arquivo_completa and arquivo_cpfs:
    # Ler base completa
    if arquivo_completa.name.endswith(".csv"):
        df_completa = pd.read_csv(arquivo_completa, dtype=str)
    else:
        df_completa = pd.read_excel(arquivo_completa, dtype=str)

    # Encontrar coluna mascarada
    col_cpf_mask = next((col for col in df_completa.columns if "MASCARADO" in col.upper()), None)
    if not col_cpf_mask:
        st.error("❌ Nenhuma coluna com 'MASCARADO' encontrada.")
    else:
        # Ler base de CPFs
        if arquivo_cpfs.name.endswith(".csv"):
            df_cpfs_raw = pd.read_csv(arquivo_cpfs, header=None, dtype=str)
        else:
            df_cpfs_raw = pd.read_excel(arquivo_cpfs, header=None, dtype=str)

        df_cpfs = df_cpfs_raw[df_cpfs_raw[0].str.match(r"^\d{11}$", na=False)].copy()
        df_cpfs.columns = ["CPF"]
        lista_cpfs = df_cpfs["CPF"].tolist()

        # Desmascarar CPFs
        df_completa["CPF_DESMASCARADO"] = df_completa[col_cpf_mask].apply(lambda x: encontrar_cpf(x, lista_cpfs))

        # Explodir múltiplos candidatos
        df_final = df_completa.explode("CPF_DESMASCARADO")

        # Remover linhas com CPFs duplicados
        contagem = df_final["CPF_DESMASCARADO"].value_counts()
        cpfs_unicos = contagem[contagem == 1].index
        df_final = df_final[df_final["CPF_DESMASCARADO"].isin(cpfs_unicos)]

        st.success("✅ Processamento concluído! Linhas duplicadas removidas.")
        st.dataframe(df_final.head())

        # Preparar download
        output = BytesIO()
        df_final.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Baixar resultado",
            data=output,
            file_name="Base_desmascarada_limpa.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
