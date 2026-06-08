# Power BI Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hướng dẫn từng bước xây dựng Dashboard Power BI hoàn chỉnh cho Olist Brazilian E-Commerce dựa trên tài liệu đặc tả thiết kế "Midnight Executive".

**Architecture:** Xây dựng mô hình dữ liệu dạng hình sao (Star Schema) với Fact Orders liên kết với các bảng Dimension, viết các DAX Measure tối ưu, kéo thả các visual và thiết lập bộ lọc tương tác.

**Tech Stack:** Power BI Desktop, DAX, Power Query (M Language).

---

### Task 1: Thiết lập Mô hình Dữ liệu (Data Model - Star Schema)

**Files:**
- Create: Power BI Desktop file `Brazilian_Ecommerce_Sales_Dashboard.pbix`
- Data Sources: Các file CSV tại `e:\PROJECT\01_Data_Analytics\Operation Analytics\Brazilian Ecommerce\Data\`

- [ ] **Step 1: Load dữ liệu qua Power Query (ETL)**
  * Mở Power BI Desktop, chọn **Get Data -> Text/CSV** và load các bảng sau:
    1. `olist_orders_dataset.csv`
    2. `olist_order_items_dataset.csv`
    3. `olist_order_payments_dataset.csv`
    4. `olist_order_reviews_dataset.csv`
    5. `olist_customers_dataset.csv`
    6. `olist_sellers_dataset.csv`
    7. `olist_products_dataset.csv`
    8. `product_category_name_translation.csv`

- [ ] **Step 2: Chuẩn hóa dữ liệu trong Power Query Editor**
  * Đổi tên cột trong bảng translation: `product_category_name` thành `product_category_name_pt`, `product_category_name_english` thành `product_category_name`.
  * Thực hiện **Merge Queries** bảng `olist_products_dataset` với `product_category_name_translation` qua cột `product_category_name` (tiếng Bồ Đào Nha) để lấy cột tên tiếng Anh.
  * Chuyển các cột ngày tháng sau thành kiểu **Date/Time**:
    - `order_purchase_timestamp`
    - `order_approved_at`
    - `order_delivered_carrier_date`
    - `order_delivered_customer_date`
    - `order_estimated_delivery_date`
  * Đặt tên bảng rõ ràng (Ví dụ: `Fact_Orders`, `Dim_Customers`, `Dim_Sellers`, `Dim_Products`, `Dim_Reviews`, `Fact_Order_Payments`, `Fact_Order_Items`).

- [ ] **Step 3: Thiết lập các mối quan hệ (Relationships)**
  * Chuyển sang thẻ Model View, thiết lập các mối quan hệ 1-nhiều (1-to-many) với hướng lọc Single:
    - `Dim_Customers[customer_id]` -> `Fact_Orders[customer_id]` (1:*)
    - `Dim_Sellers[seller_id]` -> `Fact_Order_Items[seller_id]` (1:*)
    - `Dim_Products[product_id]` -> `Fact_Order_Items[product_id]` (1:*)
    - `Fact_Orders[order_id]` -> `Fact_Order_Items[order_id]` (1:*)
    - `Fact_Orders[order_id]` -> `Fact_Order_Payments[order_id]` (1:*)
    - `Fact_Orders[order_id]` -> `Dim_Reviews[order_id]` (1:*)

---

### Task 2: Viết các DAX Measure Cốt lõi

**Files:**
- Create: Bảng ảo chứa Measure `_Measures` trong Power BI.

- [ ] **Step 1: Tạo bảng Measure và viết KPI Doanh thu & Đơn hàng**
  * Tạo bảng mới tên `_Measures` bằng DAX:
    ```dax
    _Measures = ROW("Temp", 0)
    ```
  * Tạo Measure **Doanh thu Realized**:
    ```dax
    Realized Revenue = SUM(Fact_Order_Payments[payment_value])
    ```
  * Tạo Measure **Số đơn hàng Delivered**:
    ```dax
    Delivered Orders = CALCULATE(DISTINCTCOUNT(Fact_Orders[order_id]), Fact_Orders[order_status] = "delivered")
    ```

- [ ] **Step 2: Viết các Measure AOV và So sánh tăng trưởng**
  * Tạo Measure **AOV (Average Order Value)**:
    ```dax
    AOV = DIVIDE([Realized Revenue], [Delivered Orders], 0)
    ```
  * Tạo Measure **Doanh thu cùng kỳ năm trước (YoY Revenue)** và **Tăng trưởng %**:
    ```dax
    YoY Revenue = CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date]))
    YoY Revenue Growth % = DIVIDE([Realized Revenue] - [YoY Revenue], [YoY Revenue], 0)
    ```

- [ ] **Step 3: Viết các Measure Vận hành & CSAT**
  * Tạo Measure **Tỷ lệ giao đúng hạn (On-Time Rate)**:
    ```dax
    On-Time Delivery Rate = 
    VAR TotalDelivered = [Delivered Orders]
    VAR OnTimeOrders = CALCULATE(
        DISTINCTCOUNT(Fact_Orders[order_id]),
        Fact_Orders[order_status] = "delivered",
        Fact_Orders[order_delivered_customer_date] <= Fact_Orders[order_estimated_delivery_date]
    )
    RETURN DIVIDE(OnTimeOrders, TotalDelivered, 0)
    ```
  * Tạo Measure **Tỷ lệ giao trễ (Late Delivery Rate)**:
    ```dax
    Late Delivery Rate = 1 - [On-Time Delivery Rate]
    ```
  * Tạo Measure **CSAT (Review trung bình)**:
    ```dax
    CSAT Score = AVERAGE(Dim_Reviews[review_score])
    ```

---

### Task 3: Thiết kế Giao diện Canvas và KPI Cards

**Files:**
- Canvas Layout: e:\PROJECT\01_Data_Analytics\Operation Analytics\Brazilian Ecommerce\docs\superpowers\specs\2026-06-08-powerbi-dashboard-design.md

- [ ] **Step 1: Thiết lập trang Canvas tông tối**
  * Định dạng kích thước trang: **16:9** (1280x720 hoặc 1920x1080).
  * Định dạng hình nền trang (Page Background): Màu xám/đen tối `#0b0f19`, độ trong suốt (Transparency) = **0%**.
  * Vẽ hình chữ nhật lớn trên cùng để làm dải tiêu đề (Header) và dải bộ lọc (Filters Bar) màu `#111827`.

- [ ] **Step 2: Tạo dải 5 thẻ chỉ số (KPI Cards)**
  * Kéo thả visual **Card (New)** hoặc 5 thẻ Card đơn độc lập.
  * Đặt kích thước nền mỗi card là `#1f2937` với độ trong suốt 30% (tạo hiệu ứng kính).
  * Gán các Measure: `Realized Revenue`, `Delivered Orders`, `AOV`, `On-Time Delivery Rate`, `CSAT Score`.
  * Định dạng màu viền trên của mỗi card:
    - Revenue & On-Time Rate: Xanh lục `#10b981`.
    - Orders: Xanh lam `#06b6d4`.
    - AOV: Tím `#8b5cf6`.
    - CSAT: Vàng `#f59e0b`.
  * Hiển thị tỷ lệ tăng trưởng YoY làm nhãn phụ (Subtitle/Label) nhỏ màu tương ứng dưới con số chính.

---

### Task 4: Tạo các Biểu đồ Bán hàng (Cột trái)

**Files:**
- Visuals: `Realized Revenue`, `Delivered Orders`, `Dim_Products`

- [ ] **Step 1: Tạo biểu đồ xu hướng doanh thu hàng tháng**
  * Kéo thả visual **Area Chart** vào góc trái phía trên.
  * Trục X: `Dim_Date[Month-Year]` hoặc `Fact_Orders[order_purchase_timestamp]` theo tháng.
  * Trục Y: Measure `[Realized Revenue]`.
  * Định dạng đường: Màu Cyan `#06b6d4`, nét vẽ dày 3pt. Phần diện tích dưới đường phủ màu Cyan với độ trong suốt 85% (Gradient Glow).
  * Bật nhãn dữ liệu (Data labels) cho các điểm cao nhất và bật chú thích cho đỉnh tháng 11/2017.

- [ ] **Step 2: Tạo biểu đồ cột ngang Top 10 danh mục**
  * Kéo thả visual **Clustered Bar Chart** (Cột ngang) vào góc trái phía dưới.
  * Trục Y: `Dim_Products[product_category_name]` (Tên tiếng Anh).
  * Trục X: Measure `[Realized Revenue]`.
  * Lọc Top 10 bằng Filter Pane: Chọn lọc loại `Top N`, nhập giá trị `10`, kéo thả Measure `Realized Revenue` làm giá trị lọc.
  * Định dạng màu các thanh: Chuyển màu gradient từ `#06b6d4` (Top 1) sang `#1e1b4b` (Top 10).

---

### Task 5: Tạo các Biểu đồ Vận hành & Giả lập Rủi ro (Cột phải)

**Files:**
- Visuals: `Late Delivery Rate`, `CSAT Score`, `Dim_Sellers`, `Dim_Customers`

- [ ] **Step 1: Tạo bảng nhiệt phân tích Giao trễ theo Bang**
  * Kéo thả visual **Table** hoặc **Matrix** vào góc phải phía trên.
  * Hàng (Rows): `Dim_Customers[customer_state]`.
  * Cột giá trị: `[Late Delivery Rate]`, `[Average Delivery Days]` (viết measure tính trung bình ngày thực tế), và Mức độ rủi ro.
  * Thiết lập Conditional Formatting cho cột `[Late Delivery Rate]`: Màu chữ hoặc màu nền chuyển dần từ xanh lá sang đỏ khi tỷ lệ trễ tăng lên (>15% là đỏ đậm).

- [ ] **Step 2: Tạo khu vực hiển thị Tối ưu hóa và Giả lập Monte Carlo**
  * Kéo thả các thẻ **Multi-row Card** hoặc bảng tĩnh biểu diễn kết quả:
    - Thẻ rủi ro doanh thu tập trung: Giá trị **21.4%** (Tô màu Tím `#8b5cf6`).
    - Thẻ rủi ro giao trễ vi phạm SLA: Giá trị **1.7%** (Tô màu Xanh lá `#10b981`).
  * Trực quan hóa danh sách 10 ngành hàng ưu tiên (BIP Priority) đã lưu trong file `category_optimization_top10.csv` bằng một Matrix table nhỏ hoặc Multi-row Card hiển thị Tên ngành hàng, Doanh thu và Review Score.

---

### Task 6: Tích hợp Bộ lọc và Kiểm thử xác nhận

**Files:**
- Slicers & Interactivity: Toàn bộ Dashboard.

- [ ] **Step 1: Kéo thả các Slicer điều phối**
  * Tạo các visual **Slicer** ngang trên thanh Filter Bar:
    1. Lọc theo Năm/Tháng.
    2. Lọc theo `Dim_Customers[customer_state]`.
    3. Lọc theo `Dim_Sellers[seller_state]`.
    4. Lọc theo `Fact_Order_Payments[payment_type]`.
  * Cấu hình các slicer dưới dạng Dropdown hoặc Tile để tiết kiệm diện tích và có nền tông tối đồng bộ.

- [ ] **Step 2: Xác nhận chéo số liệu (Data Verification)**
  * Chọn bộ lọc "Toàn thời gian", kiểm tra xem:
    - Chỉ số Doanh thu có khớp chính xác với con số **BRL 15,422,462** hay không.
    - Điểm CSAT trung bình có khớp với con số **4.16** hay không.
    - Tỷ lệ giao trễ trung bình có bằng **8.1%** hay không.
  * Bật thử bộ lọc lọc theo bang **AL** (Alagoas) và kiểm tra xem Late Delivery Rate có cập nhật thành **23.9%** hay không.
