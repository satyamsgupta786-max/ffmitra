"""Download the public credit card fraud dataset (creditcard.csv) from mirrors.

Does not require kaggle credentials. Exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "datasets" / "creditcard.csv"

MIRRORS = [
    "https://github.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/raw/master/creditcard.csv",
    "https://raw.githubusercontent.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/master/creditcard.csv",
]

TIMEOUT = 120


def download(url: str, dest: Path) -> int:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "FFMitra-model-pipeline/1.0"
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp, open(dest, "wb") as out:
        size = 0
        while True:
            chunk = resp.read(1024 * 256)
            if not chunk:
                break
            out.write(chunk)
            size += len(chunk)
    return size


def main() -> int:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    for url in MIRRORS:
        try:
            size = download(url, DEST)
            if size > 0:
                print(f"DOWNLOAD_OK: {size} bytes -> {DEST}")
                return 0
        except Exception as exc:
            print(f"MIRROR_FAILED: {url}: {exc}")
    print("DOWNLOAD_FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
