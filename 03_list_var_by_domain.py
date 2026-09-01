"""
Territory Scouting Agent - Tahap 3: List variabel langsung dari BPS API
(bypass fungsi list_dynamictable milik package stadata yang datanya
tidak lengkap untuk provinsi Banten)

Tujuan: cari var_id indikator (penduduk, PDRB, dll) yang benar-benar
terdaftar untuk wilayah Banten, dengan memanggil endpoint resmi
BPS Web API secara langsung via requests.

Dokumentasi format endpoint:
    https://webapi.bps.go.id/v1/api/list/model/var/domain/{domain}/key/{key}/

Domain provinsi kadang perlu 2 digit ("36") kadang 4 digit ("3600"),
jadi script ini coba kedua format untuk provinsi Banten (36 / 3600)
dan juga langsung ke tiap kab/kota (yang sudah pasti 4 digit).
"""

import os
import sys
import json
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")

BASE_URL = "https://webapi.bps.go.id/v1/api/list/model/var/domain/{domain}/key/{key}/"

# Kandidat kode domain untuk dicoba: provinsi (2 digit & 4 digit) + semua kab/kota
DOMAIN_CANDIDATES = {
    "36": "Banten (2 digit)",
    "3600": "Banten (4 digit)",
    "3601": "Pandeglang",
    "3602": "Lebak",
    "3603": "Tangerang (kab)",
    "3604": "Serang (kab)",
    "3671": "Tangerang (kota)",
    "3672": "Cilegon",
    "3673": "Serang (kota)",
    "3674": "Tangerang Selatan",
}


def fetch_domain(domain_code):
    url = BASE_URL.format(domain=domain_code, key=BPS_TOKEN)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def main():
    if not BPS_TOKEN:
        print("ERROR: BPS_TOKEN belum di-set.")
        sys.exit(1)

    all_results = {}
    summary_rows = []

    for domain_code, label in DOMAIN_CANDIDATES.items():
        print(f"=== Cek domain {domain_code} ({label}) ===")
        result = fetch_domain(domain_code)
        all_results[domain_code] = result

        data_list = result.get("data") if isinstance(result, dict) else None
        n_vars = 0
        if isinstance(data_list, list) and len(data_list) > 1 and isinstance(data_list[1], list):
            n_vars = len(data_list[1])
        elif isinstance(data_list, list):
            n_vars = len(data_list)

        print(f"  -> Jumlah variabel ditemukan: {n_vars}")
        summary_rows.append({"domain": domain_code, "label": label, "n_vars": n_vars})

        time.sleep(1)  # sopan ke API, hindari rate limit

    with open("bps_var_by_domain_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("\nDisimpan mentahan lengkap ke bps_var_by_domain_raw.json")

    import csv
    with open("bps_var_by_domain_summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "label", "n_vars"])
        writer.writeheader()
        writer.writerows(summary_rows)
    print("Disimpan ringkasan ke bps_var_by_domain_summary.csv")

    print("\n=== RINGKASAN ===")
    for row in summary_rows:
        print(f"{row['domain']:>6} ({row['label']:<20}): {row['n_vars']} variabel")


if __name__ == "__main__":
    main()
