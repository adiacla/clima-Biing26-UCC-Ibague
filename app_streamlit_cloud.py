import streamlit as st
import pandas as pd
import mlflow
import mlflow.sklearn
import os

# ----------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA Y SIDEBAR
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Inferencia & MLflow Tracing (Streamlit Cloud)",
    page_icon="🍷",
    layout="wide"
)

st.title("🍷 Clasificador de Vinos - Streamlit Cloud & MLflow Remote")
st.write(
    "Esta aplicación desplegada en **Streamlit Cloud** consume el modelo y registra "
    "los trazos (**MLflow Trace**) en el servidor de **MLflow** alojado en Google Colab."
)

st.sidebar.header("⚙️ Configuración de Conexión MLflow")

# Obtener URL por defecto desde st.secrets si existe, o dejar campo de texto
default_uri = ""
if "MLFLOW_TRACKING_URI" in st.secrets:
    default_uri = st.secrets["MLFLOW_TRACKING_URI"]

tracking_uri = st.sidebar.text_input(
    "URL del Túnel Cloudflare (Colab):",
    value=default_uri,
    placeholder="https://xxxx.trycloudflare.com",
    help="Ingresa la URL pública generada por Cloudflare en el cuaderno de Google Colab."
)

MODEL_NAME = st.sidebar.text_input("Nombre del Modelo Registrado:", value="Modelo_Clasificador_Vinos_ISO42001")
MODEL_VERSION = st.sidebar.text_input("Versión del Modelo:", value="1")

# ----------------------------------------------------------------------
# 2. VALIDACIÓN DE LA CONEXIÓN Y CARGA DEL MODELO
# ----------------------------------------------------------------------
if not tracking_uri:
    st.warning("⚠️ Por favor, ingresa la URL pública de Cloudflare en la barra lateral para conectar con MLflow.")
    st.stop()

# Formatear protocolo si falta
if not tracking_uri.startswith("http://") and not tracking_uri.startswith("https://"):
    tracking_uri = f"https://{tracking_uri}"

# Configurar el servidor de MLflow
mlflow.set_tracking_uri(tracking_uri)
try:
    mlflow.set_experiment("Clasificacion_Vinos_Streamlit_Cloud")
    st.sidebar.success("✅ Conectado a MLflow Server")
except Exception as e:
    st.sidebar.error(f"❌ Error conectando a MLflow: {e}")

@st.cache_resource(show_spinner="Cargando modelo desde MLflow Registry...")
def load_remote_model(uri, name, version):
    mlflow.set_tracking_uri(uri)
    model_uri = f"models:/{name}/{version}"
    return mlflow.sklearn.load_model(model_uri)

try:
    model = load_remote_model(tracking_uri, MODEL_NAME, MODEL_VERSION)
    st.success(f"✅ Modelo **'{MODEL_NAME}'** (v{MODEL_VERSION}) cargado correctamente desde Google Colab.")
except Exception as e:
    st.error(f"❌ No se pudo cargar el modelo desde la URI indicada: {e}")
    st.info("Verifica que el servidor de MLflow en Colab esté activo y que la URL de Cloudflare sea correcta.")
    st.stop()

# ----------------------------------------------------------------------
# 3. FUNCIÓN CON TRAZABILIDAD MLFLOW (@mlflow.trace)
# ----------------------------------------------------------------------
@mlflow.trace(name="Streamlit_Cloud_Inference_Span")
def predict_with_trace(input_df):
    """Ejecuta la predicción y envía la traza de ejecución al servidor de MLflow."""
    return model.predict(input_df)

# ----------------------------------------------------------------------
# 4. FORMULARIO DE ENTRADA Y PREDICCIÓN
# ----------------------------------------------------------------------
st.subheader("📋 Parámetros Químicos del Vino")

col1, col2, col3 = st.columns(3)

with col1:
    alcohol = st.number_input("Alcohol", value=13.0, step=0.1)
    malic_acid = st.number_input("Malic Acid", value=2.3, step=0.1)
    ash = st.number_input("Ash", value=2.36, step=0.01)
    alcalinity_of_ash = st.number_input("Alcalinity of Ash", value=18.6, step=0.5)

with col2:
    magnesium = st.number_input("Magnesium", value=101.0, step=1.0)
    total_phenols = st.number_input("Total Phenols", value=2.8, step=0.1)
    flavanoids = st.number_input("Flavanoids", value=2.98, step=0.1)
    nonflavanoid_phenols = st.number_input("Nonflavanoid Phenols", value=0.29, step=0.01)

with col3:
    proanthocyanins = st.number_input("Proanthocyanins", value=1.8, step=0.1)
    color_intensity = st.number_input("Color Intensity", value=5.1, step=0.1)
    hue = st.number_input("Hue", value=1.04, step=0.01)
    od280_od315 = st.number_input("OD280/OD315 of diluted wines", value=3.1, step=0.1)
    proline = st.number_input("Proline", value=1065.0, step=10.0)

input_data = pd.DataFrame([{
    'alcohol': alcohol, 'malic_acid': malic_acid, 'ash': ash,
    'alcalinity_of_ash': alcalinity_of_ash, 'magnesium': magnesium,
    'total_phenols': total_phenols, 'flavanoids': flavanoids,
    'nonflavanoid_phenols': nonflavanoid_phenols, 'proanthocyanins': proanthocyanins,
    'color_intensity': color_intensity, 'hue': hue,
    'od280/od315_of_diluted_wines': od280_od315, 'proline': proline
}])

if st.button("🚀 Ejecutar Predicción con MLflow Trace"):
    with st.spinner("Enviando petición a modelo y registrando traza en MLflow..."):
        try:
            preds = predict_with_trace(input_data)
            
            st.markdown("---")
            st.subheader("🎯 Resultado de la Predicción")
            st.success(f"**Clase Predicha:** Tipo de Vino #{preds[0]}")
            
            with st.expander("Ver vector de características enviado"):
                st.dataframe(input_data)

            st.info("✨ **Trazabilidad Activa:** El trazo de ejecución (*span*) ha sido registrado remotamente en el servidor de MLflow en Google Colab.")
        except Exception as e:
            st.error(f"❌ Error durante la inferencia o envío del trazo: {e}")
