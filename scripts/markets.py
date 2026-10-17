"""Write today's market board to the pinned gist (markets.txt).

Five benchmarks, each with its latest close, the day's move and a two-week sparkline.
Prices come from Yahoo Finance's chart API. If a symbol can't be fetched, its line from
the current gist is kept, so a bad day upstream never blanks the card.

Usage:  GIST_TOKEN=... python scripts/markets.py          (update the gist)
        python scripts/markets.py --print                  (just print the board)
"""
import json
import os
import sys
import urllib.request

GIST_ID = os.environ.get("GIST_ID", "6116b23402aea3b714c5cb844cbe92ac")
FILENAME = "markets.txt"
SYMBOLS = [("^GSPC", "SPX", 0), ("^NDX", "NDX", 0), ("^FTSE", "UKX", 0), ("BTC-USD", "BTC", 0), ("GBPUSD=X", "GBPUSD", 4)]
SPARK = "▁▂▃▄▅▆▇█"
UA = {"User-Agent": "Mozilla/5.0 (profile market board; github.com/fightingsleep)"}


def get(url: str, headers: dict | None = None, data: bytes | None = None, method: str = "GET") -> dict:
    req = urllib.request.Request(url, data=data, method=method, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def closes(symbol: str) -> list[float]:
    q = urllib.request.quote(symbol, safe="")
    r = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{q}?range=1mo&interval=1d")["chart"]["result"][0]
    return [c for c in r["indicators"]["quote"][0]["close"] if c is not None]


def spark(vals: list[float]) -> str:
    lo, hi = min(vals), max(vals)
    return "".join(SPARK[min(7, int((v - lo) / (hi - lo + 1e-12) * 8))] for v in vals)


def line(name: str, dp: int, c: list[float]) -> str:
    chg = (c[-1] / c[-2] - 1) * 100
    return f"{name:<7}{c[-1]:>10,.{dp}f}  {'▲' if chg >= 0 else '▼'}{abs(chg):5.2f}%  {spark(c[-14:])}"


def main() -> None:
    token = os.environ.get("GIST_TOKEN")
    auth = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"} if token else {}
    old = {}
    if GIST_ID and token:
        text = get(f"https://api.github.com/gists/{GIST_ID}", auth)["files"][FILENAME]["content"]
        old = {l.split()[0]: l for l in text.splitlines() if l.strip()}
    lines, failed = [], []
    for symbol, name, dp in SYMBOLS:
        try:
            lines.append(line(name, dp, closes(symbol)))
        except Exception as e:  # keep yesterday's line rather than dropping the row
            failed.append(f"{symbol}: {e}")
            if name in old:
                lines.append(old[name])
    for f in failed:
        print(f"warning: {f}", file=sys.stderr)
    board = "\n".join(lines) + "\n"
    if "--print" in sys.argv or not (GIST_ID and token):
        print(board, end="")
        return
    if len(failed) == len(SYMBOLS):
        sys.exit("error: no market data fetched; gist left unchanged")
    get(f"https://api.github.com/gists/{GIST_ID}", auth, method="PATCH",
        data=json.dumps({"files": {FILENAME: {"content": board}}}).encode())
    print(board, end="")


if __name__ == "__main__":
    main()
