# 15-Minute Shanghai — Track C (Affordability) · PLAN DE SPRINT FINAL

> **Contexte** : ~1 semaine restante (mode sauvetage). Stack app = **Streamlit + pydeck/folium**.
> **Pondération** : Notebooks 35% · App web 35% · Trello 15% · Lit review 15%.
> **Question de recherche (Track C)** : *Le 15-minute city à Shanghai = privilège des riches, ou existe-t-il des corridors « forte accessibilité + faible coût » ?*

---

## 📦 DONNÉES — source maître identifiée

**Jeu maître = `C:\Users\pc\Downloads\01-SHP\01-SHP\2024.09`** (Gaode/AMap 2024, complet, même base que le collègue).
Contient POI par catégorie + prix immobilier + métro/bus + réseau routier + pistes cyclables + limites admin. **On construit presque tout à partir de là.**

Compléments :
- **`Downloads\2023_Shp\Shp`** — POI 2023 par catégorie (« complete » selon le prof) → validation / fallback.
- **`xwechat_files\...\msg\file\2026-06\EDU 2026 POI`** — éducation 2026 nettoyée (AMap API, 4 143 POI, **GCJ-02**). ⚠️ chemin WeChat volatile → **copier dans `data/` dès J1**.
- **`anjuke_shanghai_cleaned.parquet`** — prix/loyers immobilier (2e source prix, Track C).
- **`regression_from_scratch.ipynb`** — régression prix ~ distance métro (à réutiliser/étendre).

### ⚠️ Pièges techniques à NE PAS oublier
1. **CRS** : SHP = `_WGS84` ; EDU 2026 = **GCJ-02** ; anjuke = à vérifier. → **tout reprojeter en WGS84 (EPSG:4326)** avant jointure spatiale, sinon décalage ~500 m. (GCJ-02→WGS84 : lib `eviltransform`/`coord-convert` ou formule de conversion.)
2. **Shapefile = 4+ fichiers** : charger en gardant `.shp .dbf .shx .prj .cpg` ensemble (jamais le `.shp` seul).
3. **Encodage chinois** : noms de fichiers + champs en chinois → lire avec `encoding` (cpg présent ; sinon GBK/UTF-8). Catégorie = `nom_fichier.split("_")[1]` (loader fourni par le prof).
4. **Volumétrie** : certains `.dbf` font >1 Go (地名地址信息, 楼栋号, 路网合集). Ne charger QUE les couches utiles, filtrer sur la bbox tôt.

### Mapping catégories Gaode → 6 besoins universels (baseline)
| Besoin | Couches 2024.09 |
|---|---|
| 🍜 Alimentation / commerces | `餐饮服务`, `购物服务` |
| 🏥 Santé | `医疗保健服务` |
| 🎓 Éducation | **EDU 2026 POI** (PRIMAIRE) — ⚠️ le prof a signalé un problème avec l'éducation 2024, donc NE PAS utiliser `科教文化服务`/`学校点` de 2024.09 ; option cross-check = éducation 2023 |
| 💼 Emploi | `公司企业`, `商务写字楼`, `产业园区-点` |
| 🌳 Loisir / sport / culture | `体育休闲服务`, `休闲娱乐`, `公园广场点`, `风景名胜-点`, `健身房` |
| 🏦 Services publics | `生活服务`, `公共设施`, `金融保险服务`, `政府机构及社会团体` |
| **Track C — coût** | `房价数据` (SHP prix) + `anjuke` + `住宅小区-面` |
| **Transit (mode)** | `地铁站`, `地铁线`, `公交车站` |
| **Réseau routing** | `行人道路`, `自行车道`, `路网合集` |

---

## ⚙️ Décisions / raccourcis assumés (mode 1 semaine)
| Sujet | Idéal (brief) | Ce qu'on fait | Pourquoi |
|---|---|---|---|
| Routing | Gaode API live | **Distance réseau** sur `行人道路` (marche) + `自行车道`/`路网合集` (vélo) via networkx | Le réseau réel est déjà dans les SHP → pas besoin d'API |
| Unité spatiale | grille 500m → H3 res 8 | **H3 res 8** directement (calcul + affichage) | Évite la double construction |
| Modes | walk/bike/transit/car | **walk + bike** (baseline) ; transit (métro/bus) en bonus si temps | Baseline = walk OR bike |
| App | React+Mapbox+deck.gl | **Streamlit + pydeck H3HexagonLayer** | 100% Python, déploiement rapide |

---

## 📅 Découpage jour par jour (7 jours)

### J1 — Fondations (AUJOURD'HUI)
- [ ] **Trello** : board « 15MC Shanghai – [Nom] », inviter l'instructeur, 5 colonnes (Sprint 1→5), y poser les cartes de ce plan. *(à bouger CHAQUE jour, pas rétroactivement)*
- [ ] **Repo Git** : `git init`, structure `notebooks/ app/ data/ data/raw/ outputs/`, `.gitignore` (exclure `.csv .parquet .shp .dbf .downloading`), `README.md`, push GitHub.
- [ ] **Env Python** : `requirements.txt` + vérifier import de `geopandas h3 shapely pyproj fiona/pyogrio folium pydeck streamlit networkx scikit-learn statsmodels`.
- [ ] **Rapatrier les données** : copier `2024.09`, `EDU 2026 POI` (chemin WeChat volatile !) et `anjuke_*.parquet` dans `data/raw/`.
- [ ] **Sanity-check + CRS** : charger 1 couche POI (loader du prof), vérifier encodage chinois OK, reprojeter en EPSG:4326, vérifier qu'EDU 2026 (GCJ-02) se superpose bien après conversion. Définir la **bbox zone d'étude** (Shanghai centrale).

### J2 — Notebook `01_data_collection.ipynb` + Lit review
- [ ] **Lit review** (markdown en tête, **≥800 mots, ≥4 papiers**) : (a) méthodo mesure accessibilité 15-min + (b) **critique équité**. *(15%)*
- [ ] Loader générique SHP (boucle glob + catégorie depuis nom de fichier + reprojection WGS84).
- [ ] Charger les couches utiles (6 besoins + prix + transit + réseau), filtrer bbox, valider, dédoublonner.
- [ ] Export `data/clean/poi.parquet`, `prices.parquet`, `network_*.parquet` documentés.

### J3 — Notebook `02_grid_isochrones.ipynb`
- [ ] Générer hexagones **H3 res 8** sur la bbox.
- [ ] Construire graphe **piéton** (`行人道路`) et **vélo** (`自行车道`+routes) avec networkx ; vitesses (marche 4.8 km/h, vélo 15 km/h) → seuil 15 min.
- [ ] Pour chaque hex : POI de chaque besoin atteignables ≤15 min marche ET ≤15 min vélo (distance réseau depuis le centre de l'hex / nœud le plus proche).
- [ ] **Cache** des calculs lourds (parquet/pickle).

### J4 — Notebook `03_scoring_h3.ipynb`
- [ ] **Score baseline** : nb des 6 besoins accessibles ≤15 min (0–6 ou %). Justifier pondération.
- [ ] **Score Track C** : jointure spatiale prix (`房价数据`+anjuke) ↔ hex → prix/m² par hex ; ratio accessibilité/prix ; **corridors « accessible + abordable »**.
- [ ] Étendre la **régression** : prix ~ distance métro + score accessibilité (répond à la question de recherche).
- [ ] **Export `outputs/hexes.geojson`** (res 8, toutes colonnes scores) → consommé par l'app.

### J5 — App Streamlit
- [ ] `app/streamlit_app.py` : charge `hexes.geojson` → **pydeck H3HexagonLayer** choroplèthe.
- [ ] Toggles baseline ↔ Track C, mode walk/bike, métrique affichée.
- [ ] Click hex → panneau détail (scores, prix, besoins manquants).
- [ ] Recommandeur « où habiter » (filtre budget + accessibilité min). Panneau transparence données.
- [ ] Vérifier **chargement < 4s** (simplifier GeoJSON si besoin).

### J6 — Déploiement + polish
- [ ] Déployer sur **Streamlit Community Cloud** (URL publique), test mobile.
- [ ] Notebooks propres (run top→bottom), markdown + figures. README repo avec liens.

### J7 — Marge / démo
- [ ] Buffer imprévus.
- [ ] Bonus *si temps* : mode transit (métro/bus), 2e métrique Track C (ratio revenu/loyer).
- [ ] Répétition démo finale.

---

## 🎯 Règle de priorité si le temps manque
1. **Notebooks 01→03 qui tournent + `hexes.geojson` exporté** (35% + socle de tout)
2. **App Streamlit déployée**, même minimale (35%)
3. **Lit review 800 mots** (15% — à sécuriser tôt)
4. **Trello à jour** (15% — gratuit si cartes bougées chaque jour)
5. Transit, car, 2e métrique = bonus, jamais au prix de ce qui précède.
