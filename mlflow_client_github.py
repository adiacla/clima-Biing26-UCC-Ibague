"""
MLflow Remote Client for GitHub Repository
------------------------------------------
Este script permite entrenar, registrar métricas/artefactos y ejecutar inferencias
trazadas (@mlflow.trace) desde cualquier entorno local o pipeline de GitHub,
conectándose directamente al servidor servidor de MLflow alojado en Google Colab.
"""

import argparse
import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature


def get_tracking_uri():
    """
    Obtiene la URI de MLflow en el siguiente orden de prioridad:
    1. Variable de entorno MLFLOW_TRACKING_URI
    2. Argumento de línea de comandos --tracking-uri
    3. Input interactivo por consola
    """
    uri = os.getenv("MLFLOW_TRACKING_URI")
    if uri:
        print(f"🌐 MLflow Tracking URI cargado desde variable de entorno: {uri}")
        return uri

    parser = argparse.ArgumentParser(description="Cliente MLOps MLflow conectado a Google Colab")
    parser.add_argument("--tracking-uri", type=str, help="URL pública de Cloudflare (ej: https://xxx.trycloudflare.com)")
    args, _ = parser.parse_known_args()

    if args.tracking_uri:
        print(f"🌐 MLflow Tracking URI cargado desde argumento CLI: {args.tracking_uri}")
        return args.tracking_uri

    print("=" * 65)
    print("📡 CONEXIÓN A SERVIDOR MLFLOW REMOTO (GOOGLE COLAB)")
    print("=" * 65)
    uri = input("Ingrese la URL pública de Cloudflare (ej: https://xxx.trycloudflare.com): ").strip()
    return uri


def main():
    # 1. Configurar Tracking URI remoto
    tracking_uri = get_tracking_uri()
    if not tracking_uri:
        raise ValueError("❌ Debe proporcionar una URL válida de MLflow Tracking URI.")

    # Asegurar protocolo https:// si falta
    if not tracking_uri.startswith("http://") and not tracking_uri.startswith("https://"):
        tracking_uri = f"https://{tracking_uri}"

    mlflow.set_tracking_uri(tracking_uri)
    
    experiment_name = "Clasificacion_Vinos_GitHub_Remote"
    mlflow.set_experiment(experiment_name)
    print(f"✅ Conectado exitosamente. Experimento activo: '{experiment_name}'")

    # 2. Carga y preparación de datos
    wine = load_wine(as_frame=True)
    X, y = wine.data, wine.target
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Definir función de inferencia decorada con @mlflow.trace
    @mlflow.trace(name="Inferencia_Remota_GitHub_Span")
    def run_traced_inference(model_obj, input_df):
        """Ejecuta la predicción y envía el span de trazo automáticamente a MLflow Server."""
        return model_obj.predict(input_df)

    # 4. Iniciar ejecución en MLflow (Run)
    print("
🚀 Iniciando entrenamiento e interacción remota con MLflow Server...")
    with mlflow.start_run(run_name="Ejecucion_Cliente_GitHub") as run:
        params = {"n_estimators": 75, "max_depth": 5, "random_state": 42}
        clf = RandomForestClassifier(**params)
        clf.fit(X_train, y_train)

        # Evaluación
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")

        # Registrar parámetros y métricas remotamente
        mlflow.log_params(params)
        mlflow.log_metrics({"accuracy": acc, "f1_score": f1})
        mlflow.set_tag("origen", "GitHub_Repository_Client")
        mlflow.set_tag("entorno", "Local_Dev / CI_CD")

        # Crear y registrar matriz de confusión como artefacto
        fig, ax = plt.subplots(figsize=(6, 5))
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Purples',
                    xticklabels=wine.target_names, yticklabels=wine.target_names, ax=ax)
        ax.set_title("Matriz de Confusión - Cliente GitHub")
        ax.set_xlabel("Predicción")
        ax.set_ylabel("Valor Real")

        with tempfile.TemporaryDirectory() as tmp_dir:
            plot_path = os.path.join(tmp_dir, "confusion_matrix.png")
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close(fig)
            mlflow.log_artifact(plot_path, artifact_path="graficos")

        # Inferencia de firma y registro del modelo
        signature = infer_signature(X_test, y_pred)
        mlflow.sklearn.log_model(
            sk_model=clf,
            artifact_path="model",
            signature=signature,
            input_example=X_test.iloc[:2]
        )

        print(f"✅ Run registrado en Colab con exito.")
        print(f"🆔 Run ID: {run.info.run_id}")
        print(f"📊 Accuracy: {acc:.4f} | F1-Score: {f1:.4f}")

        # 5. Probar Inferencia y MLflow Trace
        print("
🔍 Ejecutando inferencia en tiempo real con trazabilidad MLflow Trace...")
        sample_data = X_test.iloc[:3]
        predictions = run_traced_inference(clf, sample_data)
        
        print("🎯 Predicciones obtenidas:")
        for idx, pred in enumerate(predictions):
            print(f"   - Muestra {idx + 1}: Clase {pred} ({wine.target_names[pred]})")

        print("
✨ Trazo enviado exitosamente al servidor. Revisa la pestaña 'Traces' en la UI de MLflow.")


if __name__ == "__main__":
    main()
