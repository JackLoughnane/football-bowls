#!/usr/bin/env python3
"""Import independently verified PL player-club records to Supabase.

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment.
Never run with the public anon key. Run manually after reviewing the CSV.
"""
import csv
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from validate_appearances import validate

def request(base, key, table, records):
    url = base.rstrip("/") + "/rest/v1/" + table + "?on_conflict=" + (
        "player_id,club_id" if table == "fb_player_club_appearances"
        else "player_id" if table == "fb_players" else "club_id"
    )
    body = json.dumps(records).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "apikey": key, "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.status

def main():
    if len(sys.argv) not in (2,3):
        raise SystemExit("Usage: python scripts/import_verified.py input.csv [--apply]")
    apply = len(sys.argv) == 3 and sys.argv[2] == "--apply"
    if len(sys.argv) == 3 and not apply:
        raise SystemExit("Unknown argument. Use --apply to write.")
    accepted, rejected = validate(pathlib.Path(sys.argv[1]))
    if rejected:
        raise SystemExit(f"Import blocked: {len(rejected)} invalid/unverified records")
    players = {r["player_id"]: {"player_id":r["player_id"],"name":r["player_name"]} for r in accepted}
    clubs = {r["club_id"]: {"club_id":r["club_id"],"name":r["club_name"]} for r in accepted}
    appearances = [{"player_id":r["player_id"],"club_id":r["club_id"],
                    "appearances":int(r["appearances"]),"source_url":r["source_url"],
                    "verified_at":__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
                   for r in accepted]
    print(json.dumps({"players":len(players),"clubs":len(clubs),
                      "player_club_records":len(appearances),"mode":"APPLY" if apply else "DRY RUN"}))
    if not apply:
        print("No data written. Review source verification, then rerun with --apply.")
        return
    if not accepted:
        raise SystemExit("Refusing to apply an empty dataset")
    base = os.environ.get("SUPABASE_URL","").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY","").strip()
    if not base.startswith("https://") or not key:
        raise SystemExit("Missing valid SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    # Import in chunks to avoid large HTTP bodies; parent tables first.
    for table, records in (("fb_clubs",list(clubs.values())),
                           ("fb_players",list(players.values())),
                           ("fb_player_club_appearances",appearances)):
        for i in range(0,len(records),100):
            request(base,key,table,records[i:i+100])
        print("Imported",len(records),table)

if __name__ == "__main__":
    main()
