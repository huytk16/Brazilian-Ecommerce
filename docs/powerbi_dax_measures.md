# Hướng dẫn Cấu hình Power BI & Công thức DAX - Brazilian E-Commerce

Tài liệu này cung cấp hướng dẫn chi tiết từng bước để cấu hình Nguồn dữ liệu, Mô hình dữ liệu, công thức DAX và thông số trực quan để xây dựng Dashboard **"Midnight Executive"** trong Power BI Desktop.

---

## 1. Kết nối Nguồn Dữ liệu (SQLite Database)

Để đơn giản hóa và tăng tốc độ tải dữ liệu, chúng ta kết nối Power BI trực tiếp tới cơ sở dữ liệu SQLite đã được biên dịch sẵn tại `Data/olist_analytics.db` thay vì phải nạp và thiết lập mối quan hệ từ 9 tệp CSV thô.

### Các bước thực hiện:
1. Mở **Power BI Desktop**.
2. Chọn **Get Data** -> **More...** -> Tìm kiếm **SQLite database** (hoặc sử dụng kết nối ODBC nếu SQLite không hiển thị mặc định).
3. Tại ô kết nối, trỏ đường dẫn tới file database:
   `e:\PROJECT\01_Data_Analytics\Operation Analytics\Brazilian Ecommerce\Data\olist_analytics.db`
4. Trong cửa sổ Navigator, chọn các bảng/view sau để import (Chọn chế độ **Import**):
   * `df_master` (Dữ liệu mức đơn hàng sạch - Dùng cho các KPI tổng quan, xu hướng, địa lý)
   * `item_detail` (Dữ liệu mức mặt hàng sạch - Dùng cho phân tích danh mục, người bán, tối ưu hóa)

---

## 2. Công thức DAX Measures (KPIs & Metrics)

Tạo một bảng ảo tên `_Measures` để quản lý tập trung các công thức DAX:
* Chọn **Home** -> **Enter Data** -> Đặt tên bảng là `_Measures`.
* Click chuột phải vào bảng `_Measures` -> **New Measure** và nhập các công thức sau:

### 2.1. Doanh thu thực tế (Realized Revenue)
```dax
Realized Revenue = SUM(df_master[payment_value])
```
* **Định dạng:** Currency ($ / BRL), 2 chữ số thập phân.

### 2.2. Số đơn hàng thành công (Delivered Orders)
```dax
Delivered Orders = CALCULATE(DISTINCTCOUNT(df_master[order_id]), df_master[order_status] = "delivered")
```
* **Định dạng:** Whole number (1,000s separator).

### 2.3. Giá trị đơn hàng trung bình (AOV)
```dax
AOV = DIVIDE([Realized Revenue], [Delivered Orders], 0)
```
* **Định dạng:** Currency ($ / BRL), 2 chữ số thập phân.

### 2.4. Tỷ lệ giao hàng đúng hạn (On-Time Delivery Rate)
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
* **Định dạng:** Percentage (%), 1 chữ số thập phân.

### 2.5. Tỷ lệ giao hàng trễ (Late Delivery Rate)
```dax
Late Delivery Rate = 1 - [On-Time Delivery Rate]
```
* **Định dạng:** Percentage (%), 1 chữ số thập phân.

### 2.6. Điểm đánh giá CSAT trung bình
```dax
CSAT Score = AVERAGE(df_master[review_score])
```
* **Định dạng:** Decimal number, 2 chữ số thập phân.

### 2.7. Tỷ lệ tăng trưởng doanh thu so với cùng kỳ năm trước (YoY Revenue Growth %)
*(Lưu ý: Để sử dụng các hàm thời gian, cần tạo một bảng Date chuẩn liên kết với `df_master[order_purchase_timestamp]`)*
```dax
YoY Revenue Growth % = 
VAR CurrentRevenue = [Realized Revenue]
VAR PriorRevenue = CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date]))
RETURN 
DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)
```
* **Định dạng:** Percentage (%), 1 chữ số thập phân.

---

## 3. Cấu hình Trực quan hóa (Visuals Styling)

### 3.1. Thiết lập Canvas Chung
* **Page Size:** 16:9 (1280 x 720 Pixels).
* **Page Background:** Màu tối `#0b0f19` (Độ trong suốt 0%).
* **Filter Pane:** Ẩn mặc định để tránh nhiễu thị giác cho Giám đốc.

### 3.2. Cấu hình Thẻ chỉ số (KPI Cards)
Sử dụng visual **Card (New)** để tạo dải 5 chỉ số ngang:
* **Background:** Nền màu `#111827`, độ mờ (Transparency) = 30%.
* **Border:** Viền mỏng màu `rgba(255, 255, 255, 0.08)`.
* **Accent Line:** Kích hoạt tính năng Accent Bar (Thanh viền chỉ báo) ở phía trên mỗi Card:
  * Thẻ Doanh thu & Đúng hạn: Màu xanh lục `#10b981`.
  * Thẻ Đơn hàng: Màu xanh lam `#06b6d4`.
  * Thẻ AOV: Màu tím `#8b5cf6`.
  * Thẻ CSAT Score: Màu vàng cam `#f59e0b`.
* **Sub-labels:** Thêm nhãn phụ nhỏ hiển thị thông tin xu hướng:
  * Dưới Doanh thu: "▲ 22.1% YoY" (Màu xanh lá).
  * Dưới Đúng hạn: "Target SLA: 90.0%" (Màu xám).
  * Dưới CSAT: "8.1% rate 1-star" (Màu đỏ nhạt).

### 3.3. Biểu đồ xu hướng Doanh thu (Monthly Trend Line)
* **Visual:** Area Chart.
* **Trục X:** `df_master[purchase_month]` (Định dạng: `yyyy-MM`).
* **Trục Y:** Measure `[Realized Revenue]`.
* **Đường Line:** Màu Cyan `#06b6d4`, Stroke width: 3pt.
* **Vùng Phủ (Area Fill):** Màu `#06b6d4`, độ trong suốt (Transparency): 85% (Tạo hiệu ứng phát sáng mờ dưới đường).
* **Ghi chú Đỉnh điểm:** Thêm **Anomaly detection** hoặc một **Text Box** chỉ vào đỉnh tháng 11/2017 với nội dung: *"BRL 1.16M - Black Friday Peak"*.

### 3.4. Biểu đồ Top 10 Ngành hàng Doanh thu (Top Categories)
* **Visual:** Clustered Bar Chart (Cột nằm ngang).
* **Trục Y:** `item_detail[product_category_name_english]`.
* **Trục X:** Measure `[Realized Revenue]`.
* **Filters Pane:** Thêm bộ lọc cho visual này: Lọc theo **Top N** -> Nhập **10** -> Kéo thả `Realized Revenue` vào phần By value.
* **Màu sắc các cột:** Thiết lập Conditional Formatting theo thang màu Gradient từ xanh lục nhạt `#22d3ee` (Top 1) chuyển dần về xanh lam tối `#0e7490` (Top 10).

### 3.5. Bảng nhiệt Logistics (Customer State Risk Matrix)
* **Visual:** Table hoặc Matrix.
* **Cột hiển thị:** `df_master[customer_state]`, `[Delivered Orders]`, `[Average Delivery Days]`, `[Late Delivery Rate]`.
* **Định dạng có điều kiện (Conditional Formatting):**
  * Kích hoạt màu nền cho cột `[Late Delivery Rate]`:
    * Dưới 10%: Nền màu lục nhạt (`#10b981` với độ mờ cao).
    * Từ 10% - 15%: Nền màu vàng cam (`#f59e0b` với độ mờ cao).
    * Trên 15%: Nền màu đỏ sẫm (`#ef4444` với độ mờ cao).
  * Sắp xếp bảng theo thứ tự giảm dần của `[Late Delivery Rate]` để các điểm nóng vận hành luôn hiển thị ở trên cùng.

---

## 4. Tích hợp Bộ lọc Tương tác (Slicers Bar)

Đặt một thanh chứa 4 bộ lọc ngang phía dưới tiêu đề chính:
1. **Slicer Thời gian:** Chọn dạng *Between* hoặc *Dropdown* lọc cột `df_master[order_purchase_timestamp]`.
2. **Slicer Bang Khách hàng:** Dropdown lọc cột `df_master[customer_state]`.
3. **Slicer Bang Người bán:** Dropdown lọc cột `item_detail[seller_state]`.
4. **Slicer Hình thức thanh toán:** Dropdown lọc cột `df_master[primary_payment_type]`.

*Đảm bảo tất cả các Slicer được định dạng theo kiểu "Tile" hoặc "Dropdown" với màu nền tối `#1f2937` để hòa hợp với tông màu Midnight Executive chung.*
