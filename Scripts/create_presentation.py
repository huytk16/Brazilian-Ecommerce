#!/usr/bin/env python3
"""
Generate PowerPoint Presentation (.pptx) representing the
Power BI Dashboard Midnight Executive design and specifications.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Color definitions
BG_COLOR = RGBColor(11, 15, 25)       # #0b0f19
CARD_COLOR = RGBColor(17, 24, 39)     # #111827
BORDER_COLOR = RGBColor(31, 41, 55)   # #1f2937
TEXT_WHITE = RGBColor(248, 250, 252)  # #f8fafc
TEXT_MUTED = RGBColor(148, 163, 184)  # #94a3b8
ACCENT_CYAN = RGBColor(6, 182, 212)   # #06b6d4
ACCENT_EMERALD = RGBColor(16, 185, 129) # #10b981
ACCENT_VIOLET = RGBColor(139, 92, 246) # #8b5cf6
ACCENT_AMBER = RGBColor(245, 158, 11)  # #f59e0b
ACCENT_ROSE = RGBColor(239, 68, 68)   # #ef4444

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, title_text, badge_text="SALES DIRECTOR PANEL"):
    # Title box
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8), Inches(0.6))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.font.name = 'Segoe UI'

    # Badge box
    badge_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.5), Inches(0.4), Inches(2.3), Inches(0.35))
    badge_shape.fill.solid()
    badge_shape.fill.fore_color.rgb = RGBColor(6, 45, 60) # dark cyan glow background
    badge_shape.line.color.rgb = ACCENT_CYAN
    badge_shape.line.width = Pt(1)
    
    tf_b = badge_shape.text_frame
    tf_b.word_wrap = False
    p_b = tf_b.paragraphs[0]
    p_b.text = badge_text
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(8.5)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_CYAN
    p_b.font.name = 'Segoe UI'

def create_card(slide, left, top, width, height, title, value, subtext="", accent_color=None):
    # Main rounded card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_COLOR
    card.line.color.rgb = BORDER_COLOR
    card.line.width = Pt(1)
    
    # Accent top border
    if accent_color:
        accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.06))
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = accent_color
        accent_bar.line.fill.background()

    # Text content
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.15)
    tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.12)
    tf.margin_bottom = Inches(0.1)
    
    # Title
    p1 = tf.paragraphs[0]
    p1.text = title.upper()
    p1.font.size = Pt(8)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MUTED
    p1.font.name = 'Segoe UI'
    
    # Value
    p2 = tf.add_paragraph()
    p2.text = value
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.font.name = 'Segoe UI'
    
    # Subtext
    if subtext:
        p3 = tf.add_paragraph()
        p3.text = subtext
        p3.font.size = Pt(7.5)
        p3.font.color.rgb = accent_color if accent_color else TEXT_MUTED
        p3.font.name = 'Segoe UI'

def add_bullet_slide(prs, title, bullets):
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    set_slide_background(slide)
    add_header(slide, title)
    
    # Text Box for content
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.1), Inches(12.33), Inches(5.8))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    first = True
    for bullet in bullets:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        
        # Determine indentation
        if bullet.startswith('  * '):
            p.text = bullet[4:]
            p.level = 1
            p.font.size = Pt(13)
            p.font.color.rgb = TEXT_MUTED
        elif bullet.startswith('    - '):
            p.text = bullet[6:]
            p.level = 2
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MUTED
        else:
            p.text = bullet
            p.level = 0
            p.font.size = Pt(15)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p.space_before = Pt(8)
            
        p.font.name = 'Segoe UI'

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # ==================== SLIDE 1: DASHBOARD MOCKUP ====================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)
    add_header(slide1, "Olist E-Commerce - Dashboard Mockup Grid")
    
    # 1. Slicers Row Mock
    slicer_bar = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.0), Inches(12.33), Inches(0.6))
    slicer_bar.fill.solid()
    slicer_bar.fill.fore_color.rgb = CARD_COLOR
    slicer_bar.line.color.rgb = BORDER_COLOR
    slicer_bar.line.width = Pt(1)
    
    tf_s = slicer_bar.text_frame
    tf_s.word_wrap = False
    p_s = tf_s.paragraphs[0]
    p_s.text = " 📅 Date Range: 2016-09 - 2018-08    |    📍 Customer State: All    |    🏬 Seller State: All    |    💳 Payment Type: All"
    p_s.font.size = Pt(9)
    p_s.font.color.rgb = TEXT_MUTED
    p_s.font.name = 'Segoe UI'
    
    # 2. KPI Cards (5 Cards)
    kpi_width = Inches(2.3)
    kpi_height = Inches(1.1)
    kpi_gap = Inches(0.207)
    kpi_y = Inches(1.8)
    
    create_card(slide1, Inches(0.5) + 0 * (kpi_width + kpi_gap), kpi_y, kpi_width, kpi_height, "Doanh thu Realized", "BRL 15.42M", "▲ 22.1% YoY", ACCENT_EMERALD)
    create_card(slide1, Inches(0.5) + 1 * (kpi_width + kpi_gap), kpi_y, kpi_width, kpi_height, "Đơn hàng Delivered", "96,478", "▲ 18.4% YoY", ACCENT_CYAN)
    create_card(slide1, Inches(0.5) + 2 * (kpi_width + kpi_gap), kpi_y, kpi_width, kpi_height, "AOV (Giá trị đơn TB)", "BRL 160.00", "● Ổn định (BRL 159.8)", ACCENT_VIOLET)
    create_card(slide1, Inches(0.5) + 3 * (kpi_width + kpi_gap), kpi_y, kpi_width, kpi_height, "Giao hàng đúng hạn", "91.9%", "▲ Vượt SLA Target (90%)", ACCENT_EMERALD)
    create_card(slide1, Inches(0.5) + 4 * (kpi_width + kpi_gap), kpi_y, kpi_width, kpi_height, "CSAT (Review TB)", "4.16 / 5.0", "★ 8.1% đánh giá 1 sao", ACCENT_AMBER)
    
    # 3. Main body Layout (4 Large Widgets)
    widget_width = Inches(6.06)
    widget_height = Inches(1.9)
    
    # Left Column: Charts
    # Chart 1: Revenue Monthly Trend
    chart1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(3.1), widget_width, widget_height)
    chart1.fill.solid()
    chart1.fill.fore_color.rgb = CARD_COLOR
    chart1.line.color.rgb = BORDER_COLOR
    chart1.line.width = Pt(1)
    tf1 = chart1.text_frame
    tf1.margin_left = Inches(0.15)
    tf1.margin_top = Inches(0.15)
    p_c1 = tf1.paragraphs[0]
    p_c1.text = "📈 XU HƯỚNG DOANH THU HÀNG THÁNG (Area Chart Glow)"
    p_c1.font.bold = True
    p_c1.font.size = Pt(9)
    p_c1.font.color.rgb = ACCENT_CYAN
    p_c1.font.name = 'Segoe UI'
    
    p_c1_sub = tf1.add_paragraph()
    p_c1_sub.text = "\n[Biểu đồ vùng có hiệu ứng phát sáng mờ]\n- Trục X: purchase_month\n- Trục Y: Realized Revenue\n- Ghi chú: Cột mốc Black Friday 11/2017 đạt BRL 1.16M"
    p_c1_sub.font.size = Pt(8.5)
    p_c1_sub.font.color.rgb = TEXT_MUTED
    p_c1_sub.font.name = 'Segoe UI'

    # Chart 2: Top Categories Bar Chart
    chart2 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(5.15), widget_width, widget_height)
    chart2.fill.solid()
    chart2.fill.fore_color.rgb = CARD_COLOR
    chart2.line.color.rgb = BORDER_COLOR
    chart2.line.width = Pt(1)
    tf2 = chart2.text_frame
    tf2.margin_left = Inches(0.15)
    tf2.margin_top = Inches(0.15)
    p_c2 = tf2.paragraphs[0]
    p_c2.text = "📊 TOP 10 DANH MỤC DOANH THU LỚN NHẤT (Horizontal Bar Chart)"
    p_c2.font.bold = True
    p_c2.font.size = Pt(9)
    p_c2.font.color.rgb = ACCENT_VIOLET
    p_c2.font.name = 'Segoe UI'
    
    p_c2_sub = tf2.add_paragraph()
    p_c2_sub.text = "\n[Cột ngang được tô màu Gradient theo thứ hạng]\n- Trục Y: product_category_name_english\n- Trục X: item_price_revenue\n- Dẫn đầu: health_beauty (BRL 1.26M) và watches_gifts (BRL 1.20M)"
    p_c2_sub.font.size = Pt(8.5)
    p_c2_sub.font.color.rgb = TEXT_MUTED
    p_c2_sub.font.name = 'Segoe UI'

    # Right Column: Operations and Simulations
    # Chart 3: Logistics State Heat Table
    chart3 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.76), Inches(3.1), widget_width, widget_height)
    chart3.fill.solid()
    chart3.fill.fore_color.rgb = CARD_COLOR
    chart3.line.color.rgb = BORDER_COLOR
    chart3.line.width = Pt(1)
    tf3 = chart3.text_frame
    tf3.margin_left = Inches(0.15)
    tf3.margin_top = Inches(0.15)
    p_c3 = tf3.paragraphs[0]
    p_c3.text = "🗺️ BẢNG NHIỆT RỦI RO GIAO HÀNG TRỄ THEO BANG (Logistics Hotspots)"
    p_c3.font.bold = True
    p_c3.font.size = Pt(9)
    p_c3.font.color.rgb = ACCENT_AMBER
    p_c3.font.name = 'Segoe UI'
    
    p_c3_sub = tf3.add_paragraph()
    p_c3_sub.text = "\n[Bảng ma trận với conditional formatting đỏ/vàng/xanh]\n- Hotspots: AL (Trễ 23.9% - 24 ngày), MA (Trễ 20.1% - 21 ngày)\n- Normal: SP (Trễ 8.1% - 8.3 ngày)\n- Giúp định hướng tối ưu hóa logistics và kho bãi"
    p_c3_sub.font.size = Pt(8.5)
    p_c3_sub.font.color.rgb = TEXT_MUTED
    p_c3_sub.font.name = 'Segoe UI'

    # Chart 4: BIP Optimization & Monte Carlo Simulations
    chart4 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.76), Inches(5.15), widget_width, widget_height)
    chart4.fill.solid()
    chart4.fill.fore_color.rgb = CARD_COLOR
    chart4.line.color.rgb = BORDER_COLOR
    chart4.line.width = Pt(1)
    tf4 = chart4.text_frame
    tf4.margin_left = Inches(0.15)
    tf4.margin_top = Inches(0.15)
    p_c4 = tf4.paragraphs[0]
    p_c4.text = "🎲 KẾT QUẢ GIẢ LẬP RỦI RO & TỐI ƯU HÓA DANH MỤC (BIP & Monte Carlo)"
    p_c4.font.bold = True
    p_c4.font.size = Pt(9)
    p_c4.font.color.rgb = ACCENT_EMERALD
    p_c4.font.name = 'Segoe UI'
    
    p_c4_sub = tf4.add_paragraph()
    p_c4_sub.text = "\n- Quy hoạch nguyên (BIP): Chọn Top 10 danh mục trọng tâm (cước <= 25, review >= 3.5)\n- Giả lập Monte Carlo (N=1,000):\n  * Rủi ro doanh thu giảm >20%: 21.4% (Expected monthly mean: BRL 248.5K)\n  * Rủi ro giao trễ vi phạm SLA (>10% trễ): cực thấp (1.7%)"
    p_c4_sub.font.size = Pt(8.5)
    p_c4_sub.font.color.rgb = TEXT_MUTED
    p_c4_sub.font.name = 'Segoe UI'


    # ==================== SLIDE 2: THEME & LAYOUT SPECS ====================
    add_bullet_slide(prs, "1. Phong cách & Bố cục (Theme & Layout Specs)", [
        "Phong cách thiết kế: Midnight Executive (Tối cao cấp)",
        "  * Tông màu nền chủ đạo: Dark Slate (#0b0f19) và Navy Deep (#111827).",
        "  * Thẻ thông tin và Biểu đồ: Dark Grey bán trong suốt (rgba(31, 41, 55, 0.7)), bo góc mượt mà.",
        "  * Màu sắc điểm nhấn chức năng:",
        "    - Xanh lục (#10b981): Biểu diễn tăng trưởng doanh thu, vận hành an toàn và vượt mục tiêu SLA.",
        "    - Xanh lam (#06b6d4): Thể hiện dữ liệu đơn hàng và xu hướng công nghệ.",
        "    - Màu tím (#8b5cf6): Dành cho Giá trị đơn hàng trung bình (AOV).",
        "    - Màu vàng cam (#f59e0b) và Đỏ (#ef4444): Nhấn mạnh cảnh báo rủi ro logistics giao hàng muộn.",
        "Cấu trúc trang: Single-Page (Một trang duy nhất)",
        "  * Bố cục lưới cân bằng (Balanced Grid) tối ưu hóa kích thước màn hình 16:9.",
        "  * Sắp xếp thông tin có cấu trúc: Bộ lọc -> KPIs -> Bán hàng (Trái) & Vận hành/Rủi ro (Phải).",
        "  * Hạn chế tối đa cuộn trang hoặc chuyển đổi tab để giúp ban điều hành nắm bắt toàn cảnh nhanh nhất."
    ])


    # ==================== SLIDE 3: KPIs & DAX MEASURES ====================
    add_bullet_slide(prs, "2. Công thức DAX Measures cốt lõi", [
        "Nhóm chỉ số kinh doanh",
        "  * Doanh thu thực tế (Realized Revenue):",
        "    - DAX: Realized Revenue = SUM(df_master[payment_value])",
        "  * Số đơn hàng thành công (Delivered Orders):",
        "    - DAX: Delivered Orders = CALCULATE(DISTINCTCOUNT(df_master[order_id]), df_master[order_status] = \"delivered\")",
        "  * Giá trị đơn hàng trung bình (AOV):",
        "    - DAX: AOV = DIVIDE([Realized Revenue], [Delivered Orders], 0)",
        "Nhóm chỉ số Vận hành & CSAT",
        "  * Tỷ lệ giao hàng đúng hạn (On-Time Rate):",
        "    - DAX: On-Time Delivery Rate = DIVIDE(CALCULATE(DISTINCTCOUNT(df_master[order_id]), df_master[order_status] = \"delivered\", df_master[late_flag] = 0), [Delivered Orders], 0)",
        "  * Điểm đánh giá chất lượng (CSAT Score):",
        "    - DAX: CSAT Score = AVERAGE(df_master[review_score])",
        "  * Tăng trưởng so với cùng kỳ năm trước (YoY Growth %):",
        "    - DAX: YoY Revenue Growth % = DIVIDE([Realized Revenue] - CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date])), CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date])), 0)"
    ])


    # ==================== SLIDE 4: DATA MODELING & ETL ====================
    add_bullet_slide(prs, "3. Chuẩn bị Dữ liệu & Mô hình hình sao (Star Schema)", [
        "Kết nối CSDL SQLite phụ trợ (olist_analytics.db)",
        "  * Thay vì nạp 9 tệp CSV rời rạc, nạp trực tiếp database để cải thiện hiệu năng tải trang.",
        "  * Import view df_master làm Fact Table chính (chứa dữ liệu đơn hàng, thanh toán, ngày giao).",
        "  * Import view item_detail làm Fact/Dimension phụ (cho phân tích danh mục, sản phẩm, cước vận chuyển).",
        "Thiết lập bảng lịch Dim_Date bằng DAX",
        "  * Tạo bảng mới: Dim_Date = ADDCOLUMNS(CALENDAR(MIN(df_master[order_purchase_timestamp]), MAX(df_master[order_purchase_timestamp])), \"Year\", YEAR([Date]), \"Month Number\", MONTH([Date]), \"Month Short\", FORMAT([Date], \"MMM\"), \"Month-Year Number\", YEAR([Date]) * 100 + MONTH([Date]), \"Month-Year\", FORMAT([Date], \"YYYY-MM\"))",
        "  * Sắp xếp cột chữ theo số (Sort by Column) để hiển thị biểu đồ đúng thứ tự thời gian (Ví dụ: Month Short sắp xếp theo Month Number).",
        "Thiết lập các mối quan hệ (Relationships)",
        "  * Quan hệ 1-nhiều (1:*) từ Dim_Date[Date] đến df_master[order_purchase_timestamp].",
        "  * Quan hệ 1-nhiều (1:*) từ df_master[order_id] đến item_detail[order_id]."
    ])


    # ==================== SLIDE 5: LOGISTICS & RISK INSIGHTS ====================
    add_bullet_slide(prs, "4. Nhận diện Rủi ro & Tối ưu hóa", [
        "Điểm nóng Logistics (Geographical Hotspots)",
        "  * Bang Alagoas (AL) và Maranhão (MA) có tỷ lệ giao trễ cực kỳ cao: AL (23.9% trễ, 24.3 ngày giao trung bình); MA (20.1% trễ, 21.1 ngày giao trung bình).",
        "  * Định hướng hành động: Cần làm việc lại với đơn vị vận chuyển đối tác tại vùng Đông Bắc hoặc cân nhắc kho phân phối vệ tinh.",
        "Mô hình Tối ưu hóa ưu tiên danh mục (BIP Screen)",
        "  * Danh sách 10 danh mục trọng tâm được chọn để tối đa hóa doanh thu và đánh giá review với ràng buộc cước phí trung bình <= 25 BRL và review >= 3.5.",
        "  * Hàng đầu: health_beauty (BRL 1.26M), watches_gifts (BRL 1.20M), bed_bath_table (BRL 1.04M).",
        "Giả lập Rủi ro Monte Carlo",
        "  * Rủi ro doanh thu tập trung: Có 21.4% xác suất doanh thu hàng tháng của nhóm danh mục ưu tiên sụt giảm quá 20% so với trung bình kỳ vọng (Expected Mean BRL 248.5K).",
        "  * Rủi ro vi phạm SLA: Chỉ có 1.7% xác suất tỷ lệ giao trễ toàn sàn vượt quá 10%, cho thấy hệ thống vận hành nền tảng rất ổn định."
    ])

    # Ensure output directory exists
    output_path = os.path.join(base_dir, 'Outputs', 'reports', 'Olist_PowerBI_Dashboard_Specification.pptx')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save presentation
    prs.save(output_path)
    print(f"Presentation saved successfully at: {output_path}")

if __name__ == '__main__':
    main()
