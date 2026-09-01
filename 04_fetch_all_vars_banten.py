"""
Territory Scouting Agent - Tahap 4: Ambil SEMUA variabel domain Banten (3600)
via pagination, lalu filter yang relevan untuk white space scoring.

Domain 3600 = Provinsi Banten, totalnya 791 variabel (80 halaman @ 10/halaman).
Variabel di domain provinsi ini kebanyakan sudah pecahan per kab/kota
(judulnya mengandung "...Menurut Kabupaten/Kota di Provinsi Banten"),
jadi cukup query domain 3600 saja untuk dapat data pembanding antar wilayah.
"""

import os
import sys
import json
import time
import csv
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")

BASE_URL = "https://webapi.bps.go.id/v1/api/list/model/var/domain/3600/key/{key}/page/{page}/"

KEYWORDS = [
    "penduduk", "PDRB", "usaha", "UMKM", "miskin", "kemiskinan",
    "pengeluaran", "ekonomi", "industri", "perdagangan", "koperasi",
    "investasi", "pertumbuhan",
]


def fetch_page(page):
    url = BASE_URL.format(key=BPS_TOKEN, page=page)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Gagal ambil halaman {page}: {e}")
        return None


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        sys.exit(1)

    print("=== Mengambil semua variabel domain 3600 (Provinsi Banten) ===")

    first = fetch_page(1)
    if not first or "data" not in first:
        print("Gagal mengambil halaman pertama.")
        sys.exit(1)

    meta = first["data"][0]
    total_pages = meta["pages"]
    total_vars = meta["total"]
    print(f"Total variabel: {total_vars}, total halaman: {total_pages}")

    all_vars = list(first["data"][1])

    for page in range(2, total_pages + 1):
        print(f"  Mengambil halaman {page}/{total_pages}...")
        result = fetch_page(page)
        if result and "data" in result and len(result["data"]) > 1:
            all_vars.extend(result["data"][1])
        time.sleep(0.5)

    print(f"\nTotal variabel berhasil diambil: {len(all_vars)}")

    fieldnames = list(all_vars[0].keys()) if all_vars else []
    with open("bps_var_3600_all.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_vars)
    print("Disimpan ke bps_var_3600_all.csv")

    pattern_hits = []
    for v in all_vars:
        title = str(v.get("title", "")).lower()
        if any(kw.lower() in title for kw in KEYWORDS):
            pattern_hits.append(v)

    print(f"\nDitemukan {len(pattern_hits)} variabel relevan dari {len(all_vars)} total")
    with open("bps_var_3600_relevan.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pattern_hits)
    print("Disimpan ke bps_var_3600_relevan.csv")

    print("\n=== Daftar variabel relevan (var_id - title) ===")
    for v in pattern_hits:
        print(f"  {v.get('var_id')}: {v.get('title')}")


if __name__ == "__main__":
    main()
