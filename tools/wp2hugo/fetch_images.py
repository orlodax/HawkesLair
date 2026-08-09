"""
Download every image referenced by the converted posts into its page bundle.

Reads images.json (written by convert.py). Safe to re-run: files already on
disk are skipped, so a partial run can simply be repeated.

    python fetch_images.py [--workers N] [--retry-failed]
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

TOOLDIR  = Path(__file__).resolve().parent
ROOT     = TOOLDIR.parents[1]
MANIFEST = TOOLDIR / "images.json"
FAILLOG  = TOOLDIR / "report" / "image_failures.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
}
MIN_BYTES = 200          # anything smaller is an error page, not a photo


def fetch_one(entry: dict, session: requests.Session, timeout: int) -> dict:
    dest = ROOT / entry["bundle"] / entry["file"]
    result = dict(entry)

    if dest.exists() and dest.stat().st_size >= MIN_BYTES:
        result["status"] = "skipped"
        return result

    # Blogger's /s0/ gives the original upload; fall back to the embedded size.
    candidates = [entry["url"]]
    if entry["source"] == "blogger" and entry["url"] != entry["original"]:
        candidates.append(entry["original"])
    # WordPress often deletes generated thumbnails but keeps the upload:
    # foo-300x119.png -> foo.png
    for u in list(candidates):
        stripped = re.sub(r"-\d+x\d+(\.[A-Za-z0-9]+)$", r"\1", u)
        if stripped != u:
            candidates.append(stripped)

    last = ""
    for url in candidates:
        safe = urllib.parse.quote(url, safe=":/?&=%#~+,()'")
        for attempt in range(3):
            try:
                r = session.get(safe, headers=HEADERS, timeout=timeout, stream=True)
                if r.status_code != 200:
                    last = f"HTTP {r.status_code}"
                    break                       # a 404 will not fix itself
                data = r.content
                if len(data) < MIN_BYTES:
                    last = f"too small ({len(data)}B)"
                    break
                ctype = r.headers.get("Content-Type", "")
                if "image" not in ctype and not data[:4] in (b"\xff\xd8\xff\xe0", b"\x89PNG"):
                    if "html" in ctype:
                        last = "served HTML, not an image"
                        break
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                result["status"] = "ok"
                result["bytes"] = len(data)
                result["used"] = url
                return result
            except Exception as e:
                last = f"{type(e).__name__}"
                time.sleep(1.5 * (attempt + 1))

    result["status"] = "failed"
    result["error"] = last
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--retry-failed", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print("images.json not found — run convert.py first", file=sys.stderr)
        return 1

    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if args.retry_failed and FAILLOG.exists():
        prev = json.loads(FAILLOG.read_text(encoding="utf-8"))
        keys = {(f["bundle"], f["file"]) for f in prev}
        entries = [e for e in entries if (e["bundle"], e["file"]) in keys]
        print(f"retrying {len(entries)} previously failed images")

    print(f"{len(entries)} images queued across "
          f"{len({e['bundle'] for e in entries})} bundles")

    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(pool_maxsize=args.workers * 2))
    session.mount("http://", requests.adapters.HTTPAdapter(pool_maxsize=args.workers * 2))

    tally = collections.Counter()
    by_source = collections.Counter()
    failures = []
    total_bytes = 0
    done = 0

    with ThreadPoolExecutor(args.workers) as ex:
        futures = [ex.submit(fetch_one, e, session, args.timeout) for e in entries]
        for fut in as_completed(futures):
            r = fut.result()
            tally[r["status"]] += 1
            done += 1
            if r["status"] == "ok":
                total_bytes += r.get("bytes", 0)
                by_source[r["source"]] += 1
            elif r["status"] == "failed":
                failures.append(r)
            if done % 40 == 0:
                print(f"  {done}/{len(entries)}  ok={tally['ok']} "
                      f"skip={tally['skipped']} fail={tally['failed']}", flush=True)

    print("\n=== FETCH ===")
    for k in ("ok", "skipped", "failed"):
        print(f"  {k:10} {tally[k]}")
    print(f"  downloaded {total_bytes/1_048_576:.1f} MB")
    print(f"  by source: {dict(by_source)}")

    FAILLOG.parent.mkdir(parents=True, exist_ok=True)
    FAILLOG.write_text(json.dumps(failures, indent=1, ensure_ascii=False), encoding="utf-8")

    # An image we could not fetch would render as a broken <img>. Replace the
    # reference in the Markdown with the same marker convert.py uses for the
    # images that are known to be gone.
    patched = 0
    for f in failures:
        md = ROOT / f["bundle"] / "index.md"
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        pat = re.compile(r"!\[[^\]]*\]\(" + re.escape(f["file"]) + r"(?:\s+\"[^\"]*\")?\)")
        name = f["original"].split("/")[-1]
        marker = f'<span class="img-missing">immagine perduta nella migrazione — {name}</span>'
        new, n = pat.subn(marker, text)
        if n:
            md.write_text(new, encoding="utf-8")
            patched += n
    if patched:
        print(f"\n  marked {patched} unfetchable image reference(s) as missing in content")

    if failures:
        print(f"\n=== {len(failures)} FAILURES (logged to {FAILLOG.name}) ===")
        grouped = collections.Counter(f.get("error", "?") for f in failures)
        for err, n in grouped.most_common():
            print(f"  {n:4}  {err}")
        for f in failures[:12]:
            print(f"    {f['source']:8} {f.get('error','?'):22} {f['original'][:74]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
