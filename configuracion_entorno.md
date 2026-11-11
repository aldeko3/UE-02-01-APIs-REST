# Guía Completa: Creación y Gestión de Entornos Virtuales (`venv`) en macOS

Esta guía se centra exclusivamente en el proceso de creación, activación y gestión de entornos virtuales utilizando la herramienta nativa `venv` de Python en macOS, junto con su integración en Visual Studio Code.

---

## 1. ¿Qué es un Entorno Virtual y Por Qué Usarlo?

Un entorno virtual es un directorio aislado que contiene una instalación independiente de Python con su propia colección de librerías y ejecutables.

### Beneficios Principales
* **Aislamiento de Dependencias:** Evita conflictos entre proyectos que requieren distintas versiones de una misma librería.
* **Proyectos Limpios:** Mantiene el entorno global de macOS libre de paquetes innecesarios.
* **Portabilidad:** Facilita la recreación del entorno exacto en otros equipos mediante un archivo de requerimientos (`requirements.txt`).

---

## 2. Conceptos Clave: `venv` vs. Anaconda

| Criterio | `venv` (Recomendado) | Anaconda |
| :--- | :--- | :--- |
| **Origen** | Nativo de Python (no requiere instalaciones extra). | Distribución externa de terceros. |
| **Tamaño** | Muy ligero (~10-20 MB por entorno). | Pesado (varios Gigabytes). |
| **Uso Principal** | Desarrollo Backend, Web, Scripts y APIs. | Ciencia de Datos, Machine Learning y Análisis Cuantitativo. |

---

## 3. Guía Paso a Paso para Crear y Gestionar un Entorno Virtual

### Paso 1: Preparar la Carpeta del Proyecto

Abre la **Terminal** de macOS o la Terminal integrada de VS Code (`` Ctrl + ` ``) y navega hasta la ubicación donde crearás tu proyecto:

```bash
# Crear directorio de trabajo
mkdir mi_proyecto

# Acceder a la carpeta
cd mi_proyecto
```

---

### Paso 2: Crear el Entorno Virtual

Ejecuta la orden de `venv` indicando el nombre del directorio donde se guardará el entorno (el estándar de la industria es utilizar `.venv` o `env`):

```bash
python3 -m venv .venv --upgrade-deps
```

> **¿Qué ocurre internamente?**  
> Python creará una carpeta oculta llamada `.venv` que contiene:
> * Una copia (o enlace) del ejecutable de Python.
> * Las carpetas `bin/` y `lib/` dedicadas exclusivamente a almacenar las librerías que instales dentro de este proyecto.

---

### Paso 3: Integración con VS Code

Si estás utilizando **Visual Studio Code** con la extensión oficial de **Python (Microsoft)** instalada:

1. Abre la carpeta del proyecto en VS Code: `code .` o vía **File > Open Folder...**.
2. Aparecerá un aviso en la esquina inferior derecha:  
   *"We noticed a new environment has been created. Do you want to select it for the workspace folder?"*
3. Haz clic en **Yes**.

Esto garantizará que el autocompletado (*IntelliSense*) y el depurador utilicen las librerías del entorno virtual en lugar de las globales.

---

### Paso 4: Activar el Entorno Virtual

Para que la Terminal sepa que debe usar el entorno aislado y no el Python del sistema, debes activarlo:

```bash
source .venv/bin/activate
```

**Verificación:**
* La línea de comandos de tu Terminal mostrará el prefijo `(.venv)` a la izquierda.
* En la barra de estado de VS Code (abajo a la derecha) verás seleccionado: `Python 3.x.x ('.venv': venv)`.

---

### Paso 5: Instalar Paquetes y Comprobar el Aislamiento

Una vez activo, cualquier instalación mediante `pip` se realizará **únicamente** dentro de `.venv`:

```bash
# Instalar las dependencias del proyecto a partir del archivo requirements.txt
pip install -r requirements.txt

# Listar paquetes instalados en el entorno activo
pip list
```

---

### Paso 6: Generar el Servidor con OpenAPI Generator

A partir de tu especificación OpenAPI (por ejemplo, el archivo `openapi.yaml`), puedes generar automáticamente la estructura de tu API en Python Flask utilizando `openapi-generator-cli`:

```bash
openapi-generator-cli generate -i openapi.yaml -g python-flask -o usuarios_api
```

> **¿Qué hace este comando?**
> * `-i openapi.yaml`: Especifica el archivo de definición de la API (OpenAPI / Swagger).
> * `-g python-flask`: Indica el generador de código deseado (en este caso, un servidor Flask en Python).
> * `-o usuarios_api`: Define la carpeta de salida donde se creará el código fuente generado.

---

### Paso 7: Desactivar o Eliminar el Entorno Virtual

* **Desactivar el entorno:**  
  Cuando termines de trabajar en tu proyecto y quieras volver al shell estándar de macOS, ejecuta:
  ```bash
  deactivate
  ```

* **Eliminar el entorno:**  
  Si deseas borrar el entorno virtual para recrearlo desde cero, simplemente borra la carpeta `.venv`:
  ```bash
  rm -rf .venv
  ```