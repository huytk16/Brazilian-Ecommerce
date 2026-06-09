# Power BI Data Modeling — Brazilian E-Commerce Dashboard

Tài liệu này hướng dẫn toàn bộ bước **thiết lập mô hình dữ liệu** trong Power BI Desktop trước khi nhập DAX Measures.  
Thực hiện đúng thứ tự: **Data Types → Relationships → Date Table → Visuals → Slicers**.

> Công thức DAX xem tại: [`DAX.md`](DAX.md)  
> Nguồn dữ liệu: `Data/olist_analytics.db` (SQLite)

---

## Mục lục

1. [Kết nối dữ liệu & Kiểu dữ liệu (Power Query)](#1-kết-nối-dữ-liệu--kiểu-dữ-liệu-power-query)
2. [Mô hình quan hệ (Relationships)](#2-mô-hình-quan-hệ-relationships)
3. [Thiết lập Date Table (Dim_Date)](#3-thiết-lập-date-table-dim_date)
4. [Cấu hình 5 Visuals chính](#4-cấu-hình-5-visuals-chính)
5. [Quy chuẩn Typography (Canvas 4:3)](#5-quy-chuẩn-typography-canvas-43)
6. [Slicers (Bộ lọc tương tác)](#6-slicers-bộ-lọc-tương-tác)

---

## 1. Kết nối dữ liệu & Kiểu dữ liệu (Power Query)

Kết nối Power BI trực tiếp tới `Data/olist_analytics.db` qua **Get Data → ODBC / SQLite**.  
Khi import qua Power Query, SQLite thường chuyển tất cả cột thành **Text** hoặc **General** — bắt buộc phải đổi lại kiểu dữ liệu thủ công.

### Bảng `df_master` — Fact table mức Đơn hàng

| Kiểu dữ liệu | Các cột |
|---|---|
| **Text** | `order_id`, `customer_id`, `customer_unique_id`, `customer_state`, `customer_city`, `order_status`, `primary_payment_type`, `purchase_month` |
| **Date** ⚠️ | `order_purchase_timestamp` — **chuyển từ DateTime → Date** để khớp với `Dim_Date[Date]` |
| **Date/Time** | `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date` |
| **Whole Number** | `purchase_year`, `item_count`, `product_count`, `seller_count`, `payment_count`, `max_installments`, `review_count`, `delivered_flag`, `late_flag`, `delivery_days` |
| **Decimal Number** | `item_price`, `freight_value`, `item_gmv`, `payment_value`, `review_score` |

### Bảng `item_detail` — Fact/Dimension table mức Chi tiết mặt hàng

| Kiểu dữ liệu | Các cột |
|---|---|
| **Text** | `order_id`, `product_id`, `seller_id`, `customer_id`, `customer_state`, `seller_state`, `product_category_name_english`, `purchase_month` |
| **Date** ⚠️ | `order_purchase_timestamp` — **chuyển từ DateTime → Date** |
| **Date/Time** | `order_delivered_customer_date`, `order_estimated_delivery_date` |
| **Whole Number** | `order_item_id`, `delivered_flag`, `late_flag` |
| **Decimal Number** | `price`, `freight_value`, `review_score` |

> **Lý do chuyển `order_purchase_timestamp` về Date:**  
> Nếu giữ nguyên DateTime (ví dụ `2017-11-24 16:30:22`), relationship với `Dim_Date[Date]` (`2017-11-24`) sẽ chỉ khớp các đơn đặt đúng 00:00:00, dẫn đến **mất toàn bộ dữ liệu** trong các Measure Time Intelligence.

---

## 2. Mô hình quan hệ (Relationships)

Mô hình theo chuẩn **Star Schema** với `Dim_Date` là bảng Dimension trung tâm.

```
Dim_Date ──(1:N, Active)──► df_master
Dim_Date ──(1:N, Active)──► item_detail
df_master ──(1:N, Active)──► item_detail
Dim_Date ··(1:N, Inactive)·· df_master[order_delivered_customer_date]
Dim_Date ··(1:N, Inactive)·· df_master[order_estimated_delivery_date]
```

### Chi tiết từng Relationship

Cấu hình tại tab **Model View → Manage Relationships**:

| # | From | To | Cardinality | Cross Filter | Trạng thái |
|---|---|---|---|---|---|
| 1 | `Dim_Date[Date]` | `df_master[order_purchase_timestamp]` | 1 : Many | Single | **Active** |
| 2 | `Dim_Date[Date]` | `item_detail[order_purchase_timestamp]` | 1 : Many | Single | **Active** |
| 3 | `df_master[order_id]` | `item_detail[order_id]` | 1 : Many | Single | **Active** |
| 4 | `Dim_Date[Date]` | `df_master[order_delivered_customer_date]` | 1 : Many | Single | Inactive |
| 5 | `Dim_Date[Date]` | `df_master[order_estimated_delivery_date]` | 1 : Many | Single | Inactive |

> Relationship 4 & 5 (Inactive) được kích hoạt tạm thời bằng hàm `USERELATIONSHIP()` trong DAX khi cần phân tích theo ngày giao thực tế hoặc ngày dự kiến.

---

## 3. Thiết lập Date Table (Dim_Date)

### Bước 1 — Tạo bảng bằng DAX

**Modeling → New Table**, nhập công thức tại [`DAX.md § 1`](DAX.md#1-bảng-ngày-dim_date).

### Bước 2 — Mark as Date Table

Chọn bảng `Dim_Date` → **Table tools → Mark as date table → Mark as date table** → Chọn cột `Date`.  
*(Bắt buộc để các hàm `SAMEPERIODLASTYEAR`, `DATEADD`, v.v. hoạt động đúng.)*

### Bước 3 — Sort by Column

| Cột cần sort | Sort by |
|---|---|
| `Month Short` | `Month Number` |
| `Month Name` | `Month Number` |
| `Month-Year` | `Month-Year Number` |

---

## 4. Cấu hình 5 Visuals chính

Canvas: **Custom 1200 × 900 px** · Background: `#0b0f19` · Theme: Midnight Executive

---

### Visual 1 — KPI Cards (Card New)

5 thẻ nằm ngang ở đầu trang.

| Card | Callout Value | Sub-label | Accent Bar Color |
|---|---|---|---|
| Realized Revenue | `[Realized Revenue]` | `[Revenue Sub-label]` | `#10b981` |
| Delivered Orders | `[Delivered Orders]` | `[Orders Sub-label]` | `#06b6d4` |
| AOV | `[AOV]` | `[AOV Sub-label]` | `#8b5cf6` |
| On-Time Delivery Rate | `[On-Time Delivery Rate]` | `[On-Time Sub-label]` | `#10b981` |
| CSAT Score | `[CSAT Score]` | `[CSAT Sub-label]` | `#f59e0b` |

---

### Visual 2 — Monthly Revenue Trend (Area Chart)

| Trường | Cấu hình |
|---|---|
| X-Axis | `Dim_Date[Month-Year]` (format `yyyy-MM`) |
| Y-Axis | `[Realized Revenue]` |
| Line stroke | Cyan `#06b6d4`, width 3pt |
| Area fill | `#06b6d4`, Transparency 85% |
| Annotation | Text box tại đỉnh Nov 2017: *"BRL 1.16M — Black Friday Peak"* (màu `#f59e0b`) |

---

### Visual 3 — Top 10 Categories (Clustered Bar Chart)

| Trường | Cấu hình |
|---|---|
| Y-Axis | `item_detail[product_category_name_english]` |
| X-Axis | `[Realized Revenue]` |
| Filter | Top N = 10 by `[Realized Revenue]` (Filters pane → Visual filter) |
| Bar color | Gradient `#22d3ee` (rank 1) → `#0e7490` (rank 10) via Conditional Formatting |

---

### Visual 4 — Logistics Risk Matrix (Table)

| Cột hiển thị | Measure |
|---|---|
| Bang khách hàng | `df_master[customer_state]` |
| Số đơn giao | `[Delivered Orders]` |
| Ngày giao TB | `[Average Delivery Days]` |
| Tỷ lệ trễ | `[Late Delivery Rate]` |

**Conditional Formatting** cho cột `[Late Delivery Rate]` (Background Color → Rules):

| Điều kiện | Màu nền |
|---|---|
| < 10% | `#10b981` (opacity 70%) |
| 10% – 15% | `#f59e0b` (opacity 70%) |
| > 15% | `#ef4444` (opacity 70%) |

Sắp xếp: `[Late Delivery Rate]` **giảm dần** để các bang rủi ro cao hiển thị đầu bảng.

---

### Visual 5 — Category Prioritization & Simulation

**BIP Optimization Table** (Visual: Table):

| Cột | Nguồn |
|---|---|
| Thứ hạng | `selected_rank` |
| Danh mục | `product_category_name_english` |
| Doanh thu | `item_price_revenue` |
| CSAT TB | `avg_review_score` |
| Cước TB | `avg_freight_per_item` |

Nguồn: bảng `category_optimization_top10` (import từ `Outputs/tables/category_optimization_top10.csv`).  
Định dạng: nền `#111827`, tắt Gridlines.

**Monte Carlo Cards** (2 Card New cạnh nhau):

| Card | Giá trị | Màu chữ | Mô tả |
|---|---|---|---|
| Revenue Downside Risk | 21.4% | `#8b5cf6` | Xác suất doanh thu giảm > 20% so với kỳ vọng (Mean: BRL 248K) |
| SLA Delivery Risk | 1.7% | `#10b981` | Xác suất tỷ lệ trễ vượt ngưỡng SLA 10% |

---

## 5. Quy chuẩn Typography (Canvas 4:3)

Font hệ thống: **Segoe UI** hoặc **Inter**.

### Header & Slicers

| Thành phần | Size | Style | Màu |
|---|---|---|---|
| Dashboard title | 18pt | Bold | `#f8fafc` |
| Subtitle | 9pt | Regular | `#94a3b8` |
| Badge (Sales Director) | 8pt | Semibold | `#22d3ee` / nền `#062d3c` |
| Slicer label | 8pt | Semibold Uppercase | `#94a3b8` |
| Slicer values | 8.5pt | Regular | `#f8fafc` / nền `#1f2937` |

### KPI Cards

| Thành phần | Size | Style | Màu |
|---|---|---|---|
| Card title | 8.5pt | Semibold Uppercase | `#94a3b8` |
| Callout value | 24pt | Bold | `#f8fafc` |
| Sub-label | 8.5pt | Regular | Động theo ngữ cảnh |

> ⚠️ Không đặt Callout > 28pt để tránh bị cắt `...` với số lớn như BRL 15.42M.

### Charts

| Thành phần | Size | Style | Màu |
|---|---|---|---|
| Visual title | 10pt | Bold | `#f8fafc` hoặc `#06b6d4` |
| Axis labels | 8.5pt | Regular | `#94a3b8` |
| Data labels | 8.5pt | Bold | `#f8fafc` |

### Tables

| Thành phần | Size | Style | Màu / Nền |
|---|---|---|---|
| Header | 9pt | Bold | `#94a3b8` / nền `#111827` |
| Row values | 8.5pt | Regular | `#f8fafc` |
| Row padding | 4–5px | Sparse | — |
| Badge status | 7.5pt | Bold | Theo conditional formatting |

---

## 6. Slicers (Bộ lọc tương tác)

Đặt thanh 4 slicer nằm ngang phía dưới tiêu đề chính.  
Style: **Dropdown** hoặc **Tile** · Nền: `#1f2937`.

| # | Tên Slicer | Cột nguồn | Loại |
|---|---|---|---|
| 1 | Thời gian | `df_master[order_purchase_timestamp]` | Between / Dropdown |
| 2 | Bang Khách hàng | `df_master[customer_state]` | Dropdown |
| 3 | Bang Người bán | `item_detail[seller_state]` | Dropdown |
| 4 | Top N Filter | *(điều kiện lọc sẵn)* | Dropdown |
