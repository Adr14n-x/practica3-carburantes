# Práctica 3 — Precios de Carburantes (MITERD)

Proyecto Python que consulta la API REST de Precios de Carburantes del Ministerio para la Transición Ecológica (MITERD).

## Instalación (Windows)

```powershell
# Desde la raíz del proyecto
uv sync
```

Si no tienes `uv` instalado:

```powershell
pip install uv
```

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

## ⚠️ Geolocalización: HTTPS obligatorio

La pestaña **"Cercanas a mi ubicación"** usa la API de geolocalización del navegador, que **solo funciona en contexto seguro (HTTPS) o en localhost**.

| Acceso | ¿Funciona la geolocalización? |
|---|---|
| `http://localhost:8501` (PC) | ✅ Sí |
| `http://192.168.x.x:8501` (móvil, HTTP) | ❌ Bloqueado por el navegador |
| URL HTTPS (túnel) | ✅ Sí |

### Túnel HTTPS con cloudflared

1. Descarga cloudflared desde `https://github.com/cloudflare/cloudflared/releases`
2. Inicia la app:
   ```powershell
   uv run streamlit run actividad2/app.py
   ```
3. En otra terminal, abre el túnel:
   ```powershell
   cloudflared tunnel --url http://localhost:8501
   ```
4. cloudflared mostrará una URL pública tipo `https://xxxx.trycloudflare.com`.

---

## Estructura del proyecto

```
practica3-carburantes/
├── pyproject.toml           # dependencias unificadas (uv)
├── .python-version          # Python 3.12
├── README.md
├── actividad1/
│   ├── consultas_api.py     # script CLI con 3 consultas
│   └── salidas/             # CSVs generados
│       ├── consulta1_castilla_leon.csv
│       ├── consulta2_postes_castellon_g95e5.csv
│       └── consulta3_cullar_20260212.csv
└── actividad2/
    ├── app.py               # interfaz Streamlit (4 pestañas)
    └── api_client.py        # cliente HTTP, limpieza y caché
```
