"""
app.py — Práctica 3, Actividad 2
App Streamlit: Precios de Carburantes (MITERD)

Ejecutar:
    streamlit run app.py
Desde móvil (misma WiFi):
    streamlit run app.py --server.address=0.0.0.0
"""

import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

import api_client as api

st.set_page_config(
    page_title="Carburantes España",
    page_icon="⛽",
    layout="wide",
)
st.title("⛽ Precios de Carburantes — España")

tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Por Comunidad Autónoma",
    "⚓ Postes Marítimos",
    "📅 Provincia · Fecha · Carburante",
    "📍 Cercanas a mi ubicación",
])


def mapa(df: pd.DataFrame, hover_name: str, color_col: str = None, titulo: str = "", zoom: int = 6):
    """Renderiza un scatter_mapbox con open-street-map (sin token)."""
    kw = dict(
        lat="Latitud", lon="Longitud",
        hover_name=hover_name,
        mapbox_style="open-street-map",
        zoom=zoom,
        height=480,
        title=titulo,
    )
    if color_col:
        kw["color"] = color_col
        kw["color_continuous_scale"] = "RdYlGn_r"
    fig = px.scatter_mapbox(df, **kw)
    fig.update_layout(margin={"r": 0, "t": 35, "l": 0, "b": 0})
    st.plotly_chart(fig, width="stretch")


# ── TAB 1: Estaciones por comunidad autónoma ──────────────────────────────

with tab1:
    st.subheader("Estaciones terrestres por comunidad autónoma")

    ccaa_df = api.get_ccaa()
    ccaa_map = dict(zip(ccaa_df["CCAA"], ccaa_df["IDCCAA"]))
    ccaa_sel = st.selectbox("Comunidad autónoma", list(ccaa_map))

    with st.spinner("Cargando estaciones..."):
        df1 = api.get_estaciones_ccaa(ccaa_map[ccaa_sel])

    if df1.empty:
        st.warning("No hay datos para esta comunidad autónoma.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Estaciones", len(df1))
        media_g95 = df1["Precio Gasolina 95 E5"].mean()
        media_goa = df1["Precio Gasoleo A"].mean()
        c2.metric("Precio medio G95 E5", f"{media_g95:.3f} €/L" if pd.notna(media_g95) else "N/D")
        c3.metric("Precio medio Gasóleo A", f"{media_goa:.3f} €/L" if pd.notna(media_goa) else "N/D")

        cols = [c for c in ["Rótulo", "Dirección", "Municipio", "Provincia",
                             "Precio Gasolina 95 E5", "Precio Gasoleo A"] if c in df1.columns]
        st.dataframe(df1[cols], width="stretch")

        df1_map = df1.dropna(subset=["Latitud", "Longitud"])
        if not df1_map.empty:
            mapa(df1_map, hover_name="Rótulo", titulo=f"Estaciones — {ccaa_sel}", zoom=6)


# ── TAB 2: Postes marítimos por provincia ─────────────────────────────────

with tab2:
    st.subheader("Postes marítimos por provincia")

    prov_df = api.get_provincias()
    prov_map = dict(zip(prov_df["Provincia"], prov_df["IDProvincia"]))
    prov_sel2 = st.selectbox("Provincia", list(prov_map), key="prov2")

    with st.spinner("Cargando postes marítimos..."):
        df2 = api.get_postes_maritimos(prov_map[prov_sel2])

    if df2.empty:
        st.warning("No hay postes marítimos para esta provincia.")
    else:
        st.metric("Postes marítimos", len(df2))
        # Los postes marítimos tienen campo "Puerto" en lugar de "Dirección"
        cols2 = [c for c in ["Rótulo", "Puerto", "Municipio", "Provincia",
                              "Precio Gasolina 95 E5", "Precio Gasoleo A habitual",
                              "Tipo Venta"] if c in df2.columns]
        st.dataframe(df2[cols2], width="stretch")

        df2_map = df2.dropna(subset=["Latitud", "Longitud"])
        if not df2_map.empty:
            # Usamos "Puerto" como etiqueta de hover (más informativo que Rótulo en marítimos)
            hover = "Puerto" if "Puerto" in df2_map.columns else "Rótulo"
            mapa(df2_map, hover_name=hover, titulo=f"Postes marítimos — {prov_sel2}", zoom=8)


# ── TAB 3: Precios por provincia, fecha y carburante ──────────────────────

with tab3:
    st.subheader("Precios por provincia, fecha y carburante")

    prov_df = api.get_provincias()
    prod_df = api.get_productos()
    prov_map3 = dict(zip(prov_df["Provincia"], prov_df["IDProvincia"]))
    prod_map = dict(zip(prod_df["NombreProducto"], prod_df["IDProducto"]))

    c1, c2, c3 = st.columns([2, 1, 2])
    prov_sel3 = c1.selectbox("Provincia", list(prov_map3), key="prov3")
    fecha_sel = c2.date_input("Fecha", value=datetime.date.today(), max_value=datetime.date.today())
    prod_sel = c3.selectbox("Carburante", list(prod_map), key="prod3")

    idprov3 = prov_map3[prov_sel3]
    idprod = prod_map[prod_sel]
    hoy = datetime.date.today()

    with st.spinner("Cargando precios..."):
        if fecha_sel == hoy:
            df3 = api.get_estaciones_hoy(idprov3, idprod)
        else:
            df3 = api.get_estaciones_hist(fecha_sel.strftime("%d-%m-%Y"), idprov3, idprod)

    if df3.empty or "PrecioProducto" not in df3.columns:
        st.warning(f"Sin datos para {prov_sel3} el {fecha_sel}. Prueba otra fecha o carburante.")
    else:
        df3 = df3.dropna(subset=["PrecioProducto"]).sort_values("PrecioProducto")

        c1, c2, c3 = st.columns(3)
        c1.metric("Estaciones con precio", len(df3))
        c2.metric("Más barata", f"{df3['PrecioProducto'].min():.3f} €/L")
        c3.metric("Precio medio", f"{df3['PrecioProducto'].mean():.3f} €/L")

        cols3 = [c for c in ["Rótulo", "Dirección", "Municipio", "PrecioProducto"] if c in df3.columns]
        st.dataframe(df3[cols3], width="stretch")

        fig3 = px.histogram(
            df3, x="PrecioProducto", nbins=20,
            labels={"PrecioProducto": "Precio (€/L)"},
            title=f"Distribución de precios — {prod_sel} en {prov_sel3}",
        )
        st.plotly_chart(fig3, width="stretch")

        df3_map = df3.dropna(subset=["Latitud", "Longitud"])
        if not df3_map.empty:
            mapa(df3_map, hover_name="Rótulo", color_col="PrecioProducto",
                 titulo=f"{prod_sel} — {prov_sel3}", zoom=8)


# ── TAB 4: Estaciones más cercanas (geolocalización) ─────────────────────

with tab4:
    st.subheader("Estaciones más cercanas a mi ubicación")
    st.info(
        "Pulsa **Obtener ubicación** para que el navegador te localice. "
        "Si estás en HTTP (no HTTPS) el navegador bloqueará la petición → "
        "usa las coordenadas manuales o consulta el README para activar HTTPS con cloudflared."
    )

    loc = streamlit_geolocation()

    if loc and loc.get("latitude") and loc.get("longitude"):
        lat_usr = float(loc["latitude"])
        lon_usr = float(loc["longitude"])
        st.success(f"Ubicación obtenida: {lat_usr:.5f}, {lon_usr:.5f}")
    else:
        st.caption("O introduce las coordenadas manualmente:")
        cc1, cc2 = st.columns(2)
        lat_usr = cc1.number_input("Latitud", value=40.4168, format="%.5f")
        lon_usr = cc2.number_input("Longitud", value=-3.7038, format="%.5f")

    n = st.slider("Nº estaciones a mostrar", 5, 50, 15)

    if st.button("Buscar estaciones cercanas"):
        with st.spinner("Descargando listado nacional y calculando distancias..."):
            df_todas = api.get_todas_estaciones()
            df_val = df_todas.dropna(subset=["Latitud", "Longitud"]).copy()
            df_val["Distancia_km"] = api.haversine(lat_usr, lon_usr, df_val).round(2)
            df_cerca = df_val.nsmallest(n, "Distancia_km")

        cols4 = [c for c in ["Rótulo", "Dirección", "Municipio", "Provincia",
                              "Precio Gasolina 95 E5", "Precio Gasoleo A",
                              "Distancia_km"] if c in df_cerca.columns]
        st.dataframe(df_cerca[cols4], width="stretch")

        # Mapa combinando posición del usuario y estaciones cercanas
        usuario = pd.DataFrame([{
            "Latitud": lat_usr, "Longitud": lon_usr,
            "Rótulo": "📍 Mi ubicación", "tipo": "Yo",
        }])
        estaciones_plot = df_cerca[["Latitud", "Longitud", "Rótulo"]].copy()
        estaciones_plot["tipo"] = "Estación"
        df_plot = pd.concat([usuario, estaciones_plot], ignore_index=True)

        fig4 = px.scatter_mapbox(
            df_plot,
            lat="Latitud", lon="Longitud",
            hover_name="Rótulo",
            color="tipo",
            color_discrete_map={"Yo": "red", "Estación": "steelblue"},
            mapbox_style="open-street-map",
            zoom=12,
            height=500,
            title="Estaciones más cercanas",
        )
        fig4.update_layout(margin={"r": 0, "t": 35, "l": 0, "b": 0})
        st.plotly_chart(fig4, width="stretch")
