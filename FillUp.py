import pandas as pd
df = pd.read_csv("FillUp.csv")
import plotly.express as px
import streamlit as st
import ast
import pydeck as pdk
import streamlit as st
import mygeotab

    

def main(df):
    st.markdown("""
    # ⛽ ENTIDAD **FILLUP** (Geotab)

    La entidad **FillUp** almacena la información relacionada con **repostajes de combustible** realizados por los vehículos.  
    Es fundamental para analizar el **consumo de combustible**, los **costos asociados** y detectar posibles **anomalías o fraudes**.  

    ---

    ## 📋 CAMPOS PRINCIPALES

    | Columna              | Descripción breve                                                                 |
    |-----------------------|-----------------------------------------------------------------------------------|
    | **distance**          | Distancia recorrida desde el último repostaje.                                   |
    | **device**            | Vehículo asociado al repostaje.                                                  |
    | **driver**            | Conductor asignado en el momento del repostaje.                                  |
    | **totalFuelUsed**     | Cantidad total de combustible consumido hasta ese momento (litros).              |
    | **tankLevelExtrema**  | Niveles mínimos y máximos de combustible en el tanque durante el intervalo.      |
    | **tankCapacity**      | Capacidad total del tanque de combustible.                                       |
    | **fuelTransactions**  | Detalles de las transacciones de combustible vinculadas.                         |
    | **derivedVolume**     | Volumen de combustible calculado a partir de datos de telemetría.                |
    | **odometer**          | Odómetro del vehículo en el momento del repostaje.                               |
    | **volume**            | Volumen de combustible repostado (litros).                                       |
    | **cost**              | Costo del repostaje en la moneda especificada.                                   |
    | **currencyCode**      | Código de moneda del costo (ej: EUR, USD).                                       |
    | **location**          | Ubicación donde se realizó el repostaje.                                         |
    | **dateTime**          | Fecha y hora del repostaje.                                                      |
    | **productType**       | Tipo de combustible (ej: Diesel, Gasolina).                                      |
    | **confidence**        | Nivel de confianza en los datos (ej: confirmado, estimado).                      |
    | **version**           | Versión interna del registro.                                                    |
    | **id**                | Identificador único del evento de repostaje.                                     |

    ---

    ## 🔎 UTILIDAD EN GESTIÓN DE FLOTAS

    - Monitorear **consumo real de combustible** y eficiencia de los vehículos.  
    - Identificar **patrones de gasto** por conductor, vehículo o ruta.  
    - Detectar **inconsistencias** entre repostajes y consumo esperado.  
    - Controlar **costos de operación** y optimizar rutas de carga de combustible.  

    👉 En resumen, `FillUp` es clave para el **control de gastos y optimización del rendimiento de la flota**.
    """)
   

    st.write("---")
        # --- Preparar columna FuelTankCapacity ---
    def safe_eval(x):
        try:
            return ast.literal_eval(str(x))
        except:
            return {}

    df['tankCapacity_dict'] = df['tankCapacity'].apply(safe_eval)
    df['tankVolume'] = df['tankCapacity_dict'].apply(lambda x: x.get('volume', None))
    df['tankSource'] = df['tankCapacity_dict'].apply(lambda x: x.get('source', None))

    # --- Título ---
    st.markdown("## ⛽ FILLUP - COMBUSTIBLE")
    st.markdown(
        """
        Esta sección muestra los repostajes de combustible de los vehículos, 
        incluyendo volumen repostado, distancia recorrida, capacidad de tanque y origen de la medición.
        """
    )

    # --- Métricas ---
    st.subheader("📊 MÉTRICAS")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Combustible total repostado (L)", f"{df['totalFuelUsed'].sum():.2f}")
    

    st.markdown("---")

    # --- Tabla con volumen y fuente ---
    st.subheader("📝 Detalle de tanques")
    st.dataframe(df[['tankVolume','tankSource','totalFuelUsed','distance','device','dateTime']])

    st.markdown("---")

    # --- Gráfico distancia vs combustible ---
    st.subheader("📈 Distancia vs Combustible usado")
    fig1 = px.scatter(
        df,
        x="totalFuelUsed",
        y="distance",
        color="tankSource",
        hover_data=["device","dateTime"],
        labels={"totalFuelUsed":"Combustible usado (L)","distance":"Distancia recorrida (km)","tankSource":"Origen"},
        title="Relación entre combustible usado y distancia recorrida"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Gráfico volumen tanque vs combustible usado ---
    st.subheader("⛽ Capacidad del tanque vs Combustible usado")
    fig2 = px.scatter(
        df,
        x="tankVolume",
        y="totalFuelUsed",
        color="tankSource",
        hover_data=["device","dateTime"],
        labels={"tankVolume":"Volumen del tanque (L)","totalFuelUsed":"Combustible usado (L)","tankSource":"Origen"},
        title="Relación entre capacidad del tanque y combustible usado"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.write("---")

    st.title("Ubicación de los repostajes")

    if 'location' in df.columns:
        def parse_location(val):
            if pd.isna(val):
                return None, None
            try:
                loc = ast.literal_eval(val) if isinstance(val, str) else val
                # Ajusta según cómo vengan los datos: 'y'/'x' o 'latitude'/'longitude'
                lat = loc.get('y') or loc.get('latitude')
                lon = loc.get('x') or loc.get('longitude')
                return lat, lon
            except Exception as e:
                return None, None

        df[['lat', 'lon']] = df['location'].apply(lambda x: pd.Series(parse_location(x)))

        # Filtrar filas válidas
        df_map = df.dropna(subset=['lat', 'lon'])

        st.write(df_map[['lat', 'lon']].head())
        st.map(df_map)
    else:
        st.warning("No se encontró la columna 'location' en el DataFrame")