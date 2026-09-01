"""
Territory Scouting Agent - Tahap 2: Cari indikator (tabel dinamis) relevan
Tujuan: lihat indikator apa saja (populasi, PDRB, dll) yang tersedia di BPS,
lalu difilter yang relevan untuk white space scoring.

Kode domain Banten (hasil eksplorasi tahap 1, untuk dipakai nanti di tahap 3):
    3600 = Banten (provinsi)
    3601 = Pandeglang (kab)
    3602 = Lebak (kab)
    3603 = Tangerang (kab)
    3604 = Serang (kab)
    3671 = Tangerang (kota)
    3672 = Cilegon (kota)
    3673 = Serang (kota)
    3674 = Tangerang Selatan (kota)

Catatan: filter list_dynamictable(domain=[...]) sempat menghasilkan 0 baris
(kemungkinan format kode domain di file referensi package berbeda / tabel
dinamis didaftarkan di level nasional). Jadi di sini kita ambil SEMUA
tabel dulu (all=True), baru difilter pakai keyword judul.

Cara pakai:
    1. Set environment variable BPS_TOKEN
    2. Jalankan: python3 02_list_dynamictable_banten.py
    3. Lihat bps_dynamictable_relevan.csv untuk cari var_id indikator
       yang relevan (jumlah penduduk, PDRB, jumlah usaha, dll)
"""

import os
import sys
import stadata

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")

BANTEN_DOMAINS = ["3600", "3601", "3602", "3603", "3604", "3671", "3672", "3673", "3674"]

KEYWORDS = ["penduduk", "PDRB", "usaha", "UMKM", "miskin", "pengeluaran", "ekonomi", "industri"]


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        sys.exit(1)

    client = stadata.Client(BPS_TOKEN)

    print("=== Mengambil SELURUH katalog tabel dinamis (tanpa filter domain) ===")
    tables = client.list_dynamictable(all=True)

    if tables is None or len(tables) == 0:
        print("Gagal mengambil data / tidak ada hasil sama sekali.")
        sys.exit(1)

    print(f"Total tabel dinamis (seluruh Indonesia): {len(tables)}")
    print(tables.head(10))
    tables.to_csv("bps_dynamictable_all.csv", index=False)
    print("\nDisimpan ke bps_dynamictable_all.csv")
    print("Kolom yang tersedia:", tables.columns.tolist())

    # Cari kolom judul
    title_col = None
    for col in tables.columns:
        if "title" in col.lower():
            title_col = col
            break

    if title_col is None:
        print("\nKolom judul tidak ditemukan otomatis, cek manual kolom di atas.")
        sys.exit(0)

    print(f"\n=== Filter indikator relevan (kata kunci: {KEYWORDS}) ===")
    pattern = "|".join(KEYWORDS)
    relevant = tables[tables[title_col].astype(str).str.contains(pattern, case=False, na=False)]
    print(f"Ditemukan {len(relevant)} tabel relevan dari total {len(tables)}")
    print(relevant[[title_col]].drop_duplicates().head(50))
    relevant.to_csv("bps_dynamictable_relevan.csv", index=False)
    print("\nDisimpan ke bps_dynamictable_relevan.csv")


if __name__ == "__main__":
    main()
