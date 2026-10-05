"""Tab 4: Bandingkan dua kecamatan (kartu, radar, insight)."""

import plotly.graph_objects as go
import streamlit as st

from .hitung import LABEL_RADAR, buat_skala_radar, format_id
from .konfigurasi import PALET


def tampilkan(df, r):
    """Isi Tab 4. df = tabel kecamatan, r = hasil hitung_ringkasan(df)."""
    st.subheader("Bandingkan 2 Kecamatan Berdampingan")

    daftar_kecamatan = sorted(df["kecamatan"].tolist())
    colA, colB = st.columns(2)
    with colA:
        kec_a = st.selectbox("Kecamatan pertama:", daftar_kecamatan, index=daftar_kecamatan.index("Purworejo"),
                             help="Pilih kecamatan yang ingin dibandingkan. Harus berbeda dengan kecamatan kedua.")
    with colB:
        default_b = "Kaligesing" if "Kaligesing" in daftar_kecamatan else daftar_kecamatan[-1]
        kec_b = st.selectbox("Kecamatan kedua:", daftar_kecamatan, index=daftar_kecamatan.index(default_b),
                             help="Pilih pembanding. Hasil ditampilkan berdampingan beserta grafik radar.")

    if kec_a == kec_b:
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

        label_radar = LABEL_RADAR
        skala_radar = buat_skala_radar(df)

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=skala_radar(baris_a) + [skala_radar(baris_a)[0]],
            theta=label_radar + [label_radar[0]],
            fill="toself", name=kec_a, line_color=PALET["teal"], line_width=2.5,
            fillcolor="rgba(15,110,86,0.35)", marker=dict(size=6)
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=skala_radar(baris_b) + [skala_radar(baris_b)[0]],
            theta=label_radar + [label_radar[0]],
            fill="toself", name=kec_b, line_color=PALET["amber"], line_width=2.5,
            fillcolor="rgba(239,159,39,0.35)", marker=dict(size=6)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(
                visible=True, range=[0, 100], showticklabels=True,
                tickvals=[0, 25, 50, 75, 100], ticksuffix="%"
            )),
            height=480, showlegend=True
        )
        st.plotly_chart(fig_radar, width='stretch')
        st.caption(
            "Nilai pada radar dinormalisasi 0-100% relatif terhadap kecamatan tertinggi/terendah "
            "se-kabupaten untuk tiap metrik -- bukan skala absolut, tapi untuk membandingkan posisi relatif. "
            "Area yang tumpang tindih (transparan) menunjukkan kemiripan antar kecamatan."
        )

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
