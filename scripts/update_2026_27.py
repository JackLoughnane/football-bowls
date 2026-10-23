#!/usr/bin/env python3
"""Incremental 2026/27 Football Bowls updater; standard library only.

The 2025/26 game is the baseline. State records season appearances already
applied so repeated weekly runs never add the same appearances twice.
Unmatched/ambiguous identities are held for manual review.
"""
import csv
import io
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"
STATE = ROOT / "data" / "season_2026-27_applied.json"
REVIEW = ROOT / "data" / "season_2026-27_review.json"
URL = ("https://raw.githubusercontent.com/imadeddine-belkat/"
       "Premier-League-Stats/main/pl_stats/_merged/players/"
       "2026-27_players_stats.csv")
ALIASES = {
    "Man City": "Manchester City", "Man Utd": "Manchester United",
    "Spurs": "Tottenham H", "Newcastle": "Newcastle United",
    "West Ham": "West Ham United", "West Brom": "West Bromwich Albion",
    "Brighton": "Brighton & Hove Albion", "Nott'm Forest": "Nottingham Forest",
    "Sheffield Utd": "Sheff. Utd.", "Leicester": "Leicester City",
    "Leeds": "Leeds United", "Norwich": "Norwich City",
    "Cardiff": "Cardiff City", "Stoke": "Stoke City", "Hull": "Hull City",
    "C Palace": "Crystal Palace", "A Villa": "Aston Villa",
    "Ipswich": "Ipswich T", "Luton": "Luton Town",
}
def normal(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower())
                   if c.isalnum() and not unicodedata.combining(c))

def main():
    html = PAGE.read_text(encoding="utf-8")
    m = re.search(r"const DATA=(.*?);\s*\n", html)
    if not m:
        raise ValueError("Cannot locate game's DATA; refusing to modify")
    clubs = json.loads(m.group(1))
    byclub = {c["club"]: c for c in clubs}
    applied = json.loads(STATE.read_text()) if STATE.exists() else {}
    if not isinstance(applied, dict):
        raise ValueError("Invalid applied-state ledger")
    with urllib.request.urlopen(urllib.request.Request(URL, headers={
        "User-Agent": "FootballBowlsUpdater/1.0"
    }), timeout=45) as response:
        body = response.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(body))
    required = {"playerId", "playerName", "team_name", "season", "appearances"}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("Source CSV schema changed; refusing update")
    latest = {}
    for row in reader:
        if row["season"] != "2026-27":
            raise ValueError("Unexpected season in 2026/27 source")
        club = ALIASES.get(row["team_name"], row["team_name"])
        name = row["playerName"].strip()
        pid = row["playerId"].strip()
        if not (club and name and pid):
            raise ValueError("Missing player identity")
        value = float(row["appearances"] or 0)
        if not value.is_integer() or not 0 <= value <= 38:
            raise ValueError("Invalid single-season appearances")
        count = int(value)
        key = pid + "|" + club
        if key in latest:
            raise ValueError("Duplicate player ID and club in source")
        latest[key] = {"id": pid, "club": club, "name": name, "apps": count}
    if len(latest) < 250:
        raise ValueError("Source has too few players; refusing update")
    reviews = []
    changed = 0
    for key, item in latest.items():
        current = item["apps"]
        previous = applied.get(key, 0)
        if current < previous:
            raise ValueError("Season appearances decreased for " + key)
        if current == previous:
            continue
        club = byclub.get(item["club"])
        if club is None:
            # New PL clubs are fine, but their name is recorded for review.
            reviews.append({**item, "reason": "unrecognized club"})
            continue
        matches = [p for p in club["players"]
                   if normal(p[0]) == normal(item["name"])]
        if len(matches) != 1:
            reviews.append({**item, "reason": "ambiguous or unmatched player name",
                            "matches": len(matches)})
            continue
        matches[0][1] += current - previous
        applied[key] = current
        changed += 1
    for c in clubs:
        c["players"].sort(key=lambda p: (-p[1], p[0]))
    STATE.parent.mkdir(parents=True, exist_ok=True)
    if changed:
        updated = html[:m.start(1)] + json.dumps(clubs, ensure_ascii=False,
            separators=(",", ":")) + html[m.end(1):]
        PAGE.write_text(updated, encoding="utf-8")
    STATE.write_text(json.dumps(applied, indent=2, sort_keys=True) + "\n")
    REVIEW.write_text(json.dumps(reviews, indent=2, ensure_ascii=False) + "\n")
    print(f"2026/27: {len(latest)} source records, {changed} updated, "
          f"{len(reviews)} held for review")
    if reviews:
        print("WARNING: some player records require identity review", file=sys.stderr)

if __name__ == "__main__":
    main()
