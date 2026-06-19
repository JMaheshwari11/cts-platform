"""
========================================================================
 CTS Analytics Platform — In-Memory Data Cache
========================================================================
 Singleton cache that loads the master Parquet file into a Pandas
 DataFrame at startup. All API routes query this in-memory DF.
 
 Why in-memory:
   - 36k rows × 126 cols fits comfortably in RAM (~30MB)
   - Sub-second query times for any aggregation
   - No DB setup/maintenance overhead
========================================================================
"""

from typing import Optional
import pandas as pd
import duckdb
from loguru import logger

from app.config import settings


class DataCache:
    """Singleton holding the master DataFrame + DuckDB connection."""

    _instance: Optional["DataCache"] = None
    _df: Optional[pd.DataFrame] = None
    _duck: Optional[duckdb.DuckDBPyConnection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ─── Loading ──────────────────────────────────────────────────
    def load(self) -> None:
        """Load the master Parquet file into memory."""
        parquet_path = settings.parquet_path

        if not parquet_path.exists():
            logger.error(f"❌ Parquet file not found: {parquet_path}")
            logger.error("   Run: python scripts/ingest.py")
            raise FileNotFoundError(
                f"Parquet not found at {parquet_path}. "
                f"Run ingestion first: python scripts/ingest.py"
            )

        logger.info(f"📂 Loading Parquet: {parquet_path.name}")
        self._df = pd.read_parquet(parquet_path)
        logger.info(f"   ✅ Loaded {len(self._df):,} rows × {len(self._df.columns)} cols")
        logger.info(f"   💾 Memory: {self._df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

        # Register with DuckDB for fast SQL queries
        self._duck = duckdb.connect(":memory:")
        self._duck.register("master", self._df)
        logger.info(f"   🦆 DuckDB registered as table: 'master'")

    # ─── Accessors ────────────────────────────────────────────────
    @property
    def df(self) -> pd.DataFrame:
        """Get the master DataFrame."""
        if self._df is None:
            raise RuntimeError("DataCache not loaded. Call .load() first.")
        return self._df

    @property
    def duck(self) -> duckdb.DuckDBPyConnection:
        """Get the DuckDB connection (for complex SQL queries)."""
        if self._duck is None:
            raise RuntimeError("DataCache not loaded. Call .load() first.")
        return self._duck

    # ─── Diagnostics ──────────────────────────────────────────────
    def stats(self) -> dict:
        """Return diagnostic stats about the loaded data."""
        if self._df is None:
            return {"status": "not_loaded"}

        df = self._df
        return {
            "status": "loaded",
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
            "date_range": {
                "min": str(df["ship_date"].min().date()) if "ship_date" in df.columns else None,
                "max": str(df["ship_date"].max().date()) if "ship_date" in df.columns else None,
            },
            "uniques": {
                "products": df["product_id"].nunique() if "product_id" in df.columns else 0,
                "carriers": df["carrier_id"].nunique() if "carrier_id" in df.columns else 0,
                "origin_cities": df["origin_city"].nunique() if "origin_city" in df.columns else 0,
                "destination_cities": df["destination_city"].nunique() if "destination_city" in df.columns else 0,
                "categories": df["category"].nunique() if "category" in df.columns else 0,
            },
        }


# Singleton instance
cache = DataCache()