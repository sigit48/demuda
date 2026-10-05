"""Rumus dan perhitungan ringkasan (tanpa HTML).

- format_id, markdown_bold_ke_html : pembantu format
- hitung_ringkasan(df)  : angka kabupaten, ranking, teks Ringkasan Eksekutif
- hitung_tren_penduduk  : tambahan jiwa, persen, laju per tahun (2020-2026)
- buat_skala_radar      : normalisasi 0-100 untuk grafik radar
"""

from types import SimpleNamespace


def format_id(n):
    return f"{n:,.0f}".replace(",", ".")


def markdown_bold_ke_html(teks):
    import re
    return re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", teks)


def hitung_ringkasan(df):
    """Hitung semua angka ringkasan dari tabel df hasil load_data()."""
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

    ringkasan_teks = (
        f"Kabupaten Purworejo memiliki **{format_id(total_penduduk)}** penduduk (data BPS 2026), dengan "
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
    return SimpleNamespace(
        total_penduduk=total_penduduk,
        total_produktif=total_produktif,
        total_pemuda=total_pemuda,
        rasio_ketergantungan_kab=rasio_ketergantungan_kab,
        ranking=ranking,
        tertinggi=tertinggi,
        terendah=terendah,
        rata_rata_proporsi=rata_rata_proporsi,
        jumlah_di_atas_rata2=jumlah_di_atas_rata2,
        ringkasan_teks=ringkasan_teks,
    )


def hitung_tren_penduduk(df_historis):
    """Selisih, persen, dan laju pertumbuhan rata-rata per tahun (geometrik) 2020 -> 2026."""
    penduduk_awal_tren = df_historis.iloc[0]["penduduk"]
    penduduk_akhir_tren = df_historis.iloc[-1]["penduduk"]
    tambahan_tren = penduduk_akhir_tren - penduduk_awal_tren
    persen_tren = tambahan_tren / penduduk_awal_tren * 100
    laju_tren = ((penduduk_akhir_tren / penduduk_awal_tren) ** (1 / 6) - 1) * 100
    return tambahan_tren, persen_tren, laju_tren


# ⚠️ FIX: sebelumnya pakai "kepadatan" sebagai salah satu sumbu -- tapi
# kepadatan, proporsi_pemuda, dan rasio_ketergantungan SEMUANYA berasal
# dari rumus penyesuaian yang sama (lihat load_data), sehingga ketiganya
# selalu bergerak bareng. Akibatnya radar 2 kecamatan yang ekstrem jadi
# nyaris 100/100/100/0 vs 0/0/0/100 -- bentuknya "runcing" dan kurang
# informatif. Diganti dengan "luas_km2" (data riil & independen, tidak
# diturunkan dari rumus kita) supaya bentuk radar lebih bervariasi dan
# benar-benar mencerminkan 4 dimensi yang berbeda.
METRIK_RADAR = ["total_penduduk", "luas_km2", "proporsi_pemuda_dari_total", "rasio_ketergantungan"]
LABEL_RADAR = ["Total Penduduk", "Luas Wilayah", "Proporsi Pemuda", "Rasio Ketergantungan"]


def buat_skala_radar(df):
    """Kembalikan fungsi yang mengubah satu baris kecamatan menjadi 4 nilai 0-100 (min-max se-kabupaten)."""
    min_vals = df[METRIK_RADAR].min()
    max_vals = df[METRIK_RADAR].max()

    def skala_radar(baris):
        return [
            ((baris[m] - min_vals[m]) / (max_vals[m] - min_vals[m]) * 100) if max_vals[m] > min_vals[m] else 50
            for m in METRIK_RADAR
        ]

    return skala_radar
