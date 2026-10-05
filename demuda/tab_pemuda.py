"""Tab 3: Fokus Pemuda (ranking dan insight otomatis)."""

import plotly.express as px
import streamlit as st


def tampilkan(df, r):
    """Isi Tab 3. df = tabel kecamatan, r = hasil hitung_ringkasan(df)."""
    ranking = r.ranking
    tertinggi = r.tertinggi
    terendah = r.terendah
    rata_rata_proporsi = r.rata_rata_proporsi
    jumlah_di_atas_rata2 = r.jumlah_di_atas_rata2

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
