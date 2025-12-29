import streamlit as st
import pandas as pd
import km
import api
import exceptionEvent
import FillUp
import viewer_trip
import mygeotab

DATABASE = "dieboldnixdorf"

# Inicializar variables de sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "api_instance" not in st.session_state:
    st.session_state.api_instance = None

# ---------------------------------------
# Formulario de login
# ---------------------------------------
if not st.session_state.logged_in:
    st.sidebar.title("Login")
    with st.sidebar.form("login_form"):
        username_input = st.text_input("Usuario (email)")
        password_input = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")
    
    if submitted:
        try:
            api_instance = mygeotab.API(username=username_input, password=password_input, database=DATABASE)
            api_instance.authenticate()
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.session_state.password = password_input
            st.session_state.api_instance = api_instance
            st.sidebar.success("✅ Conectado correctamente")
        except Exception as e:
            st.sidebar.error("❌ Usuario o contraseña incorrectos")

# ---------------------------------------
# Cargar app solo si login correcto
# ---------------------------------------
if st.session_state.logged_in:
    opcion = st.sidebar.radio(
        "Navegación",
        ("Inicio", "API" ,"Trips","ExceptionEvent","FillUp","GPS Route Viewer")
    )

    api_instance = st.session_state.api_instance

    if opcion == "Inicio":
        st.markdown("""
        ## 🚀 Geotab Visualizer
        Explora el potencial de la **API de Geotab** en telemetría y gestión de flotas.
        """)

        deviceStatusInfo = pd.DataFrame(api_instance.get('DeviceStatusInfo'))
        device = pd.DataFrame(api_instance.get('Device'))

        info_vehiculo = {
            "Matrícula": device["licensePlate"][0],
            "Conductor": device["name"],
            "Coche": device["comment"],
            "Bastidor": device["engineVehicleIdentificationNumber"][0],
            "Dispositivo Comunicando": deviceStatusInfo["isDeviceCommunicating"],
            "Vehiculo en Movimiento": deviceStatusInfo["isDriving"]
        }

        deviceStatusInfo = deviceStatusInfo.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(deviceStatusInfo, zoom=8)

        df = pd.DataFrame(info_vehiculo)
        st.subheader("🚗 Información del Vehículo")
        st.table(df)

    if opcion == "Trips":
        trips = api_instance.get('Trip')
        data = pd.DataFrame(trips)   
        data["start"] = pd.to_datetime(data["start"], utc=True) + pd.Timedelta(hours=2)
        data["stop"] = pd.to_datetime(data["stop"], utc=True) + pd.Timedelta(hours=2)
        data["nextTripStart"] = pd.to_datetime(data["nextTripStart"], utc=True) + pd.Timedelta(hours=2)
        st.dataframe(data)
        km.intro_km(data)

    if opcion == "API":
        api.botonAPI()

    if opcion == "ExceptionEvent":
        exceptionEvent.main()

    if opcion == "FillUp":
        df = pd.DataFrame(api_instance.get('FillUp'))
        FillUp.main(df)

    if opcion == "GPS Route Viewer":
        viewer_trip.main(st.session_state.username, st.session_state.password, DATABASE)

else:
    st.warning("🔒 Por favor, ingresa tus credenciales para acceder a la aplicación.")
