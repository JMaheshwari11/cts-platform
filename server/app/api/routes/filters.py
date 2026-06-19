"""Filter options — populates dropdowns in the UI."""

from fastapi import APIRouter
from app.data.cache import cache

router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("/options")
def filter_options():
    """All available filter values for UI dropdowns."""
    df = cache.df

    def uniques(col):
        if col not in df.columns:
            return []
        return sorted([str(v) for v in df[col].dropna().unique()])

    return {
        "from_tiers": uniques("from_tier"),
        "to_tiers": uniques("to_tier"),
        "transport_modes": uniques("transport_mode"),
        "load_types": uniques("load_type"),
        "service_levels": uniques("service_level"),
        "streams": uniques("stream"),
        "categories": uniques("category"),
        "carriers": [
            {"id": str(row.carrier_id), "name": str(row.carrier_name)}
            for row in df[["carrier_id", "carrier_name"]].drop_duplicates().itertuples()
        ],
        "origin_states": uniques("origin_state"),
        "destination_states": uniques("destination_state"),
        "years": sorted([int(y) for y in df["year"].dropna().unique()]),
        "quarters": [1, 2, 3, 4],
        "date_range": {
            "min": str(df["ship_date"].min().date()),
            "max": str(df["ship_date"].max().date()),
        },
    }