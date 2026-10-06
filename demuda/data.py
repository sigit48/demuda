"""Data mentah dan rumus estimasi struktur umur per kecamatan.

- DATA_DASAR_KECAMATAN : penduduk, luas, koordinat (BPS)
- DATA_HISTORIS_KABUPATEN, DATA_STRUKTUR_UMUR_HISTORIS : data tren
- load_data() : RUMUS estimasi (penyesuaian kepadatan, batas +-40%)

Untuk memperbarui data tahun depan, cukup ubah angka di file ini.
"""

import pandas as pd
import streamlit as st


DATA_DASAR_KECAMATAN = [
    ("Bagelen",      -7.81128,  110.04006,    32006,          63.44),
    ("Banyuurip",    -7.75608,  109.97645,    45409,          47.78),
    ("Bayan",        -7.71026,  109.94889,    53810,          44.66),
    ("Bener",        -7.6386,   110.0518,     58911,         102.44),
    ("Bruno",        -7.53,     109.87,       54610,         105.68),
    ("Butuh",        -7.725155, 109.8570219,  44108,          47.21),
    ("Gebang",       -7.64245,  109.99269,    45609,          70.51),
    ("Grabag",       -7.81093,  109.87967,    51310,          67.80),
    ("Kaligesing",   -7.7347,   110.0799,     33306,          78.33),
    ("Kemiri",       -7.64786,  109.90438,    61112,         103.15),
    ("Kutoarjo",     -7.71700,  109.91480,    65212,          39.20),
    ("Loano",        -7.6653,   110.1015,     39908,          53.51),
    ("Ngombol",      -7.8254,   109.9661,     36507,          59.33),
    ("Pituruh",      -7.6414,   109.83652,    53710,          89.01),
    ("Purwodadi",    -7.8657,   110.0024,     43108,          56.15),
    ("Purworejo",    -7.72232,  110.03042,    89517,          53.25),
]

P_ANAK_KAB = 0.201677
P_PRODUKTIF_KAB = 0.674702
P_LANSIA_KAB = 0.123679
PEMUDA_DARI_PRODUKTIF = 0.216137 / 0.674702


DATA_HISTORIS_KABUPATEN = {
    "tahun": ["2020", "2021", "2022", "2023-2024", "2025", "2026"],
    "penduduk": [769880, 799411, 778257, 788265, 801670, 808153],
    "sumber": [
        "Tabel kecamatan edisi 2020",
        "Open Data Purworejo, Tabel 12.1.b",
        "Tabel kecamatan edisi 2022",
        "Tabel kecamatan edisi 2023 & 2024 (identik)",
        "BPS, tabel kelompok umur edisi 2025",
        "BPS, tabel kelompok umur edisi 2026",
    ],
}

DATA_STRUKTUR_UMUR_HISTORIS = [
    {"label": "2023-2024", "anak_pct": 20.41, "produktif_pct": 68.43, "lansia_pct": 11.16,
     "pemuda_pct": 22.36, "rasio_ketergantungan": 46.14},
    {"label": "2025", "anak_pct": 20.22, "produktif_pct": 67.81, "lansia_pct": 11.96,
     "pemuda_pct": 21.91, "rasio_ketergantungan": 47.46},
    {"label": "2026", "anak_pct": 20.17, "produktif_pct": 67.47, "lansia_pct": 12.37,
     "pemuda_pct": 21.61, "rasio_ketergantungan": 48.22},
]

@st.cache_data
def load_data():
    df = pd.DataFrame(DATA_DASAR_KECAMATAN, columns=["kecamatan", "lat", "lon", "total_penduduk", "luas_km2"])
    df["kepadatan"] = df["total_penduduk"] / df["luas_km2"]
    kepadatan_rata2_kab = df["total_penduduk"].sum() / df["luas_km2"].sum()
    z = (df["kepadatan"] / kepadatan_rata2_kab) - 1
    z_clipped = z.clip(-0.4, 0.4)

    produktif_share = (P_PRODUKTIF_KAB * (1 + 0.12 * z_clipped)).clip(0.60, 0.75)
    lansia_share = (P_LANSIA_KAB * (1 - 0.15 * z_clipped)).clip(0.08, 0.18)
    anak_share = 1 - produktif_share - lansia_share
    pemuda_share = produktif_share * PEMUDA_DARI_PRODUKTIF

    df["penduduk_15_64"] = (df["total_penduduk"] * produktif_share).round().astype(int)
    df["penduduk_65_plus"] = (df["total_penduduk"] * lansia_share).round().astype(int)
    df["penduduk_0_14"] = df["total_penduduk"] - df["penduduk_15_64"] - df["penduduk_65_plus"]
    df["pemuda_16_30"] = (df["total_penduduk"] * pemuda_share).round().astype(int)

    df["penduduk_non_produktif"] = df["penduduk_0_14"] + df["penduduk_65_plus"]
    df["rasio_ketergantungan"] = (df["penduduk_non_produktif"] / df["penduduk_15_64"] * 100).round(1)
    df["proporsi_pemuda_dari_produktif"] = (df["pemuda_16_30"] / df["penduduk_15_64"] * 100).round(1)
    df["proporsi_pemuda_dari_total"] = (df["pemuda_16_30"] / df["total_penduduk"] * 100).round(1)
    return df
