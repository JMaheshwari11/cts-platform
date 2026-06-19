"""
========================================================================
 CTS Analytics Platform — Data Ingestion Pipeline
========================================================================
 Purpose : Reads cleaned Excel → enriches → saves as Parquet
 
 Steps   : 1. Load Master_Combined from cleaned Excel
           2. Convert dtypes (dates, bools, categoricals)
           3. Add derived columns (lead times, on-time %, etc.)
           4. Save as Parquet (columnar, compressed)

 Input   : data/FMCG_CTS_Dataset_v4_Clean.xlsx
 Output  : server/processed/master_combined.parquet

 Usage   : python scripts/ingest.py
========================================================================
"""

import sys
from pathlib import Path

# Ensure we can import from app/
SCRIPT_DIR = Path(__file__).resolve().parent
SERVER_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SERVER_DIR))

import pandas as pd
import numpy as np
from loguru import logger

from app.config import settings, PROCESSED_DIR


def load_excel() -> pd.DataFrame:
    """Load Master_Combined sheet from cleaned Excel."""
    excel_path = settings.excel_path

    if not excel_path.exists():
        logger.error(f"❌ Input not found: {excel_path}")
        logger.error("   Run cleanup first: python scripts/clean_data.py")
        sys.exit(1)

    logger.info(f"📂 Reading Excel: {excel_path.name}")
    df = pd.read_excel(excel_path, sheet_name="Master_Combined", engine="openpyxl")
    logger.info(f"   ✅ Loaded {len(df):,} rows × {len(df.columns)} cols")
    return df


def normalize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to optimal dtypes for performance."""
    logger.info("🔧 Normalizing dtypes...")

    # Date columns
    date_cols = [
        "po_date", "order_date", "ship_date",
        "expected_delivery_date", "actual_delivery_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Bool columns
    bool_cols = [
        "consolidation_flag", "is_weekend", "is_peak_season",
        "temperature_controlled_required", "origin_temp_controlled",
        "dest_temp_controlled", "edge_is_active", "is_hazardous",
        "temperature_sensitive",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    # Categorical columns (saves significant memory)
    cat_cols = [
        "from_tier", "to_tier", "origin_city", "origin_state",
        "destination_city", "destination_state", "category",
        "transport_mode", "load_type", "service_level",
        "stream", "payment_status", "payment_terms",
        "shipment_priority", "velocity_tier", "value_tier",
        "delay_root_cause", "return_reason", "damage_type",
        "primary_issue", "distance_bucket", "volume_class",
        "carrier_name", "origin_storage_type", "dest_storage_type",
        "carrier_mode",
    ]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    logger.info("   ✅ Dtypes normalized")
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Compute analytics-friendly derived columns."""
    logger.info("⚙️  Computing derived columns...")

    # Lead time: PO → Actual Delivery (days)
    if {"po_date", "actual_delivery_date"}.issubset(df.columns):
        df["lead_time_days"] = (
            df["actual_delivery_date"] - df["po_date"]
        ).dt.days

    # Order-to-ship time (days)
    if {"order_date", "ship_date"}.issubset(df.columns):
        df["order_to_ship_days"] = (
            df["ship_date"] - df["order_date"]
        ).dt.days

    # Ship-to-delivery time (days)
    if {"ship_date", "actual_delivery_date"}.issubset(df.columns):
        df["ship_to_delivery_days"] = (
            df["actual_delivery_date"] - df["ship_date"]
        ).dt.days

    # YearMonth for time-series aggregations
    if "ship_date" in df.columns:
        df["year_month"] = df["ship_date"].dt.to_period("M").astype(str)

    # Cost intensity tier (for outlier detection)
    if "total_cost" in df.columns:
        df["cost_tier"] = pd.qcut(
            df["total_cost"], q=4,
            labels=["Q1_Low", "Q2_Mid", "Q3_High", "Q4_Premium"],
            duplicates="drop"
        )

    logger.info("   ✅ Derived columns added")
    return df


def save_parquet(df: pd.DataFrame) -> None:
    """Save DataFrame as compressed Parquet."""
    out_path = settings.parquet_path
    logger.info(f"💾 Writing Parquet: {out_path.name}")
    df.to_parquet(out_path, engine="pyarrow", compression="snappy", index=False)

    size_mb = out_path.stat().st_size / 1024**2
    logger.info(f"   ✅ Saved ({size_mb:.2f} MB)")


def main():
    logger.info("=" * 72)
    logger.info(" CTS Platform — Data Ingestion")
    logger.info("=" * 72)

    df = load_excel()
    df = normalize_dtypes(df)
    df = add_derived_columns(df)
    save_parquet(df)

    logger.info("=" * 72)
    logger.info(f" ✨ INGESTION COMPLETE")
    logger.info(f"    Final shape: {len(df):,} rows × {len(df.columns)} cols")
    logger.info(f"    Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    logger.info("=" * 72)


if __name__ == "__main__":
    main()