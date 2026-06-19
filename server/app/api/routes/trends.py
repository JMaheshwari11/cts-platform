"""Trends analytics - rolling avg, seasonality, anomalies, YoY."""

import pandas as pd
import numpy as np
from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/kpis")
def trends_kpis():
    """Trends-specific KPIs including YoY comparison."""
    df = cache.df.copy()
    df["year"] = df["ship_date"].dt.year

    years = sorted(df["year"].dropna().unique().tolist())
    latest = max(years)
    prev = latest - 1

    latest_df = df[df["year"] == latest]
    prev_df = df[df["year"] == prev]

    def yoy_pct(curr, past):
        if past in (0, None) or pd.isna(past):
            return 0.0
        return float((curr - past) / past * 100)

    return {
        "total_volume": int(len(df)),
        "years_covered": len(years),
        "active_months": int(df["ship_date"].dt.to_period("M").nunique()),
        "latest_year": int(latest),
        "yoy_cost_pct": round(yoy_pct(latest_df["total_cost"].sum(), prev_df["total_cost"].sum()), 2),
        "yoy_shipments_pct": round(yoy_pct(len(latest_df), len(prev_df)), 2),
        "yoy_otd_pp": round(float(latest_df["otd_flag"].mean() * 100 - prev_df["otd_flag"].mean() * 100), 2),
        "yoy_util_pp": round(float(latest_df["vehicle_utilization_weight"].mean() - prev_df["vehicle_utilization_weight"].mean()), 2),
        "latest_total_cost": round(float(latest_df["total_cost"].sum()), 2),
        "latest_shipments": int(len(latest_df)),
    }


@router.get("/rolling")
def rolling_trend(window: int = 7, metric: str = "total_cost"):
    """Daily series with rolling average overlay."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    elif metric == "otd_pct":
        daily = df.groupby("date")["otd_flag"].mean() * 100
    elif metric == "cost_per_kg":
        daily = df.groupby("date")["cost_per_kg"].mean()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    rolling = daily.rolling(window=window, min_periods=1).mean()

    return [
        {
            "date": str(d),
            "value": round(float(v), 2),
            "rolling": round(float(rolling.loc[d]), 2),
        }
        for d, v in daily.items()
    ]


@router.get("/anomalies")
def anomalies(metric: str = "total_cost", z_threshold: float = 2.5):
    """Detect outlier days using z-score on daily values."""
    df = cache.df.copy()
    df["date"] = df["ship_date"].dt.date

    if metric == "shipments":
        daily = df.groupby("date").size()
    elif metric == "total_cost":
        daily = df.groupby("date")["total_cost"].sum()
    else:
        daily = df.groupby("date")["total_cost"].sum()

    daily = daily.sort_index()
    mean = daily.mean()
    std = daily.std()
    if std == 0 or pd.isna(std):
        return []

    anomalies_list = []
    for d, v in daily.items():
        z = (v - mean) / std
        if abs(z) >= z_threshold:
            anomalies_list.append({
                "date": str(d),
                "value": round(float(v), 2),
                "z_score": round(float(z), 2),
                "direction": "above" if z > 0 else "below",
            })
    return anomalies_list


@router.get("/seasonality")
def seasonality():
    """Average monthly pattern across years (1-12)."""
    df = cache.df.copy()
    df["month"] = df["ship_date"].dt.month
    grp = df.groupby("month").agg(
        avg_shipments=("shipment_id", "count"),
        avg_cost=("total_cost", "sum"),
        avg_otd=("otd_flag", "mean"),
    ).reset_index()

    # Normalize to per-year averages
    n_years = df["ship_date"].dt.year.nunique() or 1
    grp["avg_shipments"] = (grp["avg_shipments"] / n_years).round(0).astype(int)
    grp["avg_cost"] = (grp["avg_cost"] / n_years).round(2)
    grp["avg_otd"] = (grp["avg_otd"] * 100).round(2)

    MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    return [
        {
            "month": int(row["month"]),
            "month_name": MONTH_NAMES[int(row["month"]) - 1],
            "avg_shipments": int(row["avg_shipments"]),
            "avg_cost": float(row["avg_cost"]),
            "avg_otd": float(row["avg_otd"]),
        }
        for _, row in grp.iterrows()
    ]


@router.get("/peak-seasons")
def peak_seasons():
    """Identify peak months from is_peak_season flag."""
    df = cache.df
    peak = df[df["is_peak_season"] == 1] if "is_peak_season" in df.columns else df.head(0)
    non_peak = df[df["is_peak_season"] == 0] if "is_peak_season" in df.columns else df

    return {
        "peak_shipments": int(len(peak)),
        "non_peak_shipments": int(len(non_peak)),
        "peak_pct": round(len(peak) / len(df) * 100, 2) if len(df) else 0,
        "peak_avg_cost": round(float(peak["total_cost"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_cost": round(float(non_peak["total_cost"].mean()), 2) if len(non_peak) else 0,
        "peak_avg_delay": round(float(peak["delay_days"].mean()), 2) if len(peak) else 0,
        "non_peak_avg_delay": round(float(non_peak["delay_days"].mean()), 2) if len(non_peak) else 0,
    }
