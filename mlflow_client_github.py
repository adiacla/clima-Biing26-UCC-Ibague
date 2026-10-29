import streamlit as st
import pandas as pd
import mlflow
import mlflow.sklearn

# ----------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA Y ENCABEZADO
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Inferencia & MLflow Tracing (Streamlit Cloud)",
    page_icon="🍷",
    layout="wide"
)

st.title("🍷 Clasificador de Vinos - Streamlit Cloud & MLflow Remote")
st.markdown(
    """
    Esta aplicación está desplegada en **Streamlit Cloud** y se conecta de forma remota al servidor de **MLflow** 
    alojado en Google Colab para realizar inferencias trazadas (**MLflow Trace**) y consultar el modelo.
    """
)

# ----------------------------------------------------------------------
# 2. BARRA LATERAL: CONFIGURACIÓN DE CONEXIÓN Y MODELO
# ----------------------------------------------------------------------
st.sidebar.header("⚙️ Configuración de Conexión MLflow")

# Cargar la URL por defecto desde st.secrets si existe
default_uri = ""
if "MLFLOW_TRACKING_URI" in st.secrets:
    default_uri = st.secrets["MLFLOW_TRACKING_URI"]

tracking_uri = st.sidebar.text_input(
    "URL del Túnel Cloudflare (Colab):",
    value=default_uri,
    placeholder="https://xxxx.trycloudflare.com",
    help="Ingresa la URL pública generada por Cloudflare en la consola de Google Colab."
)

model_uri_input = st.sidebar.text_input(
    "URI del Modelo en MLflow:",
    value="models:/m-e34eaf18ea5d490f9789ac49f36ced1a",
    help="Puedes ingresar una URI de artefacto físico (ej. models:/m-xxxx), una del Model Registry (ej. models:/NombreModelo/1) o una por Run ID (ej. runs:/<run_id>/model)."
)

# ----------------------------------------------------------------------
# 3. VALIDACIÓN DE CONEXIÓN Y CARGA DEL MODELO
# ----------------------------------------------------------------------
if not tracking_uri:
    st.warning("⚠️ Por favor, ingresa la URL pública de Cloudflare en la barra lateral para conectar con MLflow.")
    st.stop()

# Garantizar el protocolo https://
if not tracking_uri.startswith("http://") and not tracking_uri.startswith("https://"):
    tracking_uri = f"https://{tracking_uri}"

# Configurar el servidor de seguimiento de MLflow
mlflow.set_tracking_uri(tracking_uri)
try:
    mlflow.set_experiment("Clasificacion_Vinos_Streamlit_Cloud")
    st.sidebar.success("✅ Conectado a MLflow Server")
except Exception as e:
    st.sidebar.error(f"❌ Error al conectar con MLflow: {e}")

@st.cache_resource(show_spinner="Cargando modelo desde MLflow...")
def load_remote_model(server_uri, full_model_uri):
    """Carga el modelo scikit-learn guardado en MLflow usando su URI física o lógica."""
    mlflow.set_tracking_uri(server_uri)
    return mlflow.sklearn.load_model(full_model_uri)

try:
    model = load_remote_model(tracking_uri, model_uri_input)
    st.success(f"✅ Modelo cargado exitosamente desde `{model_uri_input}`")
except Exception as e:
    st.error(f"❌ No se pudo cargar el modelo desde la URI indicada: {e}")
    st.info("💡 **Consejo de solución:**\n- Revisa que el servidor de MLflow en Colab siga activo y escuchando.\n- Verifica que la URL del túnel Cloudflare sea la última generada.\n- Asegúrate de que la URI del modelo corresponda exactamente a la que existe en Colab.")
    st.stop()

# ----------------------------------------------------------------------
# 4. FUNCIÓN CON TRAZABILIDAD MLFLOW (@mlflow.trace)
# ----------------------------------------------------------------------
@mlflow.trace(name="Streamlit_Cloud_Inference_Span")
def predict_with_trace(input_df):
    """Ejecuta la predicción y envía el span de trazo automáticamente a MLflow Server."""
    return model.predict(input_df)

# ----------------------------------------------------------------------
# 5. FORMULARIO DE ENTRADA DE CARACTERÍSTICAS
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

# Construir el DataFrame de entrada con los nombres de características requeridos
input_data = pd.DataFrame([{
    'alcohol': alcohol,
    'malic_acid': malic_acid,
    'ash': ash,
    'alcalinity_of_ash': alcalinity_of_ash,
    'magnesium': magnesium,
    'total_phenols': total_phenols,
    'flavanoids': flavanoids,
    'nonflavanoid_phenols': nonflavanoid_phenols,
    'proanthocyanins': proanthocyanins,
    'color_intensity': color_intensity,
    'hue': hue,
    'od280/od315_of_diluted_wines': od280_od315,
    'proline': proline
}])

# ----------------------------------------------------------------------
# 6. EJECUCIÓN DE LA INFERENCIA Y MOSTRAR RESULTADOS
# ----------------------------------------------------------------------
if st.button("🚀 Ejecutar Predicción con MLflow Trace"):
    with st.spinner("Enviando petición e inferencia trazada a MLflow..."):
        try:
            preds = predict_with_trace(input_data)
            
            st.markdown("---")
            st.subheader("🎯 Resultado de la Predicción")
            st.success(f"**Clase Predicha:** Tipo de Vino #{preds[0]}")
            
            with st.expander("Ver vector de características de entrada"):
                st.dataframe(input_data)

            st.info("✨ **Trazabilidad Activa:** La traza de ejecución (*span*) ha sido registrada remotamente en el servidor de MLflow en Google Colab. Revisa la pestaña **Traces** en la interfaz de MLflow UI.")
        except Exception as e:
            st.error(f"❌ Error durante la inferencia o el envío del trazo: {e}")
