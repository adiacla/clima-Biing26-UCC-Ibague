# Orquestación de Agentes Inteligentes con n8n

> **Integración de sistemas multiagente con aplicaciones móviles para proyectos de ingeniería.**

Repositorio oficial de la conferencia y taller práctico dictado por **Alfredo Díaz Claros** (Universidad Autónoma de Bucaramanga — Smart Regions Center). Este proyecto abarca desde la automatización con modelos de lenguaje hasta la orquestación de sistemas multiagente, almacenamiento vectorial con PostgreSQL (`pgvector`), procesamiento de documentos RAG e integración con canales de mensajería como Telegram.

---

## 📌 Contenido y Estructura del Repositorio

El repositorio incluye la presentación oficial, scripts de base de datos, flujos de n8n, documentos de conocimiento para RAG y un servidor backend en Python:

```text
.
├── 01_crear_base_datos.sql                     # Script SQL con esquema ccd, tablas y vistas
├── 02_crear_tabla_vectorial.sql                # Configuración de pgvector e índice HNSW
├── Agente del Clima.json                       # Workflow de n8n: Práctica 1 (Herramientas y APIs)
├── Embedding documento RAG (1).json            # Workflow de n8n: Práctica 2 (Ingesta y Embeddings)
├── FAQ_RAG_optimizados (1).md                 # Documento Markdown de base de conocimientos
├── Propuesta Competencias Digitales UNAB V11ADC_clean (1).md # Documentación institucional para RAG
├── Orquestacion_Agentes_n8n.pptx               # Diapositivas completas de la conferencia y taller
├── aleatorios.txt                              # Datos sintéticos y valores de prueba
├── ccd_server.py                               # Servidor Python / API auxiliar para el proyecto
└── README.md                                   # Documentación principal
```

---

## 🧪 Prácticas y Talleres Guiados

### 🌤️ Práctica 1: Agente del Clima (Herramientas Dinámicas)
* **Objetivo:** Conectar un modelo de lenguaje (LLM) con APIs externas en tiempo real mediante *function calling* sin programar flujos complejos.
* **Componentes:**
  * Interfaz de entrada (Trigger Chat).
  * AI Agent Core con memoria de contexto (`Memory Buffer`).
  * Integración con la API de Open-Meteo para resolución automática de coordenadas y respuesta estructurada.
* **Archivo de flujo:** `Agente del Clima.json`

### 📚 Práctica 2: Ingesta RAG y Sistema Multiagente Avanzado
* **Objetivo:** Construir un pipeline de búsqueda semántica (RAG) e integrar un agente orquestador conectado a Telegram y PostgreSQL.
* **Componentes:**
  * **Base de Datos & Vectores:** Scripts `01_crear_base_datos.sql` y `02_crear_tabla_vectorial.sql` para alojar tablas relacionales (`ccd.conversaciones`, `v_estado_estudiante`) y soporte vectorial con índices HNSW.
  * **Ingesta RAG:** Fragmentación (*chunking* con solapamiento) de los archivos Markdown (`FAQ_RAG_optimizados (1).md` y `Propuesta Competencias Digitales UNAB V11ADC_clean (1).md`) usando el modelo `text-embedding-3-small`.
  * **Orquestador Multiagente:** Delegación dinámica entre agentes RAG (conocimiento), consultas SQL a PostgreSQL y registro de solicitudes.
* **Archivo de flujo:** `Embedding documento RAG (1).json`

---

## 🛠️ Stack Tecnológico

* **Orquestador de Automatización:** [n8n](https://n8n.io/) (Cloud / Self-hosted)
* **Modelos de Lenguaje & Embeddings:** OpenAI (`GPT-4o`, `text-embedding-3-small` - 1536d) / Anthropic Claude
* **Base de Datos & Búsqueda Vectorial:** PostgreSQL con extensión `pgvector` (Supabase o servidor propio)
* **Backend Auxiliar:** Python (`ccd_server.py`)
* **Cliente / Interfaz Móvil:** Telegram Bot API (conectado vía Webhooks)

---

## 🚀 Pasos para la Ejecución

### 1. Preparación del Entorno de Datos
Ejecuta en tu instancia de PostgreSQL los scripts en el siguiente orden:
1. `01_crear_base_datos.sql` para generar la estructura relacional de la entidad (estudiantes, estados y consultas).
2. `02_crear_tabla_vectorial.sql` para activar `pgvector` e instalar el índice HNSW por distancia coseno.

### 2. Configuración e Importación en n8n
1. Importa los archivos `.json` (`Agente del Clima.json` y `Embedding documento RAG (1).json`) en tu panel de n8n mediante **Import from File**.
2. Configura las credenciales requeridas en n8n (OpenAI API Key, PostgreSQL, Telegram Bot Token).

### 3. Carga de Documentos (Pipeline RAG)
Ejecuta el flujo de ingesta de embeddings para procesar los documentos `.md` (`FAQ_RAG_optimizados (1).md` y `Propuesta Competencias Digitales...`). El flujo utiliza una política de idempotencia limpiando registros previos por fuente (`metadata.fuente`) antes de insertar los nuevos vectores.

---

## 🔐 Buenas Prácticas de Ingeniería

* **Gestión de Credenciales:** Utiliza siempre el almacenamiento nativo de credenciales de n8n; no expongas claves en archivos JSON.
* **Idempotencia:** Los flujos de carga borran fragmentos vectoriales anteriores por origen de archivo para evitar duplicidad de respuestas en el RAG.
* **Privacidad:** Aplica los principios de Habeas Data y Ley 1581 en entornos con datos reales.

---

## 👤 Autor y Créditos

* **Autor:** Alfredo Díaz Claros
* **Institución:** Universidad Autónoma de Bucaramanga (UNAB) — Smart Regions Center