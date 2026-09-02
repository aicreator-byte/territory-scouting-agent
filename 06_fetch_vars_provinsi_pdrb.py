"""
Territory Scouting Agent - Tahap 6: Ambil data PDRB dari level provinsi
(DKI Jakarta domain 3100, Jawa Barat domain 3200)

Alasan: PDRB dengan breakdown per kab/kota TIDAK terdaftar di domain kota
(3171-3175, 3276) -- hanya terdaftar di level provinsi. Jadi khusus untuk
indikator PDRB, kita perlu ambil dari domain provinsi ini, meski domain
tersebut tidak dipakai untuk indikator lain (sesuai keputusan sebelumnya:
DKI Jakarta pakai 5 kota terpisah, Depok cukup domain kotanya saja).
"""

import os
import sys
import time
import csv
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")

BASE_URL = "https://webapi.bps.go.id/v1/api/list/model/var/domain/{domain}/key/{key}/page/{page}/"

DOMAINS = {
    "3100": "DKI Jakarta (provinsi)",
    "3200": "Jawa Barat (provinsi)",
}


def fetch_page(domain, page):
    url = BASE_URL.format(domain=domain, key=BPS_TOKEN, page=page)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"    Gagal ambil {domain} halaman {page}: {e}")
        return None


def fetch_all_vars_for_domain(domain, label):
    print(f"=== {domain} ({label}) ===")
    first = fetch_page(domain, 1)
    if not first or "data" not in first:
        print(f"  Gagal mengambil data untuk domain {domain}.")
        return []

    meta = first["data"][0]
    total_pages = meta["pages"]
    total_vars = meta["total"]
    print(f"  Total variabel: {total_vars}, total halaman: {total_pages}")

    all_vars = list(first["data"][1])
    for v in all_vars:
        v["_domain"] = domain
        v["_domain_label"] = label

    for page in range(2, total_pages + 1):
        result = fetch_page(domain, page)
        if result and "data" in result and len(result["data"]) > 1:
            for v in result["data"][1]:
                v["_domain"] = domain
                v["_domain_label"] = label
            all_vars.extend(result["data"][1])
        time.sleep(0.5)

    print(f"  -> {len(all_vars)} variabel diambil")
    return all_vars


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        sys.exit(1)

    combined = []
    for domain, label in DOMAINS.items():
        vars_for_domain = fetch_all_vars_for_domain(domain, label)
        combined.extend(vars_for_domain)
        time.sleep(1)

    print(f"\nTotal gabungan: {len(combined)}")
    if not combined:
        print("Tidak ada data.")
        sys.exit(1)

    fieldnames = list(combined[0].keys())
    with open("bps_var_provinsi_all.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined)
    print("Disimpan ke bps_var_provinsi_all.csv")

    pdrb_matches = [
        v for v in combined
        if "pdrb" in str(v.get("title", "")).lower()
        and "kabupaten/kota" in str(v.get("title", "")).lower()
    ]
    print(f"\nDitemukan {len(pdrb_matches)} variabel PDRB per kab/kota")
    with open("bps_var_provinsi_pdrb.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pdrb_matches)
    print("Disimpan ke bps_var_provinsi_pdrb.csv")

    print("\n=== Daftar variabel PDRB per kab/kota ===")
    for v in pdrb_matches:
        print(f"  var_id={v.get('var_id')} ({v.get('_domain_label')}): {v.get('title')}")


if __name__ == "__main__":
    main()
