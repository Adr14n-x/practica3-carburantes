# Práctica 3 — Precios de Carburantes (MITERD)

Proyecto Python que consulta la API REST de Precios de Carburantes del Ministerio para la Transición Ecológica (MITERD).

---

## Requisitos previos

### 1. Instalar Python 3.12

Descarga el instalador desde la web oficial:

```
https://www.python.org/downloads/release/python-3120/
```

Durante la instalación marca la opción **"Add Python to PATH"** antes de continuar.

Verifica que quedó bien instalado abriendo PowerShell y ejecutando:

```powershell
python --version
```

Debe mostrar `Python 3.12.x`.

### 2. Instalar uv

`uv` es el gestor de entornos y dependencias que usa este proyecto. Instálalo con:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y vuelve a abrir PowerShell para que se actualice el PATH. Verifica:

```powershell
uv --version
```

### 3. Clonar el repositorio

```powershell
git clone https://github.com/Adr14n-x/practica3-carburantes.git
cd practica3-carburantes
```

Si no tienes Git instalado, descárgalo desde `https://git-scm.com/download/win`.

### 4. Instalar las dependencias

Desde la raíz del proyecto:

```powershell
uv sync
```

Esto crea automáticamente un entorno virtual `.venv` e instala todos los paquetes necesarios.

---

## Actividad 1 — Script CLI

Realiza tres consultas a la API y guarda los resultados como CSV en `actividad1/salidas/`.

```powershell
uv run python actividad1/consultas_api.py
```

**Consultas incluidas:**

| Consulta | Descripción |
|---|---|
| 1 | Estaciones terrestres de Castilla y León |
| 2 | Postes marítimos de Castellón — Gasolina 95 E5 |
| 3 | Precios históricos del 12/02/2026 en Cúllar (Granada) |

---

## Actividad 2 — App Web Streamlit

App interactiva con cuatro pestañas de consulta y visualización en mapa.

```powershell
uv run streamlit run actividad2/app.py
```

Abre automáticamente `http://localhost:8501` en el navegador.

### Acceso desde el móvil (misma red WiFi)

```powershell
uv run streamlit run actividad2/app.py --server.address=0.0.0.0
```

Luego abre en el móvil `http://<IP_DEL_PC>:8501`.  
Para saber tu IP: ejecuta `ipconfig` y busca "Dirección IPv4".

**Pestañas de la app:**

1. **Por Comunidad Autónoma** — Tabla + métricas + mapa de todas las estaciones de una CCAA.
2. **Postes Marítimos** — Listado y mapa de postes marítimos por provincia.
3. **Provincia · Fecha · Carburante** — Precios de un carburante concreto, hoy o en fecha histórica. Gráfico de distribución + mapa de calor de precios.
4. **Cercanas a mi ubicación** — Geolocalización del usuario (o coordenadas manuales), cálculo de distancia Haversine y mapa con las N estaciones más próximas.

---

## Estructura del proyecto

```
practica3-carburantes/
├── pyproject.toml           # dependencias del proyecto
├── .python-version          # versión de Python requerida (3.12)
├── requirements.txt
├── README.md
├── actividad1/
│   ├── consultas_api.py     # script CLI con 3 consultas
│   └── salidas/             # CSVs generados al ejecutar
│       ├── consulta1_castilla_leon.csv
│       ├── consulta2_postes_castellon_g95e5.csv
│       └── consulta3_cullar_20260212.csv
└── actividad2/
    ├── app.py               # interfaz Streamlit con 4 pestañas
    └── api_client.py        # cliente HTTP y funciones de la API
```
