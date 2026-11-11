import os
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import win32com.client

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DECK = os.path.join(BASE_DIR, 'presentation', 'Presentasi_Laporan_Tahap_1_Sistem_Cerdas_Telkom.pptx')
SAMPLE_IMG = os.path.join(BASE_DIR, 'results', 'sample_setup_visual.png')
LOSS_PLOT_IMG = os.path.join(BASE_DIR, 'results', 'grafik_loss_pelatihan_ann.png')

def generate_dashboard_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Executive Engineering Dashboard Color Palette
    C_TELKOM_RED = RGBColor(176, 28, 46)     # #B01C2E Official Telkom Red
    C_SLATE_DARK = RGBColor(15, 23, 42)      # #0F172A Dark Navy Slate
    C_CHARCOAL = RGBColor(30, 41, 59)        # #1E293B Text Dark
    C_MUTED = RGBColor(100, 116, 139)        # #64748B Secondary Slate
    C_PAGE_BG = RGBColor(248, 250, 252)      # #F8FAFC Soft Page Background
    C_CARD_BG = RGBColor(255, 255, 255)      # Pure White Card
    C_CARD_BG_MUTED = RGBColor(241, 245, 249)# #F1F5F9 Soft Inner Box
    C_BORDER = RGBColor(226, 232, 240)       # #E2E8F0 Subtle Border
    C_GREEN = RGBColor(22, 163, 74)          # #16A34A Success Emerald
    C_GREEN_BG = RGBColor(240, 253, 244)     # #F0FDF4 Pill Green
    C_GOLD = RGBColor(202, 138, 4)           # #CA8A04 Metric Gold
    C_GOLD_BG = RGBColor(254, 252, 232)      # #FEFCE8 Pill Gold
    C_RED_BG = RGBColor(254, 242, 242)       # #FEF2F2 Pill Red
    C_BLUE = RGBColor(37, 99, 235)           # #2563EB Tech Blue
    C_BLUE_BG = RGBColor(239, 246, 255)      # #EFF6FF Pill Blue
    C_WHITE = RGBColor(255, 255, 255)

    def set_slide_background(slide, color):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER, line_width=1.0):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(line_width)
        else:
            shape.line.fill.background()
        return shape

    def add_badge(slide, left, top, width, height, text, bg_color, text_color):
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = bg_color
        badge.line.fill.background()
        tf = badge.text_frame
        tf.word_wrap = False
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = text_color
        p.alignment = PP_ALIGN.CENTER
        return badge

    def add_stat_callout(slide, left, top, width, height, num_str, label_str, sub_str="", num_color=C_TELKOM_RED, bg_color=C_CARD_BG):
        card = add_card(slide, left, top, width, height, bg_color=bg_color, border_color=C_BORDER)
        tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

        p1 = tf.paragraphs[0]
        p1.text = num_str
        p1.font.name = "Arial"
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = num_color

        p2 = tf.add_paragraph()
        p2.text = label_str
        p2.font.name = "Arial"
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = C_CHARCOAL
        p2.space_before = Pt(2)

        if sub_str:
            p3 = tf.add_paragraph()
            p3.text = sub_str
            p3.font.name = "Calibri"
            p3.font.size = Pt(9.5)
            p3.font.color.rgb = C_MUTED
            p3.space_before = Pt(2)
        return card

    def add_dashboard_header(slide, title, chapter_tag="BAB I: PENDAHULUAN", badge_text="CPMK-2"):
        # Top Institutional Header
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(8.5), Inches(0.3))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"TELKOM UNIVERSITY  |  FAKULTAS TEKNIK ELEKTRO — S1 TEKNIK FISIKA"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_MUTED

        # Badges on Top Right
        add_badge(slide, Inches(9.8), Inches(0.32), Inches(1.0), Inches(0.28), chapter_tag, C_CARD_BG_MUTED, C_CHARCOAL)
        add_badge(slide, Inches(10.9), Inches(0.32), Inches(1.6), Inches(0.28), badge_text, C_RED_BG, C_TELKOM_RED)

        # Slide Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = "Arial"
        p_t.font.size = Pt(23)
        p_t.font.bold = True
        p_t.font.color.rgb = C_SLATE_DARK

    def add_dashboard_footer(slide, current_slide, total_slides=10):
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.3))
        tf = footer_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"Sidang Tugas Besar Sistem Cerdas 2026  •  Tahap I: Pemodelan ANN  •  Dosen: CMI, DDW, AQR           Slide {current_slide} of {total_slides}"
        p.font.name = "Calibri"
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_MUTED

    # =========================================================================
    # SLIDE 1: EXECUTIVE COVER DASHBOARD (Dark Slate Theme with Metric Badges)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, C_SLATE_DARK)

    # Frame Container
    add_card(s1, Inches(0.7), Inches(0.7), Inches(11.933), Inches(6.1), bg_color=RGBColor(24, 33, 47), border_color=C_TELKOM_RED, line_width=1.5)

    # Top Institutional Track
    add_badge(s1, Inches(1.2), Inches(1.1), Inches(4.5), Inches(0.35), "TELKOM UNIVERSITY  |  FAKULTAS TEKNIK ELEKTRO", RGBColor(38, 50, 70), C_WHITE)
    add_badge(s1, Inches(5.8), Inches(1.1), Inches(2.2), Inches(0.35), "S1 TEKNIK FISIKA", RGBColor(38, 50, 70), C_GOLD)
    add_badge(s1, Inches(8.1), Inches(1.1), Inches(2.2), Inches(0.35), "SIDANG TUGAS BESAR", C_RED_BG, C_TELKOM_RED)

    # Main Title
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.65), Inches(10.9), Inches(1.6))
    tf = t_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Koreksi Pengukuran Warna Berbasis Smartphone Menggunakan Artificial Neural Network"
    p.font.name = "Arial"
    p.font.size = Pt(29)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(1.2), Inches(3.3), Inches(10.9), Inches(0.6))
    tf = sub_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Rekayasa Sistem Pengukuran Optik & Reduksi Distorsi Iluminansi Eksternal dengan Kartu Referensi Abu-Abu 18%"
    p.font.name = "Calibri"
    p.font.size = Pt(13.5)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # 4 Executive Metric Badges on Cover
    metrics_cover = [
        ("90 Citra", "Dataset Terstandarisasi", C_BLUE, RGBColor(30, 41, 59)),
        ("30 Resep", "Campuran M, K, B", C_GOLD, RGBColor(30, 41, 59)),
        ("66.4%", "Reduksi Error MAE", C_GREEN, RGBColor(30, 41, 59)),
        ("PyTorch", "Multi-Layer Perceptron", C_TELKOM_RED, RGBColor(30, 41, 59))
    ]
    for i, (m_val, m_lbl, col, bg_col) in enumerate(metrics_cover):
        add_card(s1, Inches(1.2 + i * 2.75), Inches(4.05), Inches(2.6), Inches(0.95), bg_color=bg_col, border_color=col, line_width=1.0)
        tb_m = s1.shapes.add_textbox(Inches(1.35 + i * 2.75), Inches(4.15), Inches(2.3), Inches(0.75))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        p1 = tf_m.paragraphs[0]
        p1.text = m_val
        p1.font.name = "Arial"
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_m.add_paragraph()
        p2.text = m_lbl
        p2.font.name = "Calibri"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = RGBColor(148, 163, 184)

    # Metadata Card Bottom
    add_card(s1, Inches(1.2), Inches(5.2), Inches(10.9), Inches(1.2), bg_color=RGBColor(24, 33, 47), border_color=RGBColor(51, 65, 85))
    info_box = s1.shapes.add_textbox(Inches(1.4), Inches(5.3), Inches(10.5), Inches(1.0))
    tf = info_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Mata Kuliah : Sistem Cerdas (Tugas Besar 2026 — Capaian CPMK-2)"
    p.font.name = "Arial"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    p = tf.add_paragraph()
    p.text = "Program Studi : S1 Teknik Fisika  |  Fakultas Teknik Elektro  |  Telkom University"
    p.font.name = "Calibri"
    p.font.size = Pt(11.5)
    p.font.color.rgb = C_WHITE

    p = tf.add_paragraph()
    p.text = "Tim Dosen Pengampu & Penguji : CMI, DDW, AQR"
    p.font.name = "Calibri"
    p.font.size = Pt(11.5)
    p.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 2: BAB I - PROBLEM & SOLUTION EXECUTIVE MATRIX
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, C_PAGE_BG)
    add_dashboard_header(s2, "Problematika Optik vs Solusi Rekayasa Cerdas", "BAB I", "PENDAHULUAN")
    add_dashboard_footer(s2, 2)

    # Left Column: Problem Card
    add_card(s2, Inches(0.8), Inches(1.35), Inches(5.6), Inches(4.5), bg_color=C_CARD_BG)
    add_badge(s2, Inches(1.1), Inches(1.55), Inches(2.2), Inches(0.3), "TANTANGAN OPTIK", C_RED_BG, C_TELKOM_RED)

    tb = s2.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(5.0), Inches(3.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Ketidakpastian Sensor Smartphone"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    p_items_s2 = [
        ("Sensitivitas Iluminansi:", " Sensor kamera menangkap perkalian antara reflektansi spektral objek dengan intensitas sumber cahaya luar (E = I x R)."),
        ("Fluktuasi Nilai RGB:", " Larutan warna yang sama menghasilkan pembacaan digital RGB berbeda drastis saat suhu lampu (Kelvin) atau kecerahan berubah."),
        ("Non-Linearitas CMOS:", " Respon fotodioda sensor digital tidak linier sempurna; transformasi matriks linier sederhana tidak memadai."),
        ("Akses Industri Terbatas:", " Spektrofotometer laboratorium mahal; dibutuhkan sistem cerdas berbasis kamera terjangkau.")
    ]
    for h_txt, b_txt in p_items_s2:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Right Column: Solution Card
    add_card(s2, Inches(6.8), Inches(1.35), Inches(5.7), Inches(4.5), bg_color=C_CARD_BG)
    add_badge(s2, Inches(7.1), Inches(1.55), Inches(2.3), Inches(0.3), "SOLUSI SISTEM CERDAS", C_BLUE_BG, C_BLUE)

    tb = s2.shapes.add_textbox(Inches(7.1), Inches(1.95), Inches(5.1), Inches(3.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Pemodelan Non-Linier ANN"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    s_items_s2 = [
        ("Kartu Referensi Abu-Abu 18%:", " Objek optik stabil ditempatkan berdampingan dengan wadah sebagai penangkap vektor iluminansi lokal."),
        ("Koreksi Non-Linier Multi-Variabel:", " Jaringan Syaraf Tiruan (ANN) memetakan 6 input [Rs, Gs, Bs, Rref, Gref, Bref] kembali ke RGB acuan [Rc, Gc, Bc]."),
        ("Ketercapaian CPMK-2:", " Membuktikan kompetensi pemodelan sistem menggunakan PyTorch dengan reduksi MAE signifikan."),
        ("Umpan Balik Tahap II:", " Nilai warna terkoreksi yang stabil menjadi masukan andal bagi kontroler Fuzzy Logic pencocokan pewarna.")
    ]
    for h_txt, b_txt in s_items_s2:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_BLUE
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Bottom KPI Target Banner
    add_card(s2, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.85), bg_color=C_GREEN_BG, border_color=C_GREEN)
    tb_kpi = s2.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(11.1), Inches(0.65))
    tf_kpi = tb_kpi.text_frame
    tf_kpi.word_wrap = True
    p_kpi = tf_kpi.paragraphs[0]
    r_kpi_t = p_kpi.add_run()
    r_kpi_t.text = "TARGET CAPAIAN PROYEK : "
    r_kpi_t.font.bold = True
    r_kpi_t.font.size = Pt(11.5)
    r_kpi_t.font.color.rgb = C_GREEN
    r_kpi_d = p_kpi.add_run()
    r_kpi_d.text = "Membangun model komputasi cerdas yang mampu mengembalikan nilai RGB terdistorsi ke nilai acuan dengan reduksi MAE > 50% pada kondisi cahaya yang tidak digunakan dalam pelatihan (Unseen Test Data)."
    r_kpi_d.font.size = Pt(11.5)
    r_kpi_d.font.color.rgb = C_SLATE_DARK

    # =========================================================================
    # SLIDE 3: BAB III - DESAIN FORMULASI 30 CAMPURAN
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, C_PAGE_BG)
    add_dashboard_header(s3, "Desain Formulasi Spektral 30 Campuran", "BAB III", "METODOLOGI")
    add_dashboard_footer(s3, 3)

    # 3 Top Stat Callout Cards
    add_stat_callout(s3, Inches(0.8), Inches(1.35), Inches(3.7), Inches(2.0), "6", "Primer Monokromatik", "Merah (M1, M5), Kuning (K1, K5), Biru (B1, B5) untuk karakterisasi respon spektral dasar.", num_color=C_TELKOM_RED)
    add_stat_callout(s3, Inches(4.8), Inches(1.35), Inches(3.7), Inches(2.0), "15", "Campuran Biner", "Kombinasi 2 pigmen: Oranye (M+K), Hijau (K+B), Ungu (M+B) dengan variasi rasio 1-5 tetes.", num_color=C_BLUE)
    add_stat_callout(s3, Inches(8.8), Inches(1.35), Inches(3.7), Inches(2.0), "9", "Campuran Tersier", "Campuran simultan 3 warna primer (M+K+B) membentuk spektrum subtraktif kompleks (cokelat, slate).", num_color=C_GOLD)

    # Bottom Standardized Physics Card
    add_card(s3, Inches(0.8), Inches(3.55), Inches(11.7), Inches(3.35), bg_color=C_CARD_BG)
    add_badge(s3, Inches(1.1), Inches(3.75), Inches(2.8), Inches(0.3), "STANDARISASI FISIK & OPTIK", C_CARD_BG_MUTED, C_CHARCOAL)

    tb = s3.shapes.add_textbox(Inches(1.1), Inches(4.15), Inches(11.1), Inches(2.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Pengendalian Parameter & Variabel Terkendali"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    params_s3 = [
        ("Volume Pelarut Terukur Konstan:", " Setiap pengujian menggunakan tepat 100 ml air bersih (dikalibrasi spuit 50 ml x 2) untuk menjaga molaritas konsentrasi zat."),
        ("Penakaran Tetes Gravitasi:", " Botol pewarna diteteskan secara vertikal tegak lurus (90°) untuk menjamin ukuran droplet seragam (~0.05 ml/tetes)."),
        ("Kartu Referensi Abu-Abu 18%:", " Reflektansi netral L*=50 direkatkan statis pada jarak 5 cm di samping wadah, terlindung dari bayangan wadah dan tripod."),
        ("Eliminasi Buih Optik:", " Pengadukan manual perlahan selama 5 detik hingga larutan homogen sempurna tanpa menimbulkan gelembung pada permukaan cairan.")
    ]
    for h_txt, b_txt in params_s3:
        p = tf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(12)
        r2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 4: BAB III - INSTRUMENTASI PEMOTRETAN & SKENARIO CAHAYA
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, C_PAGE_BG)
    add_dashboard_header(s4, "Instrumentasi Kamera & Skenario Cahaya", "BAB III", "METODOLOGI")
    add_dashboard_footer(s4, 4)

    # Left: Pro mode parameters
    add_card(s4, Inches(0.8), Inches(1.35), Inches(5.6), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s4, Inches(1.1), Inches(1.55), Inches(2.4), Inches(0.3), "SENSOR KAMERA PRO", C_BLUE_BG, C_BLUE)

    tb = s4.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Penguncian Parameter Kamera Manual"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    cam_s4 = [
        ("Sensitivitas ISO 400 (Terkunci):", " Memberikan rasio sinyal terhadap noise (SNR) optimal dalam menangkap spektrum cahaya redup."),
        ("White Balance 5500K (Daylight):", " AWB dimatikan untuk mencegah algoritma penyesuaian suhu warna otomatis oleh smartphone."),
        ("Shutter Speed 1/8s:", " Kecepatan rana kaku pada tripod stabil; menjaga piksel kartu abu-abu berada di rentang tengah (bebas clipping)."),
        ("Manual Focus (MF Lock):", " Bidang fokus dikunci presisi pada bidang permukaan cairan larutan."),
        ("Deaktivasi Fitur Komputasional:", " Auto-HDR, AI Scene Enhancer, dan Digital Filtering dinonaktifkan untuk menangkap respon foton murni.")
    ]
    for h_txt, b_txt in cam_s4:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_BLUE
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Right Top: 3 Lighting Scenarios Card
    add_card(s4, Inches(6.8), Inches(1.35), Inches(5.7), Inches(2.7), bg_color=C_CARD_BG)
    add_badge(s4, Inches(7.1), Inches(1.55), Inches(2.6), Inches(0.3), "SKENARIO PENCAHAYAAN", C_GOLD_BG, C_GOLD)

    tb_l = s4.shapes.add_textbox(Inches(7.1), Inches(1.95), Inches(5.1), Inches(2.0))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "3 Kondisi Lingkungan Terkontrol (90 Citra)"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    scenarios = [
        ("• Kondisi 1 (Acuan Terang / Ground Truth):", " Lampu LED meja 5500K jarak 25 cm. Menjadi target koreksi ideal."),
        ("• Kondisi 2 (Pencahayaan Sedang / Tengah):", " Intensitas sedang dengan pergeseran suhu warna hangat."),
        ("• Kondisi 3 (Pencahayaan Redup / Low-Light):", " Fluks iluminasi berkurang drastis (~40%) untuk menguji pemulihan sinyal.")
    ]
    for h_txt, b_txt in scenarios:
        p = tf_l.add_paragraph()
        p.space_before = Pt(3)
        r1 = p.add_run()
        r1.text = h_txt
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = C_CHARCOAL

    # Right Bottom: Embedded Setup Visual
    add_card(s4, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.65), bg_color=C_WHITE)
    if os.path.exists(SAMPLE_IMG):
        s4.shapes.add_picture(SAMPLE_IMG, Inches(7.0), Inches(4.35), width=Inches(5.3), height=Inches(2.35))

    # =========================================================================
    # SLIDE 5: BAB III - PIPELINE EKSTRAKSI FITUR & GROUP SPLITTING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, C_PAGE_BG)
    add_dashboard_header(s5, "Pipeline Ekstraksi Fitur ROI & Group Splitting", "BAB III", "METODOLOGI")
    add_dashboard_footer(s5, 5)

    # Left: ROI Extraction Card
    add_card(s5, Inches(0.8), Inches(1.35), Inches(5.6), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s5, Inches(1.1), Inches(1.55), Inches(2.3), Inches(0.3), "SPATIAL ROI AVERAGING", C_BLUE_BG, C_BLUE)

    tb = s5.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Ekstraksi Fitur Region of Interest"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    roi_s5 = [
        ("Integritas Geometri Statis:", " Dudukan tripod dan penanda wadah permanen menghasilkan koordinat spasial seragam pada seluruh 90 citra beresolusi 1280x960."),
        ("ROI Kartu Abu-Abu:", " Y=[450:550], X=[200:300] (10.000 piksel). Menghasilkan [Rref, Gref, Bref] di titik tengah kartu bebas dari distorsi tepi."),
        ("ROI Sampel Cairan:", " Y=[430:510], X=[600:680] (6.400 piksel). Menghasilkan [Rs, Gs, Bs] di inti larutan, aman dari refleksi kaustik tepi gelas."),
        ("Filter Rata-Rata Spasial (Mean Filter):", " Mereduksi variansi sensor shot-noise secara signifikan dibanding sampling titik tunggal.")
    ]
    for h_txt, b_txt in roi_s5:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_BLUE
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Right: Group Splitting Card
    add_card(s5, Inches(6.8), Inches(1.35), Inches(5.7), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s5, Inches(7.1), Inches(1.55), Inches(2.6), Inches(0.3), "ZERO-LEAKAGE GROUP SPLIT", C_RED_BG, C_TELKOM_RED)

    tb = s5.shapes.add_textbox(Inches(7.1), Inches(1.95), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Pemisahan Data Berdasarkan Campuran"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    split_s5 = [
        ("Kepatuhan Mutlak Regulasi TOR:", " Foto dari campuran yang sama tidak boleh tersebar pada data latih dan uji (mencegah instance memorization)."),
        ("Data Latih (Train Split — 80%):", " 24 campuran unik x 3 kondisi pencahayaan = 72 baris data."),
        ("Data Uji (Test Split Unseen — 20%):", " 6 campuran representatif x 3 kondisi pencahayaan = 18 baris data."),
        ("Daftar 6 Campuran Uji Independen:", " \n  1. Primer: B5 (Biru Pekat)\n  2. Biner M-K: M3 K3 (Oranye Seimbang)\n  3. Biner K-B: K2 B4 (Hijau Zamrud)\n  4. Biner M-B: M2 B4 (Ungu Indigo)\n  5. Tersier: M1 K1 B3 (Slate) & M4 K2 B1 (Cokelat Kayu)"),
        ("Uji Generalisasi Mutlak:", " Menjamin model benar-benar mempelajari relasi fungsi iluminansi-ke-warna.")
    ]
    for h_txt, b_txt in split_s5:
        p = tf.add_paragraph()
        p.space_before = Pt(7)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 6: BAB III - ARSITEKTUR MODEL ANN (PYTORCH)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, C_PAGE_BG)
    add_dashboard_header(s6, "Arsitektur Model ANN Multi-Variabel", "BAB III", "METODOLOGI")
    add_dashboard_footer(s6, 6)

    # Top Formula Card
    add_card(s6, Inches(0.8), Inches(1.35), Inches(11.7), Inches(1.3), bg_color=C_CARD_BG)
    add_badge(s6, Inches(1.1), Inches(1.5), Inches(2.0), Inches(0.28), "FORMULASI TOR", C_CARD_BG_MUTED, C_CHARCOAL)
    tb = s6.shapes.add_textbox(Inches(3.3), Inches(1.45), Inches(9.0), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "[Rc, Gc, Bc] = f_ANN { Rs, Gs, Bs, Rref, Gref, Bref }"
    p.font.name = "Arial"
    p.font.size = Pt(21)
    p.font.bold = True
    p.font.color.rgb = C_TELKOM_RED

    p2 = tf.add_paragraph()
    p2.text = "Pemetaan non-linier 6 variabel masukan (sampel + referensi) menghasilkan 3 variabel keluaran terprediksi."
    p2.font.name = "Calibri"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_MUTED

    # Bottom Left: Model 1
    add_card(s6, Inches(0.8), Inches(2.85), Inches(5.6), Inches(4.0), bg_color=C_CARD_BG)
    add_badge(s6, Inches(1.1), Inches(3.05), Inches(2.2), Inches(0.3), "MODEL 1 (BASELINE)", C_CARD_BG_MUTED, C_CHARCOAL)

    tb = s6.shapes.add_textbox(Inches(1.1), Inches(3.45), Inches(5.0), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Single Hidden Layer: 16 Neuron"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    m1_s6 = [
        ("Topologi Layer:", " Input(6) -> Linear(16) -> ReLU -> Linear(3)"),
        ("Kompleksitas Bobot:", " Total 163 parameter terbobot"),
        ("Tujuan Komparasi:", " Menguji kecukupan kapasitas aproksimator universal 1 lapis tersembunyi."),
        ("Karakteristik:", " Konvergensi sangat cepat, komputasi ringan.")
    ]
    for h_txt, b_txt in m1_s6:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_MUTED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Bottom Right: Model 2 (Champion)
    add_card(s6, Inches(6.8), Inches(2.85), Inches(5.7), Inches(4.0), bg_color=C_CARD_BG, border_color=C_TELKOM_RED, line_width=1.5)
    add_badge(s6, Inches(7.1), Inches(3.05), Inches(2.5), Inches(0.3), "MODEL 2 (CHAMPION)", C_RED_BG, C_TELKOM_RED)

    tb = s6.shapes.add_textbox(Inches(7.1), Inches(3.45), Inches(5.1), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Two Hidden Layers: 32 - 16 Neuron"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_TELKOM_RED

    m2_s6 = [
        ("Topologi Layer:", " Input(6) -> Linear(32) -> ReLU -> Linear(16) -> ReLU -> Linear(3)"),
        ("Kompleksitas Bobot:", " Total 803 parameter terbobot"),
        ("Fungsi Aktivasi Bertingkat:", " Menangkap korelasi non-linier antar kanal warna secara lebih dalam."),
        ("Konfigurasi Pelatihan:", " Optimizer Adam (lr=0.005), Criterion MSE Loss, 1500 Epochs."),
        ("Normalisasi Tensor:", " Input dan Target diskalakan pada rentang [0.0, 1.0].")
    ]
    for h_txt, b_txt in m2_s6:
        p = tf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 7: BAB IV - HASIL PELATIHAN & ANALISIS KURVA LOSS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, C_PAGE_BG)
    add_dashboard_header(s7, "Hasil Pelatihan & Analisis Kurva Konvergensi", "BAB IV", "HASIL & ANALISIS")
    add_dashboard_footer(s7, 7)

    # Left: Embedded Plot
    add_card(s7, Inches(0.8), Inches(1.35), Inches(7.3), Inches(5.5), bg_color=C_WHITE)
    if os.path.exists(LOSS_PLOT_IMG):
        s7.shapes.add_picture(LOSS_PLOT_IMG, Inches(0.9), Inches(1.45), width=Inches(7.1), height=Inches(5.3))

    # Right: Analysis Dashboard Cards
    add_card(s7, Inches(8.3), Inches(1.35), Inches(4.2), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s7, Inches(8.6), Inches(1.55), Inches(2.2), Inches(0.3), "ANALISIS KONVERGENSI", C_CARD_BG_MUTED, C_CHARCOAL)

    tb = s7.shapes.add_textbox(Inches(8.6), Inches(1.95), Inches(3.7), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Interpretasi Training Dynamics"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    points_s7 = [
        ("Penurunan Cepat Awal:", " Pada 200 epoch pertama, bobot jaringan beradaptasi drastis terhadap gradien perbedaan intensitas utama."),
        ("Stabilitas Asimtotik:", " Mendekati epoch ke-800, kurva loss mendatar dengan MSE rendah (<0.003) menandakan konvergensi optimal."),
        ("Evaluasi Bebas Overfitting:", " Test Loss pada 6 campuran unseen (garis putus-putus) secara konsisten sejajar dan di bawah Train Loss."),
        ("Keunggulan Model 2:", " Model 2 menunjukkan kurva penurunan loss yang lebih mulus dan stabil dibanding Model 1.")
    ]
    for h_txt, b_txt in points_s7:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_TELKOM_RED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 8: BAB IV - EVALUASI METRIK MAE BENCHMARK DASHBOARD
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, C_PAGE_BG)
    add_dashboard_header(s8, "Validasi Kinerja Model: Benchmark MAE per Kanal", "BAB IV", "HASIL & ANALISIS")
    add_dashboard_footer(s8, 8)

    # Top Stat Callout Card
    add_card(s8, Inches(0.8), Inches(1.35), Inches(11.7), Inches(1.35), bg_color=C_GREEN_BG, border_color=C_GREEN, line_width=1.5)
    add_badge(s8, Inches(1.1), Inches(1.5), Inches(1.8), Inches(0.28), "CPMK-2 TERCAPAI", C_WHITE, C_GREEN)

    tb = s8.shapes.add_textbox(Inches(3.1), Inches(1.45), Inches(9.1), Inches(1.1))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Model ANN Berhasil Menurunkan Rata-Rata Error MAE Sebesar 66.4% (33.64 -> 11.30)"
    p.font.name = "Arial"
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    p2 = tf.add_paragraph()
    p2.text = "Evaluasi numerik pada 18 sampel data uji independen (Unseen Mixtures). Menurunkan distorsi optik drastis."
    p2.font.name = "Calibri"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_MUTED

    # Table in the Middle
    table_shape = s8.shapes.add_table(4, 6, Inches(0.8), Inches(2.95), Inches(11.7), Inches(2.4))
    table = table_shape.table

    headers_tbl = ["Konfigurasi Model", "MAE Kanal R", "MAE Kanal G", "MAE Kanal B", "Mean MAE", "Penurunan Error (%)"]
    for col_idx, h_text in enumerate(headers_tbl):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_SLATE_DARK
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = "Arial"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER

    tbl_rows = [
        ["Sebelum Koreksi (Baseline)", "36.27", "36.02", "28.63", "33.64", "0.0% (Distorsi Awal)"],
        ["Model 1 (1 Hidden Layer: 16)", "11.84", "12.46", "9.99", "11.43", "66.0% Reduksi"],
        ["Model 2 (2 Hidden Layer: 32-16) [Champion]", "11.52", "11.59", "10.80", "11.30", "66.4% Reduksi"]
    ]
    for row_idx, r_data in enumerate(tbl_rows):
        is_champion = row_idx == 2
        for col_idx, val in enumerate(r_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(254, 245, 246) if is_champion else (C_WHITE if row_idx % 2 == 0 else C_CARD_BG_MUTED)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = "Arial"
            p.font.size = Pt(12)
            p.font.bold = is_champion or col_idx == 0
            p.font.color.rgb = C_TELKOM_RED if (is_champion and col_idx >= 4) else C_CHARCOAL
            p.alignment = PP_ALIGN.LEFT if col_idx == 0 else PP_ALIGN.CENTER

    # Bottom Notes Card
    add_card(s8, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.2), bg_color=C_CARD_BG)
    tb_b = s8.shapes.add_textbox(Inches(1.0), Inches(5.7), Inches(11.3), Inches(1.0))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.text = "Pemenuhan Indikator TOR:"
    p.font.name = "Arial"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = C_TELKOM_RED

    p2 = tf_b.add_paragraph()
    p2.text = "• Model 2 dipilih sebagai model final karena menghasilkan MAE terendah pada kanal Red (11.52) dan Green (11.59) yang sangat menentukan dalam diskriminasi warna."
    p2.font.name = "Calibri"
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 9: BAB IV - DISKUSI HASIL & KETERBATASAN SISTEM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, C_PAGE_BG)
    add_dashboard_header(s9, "Diskusi Koreksi Ekstrem & Keterbatasan Sistem", "BAB IV", "HASIL & ANALISIS")
    add_dashboard_footer(s9, 9)

    # Left: Success in Extreme Lighting
    add_card(s9, Inches(0.8), Inches(1.35), Inches(5.6), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s9, Inches(1.1), Inches(1.55), Inches(2.6), Inches(0.3), "EFEKTIVITAS KOREKSI EKSTREM", C_BLUE_BG, C_BLUE)

    tb = s9.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Pemulihan Spektrum Cahaya Ekstrem"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    disc_s9_left = [
        ("Pemulihan Spektrum Redup Drastis:", " Pada sampel K2 B4 (redup), error awal 81.44 ditekan menjadi 11.97 (penurunan error >85%)."),
        ("Kestabilan Suhu Warna Tengah:", " Pada sampel M1 K1 B3 (tengah), error 44.38 dipulihkan menjadi 4.34, membuktikan adaptabilitas terhadap pergeseran spektrum."),
        ("Dukungan Vektor Iluminansi:", " Input Rref, Gref, Bref terbukti menjadi acuan andal bagi ANN untuk membedakan apakah warna gelap berasal dari kepekatan zat atau redupnya lampu.")
    ]
    for h_txt, b_txt in disc_s9_left:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_BLUE
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # Right: Limitations and Residuals
    add_card(s9, Inches(6.8), Inches(1.35), Inches(5.7), Inches(5.5), bg_color=C_CARD_BG)
    add_badge(s9, Inches(7.1), Inches(1.55), Inches(2.8), Inches(0.3), "KETERBATASAN FISIK & OPTIK", C_RED_BG, C_TELKOM_RED)

    tb = s9.shapes.add_textbox(Inches(7.1), Inches(1.95), Inches(5.1), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Pelaporan Residu Sesuai Panduan TOR"
    p.font.name = "Arial"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_SLATE_DARK

    disc_s9_right = [
        ("Residu pada Kondisi Terang (Wajib TOR):", " Sesuai arahan TOR, kondisi di mana koreksi menambah sedikit error dilaporkan: Pada foto acuan terang mentah (error awal 0.0), ANN memunculkan residu kecil (~9-14) akibat aproksimasi fungsi non-linier global."),
        ("Refraksi Meniskus & Geometri Gelas:", " Pola bergelombang pada dasar wadah plastik membiaskan cahaya di pinggir gelas; diatasi dengan pembatasan area ROI di titik pusat larutan."),
        ("Sifat Optik Transparan Cairan:", " Tidak seperti cat opak, pewarna makanan tembus cahaya sehingga warna terukur dipengaruhi reflektansi dasar putih.")
    ]
    for h_txt, b_txt in disc_s9_right:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + h_txt
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = C_TELKOM_RED if "Residu" in h_txt else C_MUTED
        r2 = p.add_run()
        r2.text = b_txt
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = C_CHARCOAL

    # =========================================================================
    # SLIDE 10: BAB V - EXECUTIVE CONCLUSION & PHASE II ROADMAP
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, C_SLATE_DARK)

    # Frame Container
    add_card(s10, Inches(0.7), Inches(0.7), Inches(11.933), Inches(6.1), bg_color=RGBColor(24, 33, 47), border_color=C_TELKOM_RED, line_width=1.5)

    add_badge(s10, Inches(1.2), Inches(1.05), Inches(3.2), Inches(0.35), "BAB V: KESIMPULAN & ROADMAP", C_CARD_BG_MUTED, C_CHARCOAL)
    add_badge(s10, Inches(4.6), Inches(1.05), Inches(2.2), Inches(0.35), "CPMK-2 TUNTAS", C_RED_BG, C_TELKOM_RED)

    tb = s10.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Target CPMK-2 Tuntas Penuh dan Siap Terintegrasi ke Kontrol Fuzzy (CPMK-3)"
    p.font.name = "Arial"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Left: Capaian Tahap I
    add_card(s10, Inches(1.2), Inches(2.35), Inches(5.3), Inches(4.1), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(71, 85, 105))
    add_badge(s10, Inches(1.4), Inches(2.55), Inches(2.6), Inches(0.3), "HASIL AKHIR TAHAP I", C_BLUE_BG, C_BLUE)

    tb = s10.shapes.add_textbox(Inches(1.4), Inches(2.95), Inches(4.9), Inches(3.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Capaian CPMK-2 (Tuntas)"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    conc_s10 = [
        "Dataset 90 citra berstandar tinggi tersusun lengkap dengan kepatuhan zero-leakage group split.",
        "Model 2 (PyTorch ANN 32-16) terbukti menurunkan rata-rata error pada unseen mixtures sebesar 66.4%.",
        "Artefak model terbaik (.pt) dan seluruh dokumentasi metrik telah terekspor dan terverifikasi secara numerik."
    ]
    for cp in conc_s10:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = "✓  " + cp
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)

    # Right: Rencana Tahap II
    add_card(s10, Inches(6.8), Inches(2.35), Inches(5.4), Inches(4.1), bg_color=RGBColor(30, 41, 59), border_color=C_TELKOM_RED, line_width=1.5)
    add_badge(s10, Inches(7.0), Inches(2.55), Inches(2.8), Inches(0.3), "NEXT STEPS: TAHAP II", C_GOLD_BG, C_GOLD)

    tb = s10.shapes.add_textbox(Inches(7.0), Inches(2.95), Inches(5.0), Inches(3.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Rencana Kontrol Fuzzy (CPMK-3)"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    next_s10 = [
        "Karakterisasi respons subtraktif: mengukur pergeseran kanal RGB per tetes penambahan larutan stok.",
        "Perancangan kontroler Fuzzy Mamdani (3 input error: eR, eG, eB -> 3 output volume tetes M, K, B).",
        "Implementasi sistem loop tertutup (closed-loop): Pengukuran Foto -> Koreksi ANN -> Inferensi Fuzzy -> Rekomendasi Tetes -> Evaluasi ERGB."
    ]
    for rp in next_s10:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = "→  " + rp
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    prs.save(OUTPUT_DECK)
    print(f"Executive Dashboard deck saved to: {OUTPUT_DECK}")

def inject_transitions_and_animations():
    print("Connecting to PowerPoint COM to inject transitions and animations...")
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    pres = ppt.Presentations.Open(os.path.abspath(OUTPUT_DECK), WithWindow=False)

    total_slides = pres.Slides.Count
    print(f"Applying transitions and animations across {total_slides} slides...")

    for i in range(1, total_slides + 1):
        slide = pres.Slides(i)
        
        # Apply smooth Pan/Fade transition
        if i in [1, 10]:
            slide.SlideShowTransition.EntryEffect = 770 # Fade smoothly for Cover and Conclusion
            slide.SlideShowTransition.Duration = 0.8
        else:
            slide.SlideShowTransition.EntryEffect = 3896 # Pan Left (Smooth Pan/Morph between chapters)
            slide.SlideShowTransition.Duration = 0.65

        # Sequential entrance animations on main dashboard cards
        shape_count = slide.Shapes.Count
        if shape_count >= 2:
            for s_idx in range(2, min(shape_count + 1, 7)):
                try:
                    eff = slide.TimeLine.MainSequence.AddEffect(slide.Shapes(s_idx), 10, 0, 1) # Fade In
                    eff.Timing.Duration = 0.35
                except Exception:
                    pass

    pres.Save()
    pres.Close()
    print("Transitions and animations successfully injected!")

if __name__ == '__main__':
    generate_dashboard_deck()
    inject_transitions_and_animations()
