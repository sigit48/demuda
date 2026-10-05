"""Konfigurasi tampilan: palet warna dan logo (SVG).

Ubah warna tema di sini; semua grafik, CSS, dan PDF ikut berubah.
"""

PALET = {
    "teal": "#0F6E56",
    "teal_muda": "#5DCAA5",
    "amber": "#EF9F27",
    "amber_gelap": "#BA7517",
    "teks_utama": "#2C2C2A",
    "teks_sekunder": "#5F5E5A",
}

LOGO_SVG = """
<svg width="140" height="140" viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg">
  <path d="M340,240 C300,190 260,160 260,120 C260,75 296,40 340,40 C384,40 420,75 420,120 C420,160 380,190 340,240 Z"
        fill="#0F6E56" stroke="#085041" stroke-width="2"/>
  <rect x="300" y="145" width="18" height="30" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <rect x="330" y="125" width="18" height="50" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <rect x="360" y="95"  width="18" height="80" rx="3" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
  <circle cx="369" cy="80" r="9" fill="#EF9F27" stroke="#BA7517" stroke-width="1"/>
</svg>
"""
