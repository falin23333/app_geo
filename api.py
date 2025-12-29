import streamlit as st
import mygeotab
import pandas as pd
import io
import zipfile

def descargar(username, password):
    DATABASE = "dieboldnixdorf"
    st.title("📡 Extracción de datos Geotab")
    st.write("Conectando con la API y descargando colecciones...")

    # --- Autenticación API ---
    with st.spinner("Autenticando..."):
        api = mygeotab.API(username=username, password=password, database=DATABASE)
        api.authenticate()
    st.success("✅ Autenticación exitosa")

    # --- Colecciones a descargar ---
    collections = [
        "A1","AddInData","AnnotationLog","Audit","BinaryPayload","Condition","Controller",
        "CustomData","CustomDevice","DataDiagnostic","DebugData","Device","DeviceShare",
        "DeviceStatusInfo","Diagnostic","DistributionList","Driver","DriverChange",
        "DutyStatusAvailability","DutyStatusLog","DutyStatusViolation","DVIRLog",
        "EmissionVehicleEnrollment","ExceptionEvent","FailureMode","FaultData","FillUp",
        "FlashCode","FuelTaxDetail","FuelUsed","FuelTransaction","Go5","Go6","Go7","Go8",
        "Go9","Go9B","GoCurve","GoCurveAuxiliary","GoDevice","Group","GroupSecurity",
        "IoxAddOn","LogRecord","MediaFile","ParameterGroup","Recipient","RequestLocation",
        "Route","RoutePlanItem","Rule","SecurityClearance","ShipmentLog","Source",
        "StatusData","TachographDataFile","TextMessage","Trailer","TrailerAttachment",
        "Trip","UnitOfMeasure","User","WifiHotspot","WorkTimeDetail","Zone"
    ]

    dataframes = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    total_collections = len(collections)

    for idx, col in enumerate(collections, start=1):
        status_text.text(f"⏳ Descargando {col} ({idx}/{total_collections})...")
        try:
            all_data = api.get(col)
        except Exception as e:
            st.warning(f"❌ Error descargando {col}: {e}")
            continue

        if all_data:
            df = pd.DataFrame(all_data)
            dataframes[col] = df
            st.success(f"{col}: {len(df)} filas guardadas")
        else:
            st.info(f"{col}: sin datos")

        progress_bar.progress(idx / total_collections)

    st.balloons()
    st.success("✅ Extracción completa.")
    return dataframes

def descargar_y_comprimir(dataframes):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for col, df in dataframes.items():
            csv_bytes = df.to_csv(index=False).encode('utf-8')
            zf.writestr(f"{col}.csv", csv_bytes)
    zip_buffer.seek(0)

    st.download_button(
        label="📥 Descargar todos los CSV en ZIP",
        data=zip_buffer,
        file_name="geotab_data.zip",
        mime="application/zip"
    )

def botonAPI():
    st.sidebar.title("Login para descargar datos")
    
    # Inicializar variables de sesión
    if "username_api" not in st.session_state:
        st.session_state.username_api = ""
    if "password_api" not in st.session_state:
        st.session_state.password_api = ""
    if "api_logged_in" not in st.session_state:
        st.session_state.api_logged_in = False

    # Formulario de login
    with st.sidebar.form("login_api_form"):
        username_input = st.text_input("Usuario (email)", value=st.session_state.username_api)
        password_input = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("🔑 Conectar API")
    
    if submitted:
        try:
            api = mygeotab.API(username=username_input, password=password_input, database="dieboldnixdorf")
            api.authenticate()
            st.session_state.username_api = username_input
            st.session_state.password_api = password_input
            st.session_state.api_logged_in = True
            st.sidebar.success("✅ Autenticación correcta")
        except Exception as e:
            st.session_state.api_logged_in = False
            st.sidebar.error("❌ Usuario o contraseña incorrectos")

    # Botón para descargar datos solo si login fue exitoso
    if st.session_state.api_logged_in:
        if st.button("📡 Descargar datos Geotab"):
            dataframes = descargar(st.session_state.username_api, st.session_state.password_api)
            if dataframes:
                st.write("Datos descargados con éxito. Puedes descargarlos como ZIP:")
                descargar_y_comprimir(dataframes)
