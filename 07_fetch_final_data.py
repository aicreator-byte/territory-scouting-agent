"""
Territory Scouting Agent - Tahap 7: Ambil ANGKA DATA untuk indikator final
(bukan cuma daftar nama variabel lagi, tapi nilai aktualnya)

Indikator final yang sudah ditentukan:
    Banten (domain 3600):
        var 521 = Jumlah Penduduk
        var 235 = PDRB Perkapita
        var 78  = Persentase Penduduk Miskin
        var 145 = Jumlah Penduduk Miskin

    DKI Jakarta (domain 3171, breakdown 5 kota):
        var 254 = Jumlah Penduduk
        var 270 = Persentase Penduduk Miskin
        var 273 = Garis Kemiskinan
        var 255 = IPM
    DKI Jakarta (domain 3100, khusus PDRB):
        var 1334 = PDRB Triwulanan ADHB per kab/kota

    Depok / Jawa Barat (domain 3276):
        var 236 = Jumlah Penduduk
        var 237 = Jumlah Penduduk Miskin
        var 238 = IPM
    Jawa Barat (domain 3200, khusus PDRB):
        var 708 = PDRB per Kapita ADHB per kab/kota
"""

import os
import sys
import time
import json
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BPS_TOKEN = os.environ.get("BPS_TOKEN")

TH_URL = "https://webapi.bps.go.id/v1/api/list/model/th/domain/{domain}/var/{var}/key/{key}/"
DATA_URL = "https://webapi.bps.go.id/v1/api/list/model/data/domain/{domain}/var/{var}/th/{th}/key/{key}/"

# (domain, var_id, label_untuk_file)
TARGETS = [
    ("3600", "521", "banten_jumlah_penduduk"),
    ("3600", "235", "banten_pdrb_perkapita"),
    ("3600", "78", "banten_persen_penduduk_miskin"),
    ("3600", "145", "banten_jumlah_penduduk_miskin"),
    ("3171", "254", "jakarta_jumlah_penduduk"),
    ("3171", "270", "jakarta_persen_penduduk_miskin"),
    ("3171", "273", "jakarta_garis_kemiskinan"),
    ("3171", "255", "jakarta_ipm"),
    ("3100", "1334", "jakarta_pdrb_triwulanan"),
    ("3276", "236", "depok_jumlah_penduduk"),
    ("3276", "237", "depok_jumlah_penduduk_miskin"),
    ("3276", "238", "depok_ipm"),
    ("3200", "708", "jabar_pdrb_perkapita"),
]


def fetch_th_list(domain, var):
    url = TH_URL.format(domain=domain, var=var, key=BPS_TOKEN)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def fetch_data(domain, var, th):
    url = DATA_URL.format(domain=domain, var=var, th=th, key=BPS_TOKEN)
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

    for domain, var, label in TARGETS:
        print(f"=== {label} (domain={domain}, var={var}) ===")

        # 1. Cari daftar periode/tahun yang tersedia
        th_result = fetch_th_list(domain, var)
        th_list = th_result.get("data") if isinstance(th_result, dict) else None

        chosen_th = None
        if isinstance(th_list, list) and len(th_list) > 1 and isinstance(th_list[1], list) and len(th_list[1]) > 0:
            available = th_list[1]
            chosen_th = available[-1].get("th_id")
            print(f"  Periode tersedia: {len(available)}, pakai th_id={chosen_th} ({available[-1].get('th')})")
        else:
            print(f"  Gagal dapat daftar periode: {th_result}")

        # 2. Ambil data pakai th yang dipilih
        if chosen_th:
            data_result = fetch_data(domain, var, chosen_th)
        else:
            data_result = {"error": "th tidak ditemukan"}

        all_results[label] = {
            "domain": domain, "var": var, "th_used": chosen_th,
            "th_list_raw": th_result, "data_result": data_result,
        }

        has_data = isinstance(data_result, dict) and "data" in data_result
        print(f"  Data: {'OK' if has_data else 'GAGAL'}")
        time.sleep(1)

    with open("bps_final_data_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("\nSemua data disimpan ke bps_final_data_raw.json")

    print("\n=== RINGKASAN ===")
    for label, entry in all_results.items():
        data_result = entry["data_result"]
        has_data = isinstance(data_result, dict) and "data" in data_result
        print(f"  {label}: {'OK (th=' + str(entry['th_used']) + ')' if has_data else 'GAGAL/KOSONG'}")


if __name__ == "__main__":
    main()
