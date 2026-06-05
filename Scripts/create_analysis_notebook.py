# -*- coding: utf-8 -*-
"""Create the interactive Olist Operations Analytics notebook."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


BASE_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = BASE_DIR / "Notebook"
NOTEBOOK_PATH = NOTEBOOK_DIR / "olist_operations_analytics.ipynb"


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def markdown(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }

    nb.cells = [
        markdown(
            """
# Olist Brazilian E-Commerce Operations Analytics

This notebook uses both SQL and Python:

- SQL handles relational joins, order-level aggregation, KPI views, category views, and logistics views.
- Python handles data loading, interactive exploration, visualization, optimization screening, and Monte Carlo simulation.

Run this notebook from the `Brazilian Ecommerce/Notebook` folder or keep the default path logic below.
"""
        ),
        code(
            """
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path.cwd()
if BASE_DIR.name == "Notebook":
    BASE_DIR = BASE_DIR.parent
elif not (BASE_DIR / "olist_orders_dataset.csv").exists():
    BASE_DIR = Path("Brazilian Ecommerce").resolve()

SQL_PATH = BASE_DIR / "SQL" / "01_olist_core_analysis.sql"
OUTPUT_DIR = BASE_DIR / "Outputs"
CHART_DIR = OUTPUT_DIR / "charts"
TABLE_DIR = OUTPUT_DIR / "tables"

for path in [CHART_DIR, TABLE_DIR]:
    path.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
N_RUNS = 1000

BASE_DIR
"""
        ),
        markdown(
            """
## 1. Load CSV tables

The raw Olist data is relational. We load each CSV into pandas first, then register it in an in-memory SQLite database for SQL analysis.
"""
        ),
        code(
            """
parse_orders = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

orders = pd.read_csv(BASE_DIR / "olist_orders_dataset.csv", parse_dates=parse_orders)
items = pd.read_csv(BASE_DIR / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
payments = pd.read_csv(BASE_DIR / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(
    BASE_DIR / "olist_order_reviews_dataset.csv",
    parse_dates=["review_creation_date", "review_answer_timestamp"],
)
customers = pd.read_csv(BASE_DIR / "olist_customers_dataset.csv")
sellers = pd.read_csv(BASE_DIR / "olist_sellers_dataset.csv")
products = pd.read_csv(BASE_DIR / "olist_products_dataset.csv")
translation = pd.read_csv(BASE_DIR / "product_category_name_translation.csv")

raw_summary = pd.DataFrame({
    "table": ["orders", "items", "payments", "reviews", "customers", "sellers", "products", "translation"],
    "rows": [len(orders), len(items), len(payments), len(reviews), len(customers), len(sellers), len(products), len(translation)],
    "columns": [orders.shape[1], items.shape[1], payments.shape[1], reviews.shape[1], customers.shape[1], sellers.shape[1], products.shape[1], translation.shape[1]],
})
raw_summary
"""
        ),
        markdown(
            """
## 2. Register data in SQLite and run SQL model

The SQL file creates:

- `df_master`: order-level master table view
- `item_detail`: item-level analytical view
- `yearly_kpis`, `monthly_kpis`
- `category_performance`
- `customer_state_logistics`
- `seller_performance`
"""
        ),
        code(
            """
conn = sqlite3.connect(":memory:")

table_map = {
    "orders": orders,
    "items": items,
    "payments": payments,
    "reviews": reviews,
    "customers": customers,
    "sellers": sellers,
    "products": products,
    "translation": translation,
}

for table_name, df in table_map.items():
    df.to_sql(table_name, conn, index=False, if_exists="replace")

sql_text = SQL_PATH.read_text(encoding="utf-8")
conn.executescript(sql_text)

pd.read_sql_query("SELECT name, type FROM sqlite_master WHERE type = 'view' ORDER BY name", conn)
"""
        ),
        markdown(
            """
## 3. Business health KPIs

Use `payment_value` for realized revenue and `price + freight_value` for item-level GMV diagnostics.
"""
        ),
        code(
            """
yearly_kpis = pd.read_sql_query("SELECT * FROM yearly_kpis ORDER BY year", conn)
monthly_kpis = pd.read_sql_query("SELECT * FROM monthly_kpis ORDER BY purchase_month", conn)

yearly_kpis["payment_revenue_yoy"] = yearly_kpis["payment_revenue"].pct_change()
yearly_kpis["delivered_orders_yoy"] = yearly_kpis["delivered_orders"].pct_change()
yearly_kpis["aov_payment_yoy"] = yearly_kpis["aov_payment"].pct_change()

yearly_kpis
"""
        ),
        code(
            """
monthly_kpis.head(), monthly_kpis.tail()
"""
        ),
        code(
            """
monthly_plot = monthly_kpis.copy()
monthly_plot["purchase_month_dt"] = pd.to_datetime(monthly_plot["purchase_month"])

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_plot["purchase_month_dt"], monthly_plot["payment_revenue"], marker="o")
ax.set_title("Monthly payment revenue - delivered orders")
ax.set_xlabel("Month")
ax.set_ylabel("Payment revenue (BRL)")
ax.ticklabel_format(axis="y", style="plain")
fig.autofmt_xdate()
plt.show()
"""
        ),
        markdown(
            """
## 4. Category analysis and optimization screen

This is not a full solver yet. It is the first optimization screen from `GEMINI.md`: keep categories with review score >= 3.5 and average freight <= BRL 25, then rank by `revenue x review_score`.
"""
        ),
        code(
            """
category = pd.read_sql_query(
    "SELECT * FROM category_performance ORDER BY item_price_revenue DESC",
    conn,
)
category["revenue_share"] = category["item_price_revenue"] / category["item_price_revenue"].sum()
category["cumulative_revenue_share"] = category["revenue_share"].cumsum()

category.head(10)
"""
        ),
        code(
            """
category_optimization_top10 = (
    category[
        (category["avg_review_score"] >= 3.5)
        & (category["avg_freight_per_item"] <= 25)
    ]
    .sort_values("weighted_objective", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
category_optimization_top10.insert(0, "selected_rank", np.arange(1, len(category_optimization_top10) + 1))
category_optimization_top10
"""
        ),
        code(
            """
top_cat = category.head(10).sort_values("item_price_revenue")

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top_cat["product_category_name_english"], top_cat["item_price_revenue"])
ax.set_title("Top 10 categories by item price revenue")
ax.set_xlabel("Item price revenue (BRL)")
ax.ticklabel_format(axis="x", style="plain")
plt.show()
"""
        ),
        markdown(
            """
## 5. Logistics analysis
"""
        ),
        code(
            """
customer_state_logistics = pd.read_sql_query(
    "SELECT * FROM customer_state_logistics ORDER BY late_rate DESC, orders DESC",
    conn,
)
seller_performance = pd.read_sql_query(
    "SELECT * FROM seller_performance ORDER BY item_price_revenue DESC",
    conn,
)

customer_state_logistics.head(10)
"""
        ),
        code(
            """
top_state = customer_state_logistics.head(10).sort_values("late_rate")

fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(top_state["customer_state"], top_state["late_rate"])
ax.set_title("Top 10 customer states by late delivery rate")
ax.set_xlabel("Late delivery rate")
ax.xaxis.set_major_formatter(lambda x, pos: f"{x:.0%}")
plt.show()
"""
        ),
        markdown(
            """
## 6. Monte Carlo simulation

Simulation is done in Python because it is more natural for random sampling and risk metrics.
"""
        ),
        code(
            """
item_detail = pd.read_sql_query("SELECT * FROM item_detail WHERE delivered_flag = 1", conn)
top_categories = (
    item_detail.groupby("product_category_name_english")["price"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

monthly_cat = (
    item_detail[item_detail["product_category_name_english"].isin(top_categories)]
    .groupby(["purchase_month", "product_category_name_english"], as_index=False)["price"]
    .sum()
)

revenue_stats = (
    monthly_cat.groupby("product_category_name_english", as_index=False)
    .agg(mu_monthly_revenue=("price", "mean"), sigma_monthly_revenue=("price", "std"))
    .fillna({"sigma_monthly_revenue": 0})
)

rng = np.random.default_rng(RANDOM_SEED)
draws = [
    np.clip(rng.normal(row.mu_monthly_revenue, row.sigma_monthly_revenue, N_RUNS), 0, None)
    for row in revenue_stats.itertuples(index=False)
]
total_revenue = np.vstack(draws).sum(axis=0)

revenue_simulation_summary = pd.DataFrame({
    "scenario": ["top_5_category_monthly_revenue"],
    "n_runs": [N_RUNS],
    "expected_revenue": [total_revenue.mean()],
    "stddev_revenue": [total_revenue.std(ddof=1)],
    "p_revenue_below_80pct_mean": [(total_revenue < 0.8 * total_revenue.mean()).mean()],
    "percentile_5": [np.percentile(total_revenue, 5)],
    "percentile_95": [np.percentile(total_revenue, 95)],
})

revenue_simulation_summary
"""
        ),
        code(
            """
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(total_revenue, bins=35, color="#2F6B5F", alpha=0.85)
ax.set_title("Monte Carlo simulation - top 5 category monthly revenue")
ax.set_xlabel("Total monthly revenue (BRL)")
ax.set_ylabel("Runs")
ax.ticklabel_format(axis="x", style="plain")
plt.show()
"""
        ),
        markdown(
            """
## 7. Export key notebook tables
"""
        ),
        code(
            """
exports = {
    "notebook_yearly_kpis.csv": yearly_kpis,
    "notebook_monthly_kpis.csv": monthly_kpis,
    "notebook_category_optimization_top10.csv": category_optimization_top10,
    "notebook_customer_state_logistics.csv": customer_state_logistics,
    "notebook_revenue_simulation_summary.csv": revenue_simulation_summary,
}

for filename, df in exports.items():
    df.to_csv(TABLE_DIR / filename, index=False, encoding="utf-8-sig")

sorted(exports)
"""
        ),
    ]

    return nb


def main() -> None:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    nbf.write(nb, NOTEBOOK_PATH)
    print(NOTEBOOK_PATH)


if __name__ == "__main__":
    main()
