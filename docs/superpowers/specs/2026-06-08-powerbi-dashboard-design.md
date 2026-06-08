# Tài liệu Đặc tả Thiết kế Dashboard Power BI Brazilian E-Commerce

Tài liệu đặc tả này trình bày thiết kế chi tiết cho Dashboard Power BI phân tích hoạt động kinh doanh và vận hành thương mại điện tử Olist (Brazil). Dashboard này được thiết kế tối ưu riêng cho đối tượng Giám đốc Kinh doanh (Sales Director) để đưa ra các quyết định chiến lược nhanh chóng.

---

## 1. Tổng quan & Đối tượng sử dụng
* **Đối tượng:** Giám đốc Kinh doanh (Sales Director).
* **Mục tiêu:** Cung cấp bức tranh toàn cảnh tức thời về sức khỏe kinh doanh (Doanh thu, Đơn hàng, Giá trị đơn TB AOV), hiệu quả vận hành chuỗi cung ứng (Tỷ lệ giao hàng đúng hạn, Điểm đánh giá CSAT), kết hợp cùng kết quả từ các mô hình Tối ưu hóa Danh mục và Giả lập Rủi ro Tài chính/Logistics.
* **Tần suất sử dụng:** Hàng ngày/Hàng tuần để họp giao ban điều hành và điều chỉnh chiến lược kinh doanh/vận hành.

---

## 2. Phong cách Thiết kế (Design Theme)
* **Chủ đề (Theme):** **Midnight Executive (Tối cao cấp)**.
  * **Màu nền chủ đạo:** Dark Slate (#0b0f19) và Navy Deep (#111827).
  * **Màu sắc các thẻ thông tin (Card Background):** Dark Grey bán trong suốt (rgba(31, 41, 55, 0.7)), kết hợp hiệu ứng bo viền mờ (glassmorphism) và đổ bóng nổi.
  * **Màu sắc điểm nhấn (Accent Colors):**
    * **Doanh thu & Đúng hạn (Tích cực):** Glowing Emerald (#10b981) - Xanh lục phát sáng.
    * **Đơn hàng & Xu hướng (Công nghệ/Thông tin):** Glowing Cyan (#06b6d4) - Xanh lam sáng.
    * **Giá trị đơn AOV & Phân bổ (Cao cấp):** Violet Bright (#8b5cf6) - Tím sáng.
    * **Cảnh báo rủi ro giao trễ (Cần chú ý):** Amber Gold (#f59e0b) và Rose Red (#ef4444) - Vàng/Đỏ cảnh báo.
  * **Font chữ sử dụng:** **Inter** hoặc **Segoe UI** (font tiêu chuẩn hỗ trợ cực tốt trong Power BI), hiển thị sắc nét trên nền tối.

---

## 3. Cấu trúc Trang & Bố cục (Layout & Grid)
Dashboard được thiết kế trên **Một trang duy nhất (Single-Page Dashboard)** theo cấu trúc **Balanced Grid (Lưới cân bằng)** giúp tối ưu hóa diện tích hiển thị và giảm thiểu thao tác chuyển tab của người điều hành.

Bố cục cụ thể từ trên xuống dưới:
1. **Header Bar (Thanh tiêu đề):** Nằm trên cùng bên trái. Bên phải chứa thẻ phân vai của tài khoản và nút xuất báo cáo.
2. **Filters/Slicers Row (Thanh bộ lọc ngang):** Nằm ngay dưới tiêu đề.
3. **KPI Cards Row (Dải thẻ chỉ số chính):** Gồm 5 thẻ xếp ngang với hiệu ứng viền phát sáng tương ứng với trạng thái chỉ số.
4. **Dashboard Body (Thân Dashboard chia làm 2 cột):**
   * **Cột trái (Kinh doanh):**
     * Biểu đồ xu hướng doanh thu hàng tháng (Line Chart).
     * Biểu đồ đóng góp doanh thu của Top 10 danh mục (Horizontal Bar Chart).
   * **Cột phải (Vận hành & Giả lập Rủi ro):**
     * Bảng nhiệt phân tích rủi ro giao hàng trễ theo bang (Geographical Logistics Hotspots).
     * Bảng danh sách Top 10 danh mục ưu tiên từ mô hình tối ưu hóa tuyến tính BIP.
     * Thẻ hiển thị kết quả giả lập rủi ro Monte Carlo (Revenue Downside Risk & SLA Violation Risk).

---

## 4. Chi tiết các Bộ lọc Tương tác (Interactive Slicers)
Dashboard cung cấp bộ lọc nâng cao giúp Giám đốc Kinh doanh dễ dàng lọc chéo và drill-down:
* **Slicer 1 - Khoảng thời gian (Date Range / Period Slicer):** Bộ chọn khoảng thời gian dạng dropdown hoặc slider từ tháng 09/2016 đến 08/2018. Có các mốc chọn nhanh (Năm 2017, Năm 2018, Đỉnh điểm Black Friday 2017).
* **Slicer 2 - Bang của Khách hàng (Customer State):** Dropdown lọc theo bang của người mua hàng (Ví dụ: SP, RJ, MG, RS, AL...).
* **Slicer 3 - Bang của Người bán (Seller State):** Dropdown lọc theo bang của nhà bán hàng để đánh giá luồng vận chuyển liên bang.
* **Slicer 4 - Phương thức thanh toán (Payment Method):** Dropdown lọc theo Credit Card, Boleto, Voucher, Debit Card.
* **Slicer 5 - Top N Categories:** Cho phép chuyển đổi nhanh giữa xem Top 10 danh mục ưu tiên, Top 5 danh mục doanh thu hoặc Toàn bộ.

---

## 5. Danh sách Chỉ số Chính (KPI Cards Specification)
Mỗi thẻ KPI được thiết kế bo góc, có thanh chỉ báo màu sắc ở viền trên và hiển thị xu hướng tăng trưởng so với kỳ trước (YoY hoặc MoM):

| Thẻ KPI | Chỉ số Hiển thị | Công thức DAX / Mô tả | Chỉ báo Xu hướng (Trend Indicator) | Màu viền trên |
| :--- | :--- | :--- | :--- | :--- |
| **Doanh thu realized** | BRL 15.42M | `SUM(olist_order_payments_dataset[payment_value])` | Tăng **▲ 22.1%** so với năm trước | Emerald Green (#10b981) |
| **Đơn hàng thành công** | 96,478 | `DISTINCTCOUNT(olist_orders_dataset[order_id])` với Status = "delivered" | Tăng **▲ 18.4%** | Cyan Blue (#06b6d4) |
| **AOV (Giá trị đơn TB)** | BRL 160.00 | `[Doanh thu realized] / [Đơn hàng thành công]` | Ổn định (BRL 159.8) | Bright Violet (#8b5cf6) |
| **Giao đúng hạn** | 91.9% | `DIVIDE(CALCULATE([Đơn hàng], olist_orders_dataset[delivered_date] <= olist_orders_dataset[estimated_date]), [Đơn hàng])` | Vượt SLA mục tiêu (SLA: **90.0%**) | Emerald Green (#10b981) |
| **CSAT (Điểm review TB)** | 4.16 / 5.0 | `AVERAGE(olist_order_reviews_dataset[review_score])` | Tốt (Tỷ lệ đánh giá 1 sao: 8.1%) | Amber Gold (#f59e0b) |

---

## 6. Chi tiết các Biểu đồ & Thành phần Trực quan (Visualizations)

### 6.1. Biểu đồ Đường Xu hướng Doanh thu (Monthly Payment Revenue)
* **Loại biểu đồ:** Line and Area Chart (Biểu đồ đường kết hợp vùng phủ gradient phía dưới để tạo chiều sâu).
* **Trục X (Thời gian):** Tháng/Năm (từ 2016-09 đến 2018-08).
* **Trục Y (Doanh thu):** Số tiền thanh toán (BRL).
* **Chú thích đặc biệt (Annotation):** Thêm điểm đánh dấu (Data Point marker) đặc biệt vào tháng 11/2017 để ghi chú: *"BRL 1.16M - Black Friday Peak"*.
* **Mục tiêu:** Giúp Giám đốc Kinh doanh nắm bắt chu kỳ tăng trưởng và tác động của các chương trình khuyến mãi lớn.

### 6.2. Biểu đồ Cột Ngang Top 10 Danh mục Doanh thu (Top 10 Categories by Revenue)
* **Loại biểu đồ:** Clustered Horizontal Bar Chart (Cột ngang xếp chồng hoặc cột ngang đơn).
* **Trục Y (Danh mục):** Tên tiếng Anh của danh mục (sau khi map từ bảng dịch category translation).
* **Trục X (Doanh thu):** Giá trị đơn hàng (BRL Price Revenue).
* **Thứ tự sắp xếp:** Giảm dần từ trên xuống dưới (Bắt đầu từ *health_beauty*, *watches_gifts*, *bed_bath_table*...).
* **Màu sắc:** Sử dụng dải màu chuyển từ Cyan sáng xuống Deep Blue để nhấn mạnh các danh mục dẫn đầu doanh thu.

### 6.3. Bảng phân tích Logistics Địa lý (Geographical Logistics Hotspots Table)
* **Loại biểu đồ:** Matrix Table với tính năng Conditional Formatting (Định dạng có điều kiện).
* **Các cột:** Bang khách hàng (Customer State), Tỷ lệ giao hàng trễ (Late Delivery Rate), Số ngày giao hàng thực tế trung bình (Average Delivery Days), Mức độ rủi ro (Risk Level - badge màu).
* **Quy tắc màu sắc rủi ro:**
    * Tỷ lệ trễ > 15%: Badge màu Đỏ sẫm (Critical - Rất cao). Ví dụ: **AL** (23.9% - 24.3 ngày), **MA** (20.1% - 21.1 ngày).
    * Tỷ lệ trễ từ 10% - 15%: Badge màu Vàng cam (Warning - Trung bình). Ví dụ: **BA** (15.4%), **RJ** (10.2%).
    * Tỷ lệ trễ < 10%: Badge màu Xanh lá (Normal - Bình thường). Ví dụ: **SP** (8.1% - 8.3 ngày).
* **Mục tiêu:** Phát hiện nhanh các điểm nghẽn địa lý để đưa ra chính sách điều phối kho bãi hoặc lựa chọn đơn vị vận chuyển mới.

### 6.4. Kết quả Tối ưu hóa Danh mục Trọng tâm (BIP Priority List)
* **Loại hiển thị:** Card Grid (Mạng lưới thẻ nhỏ).
* **Mô tả:** Trực quan hóa danh sách 10 ngành hàng được chọn bởi mô hình Quy hoạch tuyến tính nguyên (Binary Integer Programming Screen).
* **Tiêu chí tối ưu:** Tối đa hóa `Doanh thu * Điểm review` dưới ràng buộc cước phí vận chuyển trung bình của danh mục `<= BRL 25` và điểm review trung bình `>= 3.5`.
* **Thông tin hiển thị trên mỗi thẻ danh mục:** Thứ hạng ưu tiên, Tên danh mục, Tổng doanh thu đóng góp, và Điểm đánh giá trung bình. (Ví dụ: 1. *health_beauty*: BRL 1.26M, Review: 4.14).

### 6.5. Kết quả Giả lập Rủi ro Vận hành & Tài chính (Monte Carlo Simulation Widgets)
* **Loại hiển thị:** 2 Thẻ rủi ro (Simulated Risk Cards) lớn với màu sắc phân biệt.
* **Thẻ 1 - Rủi ro Doanh thu tập trung (Revenue Downside Risk):** 
  * Hiển thị tỷ lệ **21.4%**. 
  * Định nghĩa: Xác suất doanh thu của chiến lược tập trung Top 5 danh mục bị giảm dưới 20% so với kỳ vọng trung bình (Expected Mean BRL 248.5K/tháng).
* **Thẻ 2 - Rủi ro Vi phạm SLA Giao trễ (SLA Delivery Risk):** 
  * Hiển thị tỷ lệ **1.7%**. 
  * Định nghĩa: Xác suất tỷ lệ đơn hàng giao trễ trung bình của toàn nền tảng vượt ngưỡng giới hạn cho phép 10%. (Kết quả mô phỏng cho thấy rủi ro này cực kỳ thấp, hệ thống logistics vận hành rất ổn định).

---

## 7. Kế hoạch Kiểm thử & Xác nhận (Verification Plan)
Để đảm bảo Dashboard Power BI hoạt động chính xác trước khi bàn giao cho Giám đốc Kinh doanh:
1. **Kiểm tra Đối chiếu Dữ liệu (Data Reconciliation):** So khớp tổng doanh thu realized hiển thị trên dashboard với kết quả chạy từ file phân tích python `Scripts/olist_operations_analysis.py` (BRL 15,422,462).
2. **Kiểm thử Tương tác Lọc chéo (Cross-filtering Test):** Đảm bảo khi người dùng click chọn một Bang trên bảng nhiệt Logistics, các thẻ KPI và biểu đồ doanh thu tự động lọc dữ liệu của bang đó.
3. **Kiểm thử hiệu năng (Performance Analyzer):** Đảm bảo các biểu đồ và thẻ KPI tải xong dưới 2 giây bằng cách tối ưu hóa các DAX Measure (tránh dùng các hàm lặp lồng nhau hoặc tính toán trực tiếp trên cột thô mà không thông qua bảng Dimension).
4. **Kiểm tra tính tương thích Responsive:** Dashboard phải hiển thị rõ ràng trên màn hình máy tính làm việc chuẩn (Full HD 1920x1080) và chế độ xem trên máy tính bảng (Tablet View) phục vụ nhu cầu di chuyển của Giám đốc.

---

## 8. Hướng dẫn Triển khai & Các bước tiếp theo
1. **Chuẩn bị Dữ liệu (ETL Layer):** Load dữ liệu từ các file CSV trong thư mục `Data/` vào Power Query. Tiến hành chuẩn hóa định dạng ngày tháng và xử lý giá trị null.
2. **Thiết lập Mô hình Dữ liệu (Data Model - Star Schema):**
   * **Bảng Fact:** `Fact_Orders` (chứa khóa ngoại kết nối khách hàng, người bán, ngày mua).
   * **Bảng Dimension:** `Dim_Customers`, `Dim_Sellers`, `Dim_Products` (đã map tên danh mục tiếng Anh), `Dim_Date`, `Dim_Reviews`.
3. **Tạo các DAX Measure:** Tạo thư mục `_Measures` riêng biệt và viết công thức DAX cho Doanh thu, Số đơn hàng, AOV, Điểm CSAT, Tỷ lệ giao hàng đúng hạn, Tỷ lệ giao trễ và các phép so sánh YoY.
4. **Thiết kế giao diện UI/UX:** Tạo hình nền (Background template) tông tối Midnight Executive bằng Figma hoặc Power BI Shape, sau đó kéo thả các visual và căn chỉnh tọa độ Pixel chính xác.
