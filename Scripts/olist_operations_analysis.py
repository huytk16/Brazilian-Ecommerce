# -*- coding: utf-8 -*-
"""End-to-end Operations Analytics pipeline for the Olist dataset.

Run from the project root:
    python "Brazilian Ecommerce/Scripts/olist_operations_analysis.py"
"""

from __future__ import annotations

import sqlite3
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
CHART_DIR = BASE_DIR / "Outputs" / "charts"
TABLE_DIR = BASE_DIR / "Outputs" / "tables"
REPORT_DIR = BASE_DIR / "Outputs" / "reports"

RANDOM_SEED = 42
N_RUNS = 1_000


def pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.1%}"


def money(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"BRL {value:,.0f}"


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a compact Markdown table without optional pandas dependencies."""
    text_df = df.astype(object).where(pd.notna(df), "")
    headers = [str(col) for col in text_df.columns]
    rows = [[str(value) for value in row] for row in text_df.to_numpy()]
    widths = [
        max(len(headers[idx]), *(len(row[idx]) for row in rows)) if rows else len(headers[idx])
        for idx in range(len(headers))
    ]
    header_line = "| " + " | ".join(headers[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
    sep_line = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    body = [
        "| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
        for row in rows
    ]
    return "\n".join([header_line, sep_line, *body])


def dataframe_to_html(df: pd.DataFrame, classes: str = "data-table") -> str:
    text_df = df.astype(object).where(pd.notna(df), "")
    header = "".join(f"<th>{escape(str(col))}</th>" for col in text_df.columns)
    rows = []
    for _, row in text_df.iterrows():
        cells = "".join(f"<td>{escape(str(value))}</td>" for value in row)
        rows.append(f"<tr>{cells}</tr>")
    return f'<table class="{classes}"><thead><tr>{header}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def save_table(df: pd.DataFrame, filename: str) -> Path:
    path = TABLE_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def load_data() -> dict[str, pd.DataFrame]:
    parse_orders = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    return {
        "orders": pd.read_csv(BASE_DIR / "olist_orders_dataset.csv", parse_dates=parse_orders),
        "items": pd.read_csv(BASE_DIR / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"]),
        "payments": pd.read_csv(BASE_DIR / "olist_order_payments_dataset.csv"),
        "reviews": pd.read_csv(
            BASE_DIR / "olist_order_reviews_dataset.csv",
            parse_dates=["review_creation_date", "review_answer_timestamp"],
        ),
        "customers": pd.read_csv(BASE_DIR / "olist_customers_dataset.csv"),
        "sellers": pd.read_csv(BASE_DIR / "olist_sellers_dataset.csv"),
        "products": pd.read_csv(BASE_DIR / "olist_products_dataset.csv"),
        "translation": pd.read_csv(BASE_DIR / "product_category_name_translation.csv"),
    }


def mode_or_join(values: pd.Series) -> str:
    clean = values.dropna().astype(str)
    if clean.empty:
        return "unknown"
    counts = clean.value_counts()
    if len(counts) == 1:
        return counts.index[0]
    return "+".join(counts.index[:3])


def build_master(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders = data["orders"].copy()
    items = data["items"].copy()
    payments = data["payments"].copy()
    reviews = data["reviews"].copy()
    products = data["products"].merge(
        data["translation"], on="product_category_name", how="left"
    )
    products["product_category_name_english"] = products[
        "product_category_name_english"
    ].fillna("unknown")

    item_order = (
        items.groupby("order_id", as_index=False)
        .agg(
            item_count=("order_item_id", "count"),
            product_count=("product_id", "nunique"),
            seller_count=("seller_id", "nunique"),
            item_price=("price", "sum"),
            freight_value=("freight_value", "sum"),
        )
        .assign(item_gmv=lambda df: df["item_price"] + df["freight_value"])
    )

    payment_order = (
        payments.groupby("order_id", as_index=False)
        .agg(
            payment_value=("payment_value", "sum"),
            payment_count=("payment_sequential", "count"),
            max_installments=("payment_installments", "max"),
            payment_type=("payment_type", mode_or_join),
        )
    )

    review_order = (
        reviews.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            review_count=("review_id", "nunique"),
        )
    )

    master = (
        orders.merge(data["customers"], on="customer_id", how="left")
        .merge(item_order, on="order_id", how="left")
        .merge(payment_order, on="order_id", how="left")
        .merge(review_order, on="order_id", how="left")
    )

    for col in ["item_count", "product_count", "seller_count", "payment_count"]:
        master[col] = master[col].fillna(0)

    for col in ["item_price", "freight_value", "item_gmv", "payment_value"]:
        master[col] = master[col].fillna(0.0)

    master["purchase_month"] = master["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    master["purchase_year"] = master["order_purchase_timestamp"].dt.year
    master["delivered_flag"] = master["order_status"].eq("delivered")
    master["delivery_days"] = (
        master["order_delivered_customer_date"] - master["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    late_condition = (
        master["order_delivered_customer_date"] > master["order_estimated_delivery_date"]
    )
    master["late_flag"] = np.where(master["delivered_flag"], late_condition.astype(float), np.nan)
    master.loc[~master["delivered_flag"], "delivery_days"] = np.nan
    master["on_time_flag"] = np.where(master["delivered_flag"], 1 - master["late_flag"], np.nan)

    item_detail = (
        items.merge(orders[["order_id", "customer_id", "order_status", "order_purchase_timestamp",
                            "order_delivered_customer_date", "order_estimated_delivery_date"]],
                    on="order_id", how="left")
        .merge(data["customers"][["customer_id", "customer_state"]], on="customer_id", how="left")
        .merge(data["sellers"], on="seller_id", how="left")
        .merge(products[["product_id", "product_category_name_english"]], on="product_id", how="left")
        .merge(review_order, on="order_id", how="left")
    )
    item_detail["product_category_name_english"] = item_detail[
        "product_category_name_english"
    ].fillna("unknown")
    item_detail["purchase_month"] = item_detail["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
    item_detail["delivered_flag"] = item_detail["order_status"].eq("delivered")
    item_late_condition = (
        item_detail["order_delivered_customer_date"] > item_detail["order_estimated_delivery_date"]
    )
    item_detail["late_flag"] = np.where(
        item_detail["delivered_flag"], item_late_condition.astype(float), np.nan
    )

    return master, item_detail


def run_sql_summaries(master: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    delivered = master[master["delivered_flag"]].copy()
    delivered["purchase_month"] = delivered["purchase_month"].dt.strftime("%Y-%m")
    conn = sqlite3.connect(":memory:")
    delivered.to_sql("orders_delivered", conn, index=False, if_exists="replace")

    yearly = pd.read_sql_query(
        """
        SELECT
            purchase_year AS year,
            COUNT(DISTINCT order_id) AS delivered_orders,
            SUM(payment_value) AS payment_revenue,
            SUM(item_price) AS item_price_revenue,
            SUM(freight_value) AS freight_revenue,
            SUM(payment_value) / COUNT(DISTINCT order_id) AS aov_payment,
            AVG(CASE WHEN late_flag = 0 THEN 1.0 ELSE 0.0 END) AS on_time_rate,
            AVG(review_score) AS avg_review_score,
            AVG(delivery_days) AS avg_delivery_days
        FROM orders_delivered
        WHERE purchase_year IN (2017, 2018)
        GROUP BY purchase_year
        ORDER BY purchase_year
        """,
        conn,
    )
    for col in ["payment_revenue", "delivered_orders", "aov_payment"]:
        yearly[f"{col}_yoy"] = yearly[col].pct_change()

    monthly = pd.read_sql_query(
        """
        SELECT
            purchase_month,
            COUNT(DISTINCT order_id) AS delivered_orders,
            SUM(payment_value) AS payment_revenue,
            SUM(item_price) AS item_price_revenue,
            AVG(CASE WHEN late_flag = 1 THEN 1.0 ELSE 0.0 END) AS late_rate,
            AVG(review_score) AS avg_review_score
        FROM orders_delivered
        GROUP BY purchase_month
        ORDER BY purchase_month
        """,
        conn,
    )
    conn.close()
    return yearly, monthly


def analyze_categories(item_detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    delivered_items = item_detail[item_detail["delivered_flag"]].copy()
    category = (
        delivered_items.groupby("product_category_name_english", as_index=False)
        .agg(
            item_price_revenue=("price", "sum"),
            freight_value=("freight_value", "sum"),
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            avg_review_score=("review_score", "mean"),
            late_rate=("late_flag", "mean"),
            avg_freight_per_item=("freight_value", "mean"),
        )
        .assign(
            aov_item_price=lambda df: df["item_price_revenue"] / df["orders"],
            weighted_objective=lambda df: df["item_price_revenue"] * df["avg_review_score"].fillna(0),
        )
        .sort_values("item_price_revenue", ascending=False)
    )
    category["revenue_share"] = category["item_price_revenue"] / category["item_price_revenue"].sum()
    category["cumulative_revenue_share"] = category["revenue_share"].cumsum()

    optimized = (
        category[
            (category["avg_review_score"] >= 3.5)
            & (category["avg_freight_per_item"] <= 25)
        ]
        .sort_values("weighted_objective", ascending=False)
        .head(10)
        .copy()
    )
    optimized.insert(0, "selected_rank", range(1, len(optimized) + 1))
    return category, optimized


def analyze_logistics(master: pd.DataFrame, item_detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    delivered = master[master["delivered_flag"]].copy()
    state = (
        delivered.groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            payment_revenue=("payment_value", "sum"),
            avg_delivery_days=("delivery_days", "mean"),
            late_rate=("late_flag", "mean"),
            avg_freight=("freight_value", "mean"),
            avg_review_score=("review_score", "mean"),
        )
        .query("orders >= 30")
        .sort_values(["late_rate", "orders"], ascending=[False, False])
    )

    delivered_items = item_detail[item_detail["delivered_flag"]].copy()
    seller = (
        delivered_items.groupby(["seller_id", "seller_state"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            item_price_revenue=("price", "sum"),
            avg_review_score=("review_score", "mean"),
            late_rate=("late_flag", "mean"),
            avg_freight_per_item=("freight_value", "mean"),
        )
        .query("orders >= 30")
        .sort_values("item_price_revenue", ascending=False)
    )
    return state, seller


def simulate_revenue(item_detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    delivered_items = item_detail[item_detail["delivered_flag"]].copy()
    top_categories = (
        delivered_items.groupby("product_category_name_english")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )
    monthly_cat = (
        delivered_items[delivered_items["product_category_name_english"].isin(top_categories)]
        .groupby(["purchase_month", "product_category_name_english"], as_index=False)["price"]
        .sum()
    )
    stats = (
        monthly_cat.groupby("product_category_name_english", as_index=False)
        .agg(mu_monthly_revenue=("price", "mean"), sigma_monthly_revenue=("price", "std"))
        .fillna({"sigma_monthly_revenue": 0})
    )

    draws = []
    for _, row in stats.iterrows():
        category_draw = rng.normal(
            row["mu_monthly_revenue"],
            row["sigma_monthly_revenue"],
            N_RUNS,
        )
        draws.append(np.clip(category_draw, 0, None))

    total_revenue = np.vstack(draws).sum(axis=0)
    mean_revenue = total_revenue.mean()
    simulation_summary = pd.DataFrame(
        {
            "scenario": ["top_5_category_monthly_revenue"],
            "n_runs": [N_RUNS],
            "expected_revenue": [mean_revenue],
            "stddev_revenue": [total_revenue.std(ddof=1)],
            "p_revenue_below_80pct_mean": [(total_revenue < 0.8 * mean_revenue).mean()],
            "percentile_5": [np.percentile(total_revenue, 5)],
            "percentile_95": [np.percentile(total_revenue, 95)],
        }
    )
    simulation_runs = pd.DataFrame({"run": np.arange(1, N_RUNS + 1), "total_revenue": total_revenue})
    return stats, simulation_summary, simulation_runs


def simulate_late_delivery(master: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    delivered = master[master["delivered_flag"]].dropna(subset=["late_flag"]).copy()
    late_p = float(delivered["late_flag"].mean())
    sample_late_rates = rng.binomial(n=1_000, p=late_p, size=N_RUNS) / 1_000
    return pd.DataFrame(
        {
            "scenario": ["platform_late_rate_1000_order_sample"],
            "n_runs": [N_RUNS],
            "sample_orders_per_run": [1_000],
            "expected_late_rate": [sample_late_rates.mean()],
            "stddev_late_rate": [sample_late_rates.std(ddof=1)],
            "p_late_rate_above_10pct": [(sample_late_rates > 0.10).mean()],
            "percentile_5": [np.percentile(sample_late_rates, 5)],
            "percentile_95": [np.percentile(sample_late_rates, 95)],
        }
    )


def create_charts(
    monthly: pd.DataFrame,
    category: pd.DataFrame,
    state: pd.DataFrame,
    simulation_runs: pd.DataFrame,
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")

    monthly_plot = monthly.copy()
    monthly_plot["purchase_month"] = pd.to_datetime(monthly_plot["purchase_month"])
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(monthly_plot["purchase_month"], monthly_plot["payment_revenue"], marker="o", linewidth=2)
    ax.set_title("Monthly Payment Revenue - Delivered Orders")
    ax.set_xlabel("Month")
    ax.set_ylabel("Payment revenue (BRL)")
    ax.ticklabel_format(axis="y", style="plain")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "01_monthly_payment_revenue.png", dpi=160)
    plt.close(fig)

    top_cat = category.head(10).sort_values("item_price_revenue")
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(top_cat["product_category_name_english"], top_cat["item_price_revenue"])
    ax.set_title("Top 10 Categories by Item Price Revenue")
    ax.set_xlabel("Item price revenue (BRL)")
    ax.ticklabel_format(axis="x", style="plain")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "02_top_10_categories_revenue.png", dpi=160)
    plt.close(fig)

    top_state = state.head(10).sort_values("late_rate")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_state["customer_state"], top_state["late_rate"])
    ax.set_title("Top 10 Customer States by Late Delivery Rate")
    ax.set_xlabel("Late delivery rate")
    ax.set_xlim(0, max(0.2, top_state["late_rate"].max() * 1.15))
    ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "03_late_rate_by_customer_state.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(simulation_runs["total_revenue"], bins=35, color="#2F6B5F", alpha=0.85)
    ax.set_title("Monte Carlo Simulation - Top 5 Category Monthly Revenue")
    ax.set_xlabel("Total monthly revenue (BRL)")
    ax.set_ylabel("Runs")
    ax.ticklabel_format(axis="x", style="plain")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "04_revenue_simulation_histogram.png", dpi=160)
    plt.close(fig)


def write_report(
    master: pd.DataFrame,
    yearly: pd.DataFrame,
    monthly: pd.DataFrame,
    category: pd.DataFrame,
    optimized: pd.DataFrame,
    state: pd.DataFrame,
    seller: pd.DataFrame,
    revenue_sim: pd.DataFrame,
    late_sim: pd.DataFrame,
) -> Path:
    delivered = master[master["delivered_flag"]].copy()
    overall = {
        "orders": delivered["order_id"].nunique(),
        "payment_revenue": delivered["payment_value"].sum(),
        "item_gmv": delivered["item_gmv"].sum(),
        "aov": delivered["payment_value"].sum() / delivered["order_id"].nunique(),
        "on_time_rate": 1 - delivered["late_flag"].mean(),
        "late_rate": delivered["late_flag"].mean(),
        "avg_review": delivered["review_score"].mean(),
        "avg_delivery_days": delivered["delivery_days"].mean(),
    }
    peak_month = monthly.sort_values("payment_revenue", ascending=False).iloc[0]
    pareto_count = int((category["cumulative_revenue_share"] <= 0.8).sum() + 1)
    top_cat = category.iloc[0]
    riskiest_state = state.iloc[0]
    top_seller = seller.iloc[0]
    rev = revenue_sim.iloc[0]
    late = late_sim.iloc[0]
    period_start = delivered["order_purchase_timestamp"].min().strftime("%Y-%m")
    period_end = delivered["order_purchase_timestamp"].max().strftime("%Y-%m")
    yoy_2018 = yearly.loc[yearly["year"].eq(2018), "payment_revenue_yoy"].iloc[0]
    peak_baseline = peak_month["payment_revenue"] / monthly["payment_revenue"].median()
    top_3_categories = ", ".join(category.head(3)["product_category_name_english"].tolist())
    objective_value = optimized["weighted_objective"].sum()
    baseline_mean = monthly["payment_revenue"].mean()
    baseline_std = monthly["payment_revenue"].std(ddof=1)
    baseline_downside = (monthly["payment_revenue"] < 0.8 * baseline_mean).mean()

    yearly_md = yearly.copy()
    for col in ["payment_revenue", "item_price_revenue", "freight_revenue", "aov_payment"]:
        yearly_md[col] = yearly_md[col].map(lambda x: round(x, 2))
    for col in ["on_time_rate", "avg_review_score", "avg_delivery_days", "payment_revenue_yoy", "delivered_orders_yoy", "aov_payment_yoy"]:
        yearly_md[col] = yearly_md[col].map(lambda x: round(x, 4) if pd.notna(x) else x)

    optimization_md = optimized[
        [
            "selected_rank",
            "product_category_name_english",
            "item_price_revenue",
            "avg_review_score",
            "avg_freight_per_item",
            "late_rate",
        ]
    ].copy()
    for col in ["item_price_revenue", "avg_review_score", "avg_freight_per_item", "late_rate"]:
        optimization_md[col] = optimization_md[col].map(lambda x: round(x, 4) if pd.notna(x) else x)

    risk_table = pd.DataFrame(
        [
            {
                "Kịch bản": "Top 5 category focus",
                "E[Revenue/tháng]": money(rev["expected_revenue"]),
                "StdDev": money(rev["stddev_revenue"]),
                "P(sụt >20%)": pct(rev["p_revenue_below_80pct_mean"]),
                "Chiến lược": "Reward/Risk screen",
            },
            {
                "Kịch bản": "Baseline platform monthly payment revenue",
                "E[Revenue/tháng]": money(baseline_mean),
                "StdDev": money(baseline_std),
                "P(sụt >20%)": pct(baseline_downside),
                "Chiến lược": "Reference",
            },
            {
                "Kịch bản": "Late delivery SLA sample",
                "E[Revenue/tháng]": "n/a",
                "StdDev": pct(late["stddev_late_rate"]),
                "P(sụt >20%)": f"P(late >10%) = {pct(late['p_late_rate_above_10pct'])}",
                "Chiến lược": "Logistics risk control",
            },
        ]
    )

    report = f"""# OLIST OPERATIONS ANALYTICS REPORT

Kỳ phân tích: {period_start} đến {period_end} | Dataset: {len(master):,} orders, Olist 2016-2018 | Filter: delivered orders

## 1. TỔNG QUAN KINH DOANH

- Tổng doanh thu (`payment_value`): {money(overall['payment_revenue'])} | YoY growth 2018 vs 2017: {pct(yoy_2018)}
- AOV: {money(overall['aov'])} | On-time delivery: {pct(overall['on_time_rate'])} | Avg review: {overall['avg_review']:.2f}/5.0
- Peak demand: Tháng 11/2017 (Black Friday) - {peak_baseline:.1f}x median monthly revenue baseline
- Delivered orders analyzed: {overall['orders']:,} | Late delivery rate: {pct(overall['late_rate'])} | Avg delivery time: {overall['avg_delivery_days']:.1f} days

{dataframe_to_markdown(yearly_md)}

## 2. DANH MỤC & ĐỊA LÝ

- Top 3 categories doanh thu lớn nhất: {top_3_categories}
- State có tỷ lệ giao trễ cao nhất: {riskiest_state['customer_state']} ({pct(riskiest_state['late_rate'])})
- Pareto insight: {pareto_count} danh mục = 80% item price revenue
- Top category: {top_cat['product_category_name_english']} với {money(top_cat['item_price_revenue'])}
- Highest revenue seller >= 30 orders: {top_seller['seller_id']} ({top_seller['seller_state']}), revenue {money(top_seller['item_price_revenue'])}, late rate {pct(top_seller['late_rate'])}

## 3. MÔ HÌNH TỐI ƯU HÓA

- Bài toán: Chọn TOP K=10 danh mục nên ưu tiên đầu tư.
- Loại mô hình: Binary Integer Programming screening.
- Decision variables: x_i in {{0,1}}, x_i = 1 nếu chọn danh mục i.
- Objective: Maximize Σ(revenue_i x avg_review_score_i x x_i).
- Constraints: Σx_i = 10, avg_review_score_i >= 3.5, avg_freight_per_item_i <= BRL 25.
- Optimal solution: 10 categories trong bảng dưới.
- Objective value: {objective_value:,.0f}. Tiết kiệm vs baseline: chưa định lượng vì đây là mô hình chọn danh mục, không phải cost-minimization.

{dataframe_to_markdown(optimization_md)}

## 4. ĐÁNH GIÁ RỦI RO (N={N_RUNS:,} runs)

{dataframe_to_markdown(risk_table)}

- Revenue simulation: Normal distribution fitted from monthly revenue of top 5 categories, random seed = {RANDOM_SEED}.
- Late delivery simulation: 1,000 delivered-order sample per run, platform late probability estimated from historical delivered orders.

## 5. KHUYẾN NGHỊ CHIẾN LƯỢC

- Quyết định: Ưu tiên 10 danh mục đã chọn, đồng thời mở drill-down logistics cho các state late-rate cao trước khi mở rộng seller/category.
- EV ước tính: {money(rev['expected_revenue'])} / tháng cho top-5 category revenue simulation proxy.
- Rủi ro chính cần theo dõi: P(revenue < 80% mean) = {pct(rev['p_revenue_below_80pct_mean'])}; P(late rate > 10%) = {pct(late['p_late_rate_above_10pct'])}.
- Điều kiện để quyết định thay đổi (Sensitivity): nếu late rate của category/state được chọn vượt 10% hoặc avg review giảm dưới 3.8, cần giảm ưu tiên category/seller đó và chạy lại optimization.

## 6. GHI CHÚ KỸ THUẬT

- Revenue definition: `payment_value` dùng cho doanh thu thực thu; `price + freight_value` dùng cho GMV/item diagnostics.
- Time axis: `order_purchase_timestamp`.
- Join quality: `items`, `payments`, `reviews` được aggregate trước ở cấp `order_id` để tránh duplicate revenue.
- Output tables/charts nằm trong `Outputs/tables` và `Outputs/charts`.
"""

    html_yearly = yearly_md.copy()
    html_optimization = optimization_md.copy()
    html_risk = risk_table.copy()
    top_state_html = state.head(10)[
        ["customer_state", "orders", "payment_revenue", "avg_delivery_days", "late_rate", "avg_freight", "avg_review_score"]
    ].copy()
    for col in ["payment_revenue", "avg_delivery_days", "late_rate", "avg_freight", "avg_review_score"]:
        top_state_html[col] = top_state_html[col].map(lambda x: round(x, 4) if pd.notna(x) else x)

    html = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Olist Operations Analytics Report</title>
  <style>
    :root {{
      --ink: #1f2933;
      --muted: #5f6b7a;
      --line: #d9e2ec;
      --panel: #f7fafc;
      --brand: #0f766e;
      --accent: #b45309;
    }}
    body {{
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.55;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 28px 56px;
    }}
    header {{
      border-bottom: 3px solid var(--brand);
      padding-bottom: 18px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }}
    h2 {{
      margin-top: 34px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 6px;
      font-size: 21px;
    }}
    .subtitle, .note {{
      color: var(--muted);
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
      margin: 18px 0;
    }}
    .kpi {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 4px solid var(--brand);
      padding: 12px 14px;
      border-radius: 6px;
    }}
    .kpi span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }}
    .kpi strong {{
      display: block;
      font-size: 20px;
      margin-top: 4px;
    }}
    .data-table {{
      border-collapse: collapse;
      width: 100%;
      margin: 14px 0 22px;
      font-size: 13px;
    }}
    .data-table th {{
      background: #e6f4f1;
      text-align: left;
      border: 1px solid var(--line);
      padding: 8px;
    }}
    .data-table td {{
      border: 1px solid var(--line);
      padding: 8px;
      vertical-align: top;
    }}
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 18px;
      margin-top: 12px;
    }}
    figure {{
      margin: 0;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      background: #fff;
    }}
    figure img {{
      width: 100%;
      height: auto;
      display: block;
    }}
    figcaption {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    code {{
      background: #eef2f7;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    ul {{
      padding-left: 22px;
    }}
  </style>
</head>
<body>
<main>
  <header>
    <h1>OLIST OPERATIONS ANALYTICS REPORT</h1>
    <div class="subtitle">Kỳ phân tích: {period_start} đến {period_end} | Dataset: {len(master):,} orders, Olist 2016-2018 | Filter: delivered orders</div>
  </header>

  <section>
    <h2>1. TỔNG QUAN KINH DOANH</h2>
    <div class="kpi-grid">
      <div class="kpi"><span>Payment revenue</span><strong>{money(overall['payment_revenue'])}</strong></div>
      <div class="kpi"><span>YoY growth 2018 vs 2017</span><strong>{pct(yoy_2018)}</strong></div>
      <div class="kpi"><span>AOV</span><strong>{money(overall['aov'])}</strong></div>
      <div class="kpi"><span>On-time delivery</span><strong>{pct(overall['on_time_rate'])}</strong></div>
      <div class="kpi"><span>Avg review</span><strong>{overall['avg_review']:.2f}/5.0</strong></div>
      <div class="kpi"><span>Late delivery</span><strong>{pct(overall['late_rate'])}</strong></div>
    </div>
    <ul>
      <li>Peak demand: Tháng 11/2017 (Black Friday) - {peak_baseline:.1f}x median monthly revenue baseline.</li>
      <li>Delivered orders analyzed: {overall['orders']:,}; average delivery time: {overall['avg_delivery_days']:.1f} days.</li>
      <li>Revenue definition: <code>payment_value</code> là doanh thu thực thu; <code>price + freight_value</code> là GMV/item diagnostics.</li>
    </ul>
    {dataframe_to_html(html_yearly)}
  </section>

  <section>
    <h2>2. DANH MỤC & ĐỊA LÝ</h2>
    <ul>
      <li>Top 3 categories doanh thu lớn nhất: <strong>{escape(top_3_categories)}</strong>.</li>
      <li>State có tỷ lệ giao trễ cao nhất: <strong>{escape(str(riskiest_state['customer_state']))}</strong> ({pct(riskiest_state['late_rate'])}).</li>
      <li>Pareto insight: <strong>{pareto_count}</strong> danh mục = 80% item price revenue.</li>
      <li>Top category: <strong>{escape(str(top_cat['product_category_name_english']))}</strong> với {money(top_cat['item_price_revenue'])}.</li>
    </ul>
    <h3>Top 10 customer states by late delivery risk</h3>
    {dataframe_to_html(top_state_html)}
  </section>

  <section>
    <h2>3. MÔ HÌNH TỐI ƯU HÓA</h2>
    <ul>
      <li>Bài toán: chọn TOP K=10 danh mục nên ưu tiên đầu tư.</li>
      <li>Loại mô hình: Binary Integer Programming screening.</li>
      <li>Decision variables: <code>x_i in {{0,1}}</code>, <code>x_i = 1</code> nếu chọn danh mục i.</li>
      <li>Objective: Maximize Σ(revenue_i x avg_review_score_i x x_i).</li>
      <li>Constraints: Σx_i = 10, avg_review_score_i >= 3.5, avg_freight_per_item_i <= BRL 25.</li>
      <li>Objective value: {objective_value:,.0f}. Tiết kiệm vs baseline: chưa định lượng vì đây là mô hình chọn danh mục, không phải cost-minimization.</li>
    </ul>
    {dataframe_to_html(html_optimization)}
  </section>

  <section>
    <h2>4. ĐÁNH GIÁ RỦI RO (N={N_RUNS:,} runs)</h2>
    {dataframe_to_html(html_risk)}
    <ul>
      <li>Revenue simulation: Normal distribution fitted from monthly revenue of top 5 categories, random seed = {RANDOM_SEED}.</li>
      <li>Late delivery simulation: 1,000 delivered-order sample per run, platform late probability estimated from historical delivered orders.</li>
    </ul>
  </section>

  <section>
    <h2>5. KHUYẾN NGHỊ CHIẾN LƯỢC</h2>
    <ul>
      <li>Quyết định: ưu tiên 10 danh mục đã chọn, đồng thời drill-down logistics cho các state late-rate cao trước khi mở rộng seller/category.</li>
      <li>EV ước tính: {money(rev['expected_revenue'])} / tháng cho top-5 category revenue simulation proxy.</li>
      <li>Rủi ro chính: P(revenue &lt; 80% mean) = {pct(rev['p_revenue_below_80pct_mean'])}; P(late rate &gt; 10%) = {pct(late['p_late_rate_above_10pct'])}.</li>
      <li>Sensitivity: nếu late rate của category/state được chọn vượt 10% hoặc avg review giảm dưới 3.8, cần giảm ưu tiên category/seller đó và chạy lại optimization.</li>
    </ul>
  </section>

  <section>
    <h2>Charts</h2>
    <div class="chart-grid">
      <figure><img src="../charts/01_monthly_payment_revenue.png" alt="Monthly payment revenue"><figcaption>Monthly payment revenue - delivered orders</figcaption></figure>
      <figure><img src="../charts/02_top_10_categories_revenue.png" alt="Top 10 categories"><figcaption>Top 10 categories by item price revenue</figcaption></figure>
      <figure><img src="../charts/03_late_rate_by_customer_state.png" alt="Late rate by customer state"><figcaption>Top customer states by late delivery rate</figcaption></figure>
      <figure><img src="../charts/04_revenue_simulation_histogram.png" alt="Revenue simulation histogram"><figcaption>Monte Carlo revenue simulation histogram</figcaption></figure>
    </div>
  </section>

  <section>
    <h2>Ghi chú kỹ thuật</h2>
    <ul>
      <li>Time axis: <code>order_purchase_timestamp</code>.</li>
      <li>Join quality: <code>items</code>, <code>payments</code>, <code>reviews</code> được aggregate trước ở cấp <code>order_id</code>.</li>
      <li>Source tables/charts: <code>Outputs/tables</code> và <code>Outputs/charts</code>.</li>
    </ul>
  </section>
</main>
</body>
</html>
"""

    md_path = REPORT_DIR / "olist_operations_analytics_report.md"
    html_path = REPORT_DIR / "olist_operations_analytics_report.html"
    md_path.write_text(report, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    return html_path


def main() -> None:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    data = load_data()
    master, item_detail = build_master(data)

    yearly, monthly = run_sql_summaries(master)
    category, optimized = analyze_categories(item_detail)
    state, seller = analyze_logistics(master, item_detail)
    revenue_stats, revenue_sim, revenue_runs = simulate_revenue(item_detail)
    late_sim = simulate_late_delivery(master)

    save_table(yearly, "yearly_kpis.csv")
    save_table(monthly, "monthly_kpis.csv")
    save_table(category, "category_performance.csv")
    save_table(optimized, "category_optimization_top10.csv")
    save_table(state, "customer_state_logistics.csv")
    save_table(seller, "seller_performance.csv")
    save_table(revenue_stats, "revenue_simulation_category_stats.csv")
    save_table(revenue_sim, "revenue_simulation_summary.csv")
    save_table(late_sim, "late_delivery_simulation_summary.csv")

    create_charts(monthly, category, state, revenue_runs)
    report_path = write_report(
        master, yearly, monthly, category, optimized, state, seller, revenue_sim, late_sim
    )

    print(f"Report: {report_path}")
    print(f"Tables: {TABLE_DIR}")
    print(f"Charts: {CHART_DIR}")


if __name__ == "__main__":
    main()
