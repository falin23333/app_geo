import streamlit as st
from datetime import time
from datetime import datetime, time, timezone, timedelta
from zoneinfo import ZoneInfo
import mygeotab
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd



def visualizar(USERNAME,PASSWORD,DATABASE):
    st.title("📅 Selecciona una fecha")
    default_date = datetime.now().date()
    selected_date = st.date_input("Selecciona la fecha:", value=default_date)

    start_time = st.time_input("Hora inicio:", value=time(8, 0))
    end_time   = st.time_input("Hora fin:", value=time(17, 0))

    # --- Botón para descargar datos ---
    if st.button("📥 Descargar LogRecord Diario") or "df_trips" in st.session_state:
       
        
        local_tz = ZoneInfo("Europe/Madrid")

        local_from = datetime.combine(selected_date, time(0,0), tzinfo=local_tz)
        local_to   = datetime.combine(selected_date, time(23,59,59), tzinfo=local_tz)
        utc_from = local_from.astimezone(timezone.utc)
        utc_to   = local_to.astimezone(timezone.utc)

        api = mygeotab.API(username=USERNAME, password=PASSWORD, database=DATABASE)
        api.authenticate()
        trips = api.get('LogRecord', fromDate=utc_from.isoformat(), toDate=utc_to.isoformat())
        df = pd.DataFrame(trips)
        if df.empty:
            st.warning("⚠️ No hay datos para la fecha seleccionada.")
            return
        df["dateTime"] = df["dateTime"] + pd.Timedelta(hours=2)
        

       
        

        # --- Filtrar por rango de horas ---
        df["hora_local"] = df["dateTime"].dt.time
        df_filtered = df[(df["hora_local"] >= start_time) & (df["hora_local"] <= end_time)]
        df_filtered = df_filtered[(df_filtered['latitude'] != 1.0) & (df_filtered['longitude'] != 1.0)]

        if df_filtered.empty:
            st.warning("⚠️ No hay registros dentro del rango de horas seleccionado.")
            return

        # --- Visualización del trayecto ---
        if {"latitude", "longitude", "dateTime"}.issubset(df_filtered.columns):
            df_filtered = df_filtered.sort_values("dateTime")
            fig = px.line_mapbox(
                df_filtered,
                lat="latitude",
                lon="longitude",
                hover_name="dateTime",
                zoom=10,
                title="📍 Trayectoria del vehículo"
            )

            fig.add_scattermapbox(
                lat=[df_filtered["latitude"].iloc[0], df_filtered["latitude"].iloc[-1]],
                lon=[df_filtered["longitude"].iloc[0], df_filtered["longitude"].iloc[-1]],
                mode="markers+text",
                text=["Inicio","Fin"],
                textposition="top right",
                marker=dict(size=10, color=["green","red"]),
                name="Puntos clave"
            )
            df_filtered = df_filtered.sort_values("dateTime")

            fig = px.line_mapbox(
                df_filtered,
                lat="latitude",
                lon="longitude",
                hover_data={
                    "dateTime": True,   # Fecha y hora
                    "speed": True,      # Velocidad
                    "latitude": False,  # Ocultar lat/lon en hover si quieres
                    "longitude": False
                },
                zoom=10,
                title="📍 Trayectoria del vehículo"
            )

            # Marcadores de inicio y fin
            fig.add_scattermapbox(
                lat=[df_filtered["latitude"].iloc[0], df_filtered["latitude"].iloc[-1]],
                lon=[df_filtered["longitude"].iloc[0], df_filtered["longitude"].iloc[-1]],
                mode="markers+text",
                text=["Inicio","Fin"],
                textposition="top right",
                marker=dict(size=10, color=["green","red"]),
                name="Puntos clave"
            )

            fig.update_layout(
                mapbox_style="open-street-map",
                height=600,
                margin={"r":0,"t":30,"l":0,"b":0}
            )

            st.plotly_chart(fig, use_container_width=True)
            
                
def main(USERNAME,PASSWORD,DATABASE):
    st.title("📍 GPS Viewer")

    st.markdown("""
    Selecciona el **día** que deseas visualizar y ajusta la **hora de inicio** y **hora de fin** del viaje.  
    El mapa mostrará la **ruta completa del vehículo**, indicando la posición en cada momento.  
    Al pasar el ratón sobre la ruta, podrás ver información detallada como:  
    - **Fecha y hora** de cada punto  
    - **Velocidad** del vehículo  

    Esto te permite, por ejemplo, **ver a qué hora llega a casa** o en qué momentos se realizaron diferentes tramos del recorrido.
    """)
    visualizar(USERNAME,PASSWORD,DATABASE)
     

    
       
            

    