"""
Territory Scouting Agent - Tahap 2: Cari daftar tabel dinamis untuk Banten
Tujuan: lihat indikator apa saja (populasi, PDRB, dll) yang tersedia
di BPS untuk provinsi Banten dan kab/kota di dalamnya.

Kode domain Banten (hasil eksplorasi tahap 1):
    3600 = Banten (provinsi)
    3601 = Pandeglang (kab)
    3602 = Lebak (kab)
    3603 = Tangerang (kab)
    3604 = Serang (kab)
    3671 = Tangerang (kota)
    3672 = Cilegon (kota)
    3673 = Serang (kota)
    3674 = Tangerang Selatan (kota)

Cara pakai:
    1. Set environment variable BPS_TOKEN
    2. Jalankan: python3 02_list_dynamictable_banten.py
    3. Lihat output CSV untuk cari var_id indikator yang relevan
       (misal: jumlah penduduk, PDRB, jumlah usaha, dll)
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


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        sys.exit(1)

    client = stadata.Client(BPS_TOKEN)

    print("=== Mengambil daftar tabel dinamis untuk domain provinsi Banten (3600) ===")
    tables = client.list_dynamictable(domain=["3600"], all=False)

    if tables is None:
        print("Gagal mengambil data / tidak ada hasil.")
        sys.exit(1)

    print(f"Total tabel dinamis ditemukan: {len(tables)}")
    print(tables.head(30))
    tables.to_csv("bps_dynamictable_banten.csv", index=False)
    print("\nDisimpan ke bps_dynamictable_banten.csv")

    keywords = ["penduduk", "PDRB", "usaha", "UMKM", "miskin", "pengeluaran", "ekonomi"]
    title_col = None
    for col in tables.columns:
        if "title" in col.lower() or "subj" in col.lower():
            title_col = col
            break

    if title_col:
        print(f"\n=== Filter indikator relevan (kata kunci: {keywords}) ===")
        pattern = "|".join(keywords)
        relevant = tables[tables[title_col].astype(str).str.contains(pattern, case=False, na=False)]
        print(relevant)
        relevant.to_csv("bps_dynamictable_relevan.csv", index=False)
        print(f"\nDitemukan {len(relevant)} tabel relevan -> disimpan ke bps_dynamictable_relevan.csv")
    else:
        print("Kolom judul tabel tidak ditemukan, cek manual kolom berikut:")
        print(tables.columns.tolist())


if __name__ == "__main__":
    main()
