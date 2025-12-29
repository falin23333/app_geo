import pandas as pd
df = pd.read_csv("ExceptionEvent.csv")
import plotly.express as px
import streamlit as st
def main():
    st.markdown("""
    # 📌 EXCEPTIONEVENT

    La entidad **`ExceptionEvent`** en la API de **Geotab** representa un **evento generado cuando un vehículo viola una regla configurada** en MyGeotab (por ejemplo: exceso de velocidad, conducción fuera de horario, entrada o salida de zonas, etc.).  
    Se usa para **monitorear infracciones de conducción, seguridad y cumplimiento**.

    ---

    ## 🔎 DESCRIPCIÓN GENERAL
    Un **ExceptionEvent** indica **cuándo, dónde y por qué** se incumplió una regla.  
    Cada evento contiene información del vehículo, conductor, tiempo de inicio y fin, así como detalles de la regla y diagnóstico asociado.

    ---

    ## 📊 CAMPOS PRINCIPALES

    | <span style="color:#4CAF50">**Columna**</span> | <span style="color:#2196F3">**Descripción**</span> |
    |---------------------------|-----------------------------------------------------------------------------------|
    | **activeFrom**            | Fecha y hora en que comenzó la infracción. |
    | **activeTo**              | Fecha y hora en que terminó la infracción. |
    | **distance**              | Distancia recorrida durante el evento de excepción (ej: km a exceso de velocidad). |
    | **duration**              | Duración total de la excepción (ej: minutos en infracción). |
    | **rule**                  | Regla de MyGeotab que se violó (ej: *Exceso de velocidad*, *Fuera de horario*). |
    | **device**                | Vehículo/dispositivo asociado al evento. |
    | **diagnostic**            | Información diagnóstica asociada (ej: *Device unplugged*, *Accident event*). |
    | **driver**                | Conductor identificado (si aplica). |
    | **state**                 | Estado de la excepción (ej: activa o resuelta). |
    | **lastModifiedDateTime**  | Última vez que se actualizó este evento. |
    | **version**               | Versión del registro (interno de control de cambios). |
    | **id**                    | Identificador único del evento. |

    ---

    ## 🛠️ EJEMPLOS COMUNES DE EVENTOS
    - **Exceso de velocidad** → vehículo supera límite configurado.  
    - **Conducción fuera de horario** → movimiento fuera del rango laboral.  
    - **Entrada/salida de zona (Geofence)** → cruce de áreas predefinidas.  
    - **Dispositivo desconectado o reiniciado** → ej: `DiagnosticDeviceHasBeenUnpluggedId`.  
    - **Evento de accidente** → ej: `DiagnosticAccidentLevelAccelerationEventId`.  

    ---
    """, unsafe_allow_html=True)

    st.write("---")
   
    st.markdown("EVOLUCIÓN TEMPORAL DE EVENTOS DE EXCEPTION")
    # Asegurarnos que la fecha sea tipo datetime
    df["activeFrom"] = pd.to_datetime(df["activeFrom"])

    # Contar eventos por fecha y diagnóstico
    eventos_por_fecha = df.groupby([df["activeFrom"].dt.date, "diagnostic"]).size().reset_index(name="count")

    # Gráfico de líneas (evolución temporal de excepciones)
    fig = px.line(
        eventos_por_fecha,
        x="activeFrom",
        y="count",
        color="diagnostic",
        markers=True,
        title="EVOLUCIÓN TEMPORAL",
        labels={"activeFrom": "Fecha de inicio", "count": "Número de eventos", "diagnostic": "Tipo de diagnóstico"}
    )

    # Personalización estética
    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        title=dict(x=0.5, font=dict(size=20, color="#FF9800")),
        xaxis=dict(showgrid=True, gridcolor="gray"),
        yaxis=dict(showgrid=True, gridcolor="gray"),
        hovermode="x unified"
    )

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
