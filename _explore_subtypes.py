# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
import geopandas as gpd
from config import DATA_CLEAN, CRITERIA

poi = gpd.read_parquet(DATA_CLEAN / "poi.parquet")
cat = (poi["行业大"].fillna("") + "|" + poi["行业中"].fillna("") + "|" + poi["行业小"].fillna(""))
for key, spec in CRITERIA.items():
    if spec.get("source") == "transit":
        print(f"\n=== {key} (transit) ==="); continue
    if "need" in spec:
        sub = poi[poi["need"] == spec["need"]]
    else:
        sub = poi[cat.str.contains(spec["match"], regex=True)]
    print(f"\n=== {key} ({len(sub):,}) — top 行业小 ===")
    print(sub["行业小"].value_counts().head(12).to_string())
