"""Crawl every backend endpoint and save as static JSON files for Vercel-only deployment."""
import asyncio
import json
from pathlib import Path
import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "client" / "public" / "static-api"
BASE_URL = "http://localhost:8000/api/v1"

# (endpoint, params) — params dict gets encoded into the filename
ENDPOINTS = [
    # Dashboard
    ("/dashboard/kpis", {}),
    ("/dashboard/monthly-trend", {}),
    *[("/dashboard/heatmap-mom", {"metric": m}) for m in
        ["total_cost", "shipments", "otd_pct", "avg_cost_per_kg"]],

    # Cost
    ("/cost/breakdown", {}),
    ("/cost/by-tier", {}),
    ("/cost/by-mode", {}),
    ("/cost/by-category", {}),
    ("/cost/trend", {}),

    # Carrier
    ("/carrier/performance", {}),
    ("/carrier/comparison", {}),
    ("/carrier/mode-mix", {}),

    # Load Type
    ("/loadtype/summary", {}),
    ("/loadtype/ftl-ltl-summary", {}),
    ("/loadtype/by-tier", {}),
    ("/loadtype/by-carrier", {}),
    ("/loadtype/utilization-distribution", {}),

    # Consolidation
    ("/consolidation/summary", {}),
    ("/consolidation/score-distribution", {}),
    ("/consolidation/by-route", {}),
    ("/consolidation/by-carrier", {}),
    ("/consolidation/opportunity-funnel", {}),

    # PO
    ("/po/summary", {}),
    ("/po/lead-time-by-tier", {}),
    ("/po/lead-time-by-category", {}),
    ("/po/aging", {}),
    ("/po/payment-status", {}),

    # Delay
    ("/delay/summary", {}),
    ("/delay/root-causes", {}),
    ("/delay/by-carrier", {}),
    ("/delay/by-tier", {}),
    ("/delay/heatmap", {}),

    # Benchmark
    ("/benchmark/cost-per-kg", {}),
    ("/benchmark/inefficiency-flags", {}),
    ("/benchmark/cts-vs-order-value", {}),
    ("/benchmark/utilization-gap", {}),
    ("/benchmark/cost-distribution", {}),

    # Network
    ("/network/nodes", {}),
    ("/network/edges", {}),
    ("/network/state-heatmap", {}),
    ("/network/top-routes", {"limit": 30}),
    ("/network/top-routes", {"limit": 20}),
    ("/network/network-kpis", {}),
    ("/network/mode-breakdown", {}),
    ("/network/hub-strength", {}),

    # Alerts
    ("/alerts/active", {}),
    ("/alerts/top-issues", {}),
    ("/alerts/damage-returns", {}),

    # Filters
    ("/filters/options", {}),

    # Insights
    ("/insights/auto", {}),
    ("/insights/tier-flow", {}),
    ("/insights/streamwise", {}),
    *[("/insights/sparkline", {"metric": m}) for m in
        ["shipments", "total_cost", "otd_pct", "cost_per_kg",
         "utilization", "consolidation_rate", "delay_days", "co2_kg"]],

    # Products
    ("/products/kpis", {}),
    ("/products/category-mix", {}),
    *[("/products/top-skus", {"sort_by": s}) for s in
        ["total_cost", "shipments", "return_rate_pct", "damage_rate_pct"]],
    ("/products/velocity-value-matrix", {}),
    ("/products/shelf-life-distribution", {}),
    ("/products/returns-by-category", {}),

    # Trends
    ("/trends/kpis", {}),
    *[("/trends/rolling", {"window": w, "metric": m})
        for w in [7, 14, 30] for m in ["total_cost", "shipments", "otd_pct", "cost_per_kg"]],
    *[("/trends/anomalies", {"metric": m, "z_threshold": 2.5})
        for m in ["total_cost", "shipments"]],
    ("/trends/seasonality", {}),
    ("/trends/peak-seasons", {}),
]


def params_to_suffix(params):
    if not params:
        return ""
    parts = [f"{k}-{params[k]}" for k in sorted(params.keys())]
    return "__" + "_".join(parts)


def url_to_filepath(endpoint, params):
    clean = endpoint.lstrip("/")
    return f"{clean}{params_to_suffix(params)}.json"


async def fetch_one(client, endpoint, params, max_retries=3):
    """Fetch one endpoint with retry logic."""
    last_err = None
    for attempt in range(max_retries):
        try:
            resp = await client.get(BASE_URL + endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
            out_path = OUTPUT_DIR / url_to_filepath(endpoint, params)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(data, default=str), encoding="utf-8")
            param_str = f" ?{params}" if params else ""
            print(f"  [OK]   {endpoint}{param_str}")
            return True
        except httpx.HTTPStatusError as e:
            last_err = f"HTTP {e.response.status_code}"
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (attempt + 1))
        except httpx.ReadTimeout:
            last_err = "timeout"
            if attempt < max_retries - 1:
                await asyncio.sleep(1.0 * (attempt + 1))
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]}"
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)

    param_str = f" ?{params}" if params else ""
    print(f"  [FAIL] {endpoint}{param_str} -> {last_err}")
    return False


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print()
    print("=" * 64)
    print("  CTS Platform - Static API Builder (sequential + retry)")
    print("=" * 64)
    print(f"  Backend: {BASE_URL}")
    print(f"  Output:  {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    print(f"  Endpoints to crawl: {len(ENDPOINTS)}")
    print(f"  Mode: sequential (1 at a time), 3 retries per failure")
    print("=" * 64)
    print()

    ok = 0
    failed = []

    # Use a long timeout — some endpoints do heavy Pandas work
    async with httpx.AsyncClient(timeout=120.0) as client:
        for endpoint, params in ENDPOINTS:
            if await fetch_one(client, endpoint, params):
                ok += 1
            else:
                failed.append((endpoint, params))
            # Small pause between requests so backend can breathe
            await asyncio.sleep(0.05)

    print()
    print("=" * 64)
    print(f"  SAVED {ok}/{len(ENDPOINTS)} files to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    if failed:
        print(f"  FAILED ({len(failed)}):")
        for ep, params in failed[:10]:
            ps = f" ?{params}" if params else ""
            print(f"    {ep}{ps}")
        if len(failed) > 10:
            print(f"    ... and {len(failed) - 10} more")
    print("=" * 64)
    print()
    if not failed:
        print("All endpoints crawled successfully.")
        print("Next: run gen_msg46_frontend.py")
    else:
        print("Some endpoints still failed. Paste the FAIL lines above and I'll investigate.")


if __name__ == "__main__":
    asyncio.run(main())