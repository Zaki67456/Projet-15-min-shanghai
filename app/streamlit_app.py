# -*- coding: utf-8 -*-
"""15-Minute Shanghai — Track C (Affordability). App Streamlit + pydeck H3HexagonLayer."""
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from matplotlib import colormaps, colors as mcolors

st.set_page_config(page_title="15-Minute Shanghai — Track C", layout="wide", page_icon="🏙️")

# --- Critères d'accessibilité (écrits, pour que l'utilisateur comprenne) ---
CRITERIA = {
    "courses":    ("🛒 Courses alimentaires", "Supermarché, supérette ou marché alimentaire à ≤15 min (courses du quotidien, pas les restaurants)."),
    "sante":      ("🏥 Santé de proximité", "Hôpital, clinique, dispensaire ou pharmacie à ≤15 min."),
    "ecole":      ("🏫 École", "Crèche, école, collège ou lycée à ≤15 min."),
    "transport":  ("🚉 Transport en commun", "Station de métro ou arrêt de bus à ≤15 min (accès à l'emploi sans voiture)."),
    "services":   ("🏦 Services essentiels", "Banque, poste ou équipement public à ≤15 min."),
    "parc_sport": ("🌳 Parc / sport", "Parc, espace vert, terrain ou salle de sport à ≤15 min."),
}
AFFORD = ("🏠 Logement abordable", "Prix médian de l'hexagone sous la médiane de la ville.")


@st.cache_data
def load_data():
    here = Path(__file__).parent
    for p in [here / "hexes_app.parquet", here.parent / "data" / "clean" / "hexes_scored.parquet"]:
        if p.exists():
            df = pd.read_parquet(p)
            return df.drop(columns=[c for c in ["geometry"] if c in df.columns])
    st.error("Fichier de données introuvable."); st.stop()


df = load_data()

# Indicateurs cartographiables (l'indice pondéré-marche en 1er = vue par défaut, vrai dégradé)
METRICS = {
    "Indice d'accessibilité /100 (pondéré marche)": ("access_index", 0, 100, "RdYlGn"),
    "Score marche seule /6": ("n_walk", 0, 6, "RdYlGn"),
    "Score complet /7 (+ logement abordable)": ("score_complet_7", 0, 7, "RdYlGn"),
    "Score 15-min /6 (marche OU vélo)": ("baseline_score", 0, 6, "RdYlGn"),
    "Prix médian (¥/m²)": ("price_per_m2", None, None, "viridis_r"),
    "Value score (accès − prix)": ("value_score", -60, 60, "RdYlGn"),
}
# un indicateur binaire par critère précis
for k, (lab, _) in CRITERIA.items():
    METRICS[f"Accès — {lab}"] = (f"acc_{k}", 0, 1, "RdYlGn")
METRICS[f"Accès — {AFFORD[0]}"] = ("affordable", 0, 1, "RdYlGn")


def to_colors(values, vmin, vmax, cmap_name, faded=None):
    v = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    finite = v[np.isfinite(v)]
    if vmin is None: vmin = np.percentile(finite, 5) if finite.size else 0
    if vmax is None: vmax = np.percentile(finite, 95) if finite.size else 1
    cmap, norm = colormaps[cmap_name], mcolors.Normalize(vmin, vmax)
    out = []
    for i, val in enumerate(v):
        if not np.isfinite(val):
            out.append([210, 210, 210, 30])
        else:
            r, g, b, _ = cmap(norm(val))
            a = 175 if (faded is None or faded[i]) else 20
            out.append([int(r*255), int(g*255), int(b*255), a])
    return out


# ----------------------------- Sidebar -----------------------------
st.sidebar.title("🏙️ 15-Minute Shanghai")
st.sidebar.caption("Track C — Accessibilité × Abordabilité")
metric_label = st.sidebar.selectbox("Indicateur cartographié", list(METRICS))
col, vmin, vmax, cmap_name = METRICS[metric_label]

st.sidebar.markdown("### 🎯 Recommandeur « Où habiter ? »")
reco = st.sidebar.checkbox("Activer le filtre")
budget = st.sidebar.slider("Budget max (¥/m²)", 2000, 150000, 35000, 1000)
min_acc = st.sidebar.slider("Accessibilité minimale /100", 0, 100, 80, 5)
must = st.sidebar.multiselect("Critères obligatoires",
                              [lab for _, (lab, _) in CRITERIA.items()])
lab_to_key = {lab: k for k, (lab, _) in CRITERIA.items()}

faded = None
data = df.copy()
if reco:
    keep = (data["price_per_m2"] <= budget) & (data["access_index"] >= min_acc)
    for lab in must:
        keep &= data[f"acc_{lab_to_key[lab]}"].astype(bool)
    faded = keep.to_numpy()

data["color"] = to_colors(data[col], vmin, vmax, cmap_name, faded=faded)
data["price_txt"] = data["price_per_m2"].round(0)


def build_tip(r):
    price = r["price_per_m2"]
    if pd.isna(price):
        quartier = "<b>Quartier :</b> prix non disponible"
    else:
        aff = bool(r["affordable"])
        quartier = (f"<b>Quartier :</b> {'🟢 abordable' if aff else '🔴 cher'} "
                    f"— se loger ≈ {price:,.0f} ¥/m²")
    lines = [quartier,
             f"<b>Accessibilité :</b> {r['access_index']}/100 (15 min à pied/vélo)",
             "<i>Services accessibles en 15 min :</i>"]
    for k, (lab, _) in CRITERIA.items():
        ok = bool(r.get(f"acc_{k}", False))
        lines.append(f"{lab} : {'✅' if ok else '❌ &gt;15 min'}")
    return "<br/>".join(lines)


data["tip"] = data.apply(build_tip, axis=1)

# ----------------------------- Main -----------------------------
st.title("Le 15-minute city à Shanghai : privilège ou réalité accessible ?")
st.caption(f"Indicateur : **{metric_label}** · {len(df):,} hexagones H3 (résolution 7, ~5 km²) · "
           "distances réseau réelles · marche ≈ 1.2 km, vélo ≈ 3.75 km en 15 min.")
if col == "baseline_score":
    st.info("ℹ️ Cette vue (marche **OU** vélo) est verte presque partout : 15 min à vélo ≈ 3.75 km couvrent "
            "une grande partie de Shanghai dense. Pour voir les vraies différences, choisis **l'indice "
            "d'accessibilité** ou le **score marche seule** — à pied, l'accès varie beaucoup (école : 26 % seulement).")

layer = pdk.Layer("H3HexagonLayer", data=data, get_hexagon="cell", get_fill_color="color",
                  pickable=True, stroked=True, get_line_color=[255, 255, 255, 40],
                  line_width_min_pixels=0.5, extruded=False)
view = pdk.ViewState(latitude=31.22, longitude=121.47, zoom=8.4)
tooltip = {"html": "{tip}",
           "style": {"backgroundColor": "#222", "color": "white", "fontSize": "12px",
                     "padding": "8px", "borderRadius": "6px"}}
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, tooltip=tooltip,
                         map_style="light"), use_container_width=True)

# ----------------------------- Recommender table -----------------------------
if reco:
    sel = df[(df["price_per_m2"] <= budget) & (df["access_index"] >= min_acc)]
    for lab in must:
        sel = sel[sel[f"acc_{lab_to_key[lab]}"].astype(bool)]
    sel = sel.sort_values("value_score", ascending=False)
    st.subheader(f"🏆 {len(sel):,} hexagones correspondent à tes critères")
    st.dataframe(sel[["cell", "access_index", "price_per_m2", "value_score", "afford_type"]]
                 .head(25).rename(columns={"price_per_m2": "prix ¥/m²", "access_index": "accès/100"}),
                 use_container_width=True, hide_index=True)

# ----------------------------- KPIs -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Score 15-min moyen", f"{df['baseline_score'].mean():.2f}/6")
c2.metric("Prix médian", f"{df['price_per_m2'].median():,.0f} ¥/m²")
c3.metric("Corridors accessibles & abordables",
          f"{(df['afford_type'] == 'Accessible & abordable').sum():,}")
c4.metric("Hexagones « privilégiés »", f"{(df['afford_type'] == 'Privilégié (cher)').sum():,}")

# ----------------------------- Criteria scorecard (écrit) -----------------------------
st.markdown("### 📋 Les critères d'accessibilité mesurés")
st.caption("Chaque hexagone est évalué sur ces critères précis (atteignables à pied ou à vélo en 15 min) :")
rows = []
for k, (lab, desc) in CRITERIA.items():
    rows.append({"Critère": lab, "Définition": desc,
                 "% hexagones desservis": f"{100*df[f'acc_{k}'].mean():.0f}%"})
rows.append({"Critère": AFFORD[0], "Définition": AFFORD[1],
             "% hexagones desservis": f"{100*df['affordable'].fillna(False).mean():.0f}%"})
st.table(pd.DataFrame(rows))

with st.expander("ℹ️ Sources de données & méthodologie"):
    st.markdown("""
- **POI** : Gaode/AMap SHP 2024 — filtrés en sous-catégories précises (`行业中`/`行业小`) ; *éducation* via dataset AMap 2026 (GCJ-02→WGS84).
- **Prix** : Gaode `房价数据` + Anjuke (¥/m², médiane par hexagone).
- **Réseau** : graphe routier Gaode `路网合集` (597k nœuds) — isochrones par **distance réseau réelle** (pas euclidienne).
- **Unité** : Uber H3 **résolution 7** (~5 km²). **Score** = critères atteignables ≤15 min à pied OU à vélo.
- **Cadre** : Moreno et al. (2021) · *Shanghai 15-min Community Life Circle Guidelines* (2016) · critique équité Weng et al. (2019).
- **Limites** : présence POI ≠ qualité/capacité ; prix = prix affichés ; couverture prix ≈ 47 % des hexagones (gris = sans donnée).
""")
