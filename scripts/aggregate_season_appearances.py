#!/usr/bin/env python3
"""Aggregate independently sourced PL season appearance data.

Input rows must be PREMIER LEAGUE appearances (including substitute appearances),
not squad membership, starts, cup matches, or all-competition totals.
Does not write to Supabase or mark rows verified.
"""
import argparse
import csv
import pathlib
from collections import defaultdict

FIELDS=("player_id","player_name","club_id","club_name","season_start","appearances","source_url")
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("input",type=pathlib.Path)
    parser.add_argument("--output",type=pathlib.Path,default=pathlib.Path("output/appearance_review"))
    args=parser.parse_args()
    totals=defaultdict(int)
    names={}
    seasons=set()
    issues=[]
    with args.input.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise SystemExit("Missing columns: "+", ".join(sorted(set(FIELDS)-set(reader.fieldnames or []))))
        for n,r in enumerate(reader,2):
            try:
                for field in FIELDS:
                    if not (r[field] or "").strip():
                        raise ValueError("missing "+field)
                season=int(r["season_start"])
                apps=int(r["appearances"])
                if not 1992<=season<=2100 or not 0<=apps<=42:
                    raise ValueError("invalid season or appearance count")
                if not r["source_url"].startswith("https://"):
                    raise ValueError("source_url must be https")
                key=(r["player_id"],r["club_id"],season)
                if key in seasons:
                    raise ValueError("duplicate player-club-season")
                seasons.add(key)
                pair=key[:2]
                label=(r["player_name"],r["club_name"])
                if pair in names and names[pair]!=label:
                    raise ValueError("conflicting names for same player-club IDs")
                names[pair]=label
                totals[pair]+=apps
            except (ValueError,TypeError) as e:
                issues.append({"line":n,"issue":str(e)})
    args.output.mkdir(parents=True,exist_ok=True)
    with (args.output/"club_totals_UNVERIFIED.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["player_id","player_name","club_id","club_name","appearances","source_url","verification_status"])
        for (pid,cid),apps in sorted(totals.items()):
            if apps>0:
                w.writerow([pid,names[(pid,cid)][0],cid,names[(pid,cid)][1],apps,"","pending"])
    with (args.output/"issues.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["line","issue"])
        w.writeheader()
        w.writerows(issues)
    print(f"Read {len(seasons)} player-club-seasons; {len(totals)} club totals; {len(issues)} issues")
    print("All totals are UNVERIFIED. A per-season source URL is not sufficient for final verification.")
    if issues:
        raise SystemExit(1)

if __name__=="__main__":
    main()
