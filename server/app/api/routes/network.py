"""Network / Map data - nodes, edges, lane volumes, India state map, mode mix."""

import pandas as pd
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/network", tags=["network"])

STATE_NORM = {
    "Delhi": "NCT of Delhi", "Pondicherry": "Puducherry", "Orissa": "Odisha",
    "Andaman And Nicobar": "Andaman & Nicobar", "Jammu And Kashmir": "Jammu & Kashmir",
    "Uttaranchal": "Uttarakhand", "Chattisgarh": "Chhattisgarh",
}


@router.get("/nodes")
def network_nodes():
    df = cache.df
    origins = df.groupby(
        ["origin_city", "origin_state", "origin_latitude", "origin_longitude"], observed=True
    ).agg(shipments=("shipment_id", "count"), total_cost=("total_cost", "sum")).reset_index()
    origins.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    origins["role"] = "origin"

    dests = df.groupby(
        ["destination_city", "destination_state", "destination_latitude", "destination_longitude"], observed=True
    ).agg(shipments=("shipment_id", "count"), total_cost=("total_cost", "sum")).reset_index()
    dests.columns = ["city", "state", "lat", "lon", "shipments", "total_cost"]
    dests["role"] = "destination"

    combined = pd.concat([origins, dests], ignore_index=True).round(2)
    return combined.to_dict(orient="records")


@router.get("/edges")
def network_edges():
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city", "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(100)
    return grp.to_dict(orient="records")


@router.get("/state-heatmap")
def state_heatmap():
    df = cache.df
    grp = df.groupby("destination_state", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
    ).reset_index().round(2)
    grp["destination_state"] = grp["destination_state"].astype(str).apply(
        lambda s: STATE_NORM.get(s, s)
    )
    return grp.to_dict(orient="records")


@router.get("/top-routes")
def top_routes(limit: int = 30):
    df = cache.df
    grp = df.groupby(
        ["origin_city", "destination_city",
         "origin_latitude", "origin_longitude",
         "destination_latitude", "destination_longitude"], observed=True,
    ).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_distance_km=("distance_km", "mean"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index().round(2)
    grp = grp.sort_values("shipments", ascending=False).head(limit)
    return [
        {
            "origin": str(r["origin_city"]),
            "destination": str(r["destination_city"]),
            "from_coords": [float(r["origin_longitude"]), float(r["origin_latitude"])],
            "to_coords": [float(r["destination_longitude"]), float(r["destination_latitude"])],
            "shipments": int(r["shipments"]),
            "total_cost": float(r["total_cost"]),
            "avg_distance_km": float(r["avg_distance_km"]),
            "avg_cost_per_kg": float(r["avg_cost_per_kg"]),
            "avg_otd_pct": round(float(r["avg_otd"]) * 100, 2),
        }
        for _, r in grp.iterrows()
    ]


@router.get("/network-kpis")
def network_kpis():
    df = cache.df
    return {
        "active_lanes": int(df["lane_id"].nunique()) if "lane_id" in df.columns else 0,
        "origin_cities": int(df["origin_city"].nunique()),
        "destination_cities": int(df["destination_city"].nunique()),
        "origin_states": int(df["origin_state"].nunique()),
        "destination_states": int(df["destination_state"].nunique()),
        "total_distance_km": round(float(df["distance_km"].sum()), 2),
        "avg_distance_km": round(float(df["distance_km"].mean()), 2),
        "total_shipments": int(len(df)),
        "total_cost": round(float(df["total_cost"].sum()), 2),
    }


@router.get("/mode-breakdown")
def mode_breakdown():
    """Road / Rail / Air / Multimodal stats."""
    df = cache.df
    grp = df.groupby("transport_mode", observed=True).agg(
        shipments=("shipment_id", "count"),
        total_cost=("total_cost", "sum"),
        avg_cost_per_kg=("cost_per_kg", "mean"),
        avg_cost_per_km=("cost_per_km", "mean"),
        avg_distance_km=("distance_km", "mean"),
        avg_co2_kg=("co2_emission_kg", "mean"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index().round(2)
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)
    grp["share_pct"] = (grp["shipments"] / grp["shipments"].sum() * 100).round(2)
    grp = grp.sort_values("shipments", ascending=False)
    return grp.to_dict(orient="records")


@router.get("/hub-strength")
def hub_strength():
    """Hub cities ranked by combined origin+destination volume."""
    df = cache.df
    origins = df.groupby("origin_city", observed=True).agg(
        out_ship=("shipment_id", "count"),
        out_cost=("total_cost", "sum"),
    ).reset_index().rename(columns={"origin_city": "city"})
    dests = df.groupby("destination_city", observed=True).agg(
        in_ship=("shipment_id", "count"),
        in_cost=("total_cost", "sum"),
    ).reset_index().rename(columns={"destination_city": "city"})

    merged = pd.merge(origins, dests, on="city", how="outer").fillna(0)
    merged["total_ship"] = merged["out_ship"] + merged["in_ship"]
    merged["total_cost"] = merged["out_cost"] + merged["in_cost"]
    merged = merged.sort_values("total_ship", ascending=False).head(10).round(2)
    return [
        {
            "city": str(r["city"]),
            "out_shipments": int(r["out_ship"]),
            "in_shipments": int(r["in_ship"]),
            "total_shipments": int(r["total_ship"]),
            "total_cost": float(r["total_cost"]),
        }
        for _, r in merged.iterrows()
    ]
