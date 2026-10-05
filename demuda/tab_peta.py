"""Tab 2: Peta interaktif dan tabel profil kecamatan."""

import plotly.express as px
import streamlit as st

from .gaya import html_detail_kecamatan


def tampilkan(df, r):
    """Isi Tab 2. df = tabel kecamatan, r = hasil hitung_ringkasan(df)."""
    st.subheader("Peta Sebaran Penduduk per Kecamatan")

    metrik_peta = st.selectbox(
        "Tampilkan peta berdasarkan:",
        ["total_penduduk", "rasio_ketergantungan", "proporsi_pemuda_dari_total"],
        help="Mengubah warna lingkaran di peta. Ukuran lingkaran selalu menunjukkan total penduduk.",
        format_func=lambda x: {
            "total_penduduk": "Total Penduduk",
            "rasio_ketergantungan": "Rasio Ketergantungan (%)",
            "proporsi_pemuda_dari_total": "Proporsi Pemuda dari Total Penduduk (%)"
        }[x]
    )

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
            height=650,
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
            height=650,
        )
    fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

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
        st.markdown(html_detail_kecamatan(kec_detail), unsafe_allow_html=True)
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
