"""
========================================================================
 FMCG CTS Platform — Data Cleanup Script
========================================================================
 Purpose : Cleans Master_Combined sheet in FMCG_CTS_Dataset_v3_Final.xlsx
           - Removes 8 garbage header columns
           - Removes 6 empty unnamed columns
           - Removes 11 duplicate .1 columns
           - Fixes broken consolidation_opportunity_flag (100% null)
           - Renames the working .1 version to correct name

 Input   : data/FMCG_CTS_Dataset_v3_Final.xlsx
 Output  : data/FMCG_CTS_Dataset_v4_Clean.xlsx

 Usage   : python server/scripts/clean_data.py
========================================================================
"""

import sys
from pathlib import Path
import pandas as pd

# ────────────────────────────────────────────────────────────────────────
# PATH CONFIG (resolves from script location upward to project root)
# ────────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).resolve().parent           # server/scripts
SERVER_DIR   = SCRIPT_DIR.parent                          # server
PROJECT_ROOT = SERVER_DIR.parent                          # CTS_Platform
DATA_DIR     = PROJECT_ROOT / "data"

INPUT_FILE   = DATA_DIR / "FMCG_CTS_Dataset_v3_Final.xlsx"
OUTPUT_FILE  = DATA_DIR / "FMCG_CTS_Dataset_v4_Clean.xlsx"

# ────────────────────────────────────────────────────────────────────────
# COLUMN CLEANUP DEFINITIONS
# ────────────────────────────────────────────────────────────────────────
GARBAGE_HEADER_COLS = [
    "Avg Batch",
    "Consolidation Statistics",
    "Unnamed: 115",
    "Unnamed: 116",
    "Unnamed: 117",
    13360,
    22640,
    "13360.1",
]

EMPTY_UNNAMED_COLS = [
    "Unnamed: 133",
    "Unnamed: 134",
    "Unnamed: 135",
    "Unnamed: 136",
    "Unnamed: 137",
    "Unnamed: 139",
]

DUPLICATE_DOT1_COLS = [
    "consolidation_batch_size.1",
    "group_total_weight.1",
    "avg_utilization_group.1",
    "delay_risk_flag.1",
    "carrier_underperformance_flag.1",
    "target_utilization_pct.1",
    "utilization_gap.1",
    "distance_bucket.1",
    "primary_issue.1",
    "group_key.1",
    "target_otdr.1",
]

RENAME_MAP = {
    "consolidation_opportunity_flag.1": "consolidation_opportunity_flag",
}

# ────────────────────────────────────────────────────────────────────────
# MAIN CLEANUP FUNCTION
# ────────────────────────────────────────────────────────────────────────
def clean_master_combined() -> None:
    print("=" * 72)
    print(" FMCG CTS — Master_Combined Cleanup")
    print("=" * 72)

    # Validate input
    if not INPUT_FILE.exists():
        print(f"❌ ERROR: Input file not found:\n   {INPUT_FILE}")
        sys.exit(1)

    print(f"\n📂 Reading: {INPUT_FILE.name}")
    xls = pd.ExcelFile(INPUT_FILE, engine="openpyxl")
    sheets = {name: pd.read_excel(xls, sheet_name=name) for name in xls.sheet_names}
    print(f"   Found {len(sheets)} sheets: {list(sheets.keys())}")

    master = sheets["Master_Combined"]
    initial_shape = master.shape
    print(f"\n📊 BEFORE: {initial_shape[0]:,} rows × {initial_shape[1]} cols")

    # Step 1: Drop the broken 100%-null consolidation_opportunity_flag by POSITION
    bad_idx = None
    for i, col in enumerate(master.columns):
        if col == "consolidation_opportunity_flag" and master.iloc[:, i].isna().all():
            bad_idx = i
            break
    if bad_idx is not None:
        master = master.drop(master.columns[bad_idx], axis=1)
        print(f"   ✅ Dropped broken 'consolidation_opportunity_flag' at idx {bad_idx}")

    # Step 2-4: Drop garbage / empty / duplicate columns
    for label, cols in [
        ("garbage header cols", GARBAGE_HEADER_COLS),
        ("empty unnamed cols", EMPTY_UNNAMED_COLS),
        ("duplicate .1 cols", DUPLICATE_DOT1_COLS),
    ]:
        dropped = [c for c in cols if c in master.columns]
        master = master.drop(columns=dropped, errors="ignore")
        print(f"   ✅ Dropped {len(dropped)} {label}")

    # Step 5: Rename working .1 columns
    master = master.rename(columns=RENAME_MAP)
    if RENAME_MAP:
        print(f"   ✅ Renamed: {RENAME_MAP}")

    # Step 6: Safety net — drop any remaining Unnamed cols
    unnamed_left = [c for c in master.columns if str(c).startswith("Unnamed")]
    if unnamed_left:
        master = master.drop(columns=unnamed_left)
        print(f"   ✅ Safety-net dropped: {unnamed_left}")

    final_shape = master.shape
    print(f"\n📊 AFTER:  {final_shape[0]:,} rows × {final_shape[1]} cols")
    print(f"   🎯 Removed {initial_shape[1] - final_shape[1]} problem columns")

    # ─── Sanity checks ───
    print(f"\n🔍 SANITY CHECKS")
    checks = {
        "consolidation_opportunity_flag exists": "consolidation_opportunity_flag" in master.columns,
        "No 'Unnamed' columns left": not any(str(c).startswith("Unnamed") for c in master.columns),
        "No '.1' duplicate columns": not any(str(c).endswith(".1") for c in master.columns),
        "Row count unchanged (36,000)": len(master) == 36000,
    }
    for desc, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"   {icon} {desc}")

    if "consolidation_opportunity_flag" in master.columns:
        vc = master["consolidation_opportunity_flag"].value_counts().to_dict()
        print(f"      → values: {vc}")

    # ─── Save cleaned file ───
    sheets["Master_Combined"] = master
    print(f"\n💾 Writing: {OUTPUT_FILE.name}")
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    print(f"   ✅ Saved to: {OUTPUT_FILE}")

    print("\n" + "=" * 72)
    print(" ✨ CLEANUP COMPLETE — Ready for ingestion")
    print("=" * 72)


if __name__ == "__main__":
    clean_master_combined()