import json
from pathlib import Path

data_file = Path("data/raw/road_eqr_carpda_20260816T162343.json")
with open(data_file) as f:
    d = json.load(f)

print("ID (dimension order):", d.get("id"))
print("SIZE (dimension sizes):", d.get("size"))
print("\nDimensions:")

for dim_name in d.get("id", []):
    dim_data = d.get("dimension", {}).get(dim_name, {})
    cat_data = dim_data.get("category", {})
    cat_index = cat_data.get("index", {})
    cat_label = cat_data.get("label", {})
    
    print(f"\n{dim_name}:")
    print(f"  index type: {type(cat_index)}, value: {str(cat_index)[:100]}")
    print(f"  label type: {type(cat_label)}, count: {len(cat_label)}")
    if isinstance(cat_index, list):
        print(f"  index (first 5): {cat_index[:5]}")
    if isinstance(cat_label, dict):
        print(f"  label keys (first 5): {list(cat_label.keys())[:5]}")
