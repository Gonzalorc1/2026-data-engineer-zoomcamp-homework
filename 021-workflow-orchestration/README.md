# Workflow Orchestration con Apache Airflow

Este directorio contiene la implementación de los flujos de trabajo usando **Apache Airflow** en lugar de Kestra. Los DAGs (Directed Acyclic Graphs) de Airflow son equivalentes a los flujos YAML de Kestra.

## 📋 Estructura del Proyecto

```
021-workflow-orchestration/
├── dags/                    # DAGs de Airflow
│   ├── 07_gcp_setup.py      # Setup inicial de GCP (bucket y dataset)
│   ├── 08_gcp_taxi.py       # Procesamiento manual de datos de taxis
│   └── 09_gcp_taxi_scheduled.py  # Procesamiento programado de datos de taxis
├── logs/                    # Logs de Airflow
├── plugins/                 # Plugins personalizados (opcional)
├── config/                  # Configuración adicional
├── gcp_keys/                # Credenciales de GCP (no commitear)
├── docker-compose.yml        # Configuración de Docker Compose
├── Dockerfile              # Imagen personalizada de Airflow
├── requirements.txt        # Dependencias de Python
├── .env                    # Variables de entorno (crear manualmente)
└── README.md               # Este archivo
```

## 🚀 Configuración Inicial

### 1. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Airflow
AIRFLOW_UID=50000
AIRFLOW_PROJ_DIR=/ruta/a/tu/proyecto/021-workflow-orchestration

# GCP Configuration
GCP_PROJECT_ID=tu-proyecto-gcp
GCP_DATASET=tu-dataset-name
GCP_BUCKET_NAME=tu-bucket-name
GCP_LOCATION=us-central1
GCP_CREDENTIALS_FILE=my-creds.json

# Airflow Web UI
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

### 2. Configurar Credenciales de GCP

1. Descarga tu archivo de credenciales de GCP (JSON) desde la consola de Google Cloud
2. Colócalo en la carpeta `gcp_keys/` con el nombre que especifiques en `GCP_CREDENTIALS_FILE` (por defecto: `my-creds.json`)
3. Asegúrate de que el archivo tenga los permisos necesarios para:
   - Crear buckets en GCS
   - Crear datasets y tablas en BigQuery
   - Subir archivos a GCS

### 3. Inicializar Airflow

```bash
# Establecer el UID de Airflow (solo la primera vez)
export AIRFLOW_UID=$(id -u)

# Inicializar la base de datos
docker-compose up airflow-init

# Iniciar los servicios
docker-compose up -d
```

### 4. Acceder a la Interfaz Web

Abre tu navegador en: http://localhost:8080

- Usuario: `airflow` (o el que configuraste en `.env`)
- Contraseña: `airflow` (o la que configuraste en `.env`)

## 📝 DAGs Disponibles

### 1. `07_gcp_setup`

**Descripción**: Configura los recursos iniciales de GCP (bucket y dataset).

**Uso**: 
- Ejecutar manualmente desde la UI de Airflow
- Se ejecuta una sola vez para configurar el entorno

**Tareas**:
- `create_gcs_bucket`: Crea el bucket en Google Cloud Storage
- `create_bq_dataset`: Crea el dataset en BigQuery

### 2. `08_gcp_taxi`

**Descripción**: Procesa datos de taxis (yellow o green) desde GitHub a BigQuery. Versión manual.

**Uso**: 
- Trigger manual desde la UI de Airflow
- Requiere configuración JSON al ejecutar:

```json
{
  "taxi": "green",
  "year": "2021",
  "month": "01"
}
```

**Parámetros**:
- `taxi`: `"yellow"` o `"green"`
- `year`: Año (ej: `"2019"`, `"2020"`, `"2021"`)
- `month`: Mes (ej: `"01"`, `"02"`, ..., `"12"`)

**Flujo**:
1. `extract`: Descarga y descomprime el archivo desde GitHub
2. `upload_to_gcs`: Sube el archivo a Google Cloud Storage
3. `branch_on_taxi_type`: Decide qué pipeline ejecutar (yellow o green)
4. Pipeline específico (yellow o green):
   - Crear tabla principal
   - Crear tabla externa desde GCS
   - Crear tabla temporal con datos procesados
   - Merge de datos a la tabla principal
5. `cleanup_local_file`: Limpia el archivo local

### 3. `09_gcp_taxi_scheduled_green` y `09_gcp_taxi_scheduled_yellow`

**Descripción**: Versiones programadas que se ejecutan automáticamente.

**Programación**:
- **Green taxi**: Día 1 de cada mes a las 9:00 AM (cron: `0 9 1 * *`)
- **Yellow taxi**: Día 1 de cada mes a las 10:00 AM (cron: `0 10 1 * *`)

**Uso**: 
- Se ejecutan automáticamente según el schedule
- Usan la fecha de ejecución (`execution_date`) para determinar el año y mes a procesar

## 🔄 Comparación con Kestra

| Característica | Kestra | Airflow |
|---------------|--------|---------|
| Configuración | YAML | Python (DAGs) |
| Interfaz | Web UI | Web UI |
| Programación | Cron en YAML | Cron en Python |
| Parámetros | Inputs en YAML | `dag_run.conf` o `params` |
| Branching | `If` task | `BranchPythonOperator` |
| Variables | `{{vars.var}}` | `{{dag_run.conf.get()}}` o Jinja2 |
| Extensibilidad | Plugins | Operadores y Hooks |

## 📚 Ejemplos de Uso

### Ejemplo 1: Procesar datos manualmente para enero 2021 (green taxi)

1. Ve a la UI de Airflow: http://localhost:8080
2. Encuentra el DAG `08_gcp_taxi`
3. Haz clic en "Trigger DAG w/ config"
4. Ingresa la configuración JSON:
```json
{
  "taxi": "green",
  "year": "2021",
  "month": "01"
}
```
5. Haz clic en "Trigger"

### Ejemplo 2: Backfill para 2021

Para procesar todos los meses de 2021, puedes:

1. **Opción A**: Ejecutar manualmente el DAG `08_gcp_taxi` para cada combinación de mes y tipo de taxi
2. **Opción B**: Usar el comando de Airflow CLI para backfill (si está habilitado):
```bash
docker-compose exec airflow-scheduler airflow dags backfill 08_gcp_taxi \
  --start-date 2021-01-01 \
  --end-date 2021-07-31 \
  --conf '{"taxi": "green", "year": "2021", "month": "01"}'
```

### Ejemplo 3: Verificar logs

```bash
# Ver logs del scheduler
docker-compose logs -f airflow-scheduler

# Ver logs del webserver
docker-compose logs -f airflow-webserver

# Ver logs de una tarea específica
# (desde la UI de Airflow, haz clic en la tarea y luego en "Log")
```

## 🛠️ Comandos Útiles

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (¡cuidado! elimina la base de datos)
docker-compose down -v

# Ver estado de los servicios
docker-compose ps

# Reiniciar un servicio específico
docker-compose restart airflow-scheduler

# Ejecutar comandos de Airflow CLI
docker-compose exec airflow-scheduler airflow version
docker-compose exec airflow-scheduler airflow dags list
docker-compose exec airflow-scheduler airflow dags show 08_gcp_taxi
```

## 🔍 Troubleshooting

### Problema: Los DAGs no aparecen en la UI

**Solución**:
1. Verifica que los archivos estén en la carpeta `dags/`
2. Revisa los logs del scheduler: `docker-compose logs airflow-scheduler`
3. Verifica que no haya errores de sintaxis en los DAGs
4. Reinicia el scheduler: `docker-compose restart airflow-scheduler`

### Problema: Error de autenticación con GCP

**Solución**:
1. Verifica que el archivo de credenciales (por defecto `my-creds.json`) esté en `gcp_keys/`
2. Verifica que la variable `GOOGLE_APPLICATION_CREDENTIALS` esté configurada correctamente en `docker-compose.yml` (debe apuntar a `/opt/airflow/dags/gcp_keys/{nombre-del-archivo}`)
3. Verifica que las credenciales tengan los permisos necesarios

### Problema: No se pueden descargar archivos

**Solución**:
1. Verifica la conexión a internet desde el contenedor
2. Verifica que la URL de GitHub sea correcta
3. Revisa los logs de la tarea `extract`

## 📖 Recursos Adicionales

- [Documentación de Apache Airflow](https://airflow.apache.org/docs/)
- [Airflow Providers para Google Cloud](https://airflow.apache.org/docs/apache-airflow-providers-google/)
- [Guía de Docker Compose para Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)

## 🎯 Notas sobre el Homework

Para completar el homework del módulo 2 usando Airflow:

1. **Setup inicial**: Ejecuta `07_gcp_setup` una vez
2. **Procesar datos de 2021**: Usa `08_gcp_taxi` con las siguientes configuraciones:
   - Para cada mes de 2021 (01-07) y cada tipo de taxi (yellow, green)
   - Ejemplo para enero 2021 green: `{"taxi": "green", "year": "2021", "month": "01"}`
3. **Verificar resultados**: Consulta las tablas en BigQuery para responder las preguntas del quiz

## 📝 Licencia

Este proyecto es parte del Data Engineering Zoomcamp 2026.
