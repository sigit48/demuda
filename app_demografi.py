import streamlit as st

from demuda import bantuan, laporan, tab_bandingkan, tab_pemuda, tab_peta, tab_ringkasan
from demuda.data import load_data
from demuda.gaya import css_global, html_header, html_ringkasan_eksekutif
from demuda.hitung import hitung_ringkasan, markdown_bold_ke_html

st.set_page_config(
    page_title="DEMUDA Purworejo",
    page_icon="🗺️",
    layout="wide"
)

st.markdown(css_global(), unsafe_allow_html=True)
st.markdown(html_header(), unsafe_allow_html=True)

df = load_data()

st.caption(
    "Dashboard analisis struktur usia penduduk per kecamatan untuk mendukung "
    "perencanaan program kepemudaan yang tepat sasaran. Data bersumber dari BPS "
    "Kabupaten Purworejo (lihat metodologi di bawah)."
)

# --- Dokumentasi dan bantuan ---
bantuan.tampilkan_panduan()
bantuan.tampilkan_sidebar()
bantuan.tampilkan_metodologi()
bantuan.tampilkan_konteks()

# --- Ringkasan Eksekutif dan laporan unduhan ---
r = hitung_ringkasan(df)
st.markdown(html_ringkasan_eksekutif(markdown_bold_ke_html(r.ringkasan_teks)), unsafe_allow_html=True)
laporan.tampilkan_tombol_unduh(r)

# --- Tab ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ringkasan Kabupaten",
    "🗺️ Peta & Profil Kecamatan",
    "🧑‍🤝‍🧑 Fokus Pemuda",
    "⚖️ Bandingkan Kecamatan",
    # "🔮 Simulasi Proyeksi",
])
with tab1:
    tab_ringkasan.tampilkan(df, r)
with tab2:
    tab_peta.tampilkan(df, r)
with tab3:
    tab_pemuda.tampilkan(df, r)
with tab4:
    tab_bandingkan.tampilkan(df, r)



st.markdown("---")
st.caption(
    "Dibuat untuk Lomba Teknologi Piranti Lunak -- Jambore Pemuda Tingkat "
    "Kabupaten Purworejo 2026. Sumber data: BPS Kabupaten Purworejo "
    "(struktur umur kabupaten 2026 + populasi per kecamatan 2026)."
)
