# Sales Analytics Without Pandas: Tech Hub Kenya, September 2026

## Overview
Tech Hub Kenya wants September's revenue, its best-selling products and the sales big enough for a follow-up call. The reporting server has no third-party packages, so Tasks 1-7 use only the Python standard library (`csv`, dictionaries, tuples, comprehensions and my own functions). pandas is used only in Task 8, to check my numbers.

## Project structure
```
day2-sales-analytics/
├── sales_analysis.py
├── data/electronics_sales.csv
├── output/sales_report.txt
├── requirements.txt          # pandas only (for verification)
└── README.md
```

## How to run
1. Open a terminal in the `day2-sales-analytics` folder.
2. Run:
   ```
   python sales_analysis.py
   ```
3. The report is printed and saved to `output/sales_report.txt`.

Tasks 1-7 need no installation. For the pandas check, install it with `python -m pip install -r requirements.txt`. If pandas is not available, the script does not crash: it prints that verification was skipped and still produces the rest of the report. (My laptop blocks pandas through a security policy, so the verification block in the saved report was generated in an environment where pandas is available.)

## Approach
- **Task 1:** `read_sales` uses `csv.DictReader`, prints the row count and column names, and handles a missing file with a clear message.
- **Task 2:** `parse_number` cleans one value, and `convert_rows` returns `(clean_rows, skipped_rows)`. Each skipped row records its sale ID and a reason.
- **Task 3:** `total_revenue` sums quantity x unit price. The total is shown in KES to 2 decimal places with thousands separators.
- **Task 4:** `revenue_by` uses a plain dict (no `defaultdict` or `Counter`) and is used for product, store and payment method.
- **Task 5:** `top_n` uses `sorted()` with a key function and returns `(product, revenue)` tuples.
- **Task 6:** `high_value` is a list comprehension (threshold KES 50,000, inclusive). Sales per store above the threshold are counted with a dict comprehension.
- **Task 7:** `mean`, `median` and `minimum_maximum` are written by hand. `minimum_maximum` uses a loop, not `min()`/`max()`. Each raises a clear `ValueError` for an empty list.
- **Task 8:** `verify_with_pandas` re-reads the file with pandas, applies the same cleaning rules with its own code, and compares total, revenue by product, top 3, and mean/median.

## Cleaning rules (Task 2)
A value is **repaired** only when its meaning is certain, and **skipped** when fixing it would mean guessing.

| Rule | Example | Decision | Why |
|---|---|---|---|
| Thousands separator | `"38,999"` (S-3017) | Repaired to 38999 | The comma is formatting, and the intended number is clear. |
| `KES` prefix | `KES 18999` (S-3029) | Repaired to 18999 | The currency label is redundant, since the column is already in KES. |
| Surrounding spaces | `" 5999 "` | Repaired | Whitespace carries no meaning. |
| Blank quantity | S-3035 | Skipped | The real quantity is unknown, and guessing 1 could be wrong by a lot. |
| Blank price | S-3039 | Skipped | The price is unknown, so the revenue cannot be calculated. |
| `N/A` price | S-3030 | Skipped | An explicit statement that the value is missing. |
| Quantity written as a word, `two` | S-3006 | Skipped | It is probably 2, but converting words to numbers is guesswork, and a finance report should not contain invented values. |
| Zero or negative numbers | none in this file | Skipped | A sale needs a positive quantity and price. |
| Non-whole quantity | none in this file | Skipped | You cannot sell 1.5 phones. |

Skipped rows are listed with their reason in the report. Rows skipped: 4 (S-3006, S-3030, S-3035, S-3039). Rows repaired: 2 (S-3017, S-3029).

## Tie-breaking (Task 5)
Products with equal revenue are ranked alphabetically by name, using the sort key `(-revenue, name)`. This keeps results the same every time. There are no ties in the top 3 for this data.

## Findings
- **Rows:** 50 read, 46 used, 4 skipped.
- **Total revenue:** KES 1,310,812.00.
- **Top 3 products:** HP 15 Laptop (KES 389,994.00), Hisense 43in Smart TV (KES 272,993.00) and Lenovo Tab M10 (KES 199,992.00). Together they bring in about two thirds of all revenue.
- **High-value sales:** 5 sales are at or above KES 50,000. Kisumu Mega Plaza has the most (2), and Mombasa City Mall has none.
- **Average vs typical sale:** the mean transaction is KES 28,495.91, but the median is only KES 11,097.00. A few large laptop and TV sales pull the mean up, so the median describes a typical sale better.

## pandas verification (Task 8)
All four checks (total, revenue by product, top 3, mean/median) show MATCH. pandas applies the same rules: it strips `KES` and commas, converts to numbers, and drops rows where quantity or price is missing or not numeric. There were no mismatches to explain.

## Assumptions
- Revenue is quantity x unit price, with no discounts or taxes.
- The high-value threshold of KES 50,000 is inclusive (at or above).
- Every row is a separate sale, and there are no duplicate sale IDs.
- Skipped rows are excluded from every total, so reported revenue is slightly lower than the true figure. The dataset cannot tell us what those 4 sales were worth.
