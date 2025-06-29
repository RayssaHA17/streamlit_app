import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(layout="centered")

# Cargar datos 
@st.cache_data
def cargar_datos():
    df_residuos = pd.read_csv("BD_residuos_sólidos.csv", encoding='latin1', sep=';')
    df_ubicaciones = pd.read_csv("BD_ubicacion.csv", encoding='utf-8-sig', sep=';')
    df_residuos.columns = df_residuos.columns.str.strip()
    df_ubicaciones.columns = df_ubicaciones.columns.str.strip()
    df = pd.merge(df_residuos, df_ubicaciones, on="DISTRITO", how="inner")
    return df

df = cargar_datos()

# Barra lateral de navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a sección:", [
    "📍 Mapa de Calor",
    "📊 Análisis Comparativo",
    "📈 Evaluación de Variación",
    "🧩 Gráfico Circular"
])

#---------------------------------------------------------------------------------------------------------------------------

if opcion == "📍 Mapa de Calor":
    
    st.title("Análisis de Residuos Sólidos Domiciliarios en Perú (2019–2022)")
    
    st.markdown("**Presentado por: Rayssa Hidalgo y Matías Vidal**")
    
    st.write("""
    Este proyecto desarrolla una herramienta interactiva para analizar la generación y composición de residuos sólidos
    domiciliarios en Perú (2019 - 2023), utilizando datos oficiales. Mediante visualizaciones geoespaciales y gráficos dinámicos,
    facilita la identificación de patrones regionales y temporales, apoyando la toma de decisiones para una gestión ambiental
    sostenible y eficiente.
    """)
    
    st.subheader("Objetivos Específicos")
    
    st.markdown("""
    - Visualizar la intensidad de generación de residuos mediante mapas de calor interactivos.  
    - Comparar la composición y volumen de residuos por tipo y región con filtros dinámicos.  
    - Analizar la variación distrital de residuos entre zonas urbanas y rurales (2019-2022).  
    - Mostrar la composición de residuos por distrito y año con gráficos circulares interactivos para apoyar decisiones.
    """)
#-------------------------------------------------------------------------------------------------------------------------------------    
    st.header("Mapa de Calor de Residuos Sólidos")
    
    st.write("""
    Esta sección permite representar geográficamente la intensidad de generación de residuos sólidos domiciliarios
    en el país. A través del uso del mapa de calor, los usuarios pueden observar visualmente qué distritos presentan
    mayor o menor volumen de residuos según el tipo de residuo y el año seleccionado.
    """)

    residuos_opciones = ["QRESIDUOS_ALIMENTOS", "QRESIDUOS_MALEZA",
        "QRESIDUOS_OTROS_ORGANICOS", "QRESIDUOS_PAPEL_BLANCO",
        "QRESIDUOS_PAPEL_PERIODICO", "QRESIDUOS_PAPEL_MIXTO",
        "QRESIDUOS_CARTON_BLANCO", "QRESIDUOS_CARTON_MARRON",
        "QRESIDUOS_CARTON_MIXTO", "QRESIDUOS_VIDRIO_TRANSPARENTE",
        "QRESIDUOS_VIDRIO_OTROS_COLORES", "QRESIDUOS_VIDRIOS_OTROS",
        "QRESIDUOS_TEREFLATO_POLIETILENO", "QRESIDUOS_POLIETILENO_ALTA_DENSIDAD",
        "QRESIDUOS_POLIETILENO_BAJA_DENSIDAD", "QRESIDUOS_POLIPROPILENO",
        "QRESIDUOS_POLIESTIRENO", "QRESIDUOS_POLICLORURO_VINILO", "QRESIDUOS_TETRABRICK",
        "QRESIDUOS_LATA", "QRESIDUOS_METALES_FERROSOS", "QRESIDUOS_ALUMINIO",
        "QRESIDUOS_OTROS_METALES", "QRESIDUOS_BOLSAS_PLASTICAS", "QRESIDUOS_SANITARIOS",
        "QRESIDUOS_PILAS", "QRESIDUOS_TECNOPOR", "QRESIDUOS_INERTES", "QRESIDUOS_TEXTILES",
        "QRESIDUOS_CAUCHO_CUERO", "QRESIDUOS_MEDICAMENTOS", 
        "QRESIDUOS_ENVOLTURAS_SNAKCS_OTROS", "QRESIDUOS_OTROS_NO_CATEGORIZADOS"
    ]

    residuo_sel = st.selectbox("Selecciona un tipo de residuo", sorted(residuos_opciones))
    año_sel = st.selectbox("Selecciona un año", sorted(df["PERIODO"].dropna().unique()))

    def crear_mapa(df):
        m = folium.Map(location=[-9.189967, -75.015152], zoom_start=5)
        df_filtrado = df[df['PERIODO'] == año_sel]

        df_filtrado['latitud'] = pd.to_numeric(df_filtrado['latitud'], errors='coerce')
        df_filtrado['longitud'] = pd.to_numeric(df_filtrado['longitud'], errors='coerce')
        df_filtrado[residuo_sel] = pd.to_numeric(df_filtrado[residuo_sel], errors='coerce')

        df_filtrado = df_filtrado.dropna(subset=['latitud', 'longitud', residuo_sel])
        heat_data = df_filtrado[['latitud', 'longitud', residuo_sel]].values.tolist()

        HeatMap(heat_data, radius=15).add_to(m)
        return m

    mapa = crear_mapa(df)
    st_folium(mapa, width=700, height=500)
#---------------------------------------------------------------------------------------------------------------
elif opcion == "📊 Análisis Comparativo":
    st.header("Análisis Comparativo de Residuos")
    st.write("""
    Esta sección del proyecto permite examinar cómo varía la composición de residuos sólidos según el tipo (alimentarios,
    plásticos, orgánicos, papel, cartón, entre otros) en distintos niveles administrativos del país.Esto permite observar
    su volumen de generación y cómo se distribuye dentro de cada distrito.
    """)
    departamento_sel = st.selectbox("Departamento", sorted(df["DEPARTAMENTO"].dropna().unique()), key="dep_analisis")
    df_dep = df[df["DEPARTAMENTO"] == departamento_sel]

    provincia_sel = st.selectbox("Provincia", sorted(df_dep["PROVINCIA"].dropna().unique()), key="prov_analisis")
    df_prov = df_dep[df_dep["PROVINCIA"] == provincia_sel]

    año_comp = st.selectbox("Año", sorted(df_prov["PERIODO"].dropna().unique()), key="año_analisis")
    df_prov = df_prov[df_prov["PERIODO"] == año_comp]

    columnas_residuos = [col for col in df.columns if col.startswith("QRESIDUOS_") and col != "QRESIDUOS_DOM"]
    residuo_analisis = st.selectbox("Tipo de residuo", columnas_residuos, key="residuo_analisis")

    df_prov[residuo_analisis] = pd.to_numeric(df_prov[residuo_analisis], errors="coerce")
    resumen_distritos = df_prov.groupby("DISTRITO")[residuo_analisis].sum().reset_index()
    resumen_distritos.columns = ["Distrito", "Toneladas"]
    resumen_distritos = resumen_distritos.sort_values("Toneladas", ascending=False)

    st.dataframe(resumen_distritos.style.format({"Toneladas": "{:,.2f}"}))
    st.bar_chart(resumen_distritos.set_index("Distrito"), use_container_width=True)
    
#-------------------------------------------------------------------------------------------------------------

elif opcion == "🧩 Gráfico Circular":
    #Titulo de la grafica
    st.header("Gráfico Circular de Composición de Residuos")
    #reseña
    st.write("""
    Esta sección presenta gráficos circulares interactivos que muestran la composición porcentual de los diferentes tipos de residuos
    sólidos generados en un distrito y año específicos.Permite visualizar de manera clara y dinámica la participación relativa de cada
    fracción de residuo, facilitando la identificación de los residuos predominantes y apoyando la toma de decisiones para una gestión
    más focalizada y eficiente.
    """)
    # Cargar datos
    df_residuos = pd.read_csv("BD_residuos_sólidos.csv", encoding='latin1', sep=';')
    # Selectbox para elegir distrito
    distritos = df_residuos['DISTRITO'].unique()
    distrito_sel = st.selectbox("Selecciona un distrito", sorted(distritos))
    # Selectbox para elegir años
    años = df_residuos['PERIODO'].unique()
    año_sel = st.selectbox("Selecciona un año", sorted(años))
    # Filtrar el DataFrame por año y distrito seleccionados
    filtro = (df_residuos['DISTRITO'] == distrito_sel) & (df_residuos['PERIODO'] == año_sel)
    df_filtrado = df_residuos.loc[filtro]
    # Seleccionar columnas de residuos 
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
    # Obtener solo las columnas de residuos
    residuos = df_filtrado[columnas_residuos].sum()
    
    # Crear nuevo DataFrame para el grafico
    df_grafico = pd.DataFrame({"residuo": residuos.index, "cantidad": residuos.values})
    # Convertir 'cantidad' a valores numericos (por si acaso hay strings)
    df_grafico["cantidad"] = pd.to_numeric(df_grafico["cantidad"], errors="coerce")
    # Eliminar residuos vacios o negativos
    df_grafico = df_grafico[df_grafico["cantidad"] > 0]
    # Crear grafico circular con Plotly
    fig = px.pie(df_grafico, values="cantidad", names="residuo",
                 title=f"Distribución en {distrito_sel} ({año_sel})")
    st.plotly_chart(fig, use_container_width=True)

