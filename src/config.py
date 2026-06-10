# -*- coding: utf-8 -*-
"""Chemins centralisés du projet 15MC Shanghai — Track C."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN = PROJECT_ROOT / "data" / "clean"
OUTPUTS = PROJECT_ROOT / "outputs"

# Sources externes (hors repo — voir data_sources_15mc en mémoire)
SHP_2024 = Path(r"C:\Users\pc\Downloads\01-SHP\01-SHP\2024.09")          # jeu maître Gaode 2024
SHP_2023 = Path(r"C:\Users\pc\Downloads\2023_Shp\Shp")                    # fallback POI 2023
EDU_2026 = Path(r"C:\Users\pc\Documents\xwechat_files\wxid_5kyyf2fhk22m22_a738"
                r"\msg\file\2026-06\EDU 2026 POI\EDU 2026 POI")           # éducation (chemin volatile)
ANJUKE = PROJECT_ROOT / "anjuke_shanghai_cleaned.parquet"                 # prix immobilier

# Bounding box zone d'étude (Shanghai) — à affiner en S1, valeurs provisoires larges
SHANGHAI_BBOX = (120.85, 30.67, 122.25, 31.88)  # (minx, miny, maxx, maxy) WGS84

# Résolution H3 (7 = ~1.2 km de côté, ~5 km², hexagones plus gros — demande du prof)
H3_RES = 7

# Critères d'accessibilité PRÉCIS (Track C). Chaque critère = "atteignable à ≤15 min".
# 'match' = regex sur 行业大|行业中|行业小 ; 'need' = filtre direct ; 'source'='transit'.
CRITERIA = {
    "courses": {
        "label": "🛒 Courses alimentaires",
        "desc": "Supermarché, supérette ou marché alimentaire à ≤15 min (les courses du quotidien — pas les restaurants).",
        "match": r"便利店|便民|超市|超级市场|综合市场|菜市场|农贸|生鲜",
    },
    "sante": {
        "label": "🏥 Santé de proximité",
        "desc": "Hôpital, clinique, dispensaire ou pharmacie à ≤15 min.",
        "match": r"综合医院|专科医院|诊所|卫生院|医药|药房|药店",
    },
    "ecole": {
        "label": "🏫 École",
        "desc": "Crèche, école, collège ou lycée à ≤15 min (données scolaires 2026).",
        "need": "education",
    },
    "transport": {
        "label": "🚉 Transport en commun",
        "desc": "Station de métro ou arrêt de bus à ≤15 min (accès à l'emploi sans voiture).",
        "source": "transit",
    },
    "services": {
        "label": "🏦 Services essentiels",
        "desc": "Banque, poste ou équipement public à ≤15 min.",
        "match": r"银行|金融|邮政|邮局|公共设施|政府",
    },
    "parc_sport": {
        "label": "🌳 Parc / sport",
        "desc": "Parc, espace vert, terrain ou salle de sport à ≤15 min.",
        "match": r"公园|广场|运动场|体育|健身|绿地|风景名胜|休闲",
    },
}
# Critère d'abordabilité (calculé à partir du prix, pas du réseau)
AFFORDABLE_LABEL = "🏠 Logement abordable"

# Couches Gaode 2024 -> 6 besoins universels (utilisé par le notebook 01 de collecte)
NEEDS_LAYERS = {
    "alimentation": ["*餐饮服务*", "*购物服务*"],
    "sante":        ["*医疗保健服务*"],
    "emploi":       ["*公司企业*", "*商务写字楼*"],
    "loisir_sport": ["*体育休闲服务*", "*休闲娱乐*", "*公园广场点*", "*健身房*"],
    "services":     ["*生活服务*", "*公共设施*", "*金融保险服务*"],
    # education -> via EDU 2026 (NE PAS utiliser 科教文化服务 de 2024, signalé problématique)
}

# Vitesses pour les isochrones réseau (km/h)
WALK_KMH = 4.8
BIKE_KMH = 15.0
TIME_MIN = 15
