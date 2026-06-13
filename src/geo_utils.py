# -*- coding: utf-8 -*-
"""Utilitaires géo partagés — 15MC Shanghai Track C.

- Conversion GCJ-02 -> WGS84 (datum chinois -> standard)
- Loader générique de shapefiles POI Gaode (catégorie depuis le nom de fichier)
"""
from pathlib import Path
import math
import numpy as np
import pandas as pd
import geopandas as gpd

# --------------------------------------------------------------------------
# GCJ-02 (coordonnées "Mars" chinoises) -> WGS84
# Source EDU 2026 POI = GCJ-02 ; les SHP 2024 sont en WGS84.
# --------------------------------------------------------------------------
_A = 6378245.0
_EE = 0.00669342162296594323


def _transform_lat(x, y):
    ret = -100 + 2 * x + 3 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.abs(x))
    ret += (20 * np.sin(6 * x * np.pi) + 20 * np.sin(2 * x * np.pi)) * 2 / 3
    ret += (20 * np.sin(y * np.pi) + 40 * np.sin(y / 3 * np.pi)) * 2 / 3
    ret += (160 * np.sin(y / 12 * np.pi) + 320 * np.sin(y * np.pi / 30)) * 2 / 3
    return ret


def _transform_lon(x, y):
    ret = 300 + x + 2 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * np.sqrt(np.abs(x))
    ret += (20 * np.sin(6 * x * np.pi) + 20 * np.sin(2 * x * np.pi)) * 2 / 3
    ret += (20 * np.sin(x * np.pi) + 40 * np.sin(x / 3 * np.pi)) * 2 / 3
    ret += (150 * np.sin(x / 12 * np.pi) + 300 * np.sin(x / 30 * np.pi)) * 2 / 3
    return ret


def gcj02_to_wgs84(lng, lat):
    """Convertit des coordonnées GCJ-02 vers WGS84. Vectorisé (numpy/pandas OK)."""
    lng = np.asarray(lng, dtype=float)
    lat = np.asarray(lat, dtype=float)
    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lon(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * np.pi
    magic = 1 - _EE * np.sin(radlat) ** 2
    sqrtmagic = np.sqrt(magic)
    dlat = (dlat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrtmagic) * np.pi)
    dlng = (dlng * 180.0) / (_A / sqrtmagic * np.cos(radlat) * np.pi)
    return lng * 2 - (lng + dlng), lat * 2 - (lat + dlat)


# --------------------------------------------------------------------------
# Loader shapefiles Gaode (d'après le code fourni par le prof)
# Catégorie = 2e segment du nom de fichier : 上海市_餐饮服务_WGS84 -> 餐饮服务
# --------------------------------------------------------------------------
def load_poi_shapefiles(shp_dir, patterns=None, bbox=None, to_crs="EPSG:4326"):
    """Charge un ou plusieurs shapefiles POI d'un dossier et concatène.

    shp_dir   : dossier contenant les .shp (+ .dbf/.shx/.prj/.cpg)
    patterns  : liste de motifs glob (ex. ["*餐饮*", "*医疗*"]) ; None = tous les *.shp
    bbox      : (minx, miny, maxx, maxy) en WGS84 pour filtrer au chargement
    to_crs    : reprojection finale (par défaut WGS84)
    """
    shp_dir = Path(shp_dir)
    files = []
    for pat in (patterns or ["*.shp"]):
        files.extend(sorted(shp_dir.glob(pat if pat.endswith(".shp") else pat + ".shp")))
    files = sorted(set(files))

    gdfs = []
    for shp in files:
        gdf = gpd.read_file(shp, engine="pyogrio", bbox=bbox)
        gdf["source_file"] = shp.stem
        parts = shp.stem.split("_")
        gdf["行业大"] = parts[1] if len(parts) >= 2 else shp.stem
        gdfs.append(gdf)

    if not gdfs:
        raise FileNotFoundError(f"Aucun .shp trouvé dans {shp_dir} (patterns={patterns})")

    out = pd.concat(gdfs, ignore_index=True)
    out = gpd.GeoDataFrame(out, geometry="geometry", crs=gdfs[0].crs)
    if to_crs and out.crs is not None:
        out = out.to_crs(to_crs)
    return out


# --------------------------------------------------------------------------
# Traduction des sous-types POI Gaode (行业小/行业中) -> libellés français,
# pour afficher des types concrets dans l'app (ex. "supermarché, épicerie").
# Ordre = du plus spécifique au plus générique.
# --------------------------------------------------------------------------
SUBTYPE_FR = [
    # courses
    ("便利店", "épicerie"), ("便民", "épicerie"), ("超市", "supermarché"),
    ("农副产品", "marché de produits frais"), ("农贸", "marché de produits frais"),
    ("果品", "marché de fruits"), ("蔬菜", "marché de légumes"),
    ("水产", "marché aux poissons"), ("海鲜", "marché aux poissons"), ("综合市场", "marché"),
    # santé
    ("药", "pharmacie"), ("口腔", "dentiste"), ("眼科", "ophtalmologie"),
    ("诊所", "clinique"), ("卫生院", "dispensaire"), ("三级甲等", "grand hôpital"),
    ("专科医院", "hôpital spécialisé"), ("医院", "hôpital"),
    # école
    ("幼儿园", "maternelle"), ("小学", "école primaire"), ("中学", "collège/lycée"),
    ("高等院校", "université"), ("职业技术", "lycée pro"), ("培训", "centre de formation"),
    # services
    ("银行", "banque"), ("ATM", "distributeur"), ("证券", "banque"),
    ("金融保险", "services financiers"), ("邮局", "poste"), ("邮政", "poste"),
    ("公共厕所", "toilettes publiques"), ("避难", "abri d'urgence"),
    # parc / sport
    ("健身", "salle de sport"), ("运动场", "terrain de sport"), ("体育", "sport"),
    ("公园", "parc"), ("影剧院", "cinéma/théâtre"), ("KTV", "karaoké"),
    ("酒吧", "bar"), ("网吧", "cybercafé"), ("棋牌", "salle de jeux"),
    ("娱乐", "divertissement"), ("休闲", "loisirs"), ("采摘", "ferme de cueillette"),
]


def _label_fr(text):
    for kw, fr in SUBTYPE_FR:
        if kw in text:
            return fr
    return None


def types_per_cell(poi, transit, criteria, res, topn=3):
    """Pour chaque critère, renvoie une Series cell -> 'type1, type2, type3' (libellés FR)."""
    import h3
    poi = poi.copy()
    poi["cell"] = [h3.latlng_to_cell(la, lo, res) for la, lo in zip(poi["lat"], poi["lon"])]
    txt = poi["行业小"].fillna("") + "|" + poi["行业中"].fillna("")
    poi["fr"] = [_label_fr(t) for t in txt]
    cat = poi["行业大"].fillna("") + "|" + poi["行业中"].fillna("") + "|" + poi["行业小"].fillna("")

    def top_labels(sub):
        sub = sub.dropna(subset=["fr"])
        if sub.empty:
            return pd.Series(dtype=object)
        return (sub.groupby(["cell", "fr"]).size().reset_index(name="n")
                .sort_values("n", ascending=False).groupby("cell")["fr"]
                .apply(lambda s: ", ".join(s.head(topn))))

    out = {}
    for key, spec in criteria.items():
        if spec.get("source") == "transit":
            t = transit.copy()
            tp = t.geometry.representative_point()
            t["cell"] = [h3.latlng_to_cell(la, lo, res) for la, lo in zip(tp.y.values, tp.x.values)]
            t["fr"] = t["mode"].map({"metro": "métro", "bus": "bus"})
            out[key] = top_labels(t)
        elif "need" in spec:
            out[key] = top_labels(poi[poi["need"] == spec["need"]])
        else:
            out[key] = top_labels(poi[cat.str.contains(spec["match"], regex=True)])
    return out
