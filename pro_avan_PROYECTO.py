import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Análisis de Residuos", layout="centered")
st.title(" Análisis y Evolución de Residuos Sólidos (2019–2023)")

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("BD_residuos_sólidos.csv", encoding="latin1", sep=";")
        df["POB_URBANA"] = pd.to_numeric(df["POB_URBANA"], errors="coerce")
        df["POB_RURAL"] = pd.to_numeric(df["POB_RURAL"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.stop()

df = cargar_datos()


# --------------------------------------------------------------------
st.header("Comparación por Distrito y Provincia")

departamentos = df["DEPARTAMENTO"].dropna().unique()
departamento_sel = st.selectbox("Selecciona un departamento", sorted(departamentos), key="dep_provincia")
df_dep = df[df["DEPARTAMENTO"] == departamento_sel]

provincias = df_dep["PROVINCIA"].dropna().unique()
provincia_sel = st.selectbox("Selecciona una provincia", sorted(provincias), key="prov_ambito")
df_prov = df_dep[df_dep["PROVINCIA"] == provincia_sel]

columnas_residuos = [col for col in df.columns if col.startswith("QRESIDUOS_") and col != "QRESIDUOS_DOM"]
residuo_sel = st.selectbox("Selecciona el tipo de residuo", columnas_residuos, key="residuo_ambito")

df_prov[residuo_sel] = pd.to_numeric(df_prov[residuo_sel], errors="coerce")

st.subheader("Comparación de residuos por distrito")
resumen_distritos = df_prov.groupby("DISTRITO")[residuo_sel].sum().reset_index()
resumen_distritos.columns = ["Distrito", "Toneladas"]
resumen_distritos = resumen_distritos.sort_values("Toneladas", ascending=False)

st.dataframe(resumen_distritos.style.format({"Toneladas": "{:,.2f}"}))
st.bar_chart(resumen_distritos.set_index("Distrito"), use_container_width=True)

# --------------------------------------------------------------------
st.header(" Evolución de residuos (2019 vs 2023)")

df_dep[residuo_sel] = pd.to_numeric(df_dep[residuo_sel], errors="coerce").fillna(0)
pivot = df_dep.pivot_table(index="DISTRITO", columns="PERIODO", values=residuo_sel, aggfunc="sum").fillna(0)
periodos = pivot.columns.tolist()

if 2019 in periodos and 2023 in periodos:
    pivot["DIF_2023_2019"] = pivot[2023] - pivot[2019]
    columnas_mostrar = [2019, 2023, "DIF_2023_2019"]

    top10_aumento = pivot.sort_values("DIF_2023_2019", ascending=False).head(10)
    top10_disminuyo = pivot.sort_values("DIF_2023_2019", ascending=True).head(10)

    st.subheader("Top 10 distritos que más aumentaron")
    st.dataframe(top10_aumento[columnas_mostrar].style.format("{:,.2f}"))
    st.bar_chart(top10_aumento["DIF_2023_2019"])

    st.subheader(" Top 10 distritos que más disminuyeron")
    st.dataframe(top10_disminuyo[columnas_mostrar].style.format("{:,.2f}"))
    st.bar_chart(top10_disminuyo["DIF_2023_2019"])

