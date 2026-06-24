"""Products analytics - category, SKU, velocity/value, returns."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/kpis")
def product_kpis():
    df = cache.df
    cold_chain = df["temperature_controlled_required"].sum() if "temperature_controlled_required" in df.columns else 0
    hazardous = df["is_hazardous"].sum() if "is_hazardous" in df.columns else 0
    n_skus = df["sku"].nunique() if "sku" in df.columns else 0
    n_products = df["product_id"].nunique()
    n_categories = df["category"].nunique()
    return_rate = float(df["return_flag"].mean() * 100)
    damage_rate = float(df["damage_flag"].mean() * 100)
    avg_shelf = float(df["shelf_life_days"].mean()) if "shelf_life_days" in df.columns else 0

    return {
        "unique_products": int(n_products),
        "unique_skus": int(n_skus),
        "categories": int(n_categories),
        "cold_chain_shipments": int(cold_chain),
        "cold_chain_pct": round(float(cold_chain) / len(df) * 100, 2),
        "hazardous_shipments": int(hazardous),
        "hazardous_pct": round(float(hazardous) / len(df) * 100, 2),
        "return_rate_pct": round(return_rate, 2),
        "damage_rate_pct": round(damage_rate, 2),
        "avg_shelf_life_days": round(avg_shelf, 1),
    }


@router.get("/category-mix")
def category_mix():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("total_cost", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/top-skus")
def top_skus(limit: int = 15, sort_by: str = "total_cost"):
    df = cache.df
    grp = df.groupby(
        ["product_id", "product_name", "category", "sku"],
        observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_unit=("cost_per_unit", "mean"),
        return_count=("return_flag", "sum"),
        damage_count=("damage_flag", "sum"),
    ).reset_index().round(2)
    grp["return_rate_pct"] = (grp["return_count"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damage_count"] / grp["shipments"] * 100).round(2)

    if sort_by not in grp.columns:
        sort_by = "total_cost"
    grp = grp.sort_values(sort_by, ascending=False).head(limit)
    return grp.to_dict(orient="records")


@router.get("/velocity-value-matrix")
def velocity_value_matrix():
    """2D matrix: velocity_tier x value_tier with shipment + cost stats.
    
    Utilization returned as PERCENTAGE.
    """
    df = cache.df
    if "velocity_tier" not in df.columns or "value_tier" not in df.columns:
        return []
    grp = df.groupby(
        ["velocity_tier", "value_tier"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_util=("vehicle_utilization_weight", "mean"),
    ).reset_index()
    grp["avg_util"] = (grp["avg_util"] * 100).round(2)  # FIX
    grp = grp.round(2)
    return grp.to_dict(orient="records")


@router.get("/shelf-life-distribution")
def shelf_life_distribution():
    df = cache.df
    if "shelf_life_days" not in df.columns:
        return []
    products = df[["product_id", "shelf_life_days"]].drop_duplicates()
    bins = [0, 30, 90, 180, 365, 730, 10000]
    labels = ["<30d", "30-90d", "90-180d", "180-365d", "1-2yr", "2yr+"]
    products = products.copy()
    products["bucket"] = pd.cut(products["shelf_life_days"], bins=bins, labels=labels, right=True)
    grp = products.groupby("bucket", observed=True).size().reset_index(name="products")
    return grp.to_dict(orient="records")


@router.get("/returns-by-category")
def returns_by_category():
    df = cache.df
    grp = df.groupby("category", observed=True).agg(
        shipments=("shipment_id", "count"),
        returns=("return_flag", "sum"),
        damages=("damage_flag", "sum"),
    ).reset_index()
    grp["return_rate_pct"] = (grp["returns"] / grp["shipments"] * 100).round(2)
    grp["damage_rate_pct"] = (grp["damages"] / grp["shipments"] * 100).round(2)
    grp = grp.sort_values("return_rate_pct", ascending=False)
    return grp.to_dict(orient="records")
