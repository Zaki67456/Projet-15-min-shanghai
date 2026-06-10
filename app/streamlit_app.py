# -*- coding: utf-8 -*-
"""15-Minute Shanghai — Track C (Affordability). App Streamlit + pydeck H3HexagonLayer."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from matplotlib import colormaps, colors as mcolors

st.set_page_config(page_title="15-Minute Shanghai — Track C", layout="wide",
                   page_icon="🏙️")

NEEDS = ["alimentation", "sante", "education", "emploi", "loisir_sport", "services"]


@st.cache_data
def load_data():
    here = Path(__file__).parent
    for p in [here / "hexes_app.parquet",
              here.parent / "data" / "clean" / "hexes_scored.parquet"]:
        if p.exists():
            df = pd.read_parquet(p)
            return df.drop(columns=[c for c in ["geometry"] if c in df.columns])
    st.error("Fichier de données introuvable (hexes_app.parquet).")
    st.stop()


df = load_data()

METRICS = {
    "Score 15-min (marche OU vélo) /6": ("baseline_score", 0, 6, "RdYlGn"),
    "Score marche seule /6":            ("n_walk", 0, 6, "RdYlGn"),
    "Score vélo /6":                    ("n_bike", 0, 6, "RdYlGn"),
    "Indice d'accessibilité /100":      ("access_index", 0, 100, "RdYlGn"),
    "Prix médian (¥/m²)":               ("price_per_m2", None, None, "viridis_r"),
    "Value score (accès − prix)":       ("value_score", -60, 60, "RdYlGn"),
}


def to_colors(values, vmin, vmax, cmap_name, alpha=170, faded=None):
    v = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    finite = v[np.isfinite(v)]
    if vmin is None:
        vmin = np.percentile(finite, 5) if finite.size else 0
    if vmax is None:
        vmax = np.percentile(finite, 95) if finite.size else 1
    cmap = colormaps[cmap_name]
    norm = mcolors.Normalize(vmin, vmax)
    out = []
    for i, val in enumerate(v):
        if not np.isfinite(val):
            out.append([210, 210, 210, 30])          # gris = pas de donnée
        else:
            r, g, b, _ = cmap(norm(val))
            a = alpha if (faded is None or faded[i]) else 25
            out.append([int(r * 255), int(g * 255), int(b * 255), a])
    return out


# ----------------------------- Sidebar -----------------------------
st.sidebar.title("🏙️ 15-Minute Shanghai")
st.sidebar.caption("Track C — Accessibilité × Abordabilité")

metric_label = st.sidebar.selectbox("Indicateur cartographié", list(METRICS))
col, vmin, vmax, cmap_name = METRICS[metric_label]

st.sidebar.markdown("### 🎯 Recommandeur « Où habiter ? »")
reco = st.sidebar.checkbox("Activer le filtre")
budget = st.sidebar.slider("Budget max (¥/m²)", 2000, 150000, 45000, 1000)
min_acc = st.sidebar.slider("Accessibilité minimale /100", 0, 100, 80, 5)

faded = None
data = df.copy()
if reco:
    keep = (data["price_per_m2"] <= budget) & (data["access_index"] >= min_acc)
    faded = keep.to_numpy()

data["color"] = to_colors(data[col], vmin, vmax, cmap_name, faded=faded)
data["price_txt"] = data["price_per_m2"].round(0)

# ----------------------------- Map -----------------------------
st.title("Le 15-minute city à Shanghai : privilège ou réalité accessible ?")
st.markdown(f"**Indicateur : {metric_label}** · {len(df):,} hexagones H3 (résolution 8) · "
            "marche 15 min ≈ 1.2 km, vélo 15 min ≈ 3.75 km (distances réseau réelles).")

layer = pdk.Layer(
    "H3HexagonLayer", data=data, get_hexagon="cell",
    get_fill_color="color", pickable=True, stroked=False,
    extruded=False, opacity=0.7,
)
view = pdk.ViewState(latitude=31.22, longitude=121.47, zoom=8.6, bearing=0, pitch=0)
tooltip = {"html": "<b>Accès:</b> {access_index}/100 &nbsp; <b>Score:</b> {baseline_score}/6<br/>"
                   "<b>Prix:</b> {price_txt} ¥/m²<br/><b>Type:</b> {afford_type} &nbsp; "
                   "<b>Value:</b> {value_score}",
           "style": {"backgroundColor": "#222", "color": "white"}}
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip,
                         map_style="light"), use_container_width=True)

# ----------------------------- Recommender table -----------------------------
if reco:
    sel = df[(df["price_per_m2"] <= budget) & (df["access_index"] >= min_acc)]
    sel = sel.sort_values("value_score", ascending=False)
    st.subheader(f"🏆 {len(sel):,} hexagones correspondent à ton budget + accessibilité")
    st.dataframe(
        sel[["cell", "access_index", "price_per_m2", "value_score", "afford_type", "n_price"]]
        .head(25).rename(columns={"price_per_m2": "prix ¥/m²", "access_index": "accès/100"}),
        use_container_width=True, hide_index=True)

# ----------------------------- KPIs -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Score 15-min moyen", f"{df['baseline_score'].mean():.2f}/6")
c2.metric("Prix médian", f"{df['price_per_m2'].median():,.0f} ¥/m²")
priv = (df["afford_type"] == "Privilégié (cher)").sum()
good = (df["afford_type"] == "Accessible & abordable").sum()
c3.metric("Corridors accessibles & abordables", f"{good:,}")
c4.metric("Hexagones « privilégiés »", f"{priv:,}")

# ----------------------------- Transparency -----------------------------
with st.expander("ℹ️ Sources de données & méthodologie"):
    st.markdown("""
- **POI** : Gaode/AMap SHP 2024 (6 besoins universels) — *éducation* via dataset AMap 2026 (GCJ-02→WGS84).
- **Prix** : Gaode `房价数据` + Anjuke (¥/m², médiane par hexagone ; couverture ≈ 25 % des hexagones, gris = sans donnée).
- **Réseau** : graphe routier Gaode `路网合集` (597k nœuds) — isochrones par **distance réseau réelle** (pas euclidienne).
- **Unité** : Uber H3 résolution 8 (~0.74 km²). **Score baseline** = nb de besoins atteignables ≤15 min à pied OU à vélo.
- **Cadre** : Moreno et al. (2021) ; *Shanghai 15-min Community Life Circle Guidelines* (2016) ; critique équité Weng et al. (2019).
- **Limites** : présence POI ≠ qualité/capacité ; prix = prix affichés ; couverture rurale partielle.
""")
