"""Dokumentasi dan bantuan (kriteria 14.a.5): panduan, sidebar, metodologi, konteks.

Hanya berisi teks; tidak ada rumus. Edit teks panduan di sini.
"""

import textwrap

import streamlit as st


def tampilkan_panduan():
    """Expander "Cara Menggunakan Aplikasi"."""
    with st.expander("📖 Cara Menggunakan Aplikasi (klik untuk membuka panduan)"):
        st.markdown(textwrap.dedent("""
        Selamat datang di **DEMUDA Purworejo**. Aplikasi ini membantu Anda melihat
        *di kecamatan mana potensi pemuda paling besar* dan *di mana perlu perhatian
        lebih*, tanpa perlu keahlian analisis data. Ikuti 4 langkah singkat berikut.
        """))

        st.markdown("##### 🚀 Mulai dalam 4 langkah")
        st.markdown(textwrap.dedent("""
        1. **Baca Ringkasan Eksekutif** (kotak hijau di bawah panduan ini) untuk
           gambaran besar kondisi pemuda Kabupaten Purworejo.
        2. **Buka tab** di bagian tengah halaman. Ada 4 tab, tiap tab menjawab
           pertanyaan yang berbeda (lihat tabel di bawah).
        3. **Berinteraksi dengan grafik dan peta**: arahkan kursor, klik, atau pilih
           kecamatan dari menu.
        4. **Unduh laporan** (tombol *Unduh .txt* atau *Unduh .pdf*) untuk dibawa ke
           rapat atau dilampirkan pada proposal program.
        """))

        st.markdown("##### 🧭 Fungsi tiap tab")
        st.markdown(textwrap.dedent("""
        | Tab | Pertanyaan yang dijawab | Cara pakai |
        |---|---|---|
        | 📊 **Ringkasan Kabupaten** | Bagaimana struktur usia dan tren penduduk Purworejo? | Lihat 4 angka utama, lalu gulir ke bawah untuk grafik struktur usia dan tren penduduk 2020-2026. |
        | 🗺️ **Peta & Profil Kecamatan** | Di mana penduduk dan pemuda terkonsentrasi? | Pilih metrik pada menu, lalu **klik titik** kecamatan di peta untuk melihat kartu detailnya. Tabel profil lengkap ada di bagian bawah. |
        | 🧑‍🤝‍🧑 **Fokus Pemuda** | Kecamatan mana yang proporsi pemudanya tertinggi/terendah? | Baca grafik ranking dan *Insight Otomatis* di bawahnya. |
        | ⚖️ **Bandingkan Kecamatan** | Bagaimana dua kecamatan dibandingkan? | Pilih **dua kecamatan berbeda** pada dua menu, lalu lihat angka berdampingan dan grafik radar. |
        """))

        st.markdown("##### 🖱️ Tips berinteraksi dengan grafik")
        st.markdown(textwrap.dedent("""
        - **Arahkan kursor** ke batang, garis, atau titik untuk melihat angka pastinya.
        - **Zoom peta**: scroll mouse atau cubit layar (HP). **Geser peta**: tarik dengan mouse/jari.
        - **Reset tampilan grafik**: klik dua kali pada area grafik.
        - **Simpan grafik sebagai gambar**: klik ikon 📷 di pojok kanan atas grafik.
        - **Urutkan tabel**: klik judul kolom. **Perbesar tabel**: klik ikon layar penuh di pojoknya.
        - **Klik nama pada legenda** grafik untuk menyembunyikan/menampilkan garis tertentu.
        """))

        st.markdown("##### 🎯 Contoh skenario penggunaan")
        st.markdown(textwrap.dedent("""
        - *"Kecamatan mana yang diprioritaskan untuk pelatihan wirausaha muda?"*
          → Tab **Fokus Pemuda**, lihat kecamatan dengan proporsi pemuda tertinggi.
        - *"Apakah penduduk Purworejo bertambah dalam beberapa tahun terakhir?"*
          → Tab **Ringkasan Kabupaten**, lihat grafik Tren Penduduk 2020-2026.
        - *"Kenapa kecamatan A dan B berbeda?"*
          → Tab **Bandingkan Kecamatan**, lihat radar dan selisih proporsi pemuda.
        """))

        st.info(
            "💡 Panduan cepat, glosarium istilah, dan tanya jawab (FAQ) juga tersedia di "
            "**sidebar sebelah kiri** (klik tanda **›** di pojok kiri atas jika sidebar tertutup)."
        )


def tampilkan_sidebar():
    """Sidebar Bantuan: Panduan Cepat, Glosarium, FAQ."""
    with st.sidebar:
        st.markdown("### 📖 Bantuan")
        st.caption("Panduan singkat penggunaan DEMUDA Purworejo")

        with st.expander("🚀 Panduan Cepat", expanded=True):
            st.markdown(textwrap.dedent("""
            1. Baca **Ringkasan Eksekutif**.
            2. Pilih salah satu dari **4 tab**.
            3. **Klik peta** atau **pilih kecamatan** untuk detail.
            4. **Unduh laporan** (.txt / .pdf).

            Panduan lengkap: buka **"📖 Cara Menggunakan Aplikasi"** di halaman utama.
            """))

        with st.expander("📚 Glosarium Istilah"):
            st.markdown(textwrap.dedent("""
            **Usia produktif**: penduduk 15-64 tahun.

            **Pemuda (proksi)**: penduduk 15-29 tahun, pendekatan terdekat dari
            kelompok umur 5-tahunan BPS untuk definisi pemuda 16-30 tahun.

            **Rasio ketergantungan**: jumlah penduduk non-produktif (anak 0-14 th
            dan lansia 65+) per 100 penduduk usia produktif. Makin rendah, makin
            ringan beban usia produktif.

            **Proporsi pemuda**: persentase pemuda dari total penduduk kecamatan.

            **Kepadatan penduduk**: jumlah penduduk per km².

            **Bonus demografi**: kondisi ketika usia produktif jauh lebih banyak
            dari usia non-produktif sehingga peluang pertumbuhan ekonomi terbuka.

            **Estimasi**: angka hasil perhitungan berbasis data resmi, bukan hasil
            sensus langsung.

            **Laju pertumbuhan rata-rata per tahun**: kenaikan penduduk rata-rata
            tiap tahun, dihitung secara geometrik dari tahun awal ke tahun akhir.
            """))

        with st.expander("❓ Tanya Jawab (FAQ)"):
            st.markdown(textwrap.dedent("""
            **Apakah angka per kecamatan data resmi?**
            Total penduduk dan luas wilayah per kecamatan resmi dari BPS. Pembagian
            kelompok umur per kecamatan adalah *estimasi* (lihat "Metodologi & Sumber Data").

            **Mengapa "Pemuda 15-29" padahal definisi 16-30 tahun?**
            BPS menerbitkan data per kelompok 5 tahun, sehingga 15-29 dipakai
            sebagai pendekatan terdekat.

            **Peta tidak muncul / kosong?**
            Peta memerlukan koneksi internet (peta dasar OpenStreetMap). Periksa
            koneksi lalu muat ulang halaman (tekan F5).

            **Tombol Unduh PDF tidak bekerja?**
            Pastikan browser tidak memblokir unduhan. Alternatifnya gunakan
            tombol Unduh .txt.

            **Mengapa grafik tren penduduk ada titik "2023-2024"?**
            File BPS edisi 2023 dan 2024 berisi angka yang sama persis, sehingga
            digabung menjadi satu titik agar tidak terkesan penduduk berhenti tumbuh.

            **Bagaimana mengembalikan pilihan ke awal?**
            Muat ulang halaman (F5). Semua menu kembali ke nilai bawaan.
            """))

        st.markdown("---")
        st.caption("DEMUDA Purworejo · Jambore Pemuda Kab. Purworejo 2026")


def tampilkan_metodologi():
    """Expander Metodologi dan Sumber Data."""
    with st.expander("ℹ️ Metodologi & Sumber Data"):
        st.markdown(textwrap.dedent("""
        Dashboard ini menggabungkan **dua tabel resmi BPS** yang aslinya terpisah:

        1. **Struktur umur penduduk** -- BPS Kab. Purworejo, *"Jumlah Penduduk Menurut
           Kelompok Umur dan Jenis Kelamin di Kabupaten Purworejo, 2026"* (level
           kabupaten, agregat, tidak dipecah per kecamatan).
        2. **Populasi & luas wilayah per kecamatan** -- BPS Kab. Purworejo,
           *"Jumlah Penduduk menurut Kecamatan di Kabupaten Purworejo, 2026"*
           (per kecamatan dalam ribu jiwa, tanpa breakdown umur). Agar jumlah 16
           kecamatan sama dengan total kabupaten 2026 (808.153), angka tiap
           kecamatan diskalakan proporsional dengan selisih hanya 6-17 jiwa.
           Luas wilayah per kecamatan bersumber dari BPS.

        Untuk grafik "Tren Struktur Umur Kabupaten" di Tab Ringkasan, digunakan
        **4 edisi tambahan** dari sumber yang sama (BPS, *"Jumlah Penduduk
        Menurut Kelompok Umur..."* edisi 2023, 2024, 2025, dan 2026) -- satu
        sumber konsisten untuk seluruh rentang tahun, sehingga tren rasio
        ketergantungan & proporsi pemuda dari tahun ke tahun bisa dibandingkan
        langsung tanpa perlu estimasi tambahan.

        Untuk grafik "Tren Penduduk Kabupaten" (2020-2026), digunakan total
        penduduk dari BPS Kab. Purworejo (tabel "Jumlah Penduduk menurut Kecamatan"
        edisi 2020, 2022, 2023/2024, serta tabel kelompok umur edisi 2025 dan 2026),
        ditambah data tahun 2021 dari Open Data Kabupaten Purworejo (Tabel 12.1.b),
        karena data 2021 tidak tersedia di situs BPS. Detail catatan data ada di
        bawah grafik tersebut.

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


def tampilkan_konteks():
    """Expander Bonus Demografi dan Generasi Emas 2045."""
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
