import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# KONFIGURASI HALAMAN
# ==========================================================
st.set_page_config(
    page_title="DEMUDA Purworejo",
    page_icon="🗺️",
    layout="wide"
)

# ==========================================================
# 🎨 IDENTITAS VISUAL -- palet warna, tipografi, & logo
# ==========================================================
# Palet warna:
#   - Teal  #0F6E56 (utama, kesan resmi/data terpercaya) -- dipakai untuk
#     header, ikon peta, dan elemen struktural.
#   - Amber #EF9F27 / #BA7517 (aksen, energi & semangat muda) -- dipakai
#     untuk elemen data/grafik yang berkaitan dengan pemuda.
#   - Abu gelap #2C2C2A (teks utama), abu muda #5F5E5A (teks sekunder).
# Tipografi: "Plus Jakarta Sans" untuk judul (modern, geometris, cocok
# nuansa data/teknologi), "Inter" untuk teks isi (sangat mudah dibaca).
# Kedua font gratis dari Google Fonts.

PALET = {
    "teal": "#0F6E56",
    "teal_muda": "#5DCAA5",
    "amber": "#EF9F27",
    "amber_gelap": "#BA7517",
    "teks_utama": "#2C2C2A",
    "teks_sekunder": "#5F5E5A",
}

LOGO_SVG = """
<svg width="96" height="96" viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg">
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
    st.markdown("""
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
    """)

tab1, tab2, tab3 = st.tabs([
    "📊 Ringkasan Kabupaten",
    "🗺️ Peta & Profil Kecamatan",
    "🧑‍🤝‍🧑 Fokus Pemuda"
])
# ==========================================================
# TAB 1 -- RINGKASAN KABUPATEN
# ==========================================================
with tab1:
    total_penduduk = int(df["total_penduduk"].sum())
    total_produktif = int(df["penduduk_15_64"].sum())
    total_pemuda = int(df["pemuda_16_30"].sum())
    rasio_ketergantungan_kab = round(df["penduduk_non_produktif"].sum() / total_produktif * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Penduduk", f"{total_penduduk:,}".replace(",", "."))
    c2.metric("Usia Produktif (15-64 th)", f"{total_produktif:,}".replace(",", "."))
    c3.metric("Pemuda (15-29 th, proksi)", f"{total_pemuda:,}".replace(",", "."))
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
    st.plotly_chart(fig_map, width='stretch')
    st.caption(
        "Ukuran lingkaran = total penduduk. Warna = metrik yang dipilih. "
        "Koordinat merupakan titik pusat administratif tiap kecamatan."
    )

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

    ranking = df[["kecamatan", "pemuda_16_30", "proporsi_pemuda_dari_total"]].sort_values(
        "proporsi_pemuda_dari_total", ascending=False
    ).reset_index(drop=True)

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

    tertinggi = ranking.iloc[0]
    terendah = ranking.iloc[-1]
    rata_rata_proporsi = ranking["proporsi_pemuda_dari_total"].mean()

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
        f"Ada **{(ranking['proporsi_pemuda_dari_total'] > rata_rata_proporsi).sum()} dari 16 kecamatan** "
        f"yang berada di atas rata-rata kabupaten."
    )

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption(
    "Dibuat untuk Lomba Teknologi Piranti Lunak -- Jambore Pemuda Tingkat "
    "Kabupaten Purworejo 2026. Sumber data: BPS Kabupaten Purworejo "
    "(struktur umur kabupaten 2026 + populasi per kecamatan, Purworejo Dalam Angka 2025)."
)
