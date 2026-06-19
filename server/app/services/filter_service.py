"""
========================================================================
 CTS Analytics Platform — Filter Service
========================================================================
 Shared filtering logic. Every API route uses this to apply
 consistent filters (date range, tier, carrier, mode, etc.)
========================================================================
"""

from typing import Optional, List
from datetime import date
import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    from_tier: Optional[str] = None,
    to_tier: Optional[str] = None,
    carrier_id: Optional[str] = None,
    transport_mode: Optional[str] = None,
    load_type: Optional[str] = None,
    service_level: Optional[str] = None,
    stream: Optional[str] = None,
    category: Optional[str] = None,
    origin_state: Optional[str] = None,
    destination_state: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
) -> pd.DataFrame:
    """Apply a battery of optional filters to the master DataFrame."""

    result = df

    if start_date is not None and "ship_date" in result.columns:
        result = result[result["ship_date"] >= pd.Timestamp(start_date)]
    if end_date is not None and "ship_date" in result.columns:
        result = result[result["ship_date"] <= pd.Timestamp(end_date)]

    # Exact-match filters
    eq_filters = {
        "from_tier": from_tier,
        "to_tier": to_tier,
        "carrier_id": carrier_id,
        "transport_mode": transport_mode,
        "load_type": load_type,
        "service_level": service_level,
        "stream": stream,
        "category": category,
        "origin_state": origin_state,
        "destination_state": destination_state,
        "year": year,
        "quarter": quarter,
    }

    for col, val in eq_filters.items():
        if val is not None and col in result.columns:
            result = result[result[col] == val]

    return result


def round_dict(d: dict, decimals: int = 2) -> dict:
    """Round all numeric values in a dict (for clean JSON output)."""
    return {
        k: round(v, decimals) if isinstance(v, (int, float)) and not isinstance(v, bool) else v
        for k, v in d.items()
    }