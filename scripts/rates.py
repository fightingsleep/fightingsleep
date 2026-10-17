"""Write the latest rates to the pinned gist (rates.txt).

Overnight benchmark fixings (SOFR, SONIA, €STR) and US Treasury 2y/10y yields, from FRED.
Each row: latest value, change from the previous observation in basis points, and a
14-observation sparkline. Sparklines use a fixed basis-point scale (at least 25bp tall),
so administered overnight rates read as flat instead of turning sub-basis-point noise
into full-height swings.

Usage:  GIST_TOKEN=... python scripts/rates.py     (update the gist)
        python scripts/rates.py --print             (just print the board)
"""
import csv
import io
import json
import os
import sys
import urllib.request

GIST_ID = os.environ.get("RATES_GIST_ID", "36ae691904899474edd731c3db062944")
FILENAME = "rates.txt"
SERIES = [("SOFR", "SOFR"), ("SONIA", "IUDSOIA"), ("€STR", "ECBESTRVOLWGTTRMDMNRT"), ("UST 2Y", "DGS2"), ("UST 10Y", "DGS10")]
SPARK = "▁▂▃▄▅▆▇█"
MIN_SPAN = 0.25  # percentage points: the smallest range a sparkline is stretched to
UA = {"User-Agent": "profile rates board; github.com/fightingsleep"}


def request(url: str, headers: dict | None = None, data: bytes | None = None, method: str = "GET") -> bytes:
    req = urllib.request.Request(url, data=data, method=method, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def series(fred_id: str) -> list[float]:
    rows = csv.reader(io.StringIO(request(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}").decode()))
    next(rows)
    return [float(v) for _, v in rows if v not in (".", "")]


def spark(vals: list[float]) -> str:
    mid = (max(vals) + min(vals)) / 2
    span = max(max(vals) - min(vals), MIN_SPAN)
    lo = mid - span / 2
    return "".join(SPARK[min(7, int((v - lo) / span * 8))] for v in vals)


def line(name: str, v: list[float]) -> str:
    ch = round((v[-1] - v[-2]) * 100)
    arrow = "▲" if ch > 0 else "▼" if ch < 0 else "•"
    return f"{name:<8}{v[-1]:>7.2f}%  {arrow}{abs(ch):3d}bp  {spark(v[-14:])}"


def main() -> None:
    token = os.environ.get("GIST_TOKEN")
    auth = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"} if token else {}
    old = {}
    if GIST_ID and token:
        text = json.loads(request(f"https://api.github.com/gists/{GIST_ID}", auth))["files"][FILENAME]["content"]
        old = {l[:8].strip(): l for l in text.splitlines() if l.strip()}
    lines, failed = [], []
    for name, fred_id in SERIES:
        try:
            lines.append(line(name, series(fred_id)))
        except Exception as e:  # keep the previous line rather than dropping the row
            failed.append(f"{fred_id}: {e}")
            if name in old:
                lines.append(old[name])
    for f in failed:
        print(f"warning: {f}", file=sys.stderr)
    board = "\n".join(lines) + "\n"
    if "--print" in sys.argv or not (GIST_ID and token):
        print(board, end="")
        return
    if len(failed) == len(SERIES):
        sys.exit("error: no rates fetched; gist left unchanged")
    request(f"https://api.github.com/gists/{GIST_ID}", auth, method="PATCH",
            data=json.dumps({"files": {FILENAME: {"content": board}}}).encode())
    print(board, end="")


if __name__ == "__main__":
    main()
