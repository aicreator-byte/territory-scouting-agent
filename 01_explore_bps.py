"""
Territory Scouting Agent - Tahap 1: Eksplorasi BPS Web API
Tujuan: cari kode domain wilayah Banten (provinsi + kab/kota) dan
daftar tabel dinamis yang tersedia untuk wilayah tersebut.

Cara pakai:
    1. Set environment variable BPS_TOKEN dengan API key dari webapi.bps.go.id
       - Linux/Mac : export BPS_TOKEN="token_kamu"
       - Windows   : set BPS_TOKEN=token_kamu
       - atau simpan di file .env (lihat contoh .env.example)
    2. Jalankan: python3 01_explore_bps.py
    3. Lihat output untuk kode domain Banten dan kab/kota di dalamnya,
       lalu catat kode domain yang relevan untuk dipakai di tahap 2.
"""

import os
import sys
import stadata

# Coba load dari file .env kalau ada (opsional, butuh python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        print("Set dulu env var-nya, misalnya:")
        print('  export BPS_TOKEN="token_kamu_dari_webapi.bps.go.id"')
        print("atau buat file .env berisi: BPS_TOKEN=token_kamu")
        sys.exit(1)

    client = stadata.Client(BPS_TOKEN)

    # 1. Ambil semua kode domain (provinsi -> kab/kota)
    print("=== Mengambil daftar domain wilayah ===")
    domains = client.list_domain()

    # domains biasanya berupa DataFrame pandas (kolom: domain_id, domain_name, dst)
    print(domains.head(20))
    domains.to_csv("bps_domains_all.csv", index=False)
    print(f"\nTotal domain: {len(domains)} (disimpan ke bps_domains_all.csv)")

    # 2. Filter khusus wilayah yang mengandung kata "Banten"
    print("\n=== Mencari domain terkait Banten ===")
    name_col = None
    for col in domains.columns:
        if "name" in col.lower():
            name_col = col
            break

    if name_col:
        banten = domains[domains[name_col].str.contains("Banten", case=False, na=False)]
        print(banten)
        banten.to_csv("bps_domains_banten.csv", index=False)
        print(f"\nDitemukan {len(banten)} domain terkait 'Banten' -> disimpan ke bps_domains_banten.csv")
    else:
        print("Kolom nama wilayah tidak ditemukan, cek manual kolom berikut:")
        print(domains.columns.tolist())


if __name__ == "__main__":
    main()
