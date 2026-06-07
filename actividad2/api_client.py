"""
api_client.py — Cliente de la API REST de Carburantes del MITERD.
Centraliza peticiones HTTP y limpieza de datos para Streamlit.

Contexto técnico heredado de Actividad 1:
- User-Agent obligatorio o la API rechaza la petición.
- Precios y coordenadas vienen como texto con coma decimal ("1,459").
- La clave de la lista de estaciones es "ListaEESSPrecio".
- El servidor usa TLS 1.2 legacy: requiere SSL permisivo en Python 3.10+.
- La columna de longitud puede llamarse "Longitud" o "Longitud (WGS84)".
- El listado de provincias tiene un typo oficial: "IDPovincia" (sin segunda 'r').
"""

import ssl
import numpy as np
import httpx
import pandas as pd
import streamlit as st

BASE_URL = (
    "https://sedeaplicaciones.minetur.gob.es"
    "/ServiciosRESTCarburantes/PreciosCarburantes"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def _ssl_ctx() -> ssl.SSLContext:
    """SSL permisivo para el servidor MITERD (SECLEVEL=0 + renegociación legacy)."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
    return ctx


def get_json(url: str):
    """GET con cabecera de navegador, timeout 30 s y SSL permisivo."""
    try:
        resp = httpx.get(url, headers=HEADERS, timeout=30.0, verify=_ssl_ctx())
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        st.error(f"Error de red: {exc}")
        return {}


def _parse_float(valor) -> float:
    """Convierte "1,459" → 1.459 y cadena vacía → NaN."""
    s = str(valor).strip()
    if not s or s == "None":
        return float("nan")
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return float("nan")


def to_df(url: str) -> pd.DataFrame:
    """
    Descarga un endpoint, extrae ListaEESSPrecio y devuelve un DataFrame
    con columnas numéricas ya convertidas a float.
    """
    datos = get_json(url)
    lista = datos.get("ListaEESSPrecio", []) if isinstance(datos, dict) else []
    if not lista:
        return pd.DataFrame()
    df = pd.DataFrame(lista)
    # Algunos endpoints usan "Longitud (WGS84)" en lugar de "Longitud"
    df = df.rename(columns={"Longitud (WGS84)": "Longitud"})
    num_cols = [c for c in df.columns
                if c.startswith("Precio") or c in ("Latitud", "Longitud", "PrecioProducto")]
    for col in num_cols:
        df[col] = df[col].apply(_parse_float)
    return df


def get_ccaa() -> pd.DataFrame:
    return pd.DataFrame(get_json(f"{BASE_URL}/Listados/ComunidadesAutonomas/"))


def get_provincias() -> pd.DataFrame:
    df = pd.DataFrame(get_json(f"{BASE_URL}/Listados/Provincias/"))
    return df.rename(columns={"IDPovincia": "IDProvincia"})  # typo oficial de la API


def get_productos() -> pd.DataFrame:
    return pd.DataFrame(get_json(f"{BASE_URL}/Listados/ProductosPetroliferos/"))


def get_estaciones_ccaa(idccaa: str) -> pd.DataFrame:
    return to_df(f"{BASE_URL}/EstacionesTerrestres/FiltroCCAA/{idccaa}")


def get_postes_maritimos(idprov: str) -> pd.DataFrame:
    return to_df(f"{BASE_URL}/PostesMaritimos/FiltroProvincia/{idprov}")


def get_estaciones_hoy(idprov: str, idprod: str) -> pd.DataFrame:
    return to_df(f"{BASE_URL}/EstacionesTerrestres/FiltroProvinciaProducto/{idprov}/{idprod}")


def get_estaciones_hist(fecha: str, idprov: str, idprod: str) -> pd.DataFrame:
    return to_df(f"{BASE_URL}/EstacionesTerrestresHist/FiltroProvinciaProducto/{fecha}/{idprov}/{idprod}")


def get_todas_estaciones() -> pd.DataFrame:
    return to_df(f"{BASE_URL}/EstacionesTerrestres/")


# ── Cálculo de distancias ─────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, df: pd.DataFrame) -> pd.Series:
    """
    Calcula la distancia en km entre (lat1, lon1) y cada fila del DataFrame
    usando la fórmula de Haversine con numpy (sin librerías externas).
    """
    R = 6371.0
    lat2 = np.radians(df["Latitud"].values)
    lon2 = np.radians(df["Longitud"].values)
    dlat = lat2 - np.radians(lat1)
    dlon = lon2 - np.radians(lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return pd.Series(2 * R * np.arcsin(np.sqrt(a)), index=df.index)
