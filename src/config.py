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

# Couches Gaode 2024 -> 6 besoins universels (baseline 15-min)
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
