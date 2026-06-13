# 15-Minute Shanghai — Track C : Affordability

### 🔗 [**▶ Ouvrir l'application en ligne**](https://projet-15-min-shanghai-3u2rnygx3gwo2xfkontzpt.streamlit.app/)
Carte interactive H3 de Shanghai · accessibilité 15 min × prix du logement.

Analyse de l'accessibilité « ville du quart d'heure » à Shanghai, croisée avec le coût du logement.
**Question** : le 15-minute city à Shanghai est-il un privilège de riches, ou existe-t-il des corridors *forte accessibilité + faible coût* ?

**Livrables** : 3 notebooks (`notebooks/`) · application Streamlit déployée (lien ci-dessus) · revue de littérature (en tête du notebook 01).

## Structure
```
notebooks/   01_data_collection · 02_grid_isochrones · 03_scoring_h3
app/         application Streamlit (carte H3)
src/         utilitaires (geo_utils, config)
data/raw/    données brutes (non versionnées)
data/clean/  données nettoyées
outputs/     exports (hexes.geojson)
references/  sources de la revue de littérature
```

## Données
- **POI / prix / réseau / transit** : Gaode/AMap SHP 2024 (`01-SHP/2024.09`)
- **Éducation** : EDU 2026 POI (AMap API) — le jeu 2024 a un problème éducation signalé
- **Immobilier** : Anjuke (prix/m²)
- ⚠️ CRS : SHP en WGS84, EDU 2026 en GCJ-02 → tout reprojeté en EPSG:4326

## Installation
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Voir `PLAN.md` pour le découpage en sprints.
