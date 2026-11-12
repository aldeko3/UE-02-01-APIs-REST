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

## 3. Análisis Previo con Spotify Web API y Cambio a Genius API

Inicialmente se realizó el registro de la aplicación en [Spotify for Developers](https://developer.spotify.com/dashboard) y se validó el flujo **OAuth 2.0 (Client Credentials Flow)** mediante Postman:

* **Obtención del token (`POST https://accounts.spotify.com/api/token`):** Respuesta `200 OK` devolviendo un `access_token` válido.
* **Consulta de catálogo (`GET https://api.spotify.com/v1/search`):** Respuesta `403 Forbidden` con el mensaje:
  > *"Premium subscription required for the owner of the app. When the subscription status changes, it can take a few hours before requests are allowed again."*
* **Consulta de recomendaciones (`GET https://api.spotify.com/v1/recommendations`):** Respuesta `404 Not Found` (endpoint restringido para nuevas aplicaciones).

### Justificación técnica del cambio de proveedor

Desde **marzo de 2026**, Spotify exige que el propietario de una aplicación registrada disponga de una suscripción **Spotify Premium** activa para poder consumir los endpoints de consulta de su Web API. Al no disponer de una cuenta Premium, se decidió migrar la integración externa a **Genius API**, ya que:

1. Es **100 % gratuita** y permite realizar consultas reales de canciones y artistas sin restricciones de suscripción.
2. Mantiene el mismo esquema de autenticación profesional mediante **Bearer Token** en las cabeceras HTTP (`Authorization: Bearer <token>`), respetando fielmente el planteamiento original del ejercicio.

## 4. Registro de la Aplicación en Genius API

Siguiendo la [documentación oficial de Genius API](https://docs.genius.com/), se registró el cliente de la aplicación:

1. Acceso al portal de desarrolladores en [https://genius.com/api-clients](https://genius.com/api-clients).
2. Creación de un nuevo cliente API (`UE-02-01-APIs-REST`) con los siguientes parámetros:
   * **App Website URL:** `http://localhost:8000`
   * **Redirect URI:** `http://localhost:8000/callback`
3. Generación de las credenciales de acceso (`Client ID`, `Client Secret` y **`Client Access Token`**).
4. Almacenamiento seguro del token en el archivo local `.env`:

```env
GENIUS_ACCESS_TOKEN=tu_client_access_token_generado
```

## 5. Validación de Llamadas HTTP a Genius en Postman

Antes de programar la integración en Python, se verificó el funcionamiento del endpoint de búsqueda de Genius desde Postman:

* **Método:** `GET`
* **URL:** `https://api.genius.com/search?q=Daft%20Punk`
* **Authorization:** `Bearer Token` (introduciendo el `GENIUS_ACCESS_TOKEN` generado)
* **Body:** `none`
* **Resultado esperado:** `200 OK` con un objeto JSON estructurado (`meta` y `response.hits`) que contiene la información de las canciones y artistas encontrados (`title`, `primary_artist.name`, `url`, `song_art_image_thumbnail_url`).