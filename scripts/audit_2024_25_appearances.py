#!/usr/bin/env python3
"""Audit extracted PL 2024/25 player appearances before any import.

Checks internal arithmetic, season limits, unique player-club pairs and
team totals. This is NOT independent verification of source transcription.
"""
import argparse,csv,collections,json,pathlib,sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("csv_file",type=pathlib.Path)
    ap.add_argument("--output",type=pathlib.Path,default=pathlib.Path("output/season_2024_25/quality_report.json"))
    a=ap.parse_args()
    rows=list(csv.DictReader(a.csv_file.open(encoding="utf-8-sig",newline="")))
    expected={"club","player_name","starts","sub_appearances","unused_sub","goals","total_appearances","source_pdf_page"}
    if not rows or not expected.issubset(rows[0]):
        raise SystemExit("Missing columns or empty CSV")
    clubs=collections.defaultdict(list)
    issues=[]
    keys=set()
    for i,r in enumerate(rows,2):
        club,name=r["club"].strip(),r["player_name"].strip()
        key=(club,name.casefold())
        if not club or not name:issues.append(f"Row {i}: missing club/player")
        if key in keys:issues.append(f"Row {i}: duplicate {club}/{name}")
        keys.add(key)
        try:
            s,sub,unused,goals,total=[int(r[k]) for k in ("starts","sub_appearances","unused_sub","goals","total_appearances")]
            if min(s,sub,unused,goals,total)<0:issues.append(f"Row {i}: negative stat")
            if s+sub!=total:issues.append(f"Row {i}: appearance arithmetic mismatch")
            if total>38:issues.append(f"Row {i}: >38 appearances in one club season")
            if goals>total*6:issues.append(f"Row {i}: implausible goals count")
            if not 389<=int(r["source_pdf_page"])<=393:issues.append(f"Row {i}: unexpected PDF page")
        except ValueError:issues.append(f"Row {i}: nonnumeric stat")
        clubs[club].append(r)
    if len(clubs)!=20:issues.append(f"Expected 20 clubs, found {len(clubs)}")
    summary={}
    for club,rs in sorted(clubs.items()):
        total=sum(int(r["total_appearances"]) for r in rs if r["total_appearances"].isdigit())
        # Across 38 league games, a team fields 11 starters and up to five substitutes.
        if not 418<=total<=608:issues.append(f"{club}: {total} total appearances outside 418-608")
        summary[club]={"player_rows":len(rs),"players_who_appeared":sum(int(r["total_appearances"])>0 for r in rs),
                       "sum_player_appearances":total,"starts":sum(int(r["starts"]) for r in rs)}
        # Every match has exactly eleven starters, so 38 matches imply 418 starts.
        if summary[club]["starts"]!=418:
            issues.append(f"{club}: {summary[club]['starts']} starts, expected 418")
    result={"season":"2024/25","source_type":"official handbook PDF extraction",
            "verification_status":"internal_checks_only","player_club_rows":len(rows),
            "players_with_appearances":sum(int(r["total_appearances"])>0 for r in rows),
            "clubs":summary,"issues":issues,
            "next_step":"Independently verify source transcription and club assignments before database import"}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"rows":len(rows),"clubs":len(clubs),"issues":issues},indent=2))
    if issues:sys.exit(1)
if __name__=="__main__":main()
