#!/usr/bin/env python3
"""Triage all unmatched 2024/25 rows without silently changing player data.

Inputs are the official extraction CSV and the independent comparison artifact.
The output is a review queue; no names are automatically merged.
"""
import argparse,csv,collections,json,pathlib
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--official",type=pathlib.Path,required=True)
 p.add_argument("--comparison",type=pathlib.Path,required=True)
 p.add_argument("--output",type=pathlib.Path,default=pathlib.Path("output/season_2024_25/unmatched_review"))
 a=p.parse_args()
 with a.official.open(encoding="utf-8-sig",newline="") as f:official=list(csv.DictReader(f))
 with a.comparison.open(encoding="utf-8-sig",newline="") as f:comparison=list(csv.DictReader(f))
 by_name=collections.defaultdict(list)
 for r in official:
  if int(r["total_appearances"])>0:by_name[r["player_name"].casefold()].append(r)
 by_club=collections.Counter(r["club"] for r in comparison if r["status"]=="unmatched")
 queue=[]
 for r in comparison:
  if r["status"] not in ("unmatched","ambiguous"):continue
  others=[f'{x["club"]} ({x["total_appearances"]})' for x in by_name[r["player_name"].casefold()] if x["club"]!=r["club"]]
  queue.append({"player_name":r["player_name"],"club":r["club"],"appearances":r["official_extracted_appearances"],
    "status":r["status"],"other_club_same_name":"; ".join(others),
    "review_priority":"high" if by_club[r["club"]]<=3 else "bulk_club_coverage",
    "resolution":"","evidence_url":"","reviewer_notes":""})
 a.output.mkdir(parents=True,exist_ok=True)
 with (a.output/"unmatched_review_queue.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(queue[0]) if queue else ["player_name"]);w.writeheader();w.writerows(queue)
 report={"unmatched_or_ambiguous":len(queue),
  "unmatched_by_club":dict(sorted(by_club.items(),key=lambda x:(-x[1],x[0]))),
  "same_name_other_club":sum(bool(r["other_club_same_name"]) for r in queue),
  "verification_status":"open","next_step":"Check source coverage and alternative player names, then validate each against an independent official or trustworthy player-club record."}
 (a.output/"triage_summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
