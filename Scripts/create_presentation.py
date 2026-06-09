#!/usr/bin/env python3
"""
Generate PowerPoint Presentation (.pptx) representing the
Power BI Dashboard Midnight Executive design and specifications.

Canvas  : 4:3  →  10" × 7.5"  (standard PowerPoint 4:3)
Layout mirrors dashboard-design.html:
  - Slide 1: Full-page dashboard mockup
      Row 1  : Header  (title + badge)            ~7% height
      Row 2  : Slicers bar (full width)            ~8% height
      Row 3  : 5 KPI cards                        ~16% height
      Row 4+ : Body grid  left(1.1fr) | right(0.9fr)  ~65% height
               Left  : 2 chart cards (50/50 split)
               Right : 3 cards (40 / 35 / 25 split)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ── Canvas (4:3) ─────────────────────────────────────────────────────────────
SLIDE_W = Inches(10.0)
SLIDE_H = Inches(7.5)

# ── Color palette ─────────────────────────────────────────────────────────────
BG_COLOR       = RGBColor(11,  15,  25)   # #0b0f19
CARD_COLOR     = RGBColor(17,  24,  39)   # #111827
BORDER_COLOR   = RGBColor(31,  41,  55)   # #1f2937
TEXT_WHITE     = RGBColor(248, 250, 252)  # #f8fafc
TEXT_MUTED     = RGBColor(148, 163, 184)  # #94a3b8
ACCENT_CYAN    = RGBColor(6,   182, 212)  # #06b6d4
ACCENT_EMERALD = RGBColor(16,  185, 129)  # #10b981
ACCENT_VIOLET  = RGBColor(139, 92,  246)  # #8b5cf6
ACCENT_AMBER   = RGBColor(245, 158, 11)   # #f59e0b
ACCENT_ROSE    = RGBColor(239, 68,  68)   # #ef4444


# ── Helpers ───────────────────────────────────────────────────────────────────
def set_slide_background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR


def set_shape_corner_radius(shape, radius_pct: int = 8):
    sp = shape._element
    prstGeom = sp.find(qn("a:prstGeom"), sp.nsmap)
    if prstGeom is None:
        return
    avLst = prstGeom.find(qn("a:avLst"), sp.nsmap)
    if avLst is None:
        avLst = etree.SubElement(prstGeom, qn("a:avLst"))
    for gd in avLst.findall(qn("a:gd")):
        avLst.remove(gd)
    adj_val = max(0, min(50000, int(radius_pct * 500)))
    gd = etree.SubElement(avLst, qn("a:gd"))
    gd.set("name", "adj")
    gd.set("fmla", f"val {adj_val}")


def add_rounded_card(slide, left, top, width, height,
                     fill_color=None, border_color=None, corner_pct=8):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color or CARD_COLOR
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    set_shape_corner_radius(shape, corner_pct)
    return shape


def add_text(tf, text, size_pt, bold=False, color=None, align=None, space_before_pt=0):
    if tf.paragraphs and tf.paragraphs[-1].text == "":
        p = tf.paragraphs[-1]
    else:
        p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(size_pt)
    p.font.bold = bold
    p.font.color.rgb = color or TEXT_WHITE
    p.font.name = "Segoe UI"
    if align:
        p.alignment = align
    if space_before_pt:
        p.space_before = Pt(space_before_pt)
    return p


# ── Section: Header ───────────────────────────────────────────────────────────
def add_header(slide, title_text, badge_text="SALES DIRECTOR PANEL"):
    """Header: title left, badge pill right.  Top row ~0.50"."""
    # Title textbox
    tb = slide.shapes.add_textbox(Inches(0.35), Inches(0.14), Inches(7.0), Inches(0.42))
    tb.text_frame.word_wrap = False
    p = tb.text_frame.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.font.name = "Segoe UI"

    # Badge pill
    bw, bh = Inches(2.0), Inches(0.28)
    badge = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        SLIDE_W - bw - Inches(0.35), Inches(0.17), bw, bh
    )
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(6, 45, 60)
    badge.line.color.rgb = ACCENT_CYAN
    badge.line.width = Pt(0.75)
    set_shape_corner_radius(badge, 50)
    tf = badge.text_frame
    tf.word_wrap = False
    p_b = tf.paragraphs[0]
    p_b.text = badge_text
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(7)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_CYAN
    p_b.font.name = "Segoe UI"


# ── Section: Slicers bar ──────────────────────────────────────────────────────
def add_slicers(slide, left, top, width, height):
    """Single pill-shaped slicers bar with 4 filter labels."""
    card = add_rounded_card(slide, left, top, width, height,
                            fill_color=CARD_COLOR, border_color=BORDER_COLOR,
                            corner_pct=8)
    tf = card.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = ("  📅 Khoảng t.gian: 2016-09 – 2018-08    |    "
              "📍 Bang KH: All    |    🏬 Bang Người bán: All    |    🏆 Top N: Top 10")
    p.font.size = Pt(8)
    p.font.color.rgb = TEXT_MUTED
    p.font.name = "Segoe UI"
    tf.margin_top = Inches(0.10)
    tf.margin_left = Inches(0.12)


# ── Section: KPI cards ────────────────────────────────────────────────────────
def create_kpi_card(slide, left, top, width, height,
                    label, value, trend_text, accent_color):
    """KPI card with 3-pt accent top bar, label / value / trend."""
    add_rounded_card(slide, left, top, width, height,
                     fill_color=CARD_COLOR, border_color=BORDER_COLOR, corner_pct=8)
    # Accent strip
    strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    strip.fill.solid()
    strip.fill.fore_color.rgb = accent_color
    strip.line.fill.background()

    # Text
    pad_x, pad_top = Inches(0.12), Inches(0.10)
    tb = slide.shapes.add_textbox(
        left + pad_x, top + pad_top,
        width - 2 * pad_x, height - pad_top - Inches(0.08)
    )
    tf = tb.text_frame
    tf.word_wrap = True

    p1 = tf.paragraphs[0]
    p1.text = label.upper()
    p1.font.size = Pt(7)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MUTED
    p1.font.name = "Segoe UI"

    p2 = tf.add_paragraph()
    p2.text = value
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.font.name = "Segoe UI"

    p3 = tf.add_paragraph()
    p3.text = trend_text
    p3.font.size = Pt(6.5)
    p3.font.color.rgb = accent_color
    p3.font.name = "Segoe UI"


# ── Section: Widget cards ─────────────────────────────────────────────────────
def add_widget_card(slide, left, top, width, height,
                    icon_title, accent_color, body_lines):
    """Large chart/table widget card with header + body text."""
    add_rounded_card(slide, left, top, width, height,
                     fill_color=CARD_COLOR, border_color=BORDER_COLOR, corner_pct=7)

    pad_x, pad_top = Inches(0.13), Inches(0.11)
    tb = slide.shapes.add_textbox(
        left + pad_x, top + pad_top,
        width - 2 * pad_x, height - pad_top - Inches(0.10)
    )
    tf = tb.text_frame
    tf.word_wrap = True

    # Header title
    p0 = tf.paragraphs[0]
    p0.text = icon_title
    p0.font.size = Pt(8)
    p0.font.bold = True
    p0.font.color.rgb = accent_color
    p0.font.name = "Segoe UI"

    # Separator line
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left + pad_x, top + Inches(0.32),
        width - 2 * pad_x, Pt(0.5)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = BORDER_COLOR
    sep.line.fill.background()

    # Body
    for (txt, sz, bold, clr) in body_lines:
        p = tf.add_paragraph()
        p.text = txt
        p.font.size = Pt(sz)
        p.font.bold = bold
        p.font.color.rgb = clr or TEXT_MUTED
        p.font.name = "Segoe UI"


# ── Section: Bullet/spec slide ────────────────────────────────────────────────
def add_bullet_slide(prs, title, bullets):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide)
    add_header(slide, title)

    # Content textbox fills the remaining area
    tb = slide.shapes.add_textbox(Inches(0.38), Inches(0.82), Inches(9.24), Inches(6.35))
    tf = tb.text_frame
    tf.word_wrap = True

    first = True
    for bullet in bullets:
        if first:
            p = tf.paragraphs[0]; first = False
        else:
            p = tf.add_paragraph()

        if bullet.startswith("    - "):
            p.text = bullet[6:]
            p.level = 2
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_MUTED
        elif bullet.startswith("  * "):
            p.text = bullet[4:]
            p.level = 1
            p.font.size = Pt(11.5)
            p.font.color.rgb = TEXT_MUTED
        else:
            p.text = bullet
            p.level = 0
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            p.space_before = Pt(7)

        p.font.name = "Segoe UI"


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir   = os.path.dirname(script_dir)

    prs = Presentation()
    prs.slide_width  = SLIDE_W   # 10"
    prs.slide_height = SLIDE_H   # 7.5"

    # ── Layout constants ──────────────────────────────────────────────────────
    M   = Inches(0.32)           # outer margin (left/right)
    GAP = Inches(0.14)           # small gap between cards

    INNER_W = SLIDE_W - 2 * M   # 9.36"

    # Row tops / heights  (fraction of 7.5")
    #   Header   : top=0,       h=0.50"
    #   Slicers  : top=0.52",   h=0.44"
    #   KPI row  : top=1.00",   h=1.10"
    #   Body     : top=2.14",   bot=7.26"  → h=5.12"
    HDR_TOP  = Inches(0.00)
    HDR_H    = Inches(0.50)

    SLC_TOP  = Inches(0.52)
    SLC_H    = Inches(0.44)

    KPI_TOP  = Inches(1.00)
    KPI_H    = Inches(1.10)

    BODY_TOP = Inches(2.14)
    BODY_BOT = Inches(7.26)
    BODY_H   = BODY_BOT - BODY_TOP   # 5.12"

    # Body columns  (1.1 : 0.9 from HTML .db-body grid)
    COL_GAP  = Inches(0.16)
    LEFT_RATIO = 1.1 / 2.0
    LEFT_W  = INNER_W * LEFT_RATIO  - COL_GAP / 2   # ~5.01"
    RIGHT_W = INNER_W * (1 - LEFT_RATIO) - COL_GAP / 2  # ~4.07"
    LEFT_X  = M
    RIGHT_X = M + LEFT_W + COL_GAP

    ROW_GAP = Inches(0.13)

    # ══════════════════════════════════════════════════════════
    # SLIDE 1 — Dashboard Mockup (4:3)
    # ══════════════════════════════════════════════════════════
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(slide1)
    add_header(slide1, "Olist E-Commerce – Power BI Dashboard Mockup")

    # ── Slicers bar ───────────────────────────────────────────────────────────
    add_slicers(slide1, M, SLC_TOP, INNER_W, SLC_H)

    # ── 5 KPI cards ───────────────────────────────────────────────────────────
    n_kpi = 5
    kpi_w = (INNER_W - (n_kpi - 1) * GAP) / n_kpi
    kpis = [
        ("Doanh thu Realized",   "BRL 15.42M", "▲ 22.1% YoY",          ACCENT_EMERALD),
        ("Đơn hàng Delivered",   "96,478",     "▲ 18.4% YoY",          ACCENT_CYAN),
        ("AOV (Giá trị đơn TB)", "BRL 160.00", "● Ổn định (BRL 159.8)", ACCENT_VIOLET),
        ("Giao hàng đúng hạn",   "91.9%",      "▲ Vượt SLA (90%)",     ACCENT_EMERALD),
        ("CSAT (Review TB)",     "4.16 / 5.0", "★ 8.1% đánh giá 1 sao",ACCENT_AMBER),
    ]
    for i, (lbl, val, trnd, clr) in enumerate(kpis):
        create_kpi_card(
            slide1,
            M + i * (kpi_w + GAP), KPI_TOP, kpi_w, KPI_H,
            lbl, val, trnd, clr
        )

    # ── LEFT COLUMN: 2 chart cards (50/50 split) ──────────────────────────────
    left_card_h = (BODY_H - ROW_GAP) / 2   # ~2.50"

    # Card L1 – Revenue Trend (matches .db-card → chart-container min-height:220px)
    add_widget_card(
        slide1, LEFT_X, BODY_TOP, LEFT_W, left_card_h,
        "📈 XU HƯỚNG DOANH THU HÀNG THÁNG (Area Chart Glow)", ACCENT_CYAN,
        [
            ("", 2.5, False, TEXT_MUTED),
            ("[Biểu đồ vùng – Area Chart với hiệu ứng glow]", 8, False, TEXT_MUTED),
            ("  Trục X: purchase_month  (Dim_Date[Month-Year])", 7.5, False, TEXT_MUTED),
            ("  Trục Y: Realized Revenue (BRL)", 7.5, False, TEXT_MUTED),
            ("  Đỉnh điểm: Black Friday 11/2017  →  BRL 1.16M", 7.5, True, ACCENT_AMBER),
            ("  Gam màu: #06b6d4 vùng gradient fade-out", 7.5, False, TEXT_MUTED),
            ("", 2, False, TEXT_MUTED),
            ("  Trục X: Q3'16  Q1'17  Q3'17  Q1'18  Q3'18", 7, False, TEXT_MUTED),
            ("  Trục Y: 0 → 500K → 1.0M → 1.5M (BRL)", 7, False, TEXT_MUTED),
        ]
    )

    # Card L2 – Top 10 Categories Horizontal Bar
    add_widget_card(
        slide1, LEFT_X, BODY_TOP + left_card_h + ROW_GAP, LEFT_W, left_card_h,
        "📊 TOP 10 DANH MỤC SẢN PHẨM DOANH THU CAO NHẤT (Horizontal Bar)", ACCENT_VIOLET,
        [
            ("", 2.5, False, TEXT_MUTED),
            ("[Biểu đồ cột ngang – Gradient tô màu theo thứ hạng]", 8, False, TEXT_MUTED),
            ("  Trục Y: product_category_name_english", 7.5, False, TEXT_MUTED),
            ("  Trục X: item_price_revenue (BRL)", 7.5, False, TEXT_MUTED),
            ("", 1.5, False, TEXT_MUTED),
            ("  #1  health_beauty   →  BRL 1.26M  (Review: 4.14)", 7.5, True,  TEXT_WHITE),
            ("  #2  watches_gifts   →  BRL 1.20M  (Review: 4.02)", 7.5, False, TEXT_MUTED),
            ("  #3  bed_bath_table  →  BRL 1.04M  (Review: 3.89)", 7.5, False, TEXT_MUTED),
            ("  #4  sports_leisure  →  BRL 0.99M  (Review: 4.11)", 7.5, False, TEXT_MUTED),
            ("  #5  computers_acc   →  BRL 0.91M  (Review: 3.93)", 7.5, False, TEXT_MUTED),
        ]
    )

    # ── RIGHT COLUMN: 3 cards  (40% / 35% / 25%) ─────────────────────────────
    # Mirrors HTML: Logistics → BIP → Monte Carlo
    row_gap_r   = ROW_GAP
    rh = [
        BODY_H * 0.40 - row_gap_r * 2 / 3,
        BODY_H * 0.35 - row_gap_r * 2 / 3,
        BODY_H * 0.25 - row_gap_r * 2 / 3,
    ]

    # Card R1 – Logistics Risk Table  (mirrors .db-table in HTML)
    r_top1 = BODY_TOP
    add_widget_card(
        slide1, RIGHT_X, r_top1, RIGHT_W, rh[0],
        "🗺️ TỶ LỆ GIAO HÀNG TRỄ THEO BANG (Logistics Hotspots)", ACCENT_AMBER,
        [
            ("", 2, False, TEXT_MUTED),
            ("State          │ Trễ (%)  │ Ngày TB │ Rủi ro", 7.5, True,  TEXT_MUTED),
            ("─" * 52, 5.5, False, BORDER_COLOR),
            ("AL (Alagoas)        │  23.9%  │ 24.3 ngày │ 🔴 Rất cao",   7.5, False, ACCENT_ROSE),
            ("MA (Maranhão)       │  20.1%  │ 21.1 ngày │ 🔴 Rất cao",   7.5, False, ACCENT_ROSE),
            ("BA (Bahia)          │  15.4%  │ 18.9 ngày │ 🟡 Trung bình", 7.5, False, ACCENT_AMBER),
            ("RJ (Rio de Janeiro) │  10.2%  │ 14.8 ngày │ 🟡 Trung bình", 7.5, False, ACCENT_AMBER),
            ("SP (São Paulo)      │   8.1%  │  8.3 ngày │ 🟢 Bình thường",7.5, False, ACCENT_EMERALD),
            ("", 2, False, TEXT_MUTED),
            ("⚠ AL, MA cần làm việc lại với đối tác logistics hoặc kho vệ tinh.", 7, True, ACCENT_AMBER),
        ]
    )

    # Card R2 – BIP Category Optimization  (mirrors BIP card in HTML)
    r_top2 = r_top1 + rh[0] + row_gap_r
    add_widget_card(
        slide1, RIGHT_X, r_top2, RIGHT_W, rh[1],
        "🎯 TOP 10 NGÀNH HÀNG ƯU TIÊN – BIP Optimization", ACCENT_EMERALD,
        [
            ("", 2, False, TEXT_MUTED),
            ("BIP tối đa hóa: Doanh thu × Review  |  Ràng buộc: Cước ≤ 25 BRL, Review ≥ 3.5", 7, False, ACCENT_CYAN),
            ("", 1.5, False, TEXT_MUTED),
            ("1. health_beauty    BRL 1.26M  (Review: 4.14)", 7.5, True,  TEXT_WHITE),
            ("2. watches_gifts    BRL 1.20M  (Review: 4.02)", 7.5, False, TEXT_MUTED),
            ("3. bed_bath_table   BRL 1.04M  (Review: 3.89)", 7.5, False, TEXT_MUTED),
            ("4. sports_leisure   BRL 0.99M  (Review: 4.11)", 7.5, False, TEXT_MUTED),
            ("5. computers_acc    BRL 0.91M  (Review: 3.93)", 7.5, False, TEXT_MUTED),
            ("6. furniture_decor  BRL 0.73M  (Review: 3.90)", 7.5, False, TEXT_MUTED),
            ("+ 4 khác: cool_stuff, housewares, auto, toys", 7, False, TEXT_MUTED),
        ]
    )

    # Card R3 – Monte Carlo Simulation  (mirrors .sim-grid in HTML)
    r_top3 = r_top2 + rh[1] + row_gap_r
    add_widget_card(
        slide1, RIGHT_X, r_top3, RIGHT_W, rh[2],
        "🎲 GIẢ LẬP RỦI RO MONTE CARLO (N = 1,000 Runs)", ACCENT_VIOLET,
        [
            ("", 2, False, TEXT_MUTED),
            ("Rủi ro Doanh thu tập trung:", 7.5, True, ACCENT_VIOLET),
            ("  21.4% xác suất doanh thu danh mục giảm >20% vs mean (BRL 248K)", 7.5, False, TEXT_MUTED),
            ("", 1.5, False, TEXT_MUTED),
            ("Rủi ro vi phạm SLA giao hàng:", 7.5, True, ACCENT_EMERALD),
            ("  1.7%  xác suất tỷ lệ giao trễ vượt ngưỡng 10% – Cực kỳ an toàn.", 7.5, False, TEXT_MUTED),
        ]
    )

    # ══════════════════════════════════════════════════════════
    # SLIDE 2 – Theme & Layout Specs
    # ══════════════════════════════════════════════════════════
    add_bullet_slide(prs, "1. Phong cách & Bố cục (Theme & Layout Specs)", [
        "Phong cách thiết kế: Midnight Executive (Tối cao cấp)",
        "  * Tông màu nền: Dark Slate (#0b0f19) | Card: Navy Deep (#111827)",
        "  * Bo góc card: 12px (subtle) | Font: Inter / Segoe UI",
        "  * Màu điểm nhấn chức năng:",
        "    - Xanh lục (#10b981): tăng trưởng doanh thu, vận hành an toàn, vượt SLA",
        "    - Xanh lam (#06b6d4): dữ liệu đơn hàng, xu hướng, badge",
        "    - Tím (#8b5cf6): AOV, mô phỏng rủi ro",
        "    - Vàng cam (#f59e0b) và Đỏ (#ef4444): cảnh báo logistics giao trễ",
        "Cấu trúc trang: Single-Page Dashboard",
        "  * Bố cục lưới 4:3 – Balanced Grid (left 1.1fr | right 0.9fr)",
        "  * Luồng thông tin: Bộ lọc → KPIs → Bán hàng (Trái) & Vận hành/Rủi ro (Phải)",
        "  * Hạn chế cuộn trang để ban điều hành nắm bắt toàn cảnh ngay lập tức",
    ])

    # ══════════════════════════════════════════════════════════
    # SLIDE 3 – DAX Measures
    # ══════════════════════════════════════════════════════════
    add_bullet_slide(prs, "2. Công thức DAX Measures cốt lõi", [
        "Nhóm chỉ số Kinh doanh",
        '  * Doanh thu thực tế (Realized Revenue):',
        '    - DAX: Realized Revenue = CALCULATE(SUM(df_master[payment_value]), df_master[order_status] = "delivered")',
        '  * Số đơn hàng thành công (Delivered Orders):',
        '    - DAX: Delivered Orders = CALCULATE(DISTINCTCOUNT(df_master[order_id]), df_master[order_status] = "delivered")',
        '  * Giá trị đơn hàng trung bình (AOV):',
        '    - DAX: AOV = DIVIDE([Realized Revenue], [Delivered Orders], 0)',
        "Nhóm chỉ số Vận hành & CSAT",
        '  * Tỷ lệ giao đúng hạn (On-Time Delivery Rate):',
        '    - DAX: On-Time Rate = DIVIDE(CALCULATE(DISTINCTCOUNT(df_master[order_id]), df_master[order_status] = "delivered", df_master[late_flag] = 0), [Delivered Orders], 0)',
        '  * Điểm đánh giá chất lượng (CSAT Score):',
        '    - DAX: CSAT Score = CALCULATE(AVERAGE(df_master[review_score]), df_master[order_status] = "delivered")',
        '  * Tăng trưởng YoY:',
        '    - DAX: YoY Revenue Growth % = DIVIDE([Realized Revenue] - CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date])), CALCULATE([Realized Revenue], SAMEPERIODLASTYEAR(Dim_Date[Date])), 0)',
    ])

    # ══════════════════════════════════════════════════════════
    # SLIDE 4 – DAX Sub-labels
    # ══════════════════════════════════════════════════════════
    add_bullet_slide(prs, "2.5. Công thức DAX cho Nhãn phụ (KPI Sub-labels)", [
        "Nhóm chỉ số tăng trưởng YoY",
        '  * Revenue Sub-label:',
        '    - DAX: Revenue Sub-label = VAR Growth = [YoY Revenue Growth %] RETURN IF(ISBLANK(Growth) || Growth = 0, "No YoY Data", IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY")',
        '  * Orders Sub-label:',
        '    - DAX: Orders Sub-label = VAR Growth = [Orders YoY Growth %] RETURN IF(ISBLANK(Growth) || Growth = 0, "No YoY Data", IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY")',
        '  * AOV Sub-label:',
        '    - DAX: AOV Sub-label = VAR Growth = [AOV YoY Growth %] RETURN IF(ISBLANK(Growth) || Growth = 0, "No YoY Data", IF(Growth >= 0, "▲ ", "▼ ") & FORMAT(ABS(Growth), "0.0%") & " YoY")',
        "Nhóm chỉ số Vận hành & Trực quan",
        '  * On-Time Sub-label:',
        '    - DAX: On-Time Sub-label = VAR SLA_Target = 0.90 VAR CurrentRate = [On-Time Delivery Rate] RETURN "Target SLA: 90.0% (" & IF(CurrentRate >= SLA_Target, "Đạt SLA", "Vi phạm SLA") & ")"',
        '  * CSAT Sub-label:',
        '    - DAX: CSAT Sub-label = VAR OneStarRate = [1-Star Review Rate] RETURN FORMAT(OneStarRate, "0.0%") & " rate 1-star"',
    ])

    # ══════════════════════════════════════════════════════════
    # SLIDE 5 – Data Modeling & ETL
    # ══════════════════════════════════════════════════════════
    add_bullet_slide(prs, "3. Chuẩn bị Dữ liệu & Mô hình hình sao (Star Schema)", [
        "Kết nối CSDL SQLite phụ trợ (olist_analytics.db)",
        "  * Nạp database thay vì 9 tệp CSV rời rạc → cải thiện hiệu năng tải trang",
        "  * Import view df_master làm Fact Table chính (đơn hàng, thanh toán, ngày giao)",
        "  * Import view item_detail làm Fact/Dimension phụ (danh mục, sản phẩm, cước phí)",
        "Thiết lập bảng lịch Dim_Date bằng DAX",
        "  * Tạo bảng lịch tự động:",
        "    - Dim_Date = VAR MinDate = MIN(df_master[order_purchase_timestamp])",
        "    - VAR MaxDate = MAX(df_master[order_purchase_timestamp])",
        '    - RETURN ADDCOLUMNS(CALENDAR(MinDate, MaxDate), "Year", YEAR([Date]), ...)',
        "  * Cấu hình Sort by Column: Month Short → sắp xếp theo Month Number",
        "Thiết lập Relationships",
        "  * 1:* từ Dim_Date[Date] → df_master[order_purchase_timestamp]",
        "  * 1:* từ df_master[order_id] → item_detail[order_id]",
    ])

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(base_dir, "Outputs", "reports",
                            "Olist_PowerBI_Dashboard_Specification_4x3.pptx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prs.save(out_path)
    print(f"✅  Saved  →  {out_path}")
    print(f"   Canvas  : {prs.slide_width / 914400:.2f}\" × {prs.slide_height / 914400:.2f}\"  (4:3)")
    print(f"   Slides  : {len(prs.slides)}")


if __name__ == "__main__":
    main()
