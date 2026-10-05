"""Pembuatan laporan unduhan: TXT dan PDF, beserta tombol unduhnya.
"""

import io

import streamlit as st
from reportlab.lib import colors as pdf_colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .hitung import format_id, markdown_bold_ke_html
from .konfigurasi import PALET


def buat_txt_laporan(r):
    """Teks ringkasan laporan (.txt)."""
    total_penduduk = r.total_penduduk
    total_produktif = r.total_produktif
    total_pemuda = r.total_pemuda
    rasio_ketergantungan_kab = r.rasio_ketergantungan_kab
    ranking = r.ranking
    ringkasan_teks = r.ringkasan_teks
    laporan_unduh = f"""RINGKASAN EKSEKUTIF -- DEMUDA PURWOREJO
Peta Potensi Demografi Pemuda Kabupaten Purworejo
==========================================================

DATA AGREGAT KABUPATEN
- Total penduduk           : {format_id(total_penduduk)}
- Usia produktif (15-64 th): {format_id(total_produktif)}
- Pemuda (15-29 th, proksi): {format_id(total_pemuda)}
- Rasio ketergantungan     : {rasio_ketergantungan_kab}%

RINGKASAN
{ringkasan_teks.replace('**', '')}

RANKING PROPORSI PEMUDA PER KECAMATAN (tertinggi ke terendah)
{ranking[['kecamatan', 'proporsi_pemuda_dari_total', 'rasio_ketergantungan']].to_string(index=False)}

==========================================================
Sumber data: BPS Kabupaten Purworejo (struktur umur kabupaten 2026 +
populasi per kecamatan 2026). Breakdown umur per
kecamatan merupakan estimasi berbasis kepadatan penduduk -- lihat
metodologi lengkap di aplikasi.
Dibuat untuk Lomba Teknologi Piranti Lunak -- Jambore Pemuda Purworejo 2026.
"""
    return laporan_unduh


def buat_pdf_laporan(r):
    """Bangun laporan PDF (bytes) dengan ReportLab."""
    total_penduduk = r.total_penduduk
    total_produktif = r.total_produktif
    total_pemuda = r.total_pemuda
    rasio_ketergantungan_kab = r.rasio_ketergantungan_kab
    ranking = r.ranking
    ringkasan_teks = r.ringkasan_teks
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = getSampleStyleSheet()
    judul_style = ParagraphStyle("Judul", parent=styles["Heading1"], textColor=pdf_colors.HexColor(PALET["teal"]))
    subjudul_style = ParagraphStyle("Sub", parent=styles["Heading2"], textColor=pdf_colors.HexColor(PALET["teal"]), fontSize=13)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=15)

    elemen = [
        Paragraph("DEMUDA Purworejo", judul_style),
        Paragraph("Peta Potensi Demografi Pemuda Kabupaten Purworejo", styles["Normal"]),
        Spacer(1, 14),
        Paragraph("Data Agregat Kabupaten", subjudul_style),
    ]
    data_tabel = [
        ["Metrik", "Nilai"],
        ["Total Penduduk", format_id(total_penduduk)],
        ["Usia Produktif (15-64 th)", format_id(total_produktif)],
        ["Pemuda (15-29 th, proksi)", format_id(total_pemuda)],
        ["Rasio Ketergantungan", f"{rasio_ketergantungan_kab}%"],
    ]
    t = Table(data_tabel, colWidths=[8 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor(PALET["teal"])),
        ("TEXTCOLOR", (0, 0), (-1, 0), pdf_colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, pdf_colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor("#F5F5F0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elemen += [t, Spacer(1, 14), Paragraph("Ringkasan", subjudul_style),
               Paragraph(markdown_bold_ke_html(ringkasan_teks), body_style), Spacer(1, 14),
               Paragraph("Ranking Proporsi Pemuda per Kecamatan", subjudul_style)]

    header = ["Kecamatan", "Proporsi Pemuda (%)", "Rasio Ketergantungan (%)"]
    rows = [header] + ranking[["kecamatan", "proporsi_pemuda_dari_total", "rasio_ketergantungan"]].values.tolist()
    t2 = Table(rows, colWidths=[6 * cm, 4.5 * cm, 4.5 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pdf_colors.HexColor(PALET["amber"])),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, pdf_colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.HexColor("#F5F5F0")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elemen.append(t2)

    doc.build(elemen)
    buffer.seek(0)
    return buffer.getvalue()


def tampilkan_tombol_unduh(r):
    """Dua tombol: unduh TXT dan unduh PDF."""
    st.download_button(
        label="⬇️ Unduh Ringkasan Laporan (.txt)",
        data=buat_txt_laporan(r),
        file_name="ringkasan_demuda_purworejo.txt",
        mime="text/plain",
        help="Unduh ringkasan dalam format teks sederhana.",
    )

    st.download_button(
        label="⬇️ Unduh Laporan (.pdf)",
        data=buat_pdf_laporan(r),
        file_name="laporan_demuda_purworejo.pdf",
        mime="application/pdf",
        help="Unduh laporan berformat PDF berisi tabel agregat dan ranking kecamatan.",
    )
