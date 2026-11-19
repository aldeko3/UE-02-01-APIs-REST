# Configuración del Entorno e Integración con API Externa (Genius API)

Este documento recoge los pasos realizados para preparar el entorno de desarrollo, gestionar las credenciales de seguridad y validar la comunicación con una API externa de música antes de implementar los endpoints de la API en FastAPI.

## 1. Creación y Activación del Entorno Virtual

Para aislar las dependencias del proyecto respecto a la instalación global de Python en el sistema, se creó un entorno virtual en la raíz del proyecto (`UE-02-01-APIs-REST`):

```bash
# Crear el entorno virtual actualizando pip y setuptools
python3 -m venv .venv --upgrade-deps

# Activar el entorno virtual (macOS / Linux)
source .venv/bin/activate
```

Con el entorno activado, se instalaron los paquetes definidos en `requirements.txt` (`fastapi`, `uvicorn`, `requests`, `python-dotenv`, entre otros):

```bash
pip install -r requirements.txt
```

## 2. Gestión de Variables de Entorno y Seguridad (`.env`)

Por motivos de seguridad y buenas prácticas en control de versiones, las claves privadas nunca deben incluirse directamente en el código fuente ni subirse a GitHub:

1. **Archivo `.env`:** Creado en la raíz del proyecto para almacenar los tokens y claves privadas en formato `CLAVE=VALOR`.
2. **Archivo `.env.example`:** Plantilla sin valores reales para documentar qué variables de entorno requiere el proyecto.
3. **Archivo `.gitignore`:** Configurado para excluir `.venv/`, `.env` y `__pycache__/` del repositorio remoto.

Obtener claves de acceso de Twitch (TWITCH_CLIENT_ID y TWITCH_CLIENT_SECRET)
Gestión del Token de Twitch y su caducidad
https://dev.twitch.tv/docs/api

Nombre (UE-02-01-APIs-REST): Identifica la app vinculándola con el proyecto y la asignatura.

URL de redireccionamiento (http://localhost): Dirección local exigida por OAuth2 para desarrollo sin certificados SSL.

Categoría (Application Integration): Clasifica el proyecto como una integración de backend mediante API.

Tipo de cliente (Confidencial): Permite guardar de forma privada el Client Secret en el servidor (.env).