"""Tab 1: Ringkasan Kabupaten (kartu angka, struktur usia, dua grafik tren)."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .data import DATA_HISTORIS_KABUPATEN, DATA_STRUKTUR_UMUR_HISTORIS
from .hitung import format_id, hitung_tren_penduduk
from .konfigurasi import PALET


def tampilkan(df, r):
    """Isi Tab 1. df = tabel kecamatan, r = hasil hitung_ringkasan(df)."""
    total_penduduk = r.total_penduduk
    total_produktif = r.total_produktif
    total_pemuda = r.total_pemuda
    rasio_ketergantungan_kab = r.rasio_ketergantungan_kab

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
    st.subheader("📈 Tren Penduduk Kabupaten (2020-2026)")
    df_historis = pd.DataFrame(DATA_HISTORIS_KABUPATEN)
    fig_historis = px.line(
        df_historis, x="tahun", y="penduduk", markers=True,
        labels={"tahun": "Tahun", "penduduk": "Jumlah Penduduk", "sumber": "Sumber"},
        hover_data={"sumber": True},
        color_discrete_sequence=[PALET["teal"]]
    )
    fig_historis.update_xaxes(type="category")
    fig_historis.update_layout(height=320)
    st.plotly_chart(fig_historis, width='stretch')

    tambahan_tren, persen_tren, laju_tren = hitung_tren_penduduk(df_historis)
    st.info(
        f"📌 **Insight otomatis:** Dari 2020 ke 2026 penduduk Kabupaten Purworejo bertambah sekitar "
        f"**{format_id(tambahan_tren)} jiwa** ({persen_tren:.1f}%), "
        f"atau rata-rata **{laju_tren:.2f}% per tahun**. Laju ini dihitung dari titik awal dan akhir "
        f"saja (2020 dan 2026), yang berasal dari seri data BPS yang sama."
    )
    st.caption(
        "Sumber: BPS Kabupaten Purworejo (tabel \"Jumlah Penduduk menurut Kecamatan\" edisi 2020, 2022, "
        "2023-2024, dan tabel kelompok umur edisi 2025-2026) serta Open Data Kabupaten Purworejo "
        "(Tabel 12.1.b, hanya data tahun 2021, karena data 2021 tidak tersedia di situs BPS). "
        "Catatan: (1) edisi 2023 dan 2024 berisi angka identik, sehingga digabung menjadi satu titik; "
        "(2) data 2021 berasal dari portal dan tabel yang berbeda dengan tahun lain, sehingga lonjakan 2021 "
        "lalu penurunan 2022 sebagian mencerminkan perbedaan basis penghitungan antar tabel, bukan "
        "perubahan penduduk riil."
    )

    st.markdown("---")
    st.subheader("👥 Tren Struktur Umur Kabupaten (2023-2026)")
    df_struktur_historis = pd.DataFrame(DATA_STRUKTUR_UMUR_HISTORIS)
    fig_struktur = go.Figure()
    fig_struktur.add_trace(go.Scatter(
        x=df_struktur_historis["label"], y=df_struktur_historis["rasio_ketergantungan"],
        name="Rasio Ketergantungan (%)", mode="lines+markers",
        line=dict(color=PALET["teal"], width=3)
    ))
    fig_struktur.add_trace(go.Scatter(
        x=df_struktur_historis["label"], y=df_struktur_historis["pemuda_pct"],
        name="Proporsi Pemuda (%)", mode="lines+markers",
        line=dict(color=PALET["amber"], width=3)
    ))
    fig_struktur.update_layout(height=320, yaxis_title="Persen (%)", legend=dict(orientation="h", y=-0.2))
    fig_struktur.update_xaxes(type="category")
    st.plotly_chart(fig_struktur, width='stretch')

    rasio_awal = df_struktur_historis.iloc[0]["rasio_ketergantungan"]
    rasio_akhir = df_struktur_historis.iloc[-1]["rasio_ketergantungan"]
    pemuda_awal_pct = df_struktur_historis.iloc[0]["pemuda_pct"]
    pemuda_akhir_pct = df_struktur_historis.iloc[-1]["pemuda_pct"]
    st.warning(
        f"📌 **Insight otomatis (berbasis data resmi multi-tahun BPS, bukan estimasi):** "
        f"Rasio ketergantungan kabupaten naik dari {rasio_awal}% ({df_struktur_historis.iloc[0]['label']}) "
        f"menjadi {rasio_akhir}% ({df_struktur_historis.iloc[-1]['label']}), sementara proporsi pemuda "
        f"justru turun dari {pemuda_awal_pct}% menjadi {pemuda_akhir_pct}% pada periode yang sama. "
        f"Tren ini mengindikasikan struktur penduduk Purworejo mulai menua secara bertahap -- "
        f"memperkuat urgensi program penyiapan pemuda **sebelum jendela bonus demografi menyempit**."
    )
    st.caption(
        "Sumber: 4 file resmi BPS \"Jumlah Penduduk Menurut Kelompok Umur dan Jenis Kelamin\" "
        "edisi 2023-2026 -- satu sumber konsisten untuk seluruh rentang tahun. Data edisi 2023 "
        "dan 2024 identik (BPS belum memperbarui proyeksi antar rilis), sehingga digabung jadi "
        "satu titik \"2023-2024\"."
    )
