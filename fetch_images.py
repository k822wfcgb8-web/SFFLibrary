#!/usr/bin/env python3
"""Download the banner images listed in docs/images/images.json from
Wikimedia Commons into docs/images/, resized for the web.

Run this on the Mac (it needs internet):   python3 fetch_images.py
Re-download everything:                    python3 fetch_images.py --force

Images already in the folder are skipped. On a Mac, the built-in 'sips'
tool shrinks each picture to at most 1600 px wide and about 300 KB.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, "docs", "images")
MAX_BYTES = 300 * 1024
# Wikimedia asks scripts to identify themselves.
UA = "KelleyLibrarySFFBookclub/1.0 (personal club website; Python urllib)"


def shrink(path):
    """Use macOS sips to make a JPEG at most 1600 px wide and ~300 KB."""
    if not shutil.which("sips"):
        return
    tmp = path + ".tmp.jpg"
    for quality in (75, 65, 55, 45):
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
                        "-Z", "1600", path, "--out", tmp],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.getsize(tmp) <= MAX_BYTES:
            break
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="download again even if the file exists")
    args = ap.parse_args()

    with open(os.path.join(IMG_DIR, "images.json"), encoding="utf-8") as f:
        pools = json.load(f)["pools"]

    failed = []
    for theme, images in pools.items():
        for img in images:
            dest = os.path.join(IMG_DIR, img["file"])
            if os.path.exists(dest) and not args.force:
                print(f"  have   {img['file']}")
                continue
            url = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
                   + urllib.parse.quote(img["commons"]) + "?width=1600")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as out:
                    shutil.copyfileobj(r, out)
                shrink(dest)
                print(f"  got    {img['file']}  ({os.path.getsize(dest) // 1024} KB)")
            except Exception as e:  # keep going; report at the end
                failed.append(f"{img['file']}: {e}")
                if os.path.exists(dest):
                    os.remove(dest)
            time.sleep(1)  # be gentle with Wikimedia's servers

    if failed:
        print("\nThese could not be downloaded (try again later):")
        for f in failed:
            print("  - " + f)
        return 1
    print("\nAll images are in docs/images/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
