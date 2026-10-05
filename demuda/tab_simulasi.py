"""Tab 5: Simulasi Proyeksi Pemuda (What-If).

Pengguna memilih wilayah, asumsi pertumbuhan penduduk per tahun, dan lama proyeksi.
Rumus: nilai tahun ke-n = nilai awal x (1 + laju/100) ** n  (pertumbuhan majemuk).
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from .hitung import format_id
from .konfigurasi import PALET

SEMUA = "Se-Kabupaten (semua kecamatan)"


def tampilkan(df, r):
    """Isi Tab 5. df = tabel kecamatan, r = hasil hitung_ringkasan(df)."""
    st.subheader("🔮 Simulasi Proyeksi Pemuda (What-If)")

    # ==========================================================
    # FITUR WHAT-IF
    # ==========================================================
    col1, col2, col3 = st.columns(3)

    with col1:
        kecamatan_pilihan = st.selectbox(
            "Pilih kecamatan:",
            [SEMUA] + sorted(df["kecamatan"].tolist()),
            help="Pilih cakupan simulasi: seluruh kabupaten atau satu kecamatan.",
        )

    with col2:
        tingkat_pertumbuhan = st.slider(
            "Asumsi pertumbuhan penduduk/tahun (%):",
            min_value=-2.0, max_value=5.0, value=1.2, step=0.1,
            help="Nilai negatif = penduduk menyusut (misalnya karena migrasi keluar). "
                 "Nilai positif = penduduk bertambah.",
        )

    with col3:
        jumlah_tahun = st.slider(
            "Proyeksi berapa tahun ke depan?",
            min_value=1, max_value=25, value=10,
            help="Rentang waktu simulasi, dari 1 sampai 25 tahun.",
        )

    # --- Ambil populasi awal sesuai pilihan ---
    if kecamatan_pilihan == SEMUA:
        populasi_awal = df["total_penduduk"].sum()
        pemuda_awal = df["pemuda_16_30"].sum()
    else:
        baris = df[df["kecamatan"] == kecamatan_pilihan].iloc[0]
        populasi_awal = baris["total_penduduk"]
        pemuda_awal = baris["pemuda_16_30"]

    # --- Hitung proyeksi tahun demi tahun (rumus pertumbuhan majemuk) ---
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

    # --- Kesimpulan otomatis (ambang: <3% stabil, 3-15% cukup nyata, >=15% signifikan) ---
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
        "⚠️ Proyeksi ini adalah simulasi sederhana berbasis asumsi pertumbuhan majemuk "
        "(compound growth) dengan laju tetap, bukan model demografi penuh -- belum "
        "memperhitungkan migrasi, mortalitas, atau fertilitas secara terpisah."
    )

    # --- Tabel detail ---
    with st.expander("🔍 Lihat tabel proyeksi per tahun (untuk validasi)"):
        tabel = df_proyeksi.copy()
        tabel["populasi"] = tabel["populasi"].round(0).astype(int)
        tabel["pemuda"] = tabel["pemuda"].round(0).astype(int)
        st.dataframe(tabel, width='stretch', hide_index=True)
