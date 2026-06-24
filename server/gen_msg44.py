"""CTS Platform - Message 44 (Rename Retailer → Customer everywhere in the dashboard)"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CLIENT_DIR = PROJECT_ROOT / "client"
SERVER_DIR = SCRIPT_DIR

# Files where the term appears (tier labels, tooltips, descriptions, AI prompts)
TARGET_FILES = [
    # Frontend
    CLIENT_DIR / "src/components/charts/TierFlowDiagram.jsx",
    CLIENT_DIR / "src/components/charts/StreamwiseComparison.jsx",
    CLIENT_DIR / "src/components/charts/TopTierTransitions.jsx",
    CLIENT_DIR / "src/pages/SCModelPage.jsx",
    # Backend tier label dictionaries
    SERVER_DIR / "app/api/routes/insights.py",
    SERVER_DIR / "app/api/routes/loadtype.py",
    SERVER_DIR / "ai_layer/prompts.py",
    SERVER_DIR / "ai_layer/tools/kpi_tools.py",
]

# Replacements — exact strings to swap
REPLACEMENTS = [
    # Tier label dictionary entries (backend)
    ('"RT": "Retailer"',  '"RT": "Customer"'),
    ('"Retailer"',        '"Customer"'),

    # Frontend tier descriptions
    ('desc: "Retailers"', 'desc: "End Customers"'),
    ('desc: "Retailer"',  'desc: "End Customer"'),
    ('short: "Modern trade, general trade, e-commerce"',
     'short: "End consumers — modern trade, general trade, e-commerce, B2C buyers"'),

    # Page subtitles / descriptions
    ("T2 → T1 → MF → NH → RD → LD → DT → RT",
     "T2 → T1 → MF → NH → RD → LD → DT → Customer"),
    ("supplier to retailer",
     "supplier to end customer"),
    ("supplier to Retailer",
     "supplier to Customer"),

    # AI prompt domain notes
    ("Tiers flow: T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> RT",
     "Tiers flow: T2 -> T1 -> MF -> NH -> RD -> LD -> DT -> Customer"),
    ("RT = Retailer",
     "RT = Customer"),

    # Streamwise / general references
    ("Distributors deliver to stores",
     "Distributors deliver to customers"),
    ("distributors deliver to stores",
     "distributors deliver to customers"),

    # Tooltip definitions / explanatory text
    ("DT (Distributor) → RT (Retailer)",
     "DT (Distributor) → Customer"),
    ("T2 supplier → Retailer",
     "T2 supplier → Customer"),
    ("T2 Supplier → Retailer",
     "T2 Supplier → Customer"),
]


def patch_file(path):
    if not path.exists():
        return False
    txt = path.read_text(encoding="utf-8")
    orig = txt
    for old, new in REPLACEMENTS:
        txt = txt.replace(old, new)
    if txt != orig:
        path.write_text(txt, encoding="utf-8", newline="\n")
        return True
    return False


def main():
    print()
    print("=" * 64)
    print("  CTS Platform - Message 44: Rename Retailer → Customer")
    print("=" * 64)
    print()

    patched = 0
    for path in TARGET_FILES:
        if patch_file(path):
            patched += 1
            print(f"  [+] {path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  [skip] {path.relative_to(PROJECT_ROOT)} (no changes needed)")

    print()
    print("=" * 64)
    print(f"  Patched {patched} files")
    print("=" * 64)
    print()
    print("Hard refresh browser (Ctrl + Shift + R).")
    print()
    print("Verify:")
    print("  • SC Model page → tier flow last node label: 'Customer'")
    print("  • SC Model page → hover Customer node → 'End Customers'")
    print("  • Overview page → 8-tier flow last card: shows 'Customer'")
    print("  • AI chat: ask 'show me the tier flow' → tier mention is 'Customer'")


if __name__ == "__main__":
    main()