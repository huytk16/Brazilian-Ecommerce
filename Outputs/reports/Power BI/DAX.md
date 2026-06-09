# DAX Measures — Brazilian E-Commerce Operations Dashboard

Tài liệu này tổng hợp toàn bộ công thức DAX Measures được sử dụng trong file `Brazillian_Ecommerce.pbix`, phục vụ Dashboard **"Midnight Executive"** (4:3).  
Tất cả các Measure được tổ chức trong một bảng ảo tên `_Measures` để quản lý tập trung.

---

## Mục lục

1. [Bảng Ngày (Dim_Date)](#1-bảng-ngày-dim_date)
2. [KPI Cốt lõi](#2-kpi-cốt-lõi)
3. [Tăng trưởng YoY](#3-tăng-trưởng-yoy)
4. [Sub-labels động cho KPI Cards](#4-sub-labels-động-cho-kpi-cards)
5. [Đo lường bổ sung cho bảng Logistics](#5-đo-lường-bổ-sung-cho-bảng-logistics)

---

## 1. Bảng Ngày (Dim_Date)

> Tạo bằng cách vào **Modeling → New Table**. Bảng này là nền tảng cho tất cả hàm Time Intelligence.

```dax
Dim_Date = 
VAR MinDate = MIN(df_master[order_purchase_timestamp])
VAR MaxDate = MAX(df_master[order_purchase_timestamp])
RETURN
ADDCOLUMNS(
    CALENDAR(MinDate, MaxDate),
    "Year",             YEAR([Date]),
    "Month Number",     MONTH([Date]),
    "Month Name",       FORMAT([Date], "MMMM"),
    "Month Short",      FORMAT([Date], "MMM"),
    "Month-Year Number",YEAR([Date]) * 100 + MONTH([Date]),
    "Month-Year",       FORMAT([Date], "YYYY-MM"),
    "Quarter",          "Q" & QUARTER([Date]),
    "Week Number",      WEEKNUM([Date]),
    "Day of Week",      WEEKDAY([Date]),
    "Day of Week Name", FORMAT([Date], "dddd")
)
```

**Sau khi tạo bảng, Sort by Column:**
- `Month Short` → Sort by **Month Number**
- `Month-Year` → Sort by **Month-Year Number**

---

## 2. KPI Cốt lõi

### 2.1 Doanh thu thực tế (Realized Revenue)

```dax
Realized Revenue = 
CALCULATE(
    SUM(df_master[payment_value]),
    df_master[order_status] = "delivered"
)
```

> *Định dạng:* Currency — 2 chữ số thập phân (BRL).

---

### 2.2 Số đơn hàng thành công (Delivered Orders)

```dax
Delivered Orders = 
CALCULATE(
    DISTINCTCOUNT(df_master[order_id]),
    df_master[order_status] = "delivered"
)
```

> *Định dạng:* Whole Number — bật dấu phân cách hàng nghìn.

---

### 2.3 Giá trị đơn hàng trung bình (AOV)

```dax
AOV = DIVIDE([Realized Revenue], [Delivered Orders], 0)
```

> *Định dạng:* Currency — 2 chữ số thập phân.

---

### 2.4 Tỷ lệ giao hàng đúng hạn (On-Time Delivery Rate)

```dax
On-Time Delivery Rate = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(df_master[order_id]),
        df_master[order_status] = "delivered",
        df_master[late_flag] = 0
    ),
    [Delivered Orders],
    0
)
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.  
> `late_flag = 0` nghĩa là đơn giao **đúng hạn hoặc sớm hơn** ngày dự kiến.

---

### 2.5 Tỷ lệ giao hàng trễ (Late Delivery Rate)

```dax
Late Delivery Rate = 1 - [On-Time Delivery Rate]
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.

---

### 2.6 Điểm đánh giá CSAT trung bình

```dax
CSAT Score = 
CALCULATE(
    AVERAGE(df_master[review_score]),
    df_master[order_status] = "delivered"
)
```

> *Định dạng:* Decimal — 2 chữ số thập phân.

---

### 2.7 Số ngày giao hàng trung bình (Average Delivery Days)

```dax
Average Delivery Days = 
CALCULATE(
    AVERAGE(df_master[delivery_days]),
    df_master[order_status] = "delivered"
)
```

> *Định dạng:* Decimal — 1 chữ số thập phân.  
> Sử dụng trong bảng Logistics Risk Matrix (Visual 4).

---

### 2.8 Tỷ lệ đánh giá 1-sao (1-Star Review Rate)

```dax
1-Star Review Rate = 
DIVIDE(
    CALCULATE(
        COUNT(df_master[order_id]),
        df_master[review_score] = 1,
        df_master[order_status] = "delivered"
    ),
    CALCULATE(
        COUNT(df_master[order_id]),
        NOT(ISBLANK(df_master[review_score])),
        df_master[order_status] = "delivered"
    ),
    0
)
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.

---

## 3. Tăng trưởng YoY

> Các Measure này sử dụng hàm `SAMEPERIODLASTYEAR` yêu cầu `Dim_Date` đã được đánh dấu là **Date Table**.

### 3.1 Tăng trưởng Doanh thu YoY

```dax
YoY Revenue Growth % = 
VAR CurrentRevenue = [Realized Revenue]
VAR PriorRevenue   = CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date]))
RETURN
DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.

---

### 3.2 Tăng trưởng Đơn hàng YoY

```dax
Orders YoY Growth % = 
VAR CurrentOrders = [Delivered Orders]
VAR PriorOrders   = CALCULATE([Delivered Orders], SAMEPERIODLASTYEAR(Dim_Date[Date]))
RETURN
DIVIDE(CurrentOrders - PriorOrders, PriorOrders, 0)
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.

---

### 3.3 Tăng trưởng AOV YoY

```dax
AOV YoY Growth % = 
VAR CurrentAOV = [AOV]
VAR PriorAOV   = CALCULATE([AOV], SAMEPERIODLASTYEAR(Dim_Date[Date]))
RETURN
DIVIDE(CurrentAOV - PriorAOV, PriorAOV, 0)
```

> *Định dạng:* Percentage (%) — 1 chữ số thập phân.

---

## 4. Sub-labels động cho KPI Cards

> Sử dụng với visual **Card (New)** → trường **Reference Label**. Hiển thị thông tin xu hướng nhỏ bên dưới chỉ số chính.

### 4.1 Revenue Sub-label

```dax
Revenue Sub-label = 
VAR Growth = [YoY Revenue Growth %]
RETURN
IF(
    ISBLANK(Growth) || Growth = 0,
    "No YoY Data",
    IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY"
)
```

---

### 4.2 Orders Sub-label

```dax
Orders Sub-label = 
VAR Growth = [Orders YoY Growth %]
RETURN
IF(
    ISBLANK(Growth) || Growth = 0,
    "No YoY Data",
    IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY"
)
```

---

### 4.3 AOV Sub-label

```dax
AOV Sub-label = 
VAR Growth = [AOV YoY Growth %]
RETURN
IF(
    ISBLANK(Growth) || Growth = 0,
    "No YoY Data",
    IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY"
)
```

---

### 4.4 On-Time Sub-label

```dax
On-Time Sub-label = 
VAR SLA_Target  = 0.90
VAR CurrentRate = [On-Time Delivery Rate]
RETURN
"Target SLA: 90.0% (" & IF(CurrentRate >= SLA_Target, "Đạt SLA", "Vi phạm SLA") & ")"
```

---

### 4.5 CSAT Sub-label

```dax
CSAT Sub-label = 
VAR OneStarRate = [1-Star Review Rate]
RETURN
FORMAT(OneStarRate, "0.0%") & " rate 1-star"
```

---

## 5. Đo lường bổ sung cho bảng Logistics

> Sử dụng trong **Visual 4 — Customer State Risk Matrix**.

### 5.1 Conditional Formatting — Late Rate Color

Áp dụng **Conditional Formatting → Background Color → Rules** cho cột `[Late Delivery Rate]`:

| Điều kiện | Màu nền | Ý nghĩa |
|---|---|---|
| < 10% | `#10b981` (opacity cao) | Hiệu suất tốt |
| 10% – 15% | `#f59e0b` (opacity cao) | Cần theo dõi |
| > 15% | `#ef4444` (opacity cao) | Rủi ro cao |

---

## Ghi chú chung

| Measure | Bảng nguồn | Cột khóa |
|---|---|---|
| Tất cả KPI | `df_master` | `order_status`, `late_flag`, `delivery_days` |
| Category metrics | `item_detail` | `product_category_name_english` |
| Time Intelligence | `Dim_Date` | `Date` (phải là Date Table) |

> **Lưu ý quan trọng:** Cột `order_purchase_timestamp` trong cả `df_master` và `item_detail` **phải được chuyển về kiểu `Date`** (không phải `DateTime`) trong Power Query trước khi tạo relationship với `Dim_Date[Date]`. Nếu không, các Measure Time Intelligence sẽ trả về kết quả sai.
