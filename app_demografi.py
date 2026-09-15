import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import textwrap
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as pdf_colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# ==========================================================
# KONFIGURASI HALAMAN
# ==========================================================
st.set_page_config(
    page_title="DEMUDA Purworejo",
    page_icon="🗺️",
    layout="wide"
)

PALET = {
    "teal": "#0F6E56",
    "teal_muda": "#5DCAA5",
    "amber": "#EF9F27",
    "amber_gelap": "#BA7517",
    "teks_utama": "#2C2C2A",
    "teks_sekunder": "#5F5E5A",
}

LOGO_SVG = """
<svg width="140" height="140" viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg">
  <path d="M340,240 C300,190 260,160 260,120 C260,75 296,40 340,40 C384,40 420,75 420,120 C420,160 380,190 340,240 Z"
        fill="#0F6E56" stroke="#085041" stroke-width="2"/>
  <rect x="300" y="145" width="18" height="30" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <rect x="330" y="125" width="18" height="50" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <rect x="360" y="95"  width="18" height="80" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <circle cx="369" cy="80" r="9" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
</svg>
"""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}
.block-container {{
    padding-top: 2.2rem;
    max-width: 1150px;
}}
[data-testid="stMetric"] {{
    background: #FAFAF7;
    border: 1px solid #E7E5DD;
    border-radius: 12px;
    padding: 14px 16px 10px 16px;
}}
h1, h2, h3, .stTabs [data-baseweb="tab"] p {{
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: {PALET['teks_utama']};
}}
[data-testid="stMetricValue"] {{
    color: {PALET['teal']};
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
[data-testid="stMetricLabel"] {{
    color: {PALET['teks_sekunder']};
}}
.stTabs [aria-selected="true"] {{
    color: {PALET['teal']} !important;
    border-bottom-color: {PALET['amber']} !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f"""<div style='display:flex;align-items:center;gap:18px;margin-bottom:4px;'>
{LOGO_SVG}
<div>
<h1 style='margin:0;line-height:1.1;'>DEMUDA Purworejo</h1>
<p style='margin:2px 0 0 0;color:{PALET["teks_sekunder"]};font-size:15px;'>Peta Potensi Demografi Pemuda Kabupaten Purworejo</p>
</div>
</div>""",
    unsafe_allow_html=True
)

# ==========================================================
# 📊 DATA -- HASIL ESTIMASI DARI DUA SUMBER RESMI BPS
# ==========================================================
# METODOLOGI (penting untuk dijelaskan ke juri):
# BPS Kabupaten Purworejo mempublikasikan dua tabel terpisah yang TIDAK bisa
# langsung digabung mentah-mentah:
#   1. "Jumlah Penduduk Menurut Kelompok Umur dan Jenis Kelamin di Kabupaten
#      Purworejo, 2026" -- breakdown umur, tapi HANYA level kabupaten (agregat),
#      tidak dipecah per kecamatan.
#   2. "Jumlah Penduduk ... Menurut Kecamatan di Kabupaten Purworejo" (BPS,
#      dikutip dalam "Kabupaten Purworejo Dalam Angka 2025") -- total penduduk
#      DAN LUAS WILAYAH per kecamatan (estimasi pertengahan 2024).
#
# LANGKAH 1 -- proporsi umur dasar kabupaten (dari sumber 1, total 808.153 jiwa):
#   - 0-14 tahun (anak)      : 20,17%
#   - 15-64 tahun (produktif): 67,47%
#   - 65+ tahun (lansia)     : 12,37%
#   - 15-29 tahun ("pemuda", proksi terdekat untuk 16-30 dari band 5-tahunan
#     BPS): 21,61% dari total, atau setara 32,0% dari kelompok produktif.
#
# LANGKAH 2 -- karena BPS tidak mempublikasikan breakdown umur PER KECAMATAN,
# proporsi di atas TIDAK bisa langsung dipukul rata ke semua kecamatan (itu
# akan membuat rasio ketergantungan & proporsi pemuda identik di semua
# kecamatan -- tidak informatif). Sebagai gantinya, proporsi disesuaikan
# per kecamatan menggunakan KEPADATAN PENDUDUK (penduduk riil / luas wilayah,
# keduanya data resmi BPS) sebagai indikator pendekatan urbanisasi:
#   - Kecamatan lebih padat (pusat kota/ekonomi) diasumsikan menarik lebih
#     banyak penduduk usia produktif & pemuda (migrasi kerja/pendidikan).
#   - Kecamatan kurang padat (pedesaan/pegunungan) diasumsikan proporsi
#     lansia sedikit lebih tinggi (pemuda merantau ke kota).
# Penyesuaian dibatasi (clipping) maksimal +-40% deviasi dari rata-rata
# kabupaten, supaya variasi yang muncul tetap realistis dan tidak
# dilebih-lebihkan. Proporsi pemuda selalu dihitung sebagai 32,0% dari
# proporsi produktif (rasio kabupaten) sehingga pemuda tetap konsisten
# sebagai subset dari kelompok produktif di tiap kecamatan.
#
# ⚠️ Ini tetap ESTIMASI, bukan data resmi per kecamatan per kelompok umur --
# dijelaskan terbuka ke pengguna lewat expander "Metodologi & Sumber Data".

# Data dasar riil per kecamatan: total penduduk (estimasi pertengahan 2024,
# BPS "Kabupaten Purworejo Dalam Angka 2025") & luas wilayah (km2, sumber sama).
DATA_DASAR_KECAMATAN = [
    # nama,          lat,        lon,         total_penduduk, luas_km2
    ("Bagelen",      -7.81128,  110.04006,    30965,          63.44),
    ("Banyuurip",    -7.75608,  109.97645,    44221,          47.78),
    ("Bayan",        -7.71026,  109.94889,    53220,          44.66),
    ("Bener",        -7.6386,   110.0518,     58913,         102.44),
    ("Bruno",        -7.53,     109.87,       55454,         105.68),
    ("Butuh",        -7.725155, 109.8570219,  42998,          47.21),
    ("Gebang",       -7.64245,  109.99269,    44525,          70.51),
    ("Grabag",       -7.81093,  109.87967,    51175,          67.80),
    ("Kaligesing",   -7.7347,   110.0799,     32564,          78.33),
    ("Kemiri",       -7.64786,  109.90438,    61008,         103.15),
    ("Kutoarjo",     -7.71700,  109.91480,    63172,          39.20),
    ("Loano",        -7.6653,   110.1015,     39201,          53.51),
    ("Ngombol",      -7.8254,   109.9661,     36202,          59.33),
    ("Pituruh",      -7.6414,   109.83652,    53095,          89.01),
    ("Purwodadi",    -7.8657,   110.0024,     42725,          56.15),
    ("Purworejo",    -7.72232,  110.03042,    85595,          53.25),
]

# Proporsi umur dasar kabupaten (dari data BPS 2026, lihat perhitungan di atas)
P_ANAK_KAB = 0.201677
P_PRODUKTIF_KAB = 0.674702
P_LANSIA_KAB = 0.123679
PEMUDA_DARI_PRODUKTIF = 0.216137 / 0.674702  # = 0,3204 -> pemuda 15-29 sbg proporsi dari kelompok produktif

# ==========================================================
# 📈 DATA HISTORIS KABUPATEN (2019-2024)
# ==========================================================
# Sumber: dua laporan akademik yang mengutip BPS Kab. Purworejo (data total
# kabupaten, BUKAN estimasi kami). Breakdown PER KECAMATAN multi-tahun belum
# tersedia dalam format yang bisa diproses otomatis -- lihat catatan di
# expander "Metodologi & Sumber Data".
# ⚠️ Penurunan dari 2023 ke 2024 BUKAN penurunan penduduk riil, melainkan pola
# umum saat BPS mengkalibrasi ulang proyeksi mengikuti hasil sensus terbaru.
DATA_HISTORIS_KABUPATEN = {
    "tahun": [2019, 2020, 2021, 2022, 2023, 2024],
    "penduduk": [714816, 769880, 799411, 804335, 807790, 795033],
}

@st.cache_data
def load_data():
    df = pd.DataFrame(DATA_DASAR_KECAMATAN, columns=["kecamatan", "lat", "lon", "total_penduduk", "luas_km2"])

    # --- Hitung kepadatan & faktor penyesuaian (lihat metodologi di atas) ---
    df["kepadatan"] = df["total_penduduk"] / df["luas_km2"]
    kepadatan_rata2_kab = df["total_penduduk"].sum() / df["luas_km2"].sum()
    z = (df["kepadatan"] / kepadatan_rata2_kab) - 1
    z_clipped = z.clip(-0.4, 0.4)  # batasi deviasi maksimal +-40% dari rata-rata kabupaten

    produktif_share = (P_PRODUKTIF_KAB * (1 + 0.12 * z_clipped)).clip(0.60, 0.75)
    lansia_share = (P_LANSIA_KAB * (1 - 0.15 * z_clipped)).clip(0.08, 0.18)
    anak_share = 1 - produktif_share - lansia_share
    pemuda_share = produktif_share * PEMUDA_DARI_PRODUKTIF

    df["penduduk_15_64"] = (df["total_penduduk"] * produktif_share).round().astype(int)
    df["penduduk_65_plus"] = (df["total_penduduk"] * lansia_share).round().astype(int)
    # anak = sisa, supaya total per kecamatan TETAP PERSIS sama dengan data riil BPS
    df["penduduk_0_14"] = df["total_penduduk"] - df["penduduk_15_64"] - df["penduduk_65_plus"]
    df["pemuda_16_30"] = (df["total_penduduk"] * pemuda_share).round().astype(int)

    df["penduduk_non_produktif"] = df["penduduk_0_14"] + df["penduduk_65_plus"]
    # Rasio ketergantungan = (non-produktif / produktif) x 100
    df["rasio_ketergantungan"] = (df["penduduk_non_produktif"] / df["penduduk_15_64"] * 100).round(1)
    # Proporsi pemuda terhadap total penduduk usia produktif
    df["proporsi_pemuda_dari_produktif"] = (df["pemuda_16_30"] / df["penduduk_15_64"] * 100).round(1)
    # Proporsi pemuda terhadap total penduduk kecamatan
    df["proporsi_pemuda_dari_total"] = (df["pemuda_16_30"] / df["total_penduduk"] * 100).round(1)
    return df

df = load_data()

st.caption(
    "Dashboard analisis struktur usia penduduk per kecamatan untuk mendukung "
    "perencanaan program kepemudaan yang tepat sasaran. Data bersumber dari BPS "
    "Kabupaten Purworejo (lihat metodologi di bawah)."
)

with st.expander("ℹ️ Metodologi & Sumber Data"):
    st.markdown(textwrap.dedent("""
    Dashboard ini menggabungkan **dua tabel resmi BPS** yang aslinya terpisah:

    1. **Struktur umur penduduk** -- BPS Kab. Purworejo, *"Jumlah Penduduk Menurut
       Kelompok Umur dan Jenis Kelamin di Kabupaten Purworejo, 2026"* (level
       kabupaten, agregat, tidak dipecah per kecamatan).
    2. **Populasi & luas wilayah per kecamatan** -- BPS Kab. Purworejo,
       *"Kabupaten Purworejo Dalam Angka 2025"* (estimasi pertengahan 2024,
       per kecamatan, tanpa breakdown umur).

    Karena BPS tidak mempublikasikan breakdown umur *per kecamatan* secara
    terbuka, breakdown umur tiap kecamatan pada dashboard ini adalah
    **estimasi**, dihitung dengan langkah:
    - Proporsi umur dasar diambil dari data kabupaten (anak 20,2%, produktif
      67,5%, lansia 12,4%, pemuda 21,6% dari total / 32,0% dari produktif).
    - Proporsi tersebut disesuaikan per kecamatan menggunakan **kepadatan
      penduduk** (penduduk riil / luas wilayah, keduanya data resmi BPS)
      sebagai indikator pendekatan urbanisasi: kecamatan lebih padat
      diasumsikan sedikit lebih muda strukturnya (menarik usia kerja/pemuda),
      kecamatan kurang padat sedikit lebih tua (pemuda merantau). Penyesuaian
      dibatasi maksimal ±40% dari rata-rata kabupaten agar tetap realistis.

    Kelompok "Pemuda" memakai rentang **15-29 tahun** (kelompok umur 5-tahunan
    BPS) sebagai pendekatan terdekat untuk definisi pemuda 16-30 tahun.

    ⚠️ Angka per kecamatan pada dashboard ini adalah **estimasi berbasis data
    resmi**, bukan hasil sensus/survei langsung per kecamatan.
    """))

with st.expander("Konteks: Bonus Demografi & Generasi Emas 2045"):
    st.markdown(textwrap.dedent("""
    **Bonus Demografi** adalah kondisi ketika jumlah penduduk usia produktif
    (15-64 tahun) jauh lebih besar dibanding usia non-produktif (anak &
    lansia), sehingga rasio ketergantungan rendah -- membuka peluang besar
    percepatan pertumbuhan ekonomi, ASALKAN penduduk usia produktifnya
    berkualitas (sehat, terdidik, punya keterampilan kerja).

    Indonesia diproyeksikan mengalami puncak bonus demografi menjelang
    **2030-2035**, dengan target besar **"Generasi Emas 2045"** -- saat
    Indonesia genap 100 tahun merdeka -- yaitu generasi muda yang unggul,
    berdaya saing, dan mampu membawa Indonesia keluar dari status negara
    berkembang.

    **Kaitan dengan dashboard ini**: bonus demografi hanya jadi berkah kalau
    pemudanya disiapkan dengan baik sejak sekarang -- lewat pendidikan,
    pelatihan keterampilan, dan lapangan kerja yang memadai. Kalau tidak,
    justru berisiko jadi "bencana demografi" (banyak usia produktif, tapi
    menganggur/tidak terampil). Dashboard ini membantu Pemkab Purworejo
    **mengidentifikasi kecamatan mana yang perlu diprioritaskan** dalam
    penyiapan pemudanya, supaya bonus demografi ini benar-benar termanfaatkan
    di tingkat kabupaten, sejalan dengan agenda nasional Generasi Emas 2045.
    """))



# ==========================================================
# 📌 KALKULASI AGREGAT TERPUSAT
# ==========================================================
# Dihitung sekali di sini, dipakai bareng oleh Ringkasan Eksekutif, Tab 1,
# dan Tab 3 -- supaya tidak ada perhitungan yang diulang/berpotensi beda hasil.
def format_id(n):
    """Format angka ala Indonesia (titik sbg pemisah ribuan) TANPA mengganggu
    tanda baca lain di kalimat -- dipakai per-angka, bukan replace massal
    di seluruh string (itu bug yang pernah bikin koma kalimat ikut berubah)."""
    return f"{n:,.0f}".replace(",", ".")


def markdown_bold_ke_html(teks):
    """⚠️ FIX BUG: markdown **tebal** TIDAK otomatis dirender jadi bold kalau
    ditaruh di dalam blok HTML mentah (st.markdown unsafe_allow_html) --
    parser Markdown memperlakukan konten di dalam tag HTML sebagai teks
    apa adanya, tidak diproses lagi jadi HTML. Fungsi ini mengonversi
    **teks** secara eksplisit jadi <b>teks</b> SEBELUM ditaruh di dalam HTML,
    supaya tetap tampil tebal dengan benar."""
    import re
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", teks)

total_penduduk = int(df["total_penduduk"].sum())
total_produktif = int(df["penduduk_15_64"].sum())
total_pemuda = int(df["pemuda_16_30"].sum())
rasio_ketergantungan_kab = round(df["penduduk_non_produktif"].sum() / total_produktif * 100, 1)

ranking = df[["kecamatan", "pemuda_16_30", "proporsi_pemuda_dari_total", "rasio_ketergantungan"]].sort_values(
    "proporsi_pemuda_dari_total", ascending=False
).reset_index(drop=True)
tertinggi = ranking.iloc[0]
terendah = ranking.iloc[-1]
rata_rata_proporsi = ranking["proporsi_pemuda_dari_total"].mean()
jumlah_di_atas_rata2 = int((ranking["proporsi_pemuda_dari_total"] > rata_rata_proporsi).sum())

# ==========================================================
# 🌟 RINGKASAN EKSEKUTIF + UNDUH LAPORAN
# ==========================================================
ringkasan_teks = (
    f"Kabupaten Purworejo memiliki **{format_id(total_penduduk)}** penduduk (estimasi terkini), dengan "
    f"**{format_id(total_produktif)}** jiwa usia produktif dan **{format_id(total_pemuda)}** jiwa pemuda (15-29 tahun). "
    f"Rasio ketergantungan kabupaten sebesar **{rasio_ketergantungan_kab}%**. "
    f"Kecamatan **{tertinggi['kecamatan']}** memiliki proporsi pemuda tertinggi "
    f"({tertinggi['proporsi_pemuda_dari_total']}%), sementara **{terendah['kecamatan']}** terendah "
    f"({terendah['proporsi_pemuda_dari_total']}%). Sebanyak **{jumlah_di_atas_rata2} dari 16 kecamatan** "
    f"berada di atas rata-rata proporsi pemuda kabupaten ({rata_rata_proporsi:.1f}%). "
    f"Rekomendasi utama: prioritaskan program pengembangan pemuda (wirausaha, pelatihan keterampilan) "
    f"di kecamatan dengan proporsi tertinggi untuk memaksimalkan potensi bonus demografi, sambil "
    f"mencermati kecamatan dengan proporsi rendah untuk kebijakan penciptaan lapangan kerja lokal."
)

st.markdown(
    f"""<div style='background:#E1F5EE;border:1px solid #0F6E56;border-radius:12px;padding:18px 20px;margin-bottom:8px;'>
<p style='margin:0 0 4px 0;font-weight:600;color:#04342C;font-family:"Plus Jakarta Sans",sans-serif;'>🌟 Ringkasan Eksekutif</p>
<p style='margin:0;color:#04342C;line-height:1.6;'>{markdown_bold_ke_html(ringkasan_teks)}</p>
</div>""",
    unsafe_allow_html=True
)

laporan_unduh = f"""RINGKASAN EKSEKUTIF -- DEMUDA PURWOREJO
Peta Potensi Demografi Pemuda Kabupaten Purworejo
==========================================================

DATA AGREGAT KABUPATEN
- Total penduduk           : {format_id(total_penduduk)}
- Usia produktif (15-64 th): {format_id(total_produktif)}
- Pemuda (15-29 th, proksi): {format_id(total_pemuda)}
- Rasio ketergantungan     : {rasio_ketergantungan_kab}%

RINGKASAN
{ringkasan_teks.replace('**', '')}

RANKING PROPORSI PEMUDA PER KECAMATAN (tertinggi ke terendah)
{ranking[['kecamatan', 'proporsi_pemuda_dari_total', 'rasio_ketergantungan']].to_string(index=False)}

==========================================================
Sumber data: BPS Kabupaten Purworejo (struktur umur kabupaten 2026 +
populasi per kecamatan, Purworejo Dalam Angka 2025). Breakdown umur per
kecamatan merupakan estimasi berbasis kepadatan penduduk -- lihat
metodologi lengkap di aplikasi.
Dibuat untuk Lomba Teknologi Piranti Lunak -- Jambore Pemuda Purworejo 2026.
"""

st.download_button(
    label="⬇️ Unduh Ringkasan Laporan (.txt)",
    data=laporan_unduh,
    file_name="ringkasan_demuda_purworejo.txt",
    mime="text/plain",
)


def buat_pdf_laporan():
    """Membuat laporan PDF ringkas menggunakan reportlab -- tidak perlu
    template eksternal apapun, seluruh isi dibuat dari data yang sudah
    dihitung di atas (total_penduduk, ranking, dll)."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = getSampleStyleSheet()
    judul_style = ParagraphStyle("Judul", parent=styles["Heading1"], textColor=pdf_colors.HexColor(PALET["teal"]))
    subjudul_style = ParagraphStyle("Sub", parent=styles["Heading2"], textColor=pdf_colors.HexColor(PALET["teal"]), fontSize=13)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=15)

    elemen = [
        Paragraph("DEMUDA Purworejo", judul_style),
        Paragraph("Peta Potensi Demografi Pemuda Kabupaten Purworejo", styles["Normal"]),
        Spacer(1, 14),
        Paragraph("Data Agregat Kabupaten", subjudul_style),
    ]
    data_tabel = [
        ["Metrik", "Nilai"],
        ["Total Penduduk", format_id(total_penduduk)],
        ["Usia Produktif (15-64 th)", format_id(total_produktif)],
        ["Pemuda (15-29 th, proksi)", format_id(total_pemuda)],
        ["Rasio Ketergantungan", f"{rasio_ketergantungan_kab}%"],
    ]
    t = Table(data_tabel, colWidths=[8 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor(PALET["teal"])),
        ("TEXTCOLOR", (0, 0), (-1, 0), pdf_colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, pdf_colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor("#F5F5F0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elemen += [t, Spacer(1, 14), Paragraph("Ringkasan", subjudul_style),
               Paragraph(markdown_bold_ke_html(ringkasan_teks), body_style), Spacer(1, 14),
               Paragraph("Ranking Proporsi Pemuda per Kecamatan", subjudul_style)]

    header = ["Kecamatan", "Proporsi Pemuda (%)", "Rasio Ketergantungan (%)"]
    rows = [header] + ranking[["kecamatan", "proporsi_pemuda_dari_total", "rasio_ketergantungan"]].values.tolist()
    t2 = Table(rows, colWidths=[6 * cm, 4.5 * cm, 4.5 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor(PALET["amber"])),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, pdf_colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor("#F5F5F0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elemen.append(t2)

    doc.build(elemen)
    buffer.seek(0)
    return buffer.getvalue()


st.download_button(
    label="⬇️ Unduh Laporan (.pdf)",
    data=buat_pdf_laporan(),
    file_name="laporan_demuda_purworejo.pdf",
    mime="application/pdf",
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Ringkasan Kabupaten",
    "🗺️ Peta & Profil Kecamatan",
    "🧑‍🤝‍🧑 Fokus Pemuda",
    "⚖️ Bandingkan Kecamatan",
    "🔮 Simulasi Proyeksi"
])
# ==========================================================
# TAB 1 -- RINGKASAN KABUPATEN
# ==========================================================
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Penduduk", format_id(total_penduduk))
    c2.metric("Usia Produktif (15-64 th)", format_id(total_produktif))
    c3.metric("Pemuda (15-29 th, proksi)", format_id(total_pemuda))
    c4.metric("Rasio Ketergantungan", f"{rasio_ketergantungan_kab}%")

    st.markdown("---")
    st.subheader("Struktur Usia Penduduk Kabupaten")

    piramida = pd.DataFrame({
        "Kelompok Usia": ["0-14 tahun (Anak)", "15-64 tahun (Produktif)", "65+ tahun (Lansia)"],
        "Jumlah": [
            int(df["penduduk_0_14"].sum()),
            int(df["penduduk_15_64"].sum()),
            int(df["penduduk_65_plus"].sum()),
        ]
    })
    fig_piramida = px.bar(
        piramida, x="Jumlah", y="Kelompok Usia", orientation="h",
        color="Kelompok Usia", text="Jumlah",
        color_discrete_sequence=[PALET["amber"], PALET["teal"], PALET["teks_sekunder"]]
    )
    fig_piramida.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_piramida, width='stretch')

    st.info(
        f"📌 **Insight otomatis:** Rasio ketergantungan kabupaten sebesar **{rasio_ketergantungan_kab}%** "
        f"artinya setiap 100 penduduk usia produktif menanggung sekitar {rasio_ketergantungan_kab:.0f} "
        f"penduduk usia non-produktif (anak & lansia)."
    )

    st.markdown("---")
    st.subheader("📈 Tren Penduduk Kabupaten (2019-2024)")
    df_historis = pd.DataFrame(DATA_HISTORIS_KABUPATEN)
    fig_historis = px.line(
        df_historis, x="tahun", y="penduduk", markers=True,
        labels={"tahun": "Tahun", "penduduk": "Jumlah Penduduk"},
        color_discrete_sequence=[PALET["teal"]]
    )
    fig_historis.update_layout(height=320)
    st.plotly_chart(fig_historis, width='stretch')
    st.caption(
        "Sumber: data total kabupaten dari laporan yang mengutip BPS Kab. Purworejo. "
        "Penurunan 2023→2024 mencerminkan kalibrasi ulang proyeksi BPS mengikuti data "
        "sensus terbaru, bukan penurunan penduduk riil."
    )

# ==========================================================
# TAB 2 -- PETA & PROFIL KECAMATAN
# ==========================================================
with tab2:
    st.subheader("Peta Sebaran Penduduk per Kecamatan")

    metrik_peta = st.selectbox(
        "Tampilkan peta berdasarkan:",
        ["total_penduduk", "rasio_ketergantungan", "proporsi_pemuda_dari_total"],
        format_func=lambda x: {
            "total_penduduk": "Total Penduduk",
            "rasio_ketergantungan": "Rasio Ketergantungan (%)",
            "proporsi_pemuda_dari_total": "Proporsi Pemuda dari Total Penduduk (%)"
        }[x]
    )

    # ⚠️ FIX AttributeError: sejak Plotly >= 5.24, px.scatter_mapbox() dihapus
    # dan diganti px.scatter_map() (basis peta baru MapLibre, bukan Mapbox lagi).
    # Kode di bawah otomatis pakai fungsi yang tersedia sesuai versi plotly
    # yang terpasang, supaya tidak error di komputer manapun.
    if hasattr(px, "scatter_map"):
        fig_map = px.scatter_map(
            df,
            lat="lat", lon="lon",
            size="total_penduduk",
            color=metrik_peta,
            hover_name="kecamatan",
            hover_data={
                "lat": False, "lon": False,
                "total_penduduk": True,
                "rasio_ketergantungan": True,
                "pemuda_16_30": True,
            },
            color_continuous_scale="OrRd",
            size_max=40,
            zoom=9.3,
            center={"lat": -7.72, "lon": 109.98},
            map_style="open-street-map",
            height=550,
        )
    else:
        fig_map = px.scatter_mapbox(
            df,
            lat="lat", lon="lon",
            size="total_penduduk",
            color=metrik_peta,
            hover_name="kecamatan",
            hover_data={
                "lat": False, "lon": False,
                "total_penduduk": True,
                "rasio_ketergantungan": True,
                "pemuda_16_30": True,
            },
            color_continuous_scale="OrRd",
            size_max=40,
            zoom=9.3,
            center={"lat": -7.72, "lon": 109.98},
            mapbox_style="open-street-map",
            height=550,
        )
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # ⚡ FITUR INTERAKTIF: klik salah satu titik di peta untuk lihat kartu
    # detail kecamatan -- pakai fitur "selection event" bawaan Streamlit
    # (on_select), tidak perlu library tambahan.
    peta_event = st.plotly_chart(
        fig_map, width='stretch', on_select="rerun", selection_mode="points", key="peta_klik"
    )
    st.caption(
        "Ukuran lingkaran = total penduduk. Warna = metrik yang dipilih. "
        "Koordinat merupakan titik pusat administratif tiap kecamatan. "
        "💡 Klik salah satu titik untuk melihat detail kecamatan."
    )

    poin_terpilih = peta_event.selection.points if peta_event and peta_event.selection else []
    if poin_terpilih:
        idx_terpilih = poin_terpilih[0]["point_index"]
        kec_detail = df.iloc[idx_terpilih]
        st.markdown(
            f"""<div style='background:#FAEEDA;border:1px solid #BA7517;border-radius:12px;padding:16px 20px;margin-top:4px;'>
<p style='margin:0 0 6px 0;font-weight:600;color:#412402;font-family:"Plus Jakarta Sans",sans-serif;'>📍 Detail Kecamatan {kec_detail['kecamatan']}</p>
<p style='margin:0;color:#412402;'>Total Penduduk: <b>{format_id(int(kec_detail['total_penduduk']))}</b> &nbsp;|&nbsp; Usia Produktif: <b>{format_id(int(kec_detail['penduduk_15_64']))}</b> &nbsp;|&nbsp; Pemuda: <b>{format_id(int(kec_detail['pemuda_16_30']))}</b> ({kec_detail['proporsi_pemuda_dari_total']}%) &nbsp;|&nbsp; Rasio Ketergantungan: <b>{kec_detail['rasio_ketergantungan']}%</b></p>
</div>""",
            unsafe_allow_html=True
        )
    else:
        st.caption("Belum ada kecamatan yang dipilih -- klik salah satu titik di peta di atas.")

    st.markdown("---")
    st.subheader("Tabel Profil Lengkap per Kecamatan")
    tabel_tampil = df[[
        "kecamatan", "total_penduduk", "penduduk_15_64",
        "rasio_ketergantungan", "pemuda_16_30", "proporsi_pemuda_dari_total"
    ]].sort_values("total_penduduk", ascending=False).reset_index(drop=True)
    tabel_tampil.columns = [
        "Kecamatan", "Total Penduduk", "Usia Produktif",
        "Rasio Ketergantungan (%)", "Pemuda 15-29 th (proksi)", "Proporsi Pemuda (%)"
    ]
    st.dataframe(tabel_tampil, width='stretch', hide_index=True)

# ==========================================================
# TAB 3 -- FOKUS PEMUDA
# ==========================================================
with tab3:
    st.subheader("Ranking Kecamatan Berdasarkan Potensi Pemuda")

    fig_rank = px.bar(
        ranking, x="proporsi_pemuda_dari_total", y="kecamatan",
        orientation="h", text="proporsi_pemuda_dari_total",
        color="proporsi_pemuda_dari_total",
        color_continuous_scale="Teal",
        labels={"proporsi_pemuda_dari_total": "Proporsi Pemuda (%)", "kecamatan": "Kecamatan"}
    )
    fig_rank.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_rank.update_layout(height=550, yaxis={"categoryorder": "total ascending"}, showlegend=False)
    st.plotly_chart(fig_rank, width='stretch')

    # ------------------------------------------------------
    # 🧠 INSIGHT OTOMATIS RULE-BASED (bukan AI generatif)
    # Sengaja dibuat rule-based, bukan panggil LLM/API eksternal,
    # supaya dashboard ini TIDAK bergantung pada server/koneksi luar
    # apapun -- selalu jalan walau offline sekalipun (setelah data dimuat).
    # ------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 Insight Otomatis")

    st.success(
        f"🏆 **{tertinggi['kecamatan']}** memiliki proporsi pemuda tertinggi "
        f"({tertinggi['proporsi_pemuda_dari_total']}% dari total penduduk) -- "
        f"berpotensi menjadi prioritas program pengembangan wirausaha muda, "
        f"pelatihan keterampilan, atau ruang kreatif pemuda."
    )
    st.warning(
        f"⚠️ **{terendah['kecamatan']}** memiliki proporsi pemuda terendah "
        f"({terendah['proporsi_pemuda_dari_total']}% dari total penduduk) -- "
        f"perlu dicermati apakah ada migrasi keluar usia muda (urbanisasi ke kota lain) "
        f"yang perlu direspons dengan kebijakan penciptaan lapangan kerja lokal."
    )
    st.info(
        f"📌 Rata-rata proporsi pemuda se-Kabupaten Purworejo: **{rata_rata_proporsi:.1f}%**. "
        f"Ada **{jumlah_di_atas_rata2} dari 16 kecamatan** "
        f"yang berada di atas rata-rata kabupaten."
    )

# ==========================================================
# TAB 4 -- BANDINGKAN KECAMATAN
# ==========================================================
with tab4:
    st.subheader("Bandingkan 2 Kecamatan Berdampingan")

    daftar_kecamatan = sorted(df["kecamatan"].tolist())
    colA, colB = st.columns(2)
    with colA:
        kec_a = st.selectbox("Kecamatan pertama:", daftar_kecamatan, index=daftar_kecamatan.index("Purworejo"))
    with colB:
        default_b = "Kaligesing" if "Kaligesing" in daftar_kecamatan else daftar_kecamatan[-1]
        kec_b = st.selectbox("Kecamatan kedua:", daftar_kecamatan, index=daftar_kecamatan.index(default_b))

    if kec_a == kec_b:
        # ⚠️ FIX BUG: tanpa pengecekan ini, membandingkan kecamatan dengan
        # dirinya sendiri menghasilkan kalimat aneh ("X dan X relatif setara")
        # dan radar chart dengan dua bentuk numpuk sempurna -- bingungkan
        # pengguna. Hentikan lebih awal dengan pesan yang jelas.
        st.warning("⚠️ Pilih dua kecamatan yang berbeda untuk membandingkan.")
    else:
        baris_a = df[df["kecamatan"] == kec_a].iloc[0]
        baris_b = df[df["kecamatan"] == kec_b].iloc[0]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"#### {kec_a}")
            st.metric("Total Penduduk", format_id(int(baris_a["total_penduduk"])))
            st.metric("Proporsi Pemuda", f"{baris_a['proporsi_pemuda_dari_total']}%")
            st.metric("Rasio Ketergantungan", f"{baris_a['rasio_ketergantungan']}%")
        with c2:
            st.markdown(f"#### {kec_b}")
            st.metric("Total Penduduk", format_id(int(baris_b["total_penduduk"])))
            st.metric("Proporsi Pemuda", f"{baris_b['proporsi_pemuda_dari_total']}%")
            st.metric("Rasio Ketergantungan", f"{baris_b['rasio_ketergantungan']}%")

        st.markdown("---")
        st.subheader("Radar Perbandingan (skala relatif terhadap kabupaten)")

        # Normalisasi tiap metrik terhadap rentang min-maks seluruh kecamatan,
        # supaya bentuk radar tetap terbaca meski satuan tiap metrik beda jauh.
        metrik_radar = ["total_penduduk", "kepadatan", "proporsi_pemuda_dari_total", "rasio_ketergantungan"]
        label_radar = ["Total Penduduk", "Kepadatan", "Proporsi Pemuda", "Rasio Ketergantungan"]
        min_vals = df[metrik_radar].min()
        max_vals = df[metrik_radar].max()

        def skala_radar(baris):
            return [
                ((baris[m] - min_vals[m]) / (max_vals[m] - min_vals[m]) * 100) if max_vals[m] > min_vals[m] else 50
                for m in metrik_radar
            ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=skala_radar(baris_a) + [skala_radar(baris_a)[0]],
            theta=label_radar + [label_radar[0]],
            fill="toself", name=kec_a, line_color=PALET["teal"]
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=skala_radar(baris_b) + [skala_radar(baris_b)[0]],
            theta=label_radar + [label_radar[0]],
            fill="toself", name=kec_b, line_color=PALET["amber"]
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
            height=450, showlegend=True
        )
        st.plotly_chart(fig_radar, width='stretch')
        st.caption(
            "Nilai pada radar dinormalisasi 0-100% relatif terhadap kecamatan tertinggi/terendah "
            "se-kabupaten untuk tiap metrik -- bukan skala absolut, tapi untuk membandingkan posisi relatif."
        )

        # --- Insight otomatis perbandingan ---
        selisih_pemuda = baris_a["proporsi_pemuda_dari_total"] - baris_b["proporsi_pemuda_dari_total"]
        if abs(selisih_pemuda) < 0.5:
            st.info(f"📌 Proporsi pemuda **{kec_a}** dan **{kec_b}** relatif setara (selisih {abs(selisih_pemuda):.1f}%).")
        elif selisih_pemuda > 0:
            st.info(
                f"📌 **{kec_a}** memiliki proporsi pemuda {abs(selisih_pemuda):.1f}% lebih tinggi dibanding "
                f"**{kec_b}** -- bisa jadi acuan praktik baik yang mungkin relevan diterapkan di {kec_b}."
            )
        else:
            st.info(
                f"📌 **{kec_b}** memiliki proporsi pemuda {abs(selisih_pemuda):.1f}% lebih tinggi dibanding "
                f"**{kec_a}** -- bisa jadi acuan praktik baik yang mungkin relevan diterapkan di {kec_a}."
            )

# ==========================================================
# TAB 5 -- WHATIF
# ==========================================================
with tab5:
    st.set_page_config(page_title="What-If Demografi", page_icon="🧪", layout="wide")
    
    PALET = {"teal": "#0F6E56", "amber": "#EF9F27"}

    # --- Data sama persis dengan app_demografi.py, supaya hasil uji representatif ---
    DATA_DASAR_KECAMATAN = [
        ("Bagelen",      30965,  63.44),
        ("Banyuurip",    44221,  47.78),
        ("Bayan",        53220,  44.66),
        ("Bener",        58913, 102.44),
        ("Bruno",        55454, 105.68),
        ("Butuh",        42998,  47.21),
        ("Gebang",       44525,  70.51),
        ("Grabag",       51175,  67.80),
        ("Kaligesing",   32564,  78.33),
        ("Kemiri",       61008, 103.15),
        ("Kutoarjo",     63172,  39.20),
        ("Loano",        39201,  53.51),
        ("Ngombol",      36202,  59.33),
        ("Pituruh",      53095,  89.01),
        ("Purwodadi",    42725,  56.15),
        ("Purworejo",    85595,  53.25),
    ]

    P_PRODUKTIF_KAB = 0.674702
    P_LANSIA_KAB = 0.123679
    PEMUDA_DARI_PRODUKTIF = 0.216137 / 0.674702


    @st.cache_data
    def load_data():
        df = pd.DataFrame(DATA_DASAR_KECAMATAN, columns=["kecamatan", "total_penduduk", "luas_km2"])
        df["kepadatan"] = df["total_penduduk"] / df["luas_km2"]
        kepadatan_rata2_kab = df["total_penduduk"].sum() / df["luas_km2"].sum()
        z = (df["kepadatan"] / kepadatan_rata2_kab) - 1
        z_clipped = z.clip(-0.4, 0.4)
        produktif_share = (P_PRODUKTIF_KAB * (1 + 0.12 * z_clipped)).clip(0.60, 0.75)
        lansia_share = (P_LANSIA_KAB * (1 - 0.15 * z_clipped)).clip(0.08, 0.18)
        pemuda_share = produktif_share * PEMUDA_DARI_PRODUKTIF
        df["pemuda_16_30"] = (df["total_penduduk"] * pemuda_share).round().astype(int)
        return df
    
    
    df = load_data()

    st.title("🧪 Uji Coba: Simulasi Proyeksi Pemuda")
    
    # ==========================================================
    # FITUR WHAT-IF
    # ==========================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        kecamatan_pilihan = st.selectbox(
            "Pilih kecamatan:",
            ["Se-Kabupaten (semua kecamatan)"] + sorted(df["kecamatan"].tolist())
        )
    
    with col2:
        tingkat_pertumbuhan = st.slider(
            "Asumsi pertumbuhan penduduk/tahun (%):",
            min_value=-2.0, max_value=5.0, value=1.2, step=0.1
        )
    
    with col3:
        jumlah_tahun = st.slider("Proyeksi berapa tahun ke depan?", min_value=1, max_value=25, value=10)
    
    # --- Ambil populasi awal sesuai pilihan ---
    if kecamatan_pilihan == "Se-Kabupaten (semua kecamatan)":
        populasi_awal = df["total_penduduk"].sum()
        pemuda_awal = df["pemuda_16_30"].sum()
    else:
        baris = df[df["kecamatan"] == kecamatan_pilihan].iloc[0]
        populasi_awal = baris["total_penduduk"]
        pemuda_awal = baris["pemuda_16_30"]
    
    # --- Rumus pertumbuhan majemuk ---
    tahun_list = list(range(0, jumlah_tahun + 1))
    proyeksi_list = []
    for tahun in tahun_list:
        faktor = (1 + tingkat_pertumbuhan / 100) ** tahun
        proyeksi_list.append({
            "tahun": tahun,
            "populasi": populasi_awal * faktor,
            "pemuda": pemuda_awal * faktor,
        })
    df_proyeksi = pd.DataFrame(proyeksi_list)
    
    # --- Visualisasi ---
    fig = px.line(
        df_proyeksi, x="tahun", y=["populasi", "pemuda"],
        labels={"value": "Jumlah penduduk", "tahun": "Tahun ke depan", "variable": "Kategori"},
        color_discrete_sequence=[PALET["teal"], PALET["amber"]],
        markers=True,
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, width='stretch')
    
    # --- Insight otomatis (peka terhadap besaran perubahan) ---
    def format_id(n):
        return f"{n:,.0f}".replace(",", ".")
    
    populasi_akhir = df_proyeksi.iloc[-1]["populasi"]
    pemuda_akhir = df_proyeksi.iloc[-1]["pemuda"]
    persen_perubahan_pemuda = (pemuda_akhir - pemuda_awal) / pemuda_awal * 100
    magnitudo = abs(persen_perubahan_pemuda)
    naik = persen_perubahan_pemuda >= 0
    
    info_dasar = (
        f"populasi pemuda di **{kecamatan_pilihan}** diproyeksikan dari sekitar "
        f"**{format_id(pemuda_awal)}** menjadi **{format_id(pemuda_akhir)} jiwa** "
        f"dalam {jumlah_tahun} tahun (asumsi pertumbuhan {tingkat_pertumbuhan}%/tahun)"
    )
    
    if magnitudo < 3:
        if naik:
            pesan = f"Relatif stabil -- {info_dasar}, naik tipis {persen_perubahan_pemuda:.1f}%. Belum ada tekanan berarti terhadap kebutuhan fasilitas pemuda dalam skenario ini."
        else:
            pesan = f"Relatif stabil -- {info_dasar}, turun tipis {magnitudo:.1f}%. Perubahan masih dalam rentang wajar, belum mengindikasikan tren migrasi keluar yang signifikan."
    elif magnitudo < 15:
        if naik:
            pesan = f"Tumbuh cukup nyata -- {info_dasar} (+{persen_perubahan_pemuda:.1f}%). Perlu mulai dipikirkan penambahan kapasitas lapangan kerja dan ruang aktivitas pemuda secara bertahap."
        else:
            pesan = f"Menurun cukup nyata -- {info_dasar} ({persen_perubahan_pemuda:.1f}%). Pola ini layak dicermati sebagai kemungkinan awal tren migrasi keluar pemuda."
    else:
        if naik:
            pesan = f"Melonjak signifikan -- {info_dasar} (+{persen_perubahan_pemuda:.1f}%). Lonjakan sebesar ini perlu direspons dengan perencanaan serius: perluasan lapangan kerja, pelatihan keterampilan, dan fasilitas publik untuk pemuda."
        else:
            pesan = f"Menyusut tajam -- {info_dasar} ({persen_perubahan_pemuda:.1f}%). Penyusutan setajam ini mengindikasikan potensi migrasi keluar pemuda yang serius dan perlu ditindaklanjuti dengan kajian lebih lanjut."
    
    if naik:
        st.success(f"📌 {pesan}")
    else:
        st.warning(f"📌 {pesan}")
    
    st.caption(
        "⚠️ Proyeksi ini adalah simulasi sederhana berbasis asumsi pertumbuhan linear "
        "(compound growth), bukan model demografi penuh -- belum memperhitungkan "
        "migrasi, mortalitas, atau fertilitas secara terpisah."
    )
    
    # --- Tabel detail (untuk cek angka per tahun saat validasi) ---
    with st.expander("🔍 Lihat tabel proyeksi per tahun (untuk validasi)"):
        tabel = df_proyeksi.copy()
        tabel["populasi"] = tabel["populasi"].round(0).astype(int)
        tabel["pemuda"] = tabel["pemuda"].round(0).astype(int)
        st.dataframe(tabel, width='stretch', hide_index=True)


# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption(
    "Dibuat untuk Lomba Teknologi Piranti Lunak -- Jambore Pemuda Tingkat "
    "Kabupaten Purworejo 2026. Sumber data: BPS Kabupaten Purworejo "
    "(struktur umur kabupaten 2026 + populasi per kecamatan, Purworejo Dalam Angka 2025)."
)
