import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import DBSCAN
import numpy as np
import mygeotab
import datetime
import ast

def time_to_timedelta(t):
    if pd.isna(t):
        return pd.Timedelta(0)
    if isinstance(t, datetime.time):
        return pd.Timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    return pd.to_timedelta(t)


       





def muestra_km_total_horario_fuerahorario(data):
        # Asegurarse de que 'start' sea datetime y ordenar
    data['start'] = pd.to_datetime(data['start'])
    data = data.sort_values('start')

    # Distancia total acumulada
    data['distance_acum'] = data['distance'].cumsum()

    # Distancia acumulada fuera de horario
    data['afterHours_acum'] = data[data['afterHoursStart'] == True]['afterHoursDistance'].cumsum()

    # Distancia acumulada en horario laboral
    data['work_acum'] = data[data['afterHoursStart'] == False]['distance'].cumsum()  # ojo, usar distance no afterHoursDistance

    # Como las series tienen índices diferentes, hacemos merge en 'start'
    df_plot = pd.DataFrame({
        'start': data['start'],
        'Total': data['distance_acum'],
        'Fuera de horario': data['afterHours_acum'].reindex(data.index, fill_value=0),
        'En horario laboral': data['work_acum'].reindex(data.index, fill_value=0)
    })

    # Convertir a formato long para plotly
    df_long = df_plot.melt(
        id_vars='start', 
        value_vars=['Total','En horario laboral','Fuera de horario'],
        var_name='Tipo', value_name='Kilómetros acumulados'
    )

    # Definir colores para que sean visibles sobre fondo negro
    color_map = {
        'Total': 'blue',
        'En horario laboral': 'purple',
        'Fuera de horario': 'red'
    }

    # Gráfico
    fig = px.line(
        df_long, x='start', y='Kilómetros acumulados', color='Tipo', markers=True,
        color_discrete_map=color_map,
        title='Odometer: Distancia acumulada por tipo',
        labels={'start':'Fecha','Kilómetros acumulados':'Distancia acumulada (km)'}
    )

    # Estilo oscuro
    fig.update_layout(
        plot_bgcolor='black', 
        paper_bgcolor='black', 
        font_color='white',
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )

    st.plotly_chart(fig, use_container_width=True)




def fechas_seleecionadas(data):
    fechas = pd.to_datetime(data["start"])
    fecha_min = fechas.min().date()
    fecha_max = fechas.max().date()
    return f'{fecha_min} al {fecha_max}'

def intro_km(data):
    
    hoy = pd.Timestamp.today(tz="UTC")
    hace_7 = hoy - pd.Timedelta(days=7)
    # Semana: últimos 7 días según los datos reales
    hace_7 = data['start'].max() - pd.Timedelta(days=7)
    hoy = data['start'].max()

    data_semana = data[(data['start'] >= hace_7) & (data['start'] <= hoy)]
    data_hoy = data[data['start'].dt.date == hoy.date()]
    hist_en_horario = data['workDistance'].sum()
    hist_fuera_horario = data['afterHoursDistance'].sum()
    
    semana_en_horario = data_semana['workDistance'].sum()
    semana_fuera_horario = data_semana['afterHoursDistance'].sum()
    data_hoy = data[data['start'].dt.date == hoy.date()]
    hoy_en_horario = data_hoy['workDistance'].sum()
    hoy_fuera_horario = data_hoy['afterHoursDistance'].sum()

    # INTRODUCCIÓN
    st.markdown("## 🚌 ENTIDAD TRIP")
    st.markdown("""
    La entidad **Trip** representa los **viajes realizados por un vehículo** dentro de un rango de tiempo definido.  

    
    """)
    

    st.markdown("## Descripción de columnas de `Trip` (Geotab)")

    st.markdown("""
    - **afterHoursDistance**: Distancia recorrida fuera del horario laboral.  
    - **afterHoursDrivingDuration**: Duración de conducción fuera de horario laboral.  
    - **afterHoursEnd**: Indica si el viaje terminó fuera de horario laboral (`True/False`).  
    - **afterHoursStart**: Indica si el viaje empezó fuera de horario laboral (`True/False`).  
    - **afterHoursStopDuration**: Tiempo detenido fuera del horario laboral.  
    - **averageSpeed**: Velocidad media durante el viaje (km/h).  
    - **distance**: Distancia total recorrida en el viaje (km).  
    - **drivingDuration**: Tiempo total de conducción.  
    - **engineHours**: Horas de motor acumuladas durante el viaje.  
    - **idlingDuration**: Tiempo total en ralentí (motor encendido sin movimiento).  
    - **isSeatBeltOff**: Indica si el cinturón estaba desabrochado en algún momento (`True/False`).  
    - **maximumSpeed**: Velocidad máxima alcanzada en el viaje (km/h).  
    - **nextTripStart**: Fecha/hora de inicio del siguiente viaje.  
    - **speedRange1**: Número de minutos en rango de baja velocidad.  
    - **speedRange1Duration**: Duración total en rango de baja velocidad.  
    - **speedRange2**: Número de minutos en rango de velocidad media.  
    - **speedRange2Duration**: Duración total en rango de velocidad media.  
    - **speedRange3**: Número de minutos en rango de alta velocidad.  
    - **speedRange3Duration**: Duración total en rango de alta velocidad.  
    - **start**: Fecha/hora de inicio del viaje.  
    - **stop**: Fecha/hora de fin del viaje.  
    - **stopDuration**: Tiempo total detenido en el viaje.  
    - **stopPoint**: Punto geográfico donde terminó el viaje.  
    - **workDistance**: Distancia recorrida dentro del horario laboral.  
    - **workDrivingDuration**: Duración de conducción dentro del horario laboral.  
    - **workStopDuration**: Tiempo detenido dentro del horario laboral.  
    - **device**: Dispositivo (vehículo) asociado al viaje.  
    - **driver**: Conductor asignado al viaje (si está identificado).  
    - **version**: Versión interna del registro (control de cambios).  
    - **id**: Identificador único del viaje en la base de Geotab.
    """)
    st.dataframe(data)
    st.markdown("---")
    
    

    # Título principal
    st.markdown(f"<h2 style='color:cyan;'>📝 MÉTRICAS GENERALES: {fechas_seleecionadas(data)}</h2>", unsafe_allow_html=True)

    # Métricas principales
    
    sumaKM_fuera_horario = data["afterHoursDistance"].sum()
    sumaKM_en_horario = data[data["afterHoursStart"] == False]["distance"].sum()
    data['idlingDuration_td'] = data['idlingDuration'].apply(time_to_timedelta)

    total_idling = data['idlingDuration_td'].sum()
    total_horas = total_idling.total_seconds() / 3600

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color:#1f77b4;'>📊 DISTANCIAS</h3>", unsafe_allow_html=True)
        st.metric(label="Kilómetros en HORARIO LABORAL", value=f"{round(sumaKM_en_horario)} km", delta_color="normal")
        st.metric(label="Kilómetros FUERA DE HORARIO", value=f"{round(sumaKM_fuera_horario)} km", delta_color="inverse")
        
        st.markdown("<h3 style='color:#ff7f0e;'>⏱ TIEMPOS</h3>", unsafe_allow_html=True)
        st.metric(label="Tiempo total en RALENTÍ (h)", value=f"{round(total_horas,2)} h", delta_color="normal")

    with col2:
        st.markdown("<h3 style='color:#2ca02c;'>⚡ VELOCIDAD Y SEGURIDAD</h3>", unsafe_allow_html=True)
        st.metric(label="Velocidad máxima (km/h)", value=f"{round(data['maximumSpeed'].max())}", delta_color="normal")
        st.metric(label="Cinturón desabrochado", value=f"{round(data['isSeatBeltOff'].sum())}", delta_color="inverse")
        st.metric(label="Minutos baja velocidad", value=f"{round(data['speedRange1'].sum())} min", delta_color="normal")
        st.metric(label="Minutos media velocidad", value=f"{round(data['speedRange2'].sum())} min", delta_color="normal")
        st.metric(label="Minutos alta velocidad", value=f"{round(data['speedRange3'].sum())} min", delta_color="normal")

    
    st.markdown("---")

    
    st.markdown(f"<h2 style='color:cyan;'>📝 GRÁFICOS KILOMETROS GENERALES</h2>", unsafe_allow_html=True)
    
    fig_hist = px.pie(
        names=['Laboral','Fuera de horario'],
        values=[hist_en_horario,hist_fuera_horario],
        color_discrete_map={'Laboral':'#1f77b4','Fuera de horario':'#ff7f0e'},
        title="Histórico total KILOMETROS EN HORARIO VS FUERA DE HORARIO"
    )
    fig_hist.update_traces(textinfo="label+percent+value", hovertemplate="%{label}: %{value:.1f} km<br>(%{percent})")
    fig_hist.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', title_font_size=16)
    st.plotly_chart(fig_hist, use_container_width=True)

    
    fig_semana = px.pie(
        names=['Laboral','Fuera de horario'],
        values=[semana_en_horario, semana_fuera_horario],
        color_discrete_map={'Laboral':'#1f77b4','Fuera de horario':'#ff7f0e'},
        title="Semana anterior KILOMETROS EN HORARIO VS FUERA DE HORARIO"
    )
    fig_semana.update_traces(textinfo="label+percent+value", hovertemplate="%{label}: %{value:.1f} km<br>(%{percent})")
    fig_semana.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', title_font_size=16)
    st.plotly_chart(fig_semana, use_container_width=True)

    """
    fig_hoy = px.pie(
        names=['Laboral','Fuera de horario'],
        values=[hoy_en_horario, hoy_fuera_horario],
        color_discrete_map={'Laboral':'#1f77b4','Fuera de horario':'#ff7f0e'},
        title="Hoy KILOMETROS EN HORARIO VS FUERA DE HORARIO"
    )
    fig_hoy.update_traces(textinfo="label+percent+value", hovertemplate="%{label}: %{value:.1f} km<br>(%{percent})")
    fig_hoy.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', title_font_size=16)
    st.plotly_chart(fig_hoy, use_container_width=True)

    st.markdown("---")
    """
    
    # GRÁFICO LÍNEA EVOLUCIÓN KM DIARIOS
    data['start'] = pd.to_datetime(data['start'])
    daily_avg = data.groupby(data['start'].dt.date)['distance'].sum().reset_index()
    fig = px.line(
        daily_avg, x="start", y="distance",
        markers=True,
        title="Evolución de kilómetros diarios",
        labels={"start":"Fecha","distance":"Distancia (km)"}
    )
    fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white', xaxis=dict(showgrid=True, gridcolor='gray'), yaxis=dict(showgrid=True, gridcolor='gray'))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    muestra_km_total_horario_fuerahorario(data)

    st.markdown("---")
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    # Top 3
    top3_hoy = data_hoy.sort_values(by="maximumSpeed", ascending=False).head(5)
    top3_semana = data_semana.sort_values(by="maximumSpeed", ascending=False).head(5)
    top3_historico = data.sort_values(by="maximumSpeed", ascending=False).head(5)

    # Crear subplot vertical de 3 filas
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=False,
        subplot_titles=("🏆 TOP 5 Histórico", "📅 TOP 5 Semana", "🔥 TOP 5 Hoy")
    )

    # Función para añadir barras a subplot
    def add_bar_subplot(df, color, row):
        df = df.copy()
        df['start_str'] = df['start'].dt.strftime('%Y-%m-%d %H:%M')
        fig.add_trace(
            go.Bar(
                x=df['start_str'],
                y=df['maximumSpeed'],
                text=df['maximumSpeed'],
                textposition='outside',
                marker_color=color,
                name=""
            ),
            row=row, col=1
        )

    # Añadir los tres gráficos
    add_bar_subplot(top3_historico, '#0074D9', 1)
    add_bar_subplot(top3_semana, '#FF851B', 2)
    add_bar_subplot(top3_hoy, '#FF4136', 3)

    # Layout general
    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        showlegend=False,
        height=900,  # aumentar altura total
        title_text="🏎️ Top 3 Velocidades Máximas KM/H: Histórico, Semana, Hoy",
        title_font_size=22
    )

    # Ajustar eje Y para todas las filas
    fig.update_yaxes(range=[0,200], showgrid=True, gridcolor='gray')

    # Ajustar eje X
    fig.update_xaxes(showgrid=True, gridcolor='gray', tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)


    st.markdown("---")
    stop = data.copy()
    stop['lon'] = stop['stopPoint'].apply(lambda p: p['x'])
    stop['lat'] = stop['stopPoint'].apply(lambda p: p['y'])

   
    # stop tiene tus columnas lat/lon
    lat = stop['lat'].to_numpy()
    lon = stop['lon'].to_numpy()

    # Convertir lat/lon a coordenadas en metros usando proyección simple
    # 1° lat ≈ 111 km, 1° lon ≈ 111 km * cos(lat)
    x = lon * 111_000 * np.cos(np.radians(lat.mean()))  # metros
    y = lat * 111_000  # metros

    coords_m = np.vstack((x, y)).T

    # DBSCAN con eps en metros (ej. 100 m)
    db = DBSCAN(eps=100, min_samples=5).fit(coords_m)
    stop['cluster'] = db.labels_

    # Filtrar solo clusters reales (descartar ruido)
    clusters_validos = stop[stop['cluster'] != -1]

    # Visualización
    fig = px.scatter_mapbox(
        clusters_validos,
        lat='lat',
        lon='lon',
        color='cluster',
        zoom=12,
        mapbox_style="carto-darkmatter",
        title="Puntos calientes de paradas (≥5 paradas en radio 100 m) o lugares frecuentados"
    )
    st.plotly_chart(fig, use_container_width=True)
