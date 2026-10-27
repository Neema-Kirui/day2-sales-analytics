"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is used only in task 8, to check the work.
"""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "electronics_sales.csv"
REPORT_PATH = BASE_DIR / "output" / "sales_report.txt"
THRESHOLD = 50_000


# ---------------------------------------------------------------- Task 1
def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            columns = reader.fieldnames
    except FileNotFoundError:
        print(f"File not found: {path}")
        return []
    print(f"Rows read: {len(rows)}")
    print(f"Columns  : {columns}")
    return rows


# ---------------------------------------------------------------- Task 2
def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted.

    Repaired (the meaning is certain):
      - surrounding spaces            " 5999 "      -> 5999.0
      - a 'KES' prefix                "KES 18999"   -> 18999.0
      - thousands separators          "38,999"      -> 38999.0
    Rejected (guessing would put invented numbers in the finance report):
      - blank values, 'N/A', words such as 'two', and any other text
      - zero or negative numbers (a sale needs a positive quantity and price)
    """
    if value is None:
        return None
    text = value.strip()
    if text.upper().startswith("KES"):
        text = text[3:].strip()
    text = text.replace(",", "")
    if text == "":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number != number or number <= 0:  # NaN or non-positive
        return None
    return number


def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean, skipped = [], []
    for row in rows:
        quantity = parse_number(row["quantity"])
        price = parse_number(row["unit_price_kes"])
        if quantity is None:
            skipped.append({"sale_id": row["sale_id"],
                            "reason": f"invalid quantity {row['quantity']!r}"})
        elif price is None:
            skipped.append({"sale_id": row["sale_id"],
                            "reason": f"invalid unit price {row['unit_price_kes']!r}"})
        elif quantity != int(quantity):
            skipped.append({"sale_id": row["sale_id"],
                            "reason": f"non-whole quantity {row['quantity']!r}"})
        else:
            new_row = dict(row)
            new_row["quantity"] = int(quantity)
            new_row["unit_price_kes"] = price
            new_row["revenue"] = int(quantity) * price
            clean.append(new_row)
    return clean, skipped


# ---------------------------------------------------------------- Task 3
def total_revenue(rows: list[dict]) -> float:
    total = 0.0
    for row in rows:
        total += row["quantity"] * row["unit_price_kes"]
    return total


# ---------------------------------------------------------------- Task 4
def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals = {}
    for row in rows:
        key = row[field]
        if key not in totals:
            totals[key] = 0.0
        totals[key] += row["revenue"]
    return totals


# ---------------------------------------------------------------- Task 5
def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first. Ties: alphabetical by key."""
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


# ---------------------------------------------------------------- Task 6
def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold (use a comprehension)."""
    return [row for row in rows if row["revenue"] >= threshold]


# ---------------------------------------------------------------- Task 7
def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("mean() needs at least one value, got an empty list")
    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("median() needs at least one value, got an empty list")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("minimum_maximum() needs at least one value, got an empty list")
    low = high = values[0]
    for v in values[1:]:
        if v < low:
            low = v
        if v > high:
            high = v
    return low, high


# ---------------------------------------------------------------- Task 8
def verify_with_pandas(path: Path, my_results: dict) -> list[str]:
    """Recompute the headline numbers with pandas and report whether each one matches."""
    try:
        import pandas as pd
    except (ImportError, OSError) as e:
        return [f"pandas is not available here, verification skipped ({e})"]

    df = pd.read_csv(path, dtype=str)
    for col in ("quantity", "unit_price_kes"):
        cleaned = (df[col].str.strip()
                   .str.replace(r"(?i)^KES", "", regex=True)
                   .str.replace(",", "", regex=False)
                   .str.strip())
        df[col] = pd.to_numeric(cleaned, errors="coerce")
    df = df[(df["quantity"] > 0) & (df["unit_price_kes"] > 0)].copy()
    df["revenue"] = df["quantity"] * df["unit_price_kes"]

    def close(a, b):
        return abs(a - b) < 0.005

    lines = []
    pd_total = df["revenue"].sum()
    ok = close(pd_total, my_results["total"])
    lines.append("Total revenue      : " + ("MATCH" if ok else
                 f"MISMATCH (pure={my_results['total']:.2f}, pandas={pd_total:.2f})"))

    pd_prod = df.groupby("product")["revenue"].sum().to_dict()
    mine = my_results["by_product"]
    ok = pd_prod.keys() == mine.keys() and all(close(pd_prod[k], mine[k]) for k in mine)
    lines.append("Revenue by product : " + ("MATCH" if ok else "MISMATCH (see values)"))

    pd_top = (df.groupby("product")["revenue"].sum().reset_index()
              .sort_values(["revenue", "product"], ascending=[False, True]).head(3))
    pd_top = list(zip(pd_top["product"], pd_top["revenue"]))
    ok = [p for p, _ in pd_top] == [p for p, _ in my_results["top3"]]
    lines.append("Top 3              : " + ("MATCH" if ok else
                 f"MISMATCH (pure={my_results['top3']}, pandas={pd_top})"))

    ok = close(df["revenue"].mean(), my_results["mean"]) and close(df["revenue"].median(), my_results["median"])
    lines.append("Mean / median      : " + ("MATCH" if ok else
                 f"MISMATCH (pure={my_results['mean']:.2f}/{my_results['median']:.2f}, "
                 f"pandas={df['revenue'].mean():.2f}/{df['revenue'].median():.2f})"))
    return lines


# ---------------------------------------------------------------- Report
def build_report(raw, clean, skipped):
    by_product = revenue_by(clean, "product")
    by_store = revenue_by(clean, "store")
    by_payment = revenue_by(clean, "payment_method")
    big = high_value(clean, THRESHOLD)
    big_per_store = {s: len([r for r in big if r["store"] == s]) for s in by_store}
    revenues = [r["revenue"] for r in clean]
    low, high = minimum_maximum(revenues)
    results = {"total": total_revenue(clean), "by_product": by_product,
               "top3": top_n(by_product, 3), "mean": mean(revenues), "median": median(revenues)}

    skipped_text = ", ".join(f"{s['sale_id']}: {s['reason']}" for s in skipped)
    out = ["=== Sales report: September 2026 ===",
           f"Rows read          : {len(raw)}",
           f"Rows used          : {len(clean)}",
           f"Rows skipped       : {len(skipped)}   ({skipped_text})",
           "",
           f"Total revenue (KES): {results['total']:,.2f}",
           "", "Revenue by product (KES)"]
    for p, v in sorted(by_product.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"  {p:<24}{v:>14,.2f}")
    out += ["", "Revenue by store (KES)"]
    for s, v in sorted(by_store.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"  {s:<24}{v:>14,.2f}")
    out += ["", "Revenue by payment method (KES)"]
    for s, v in sorted(by_payment.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"  {s:<24}{v:>14,.2f}")
    out += ["", "Top 3 products"]
    for i, (p, v) in enumerate(results["top3"], 1):
        out.append(f"  {i}. {p} - KES {v:,.2f}")
    out += ["", f"High-value transactions (>= KES {THRESHOLD:,.0f}): {len(big)}"]
    for r in big:
        out.append(f"  {r['sale_id']}  {r['sale_date']}  {r['store']}  {r['product']}  KES {r['revenue']:,.2f}")
    out += ["", "High-value sales per store"]
    for s, n in sorted(big_per_store.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"  {s:<24}{n:>3}")
    out += ["", "Transaction revenue statistics",
            f"  mean   : {results['mean']:,.2f}",
            f"  median : {results['median']:,.2f}",
            f"  min    : {low:,.2f}",
            f"  max    : {high:,.2f}",
            "", "=== pandas verification ==="]
    out += verify_with_pandas(DATA_PATH, results)
    return out


if __name__ == "__main__":
    raw_rows = read_sales(DATA_PATH)
    if not raw_rows:
        raise SystemExit("No data to analyse, stopping.")
    clean_rows, skipped_rows = convert_rows(raw_rows)
    print()
    report = build_report(raw_rows, clean_rows, skipped_rows)
    print("\n".join(report))
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"\nReport saved to {REPORT_PATH}")
    
