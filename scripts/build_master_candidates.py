#!/usr/bin/env python3
"""Build candidate Premier League player roster from a public historical squad dataset.

This is NOT proof of a Premier League appearance: unused squad members are included.
No records are marked verified and nothing is imported to Supabase.
Source: https://github.com/Samoilov2004/premier_league_dataset
"""
import csv
import io
import json
import os
import pathlib
import re
import time
import urllib.request

SOURCE_REPO = "Samoilov2004/premier_league_dataset"
API = "https://api.github.com/repos/" + SOURCE_REPO
HEADERS = {"User-Agent":"FootballBowlsResearch/0.1", "Accept":"application/vnd.github+json"}
OUT = pathlib.Path("output/master_list")

def fetch(url):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def save_csv(path, rows, columns):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads(fetch(API))
    branch = meta["default_branch"]
    tree = json.loads(fetch(API + "/git/trees/" + branch + "?recursive=1"))
    if tree.get("truncated"):
        raise RuntimeError("Source GitHub tree was truncated; refusing incomplete export")
    paths = sorted(x["path"] for x in tree["tree"]
                   if x["type"] == "blob"
                   and re.fullmatch(r"dataset/DATA_CSV/Season_\d{4}/[^/]+\.csv", x["path"]))
    if not paths:
        raise RuntimeError("No historical squad CSV files found: source layout may have changed")
    players = {}
    club_seasons = set()
    errors = []
    for index, path in enumerate(paths, 1):
        try:
            raw = fetch("https://raw.githubusercontent.com/" + SOURCE_REPO + "/" + branch + "/" + path)
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
            if not {"id", "name"}.issubset(reader.fieldnames or []):
                raise ValueError("Missing id/name columns")
            season = re.search(r"Season_(\d{4})", path).group(1)
            club = pathlib.PurePosixPath(path).stem
            for row in reader:
                pid = (row.get("id") or "").strip()
                name = (row.get("name") or "").strip()
                if not pid or not name:
                    continue
                if pid not in players:
                    players[pid] = {"source_player_id":pid, "player_name":name,
                                    "source":"Transfermarkt squad via Samoilov2004",
                                    "appearance_status":"candidate_unconfirmed"}
                club_seasons.add((pid,club,season))
        except Exception as exc:
            errors.append({"source_file":path,"error":str(exc)})
        if index % 100 == 0:
            print(f"Processed {index}/{len(paths)} squad files", flush=True)
    save_csv(OUT/"candidate_players.csv", sorted(players.values(),key=lambda r:r["player_name"].casefold()),
             ["source_player_id","player_name","source","appearance_status"])
    save_csv(OUT/"candidate_club_seasons.csv",
             [{"source_player_id":p,"source_club_file":c,"season_start":s}
              for p,c,s in sorted(club_seasons)],
             ["source_player_id","source_club_file","season_start"])
    save_csv(OUT/"download_errors.csv",errors,["source_file","error"])
    summary = {"source":SOURCE_REPO,"branch":branch,"squad_files_discovered":len(paths),
               "squad_files_failed":len(errors),"unique_candidate_players":len(players),
               "candidate_player_club_seasons":len(club_seasons),
               "warning":"Squad membership is NOT proof of a Premier League appearance."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if errors:
        raise SystemExit("Some squad files failed; see download_errors.csv")

if __name__ == "__main__":
    main()
