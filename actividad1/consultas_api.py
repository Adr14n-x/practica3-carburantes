"""
Práctica 3 — Actividad 1
Consultas a la API REST de Precios de Carburantes (MITERD)

Ejecutar (desde la raíz del proyecto):
    uv run python actividad1/consultas_api.py
"""

import ssl
import sys

import httpx
import pandas as pd
from pathlib import Path
from typing import Any, Union

JsonData = Union[dict[str, Any], list[Any]]

BASE_URL = (
    "https://sedeaplicaciones.minetur.gob.es"
    "/ServiciosRESTCarburantes/PreciosCarburantes"
)

HEADERS = {
    # La API rechaza peticiones sin User-Agent de navegador
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
"""Ruta donde dejarmos csv de salida con las consultas del api"""
SALIDAS_DIR = Path(__file__).parent / "salidas" 


# ── Utilidades de limpieza de datos para guardar los csv

def limpiar_decimal(valor) -> float:
    """Convierte "1,459" → 1.459 y "" → NaN (formato español de la API)."""
    if valor is None or str(valor).strip() == "":
        return float("nan")
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return float("nan")


def limpiar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte a float todas las columnas de precio y coordenadas."""
    cols = [c for c in df.columns if c.startswith("Precio") or c in ("Latitud", "Longitud")]
    for col in cols:
        df[col] = df[col].apply(limpiar_decimal)
    return df


def get_json(url: str) -> JsonData:
    """
    GET con cabecera de navegador y timeout 30 s.
    Contexto SSL permisivo: el servidor MITERD usa TLS 1.2 con ciphers que
    OpenSSL >= 3.0 rechaza por defecto (SECLEVEL=0 + OP_LEGACY_SERVER_CONNECT).
    Esto lo he logrado a base de ensayo, error... hasta que ha funcionado.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT

    try:
        resp = httpx.get(url, headers=HEADERS, timeout=30.0, verify=ctx)
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]
    except httpx.TimeoutException:
        print(f"  [ERROR] Timeout: {url}")
        sys.exit(1)
    except httpx.HTTPStatusError as exc:
        print(f"  [ERROR] HTTP {exc.response.status_code}: {url}")
        sys.exit(1)
    except Exception as exc:
        print(f"  [ERROR] {exc}")
        sys.exit(1)


def get_estaciones(url: str) -> list[dict[str, Any]]:
    """Llama a get_json y extrae siempre la lista de estaciones."""
    datos = get_json(url)
    if isinstance(datos, dict):
        return datos.get("ListaEESSPrecio", [])  # type: ignore[return-value]
    return datos  # type: ignore[return-value]


def mostrar_y_guardar(df: pd.DataFrame, cols_precio: list, nombre_csv: str):
    """Muestra nº de registros + primeras 5 filas relevantes y guarda el CSV."""
    print(f"\n  Registros obtenidos: {len(df)}")
    if df.empty:
        print("  AVISO: La consulta no ha devuelto datos.")
    else:
        """Dejo codigo innecesario para poder ver en terminal
        el resultado de las consultas al ejecutar.
        """
        cols = [c for c in ["Rótulo", "Dirección", "Municipio", "Provincia"]
                + cols_precio + ["Latitud", "Longitud"] if c in df.columns]
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 160)
        pd.set_option("display.float_format", "{:.4f}".format)
        pd.set_option("display.max_colwidth", 28)
        print("\n  Primeras 5 filas:")
        print(df[cols].head(5).to_string(index=False))

    SALIDAS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = SALIDAS_DIR / nombre_csv
    df.to_csv(ruta, index=False, encoding="utf-8-sig", sep=";")
    print(f"\n  CSV guardado en: {ruta}")


# ── CONSULTA 1: Estaciones terrestres de Castilla y León (IDCCAA = 08) ────

def consulta1():
    print("\n" + "=" * 70)
    print("  CONSULTA 1: Estaciones de servicio de Castilla y León")
    print("=" * 70)

    url = f"{BASE_URL}/EstacionesTerrestres/FiltroCCAA/08"
    print(f"\n  URL REST empleada:\n  {url}")

    df = limpiar_dataframe(pd.DataFrame(get_estaciones(url)))
    mostrar_y_guardar(df, ["Precio Gasoleo A", "Precio Gasolina 95 E5"],
                      "consulta1_castilla_leon.csv")


# ── CONSULTA 2: Postes marítimos de Castellón, Gasolina 95 E5 ─────────────
#    IDProvincia Castellón = 12  |  IDProducto Gasolina 95 E5 = 1

def consulta2():
    print("\n" + "=" * 70)
    print("  CONSULTA 2: Postes marítimos de Castellón — Gasolina 95 E5")
    print("=" * 70)

    url = f"{BASE_URL}/PostesMaritimos/FiltroProvinciaProducto/12/1"
    print(f"\n  URL REST empleada:\n  {url}")

    df = limpiar_dataframe(pd.DataFrame(get_estaciones(url)))
    mostrar_y_guardar(df, ["Precio Gasolina 95 E5"],
                      "consulta2_postes_castellon_g95e5.csv")


# ── CONSULTA 3: Histórico 12/02/2026, municipio Cúllar (IDMunicipio = 2724)

def consulta3():
    print("\n" + "=" * 70)
    print("  CONSULTA 3: Precios históricos del 12/02/2026 en Cúllar (Granada)")
    print("=" * 70)

    url = f"{BASE_URL}/EstacionesTerrestresHist/FiltroMunicipio/12-02-2026/2724"
    print(f"\n  URL REST empleada:\n  {url}")

    df = limpiar_dataframe(pd.DataFrame(get_estaciones(url)))
    mostrar_y_guardar(df, ["Precio Gasolina 95 E5", "Precio Gasoleo A"],
                      "consulta3_cullar_20260212.csv")


# Metodo main con la ejecucion.

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  Práctica 3 — Actividad 1: API REST de Carburantes (MITERD)")
    print("=" * 70)

    consulta1()
    consulta2()
    consulta3()

    print("\n" + "=" * 70)
    print("  Ejecución completada. Resultados en actividad1/salidas/")
    print("=" * 70 + "\n")
