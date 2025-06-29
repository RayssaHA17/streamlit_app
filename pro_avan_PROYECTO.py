import streamlit as st
import pandas as pd
import numpy as np
import folium
import plotly.express as px
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(page_title="Análisis de Residuos", layout="wide")

st.title("Análisis de Composición de residuos sólidos domiciliarios ")

@st.cache_data
def cargar_datos():
    df_residuos = pd.read_csv("BD_residuos_sólidos.csv", encoding='latin1', sep=';')
    df_ubicaciones = pd.read_csv("BD_ubicacion.csv", encoding='utf-8-sig', sep=';')
    df_residuos.columns = df_residuos.columns.str.strip()
    df_ubicaciones.columns = df_ubicaciones.columns.str.strip()
    df = pd.merge(df_residuos, df_ubicaciones, on="DISTRITO", how="inner")
    df["POB_URBANA"] = pd.to_numeric(df["POB_URBANA"], errors="coerce")
    df["POB_RURAL"] = pd.to_numeric(df["POB_RURAL"], errors="coerce")
    return df

df = cargar_datos()

col1, col2, col3 = st.columns([1, 4, 1])  # Márgenes laterales y columna central ancha
with col2:
    st.header("Mapa de Calor de Residuos Sólidos")
    residuos_opciones = [col for col in df.columns if col.startswith("QRESIDUOS_")]
    residuo_sel = st.selectbox("Selecciona un tipo de residuo", sorted(residuos_opciones), key="residuo_mapa")
    años = df["PERIODO"].dropna().unique()
    año_sel = st.selectbox("Selecciona un año", sorted(años), key="año_mapa")

    def crear_mapa(df, residuo, año):
        mapa = folium.Map(location=[-9.19, -75.02], zoom_start=5)
        df_filtrado = df[df["PERIODO"] == año]
        df_filtrado["latitud"] = pd.to_numeric(df_filtrado["latitud"], errors="coerce")
        df_filtrado["longitud"] = pd.to_numeric(df_filtrado["longitud"], errors="coerce")
        df_filtrado[residuo] = pd.to_numeric(df_filtrado[residuo], errors="coerce")
        df_filtrado = df_filtrado.dropna(subset=["latitud", "longitud", residuo])
        heat_data = df_filtrado[["latitud", "longitud", residuo]].values.tolist()
        HeatMap(heat_data, radius=15).add_to(mapa)
        return mapa

    mapa = crear_mapa(df, residuo_sel, año_sel)
    st_folium(mapa, use_container_width=True, height=350)


col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.header("Análisis Comparativo por tipos de residuos a nivel distrital, departamental y provincial")

    departamento_sel = st.selectbox("Selecciona un departamento", sorted(df["DEPARTAMENTO"].dropna().unique()), key="dep_analisis")
    df_dep = df[df["DEPARTAMENTO"] == departamento_sel]

    provincia_sel = st.selectbox("Selecciona una provincia", sorted(df_dep["PROVINCIA"].dropna().unique()), key="prov_analisis")
    df_prov = df_dep[df_dep["PROVINCIA"] == provincia_sel]

    año_comp = st.selectbox("Selecciona el año a analizar", sorted(df_prov["PERIODO"].dropna().unique()), key="año_analisis")
    df_prov = df_prov[df_prov["PERIODO"] == año_comp]

    columnas_residuos = [col for col in df.columns if col.startswith("QRESIDUOS_") and col != "QRESIDUOS_DOM"]
    residuo_analisis = st.selectbox("Selecciona el tipo de residuo a analizar", columnas_residuos, key="residuo_analisis")

    df_prov[residuo_analisis] = pd.to_numeric(df_prov[residuo_analisis], errors="coerce")

    st.subheader("Comparación de residuos por distrito")
    resumen_distritos = df_prov.groupby("DISTRITO")[residuo_analisis].sum().reset_index()
    resumen_distritos.columns = ["Distrito", "Toneladas"]
    resumen_distritos = resumen_distritos.sort_values("Toneladas", ascending=False)

    st.dataframe(resumen_distritos.style.format({"Toneladas": "{:,.2f}"}))
    st.bar_chart(resumen_distritos.set_index("Distrito"), use_container_width=True)

    st.subheader("Evaluación Temporal de Residuos (2019–2023): Comparativa por Zonas y Ranking de Distritos")

    df_dep[residuo_analisis] = pd.to_numeric(df_dep[residuo_analisis], errors="coerce").fillna(0)
    pivot = df_dep.pivot_table(index="DISTRITO", columns="PERIODO", values=residuo_analisis, aggfunc="sum").fillna(0)

    if 2019 in pivot.columns and 2023 in pivot.columns:
        pivot["DIF_2023_2019"] = pivot[2023] - pivot[2019]
        columnas_mostrar = [2019, 2023, "DIF_2023_2019"]

        top10_mas = pivot.sort_values("DIF_2023_2019", ascending=False).head(10)
        top10_menos = pivot.sort_values("DIF_2023_2019", ascending=True).head(10)

        st.write("Top 10 distritos que más aumentaron")
        st.dataframe(top10_mas[columnas_mostrar].style.format("{:,.2f}"))
        st.bar_chart(top10_mas["DIF_2023_2019"])

        st.write("Top 10 distritos que más disminuyeron")
        st.dataframe(top10_menos[columnas_mostrar].style.format("{:,.2f}"))
        st.bar_chart(top10_menos["DIF_2023_2019"])


col1, col2, col3 = st.columns(([1, 4, 1])
    st.title("Grafico circular: Produccion de Residuos Solidos por tipo, año y distrito")

    df_residuos = pd.read_csv("BD_residuos_sólidos.csv", encoding='latin1', sep=';')

    distritos = df_residuos['DISTRITO'].unique()
    distrito_sel = st.selectbox("Selecciona un distrito", sorted(distritos))

    años = df_residuos['PERIODO'].unique()
    año_sel = st.selectbox("Selecciona un año", sorted(años))

    filtro = (df_residuos['DISTRITO'] == distrito_sel) & (df_residuos['PERIODO'] == año_sel)
    df_filtrado = df_residuos.loc[filtro]

    columnas_residuos = [
        "QRESIDUOS_ALIMENTOS", "QRESIDUOS_MALEZA", "QRESIDUOS_OTROS_ORGANICOS",
        "QRESIDUOS_PAPEL_BLANCO", "QRESIDUOS_PAPEL_PERIODICO", "QRESIDUOS_PAPEL_MIXTO",
        "QRESIDUOS_CARTON_BLANCO", "QRESIDUOS_CARTON_MARRON", "QRESIDUOS_CARTON_MIXTO",
        "QRESIDUOS_VIDRIO_TRANSPARENTE", "QRESIDUOS_VIDRIO_OTROS_COLORES", "QRESIDUOS_VIDRIOS_OTROS",
        "QRESIDUOS_TEREFLATO_POLIETILENO", "QRESIDUOS_POLIETILENO_ALTA_DENSIDAD",
        "QRESIDUOS_POLIETILENO_BAJA_DENSIDAD", "QRESIDUOS_POLIPROPILENO", "QRESIDUOS_POLIESTIRENO",
        "QRESIDUOS_POLICLORURO_VINILO", "QRESIDUOS_TETRABRICK", "QRESIDUOS_LATA",
        "QRESIDUOS_METALES_FERROSOS", "QRESIDUOS_ALUMINIO", "QRESIDUOS_OTROS_METALES",
        "QRESIDUOS_BOLSAS_PLASTICAS", "QRESIDUOS_SANITARIOS", "QRESIDUOS_PILAS",
        "QRESIDUOS_TECNOPOR", "QRESIDUOS_INERTES", "QRESIDUOS_TEXTILES",
        "QRESIDUOS_CAUCHO_CUERO", "QRESIDUOS_MEDICAMENTOS", "QRESIDUOS_ENVOLTURAS_SNAKCS_OTROS",
        "QRESIDUOS_OTROS_NO_CATEGORIZADOS"
    ]

    residuos = df_filtrado[columnas_residuos].sum()

    df_grafico = pd.DataFrame({
        "residuo": residuos.index,
        "cantidad": residuos.values
    })

    df_grafico["cantidad"] = pd.to_numeric(df_grafico["cantidad"], errors="coerce")
    df_grafico = df_grafico[df_grafico["cantidad"] > 0]

    fig = px.pie(df_grafico, values="cantidad", names="residuo",
                 title=f"Distribucion de residuos en {distrito_sel} ({año_sel})")
    st.plotly_chart(fig, use_container_width=True)









