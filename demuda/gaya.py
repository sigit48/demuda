"""Semua HTML dan CSS aplikasi (tampilan), dipisah dari rumus.

Setiap fungsi mengembalikan teks HTML; pemanggilnya (app_demografi.py dan
modul tab) yang menampilkannya dengan st.markdown(..., unsafe_allow_html=True).
"""

from .konfigurasi import PALET, LOGO_SVG
from .hitung import format_id


def css_global():
    """CSS tema: font, kartu metrik, warna tab."""
    return f"""
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
"""


def html_header():
    """Logo + judul aplikasi di bagian atas."""
    return f"""
{LOGO_SVG}
<div>
<h1 style='margin:0;line-height:1.1;'>DEMUDA Purworejo</h1>
<p style='margin:2px 0 0 0;color:{PALET["teks_sekunder"]};font-size:15px;'>Peta Potensi Demografi Pemuda Kabupaten Purworejo</p>
</div>
</div>"""


def html_ringkasan_eksekutif(teks_html):
    """Kotak hijau Ringkasan Eksekutif. teks_html sudah berformat <b>."""
    return f"""<div style='background:#E1F5EE;border:1px solid #0F6E56;border-radius:12px;padding:18px 20px;margin-bottom:8px;'>
<p style='margin:0 0 4px 0;font-weight:600;color:#04342C;font-family:"Plus Jakarta Sans",sans-serif;'>🌟 Ringkasan Eksekutif</p>
<p style='margin:0;color:#04342C;line-height:1.6;'>{teks_html}</p>
</div>"""


def html_detail_kecamatan(kec):
    """Kartu kuning detail kecamatan saat titik peta diklik. kec = satu baris DataFrame."""
    return f"""<div style='background:#FAEEDA;border:1px solid #BA7517;border-radius:12px;padding:16px 20px;margin-top:4px;'>
<p style='margin:0 0 6px 0;font-weight:600;color:#412402;font-family:"Plus Jakarta Sans",sans-serif;'>📍 Detail Kecamatan {kec['kecamatan']}</p>
<p style='margin:0;color:#412402;'>Total Penduduk: <b>{format_id(int(kec['total_penduduk']))}</b> &nbsp;|&nbsp; Usia Produktif: <b>{format_id(int(kec['penduduk_15_64']))}</b> &nbsp;|&nbsp; Pemuda: <b>{format_id(int(kec['pemuda_16_30']))}</b> ({kec['proporsi_pemuda_dari_total']}%) &nbsp;|&nbsp; Rasio Ketergantungan: <b>{kec['rasio_ketergantungan']}%</b></p>
</div>"""
