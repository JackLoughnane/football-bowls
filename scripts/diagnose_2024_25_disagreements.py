#!/usr/bin/env python3
"""Classify historical 2024/25 reconciliation disagreements.

Read full row_comparison.csv from reconciliation artifact. This is not an
independent source of appearances, and it never rewrites official data.
"""
import argparse,csv,collections,pathlib,json
def main():
 p=argparse.ArgumentParser()
 p.add_argument("comparison_csv",type=pathlib.Path)
 p.add_argument("--out-dir",type=pathlib.Path,default=pathlib.Path("output/season_2024_25/transfer_diagnostics"))
 a=p.parse_args()
 with a.comparison_csv.open(encoding="utf-8-sig",newline="") as f:
  rows=list(csv.DictReader(f))
 by_name=collections.defaultdict(list)
 for r in rows:
  by_name[r["player_name"].casefold()].append(r)
 decisions=[]
 for r in rows:
  if r["status"]!="disagree":continue
  season_total=sum(int(x["official_extracted_appearances"]) for x in by_name[r["player_name"].casefold()])
  independent=int(r["independent_appearances"])
  kind="independent_total_matches_all_clubs" if season_total==independent else "unresolved_difference"
  decisions.append({"player_name":r["player_name"],"club":r["club"],
    "official_club_appearances":r["official_extracted_appearances"],
    "independent_appearances":independent,"official_all_clubs":season_total,
    "classification":kind})
 a.out_dir.mkdir(parents=True,exist_ok=True)
 with (a.out_dir/"disagreement_diagnostics.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(decisions[0]) if decisions else ["classification"])
  w.writeheader();w.writerows(decisions)
 report={"disagreements":len(decisions),
         "explained_by_multi_club_season_total":sum(r["classification"]=="independent_total_matches_all_clubs" for r in decisions),
         "unresolved":sum(r["classification"]=="unresolved_difference" for r in decisions),
         "caution":"Numerical reconciliation is not proof of official correctness. 53 unmatched/ambiguous rows need individual review."}
 (a.out_dir/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
