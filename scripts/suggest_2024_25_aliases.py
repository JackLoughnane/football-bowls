#!/usr/bin/env python3
"""Generate conservative surname-assisted candidates for unmatched PL rows.

A candidate is NOT verified unless a human confirms player identity and the
club-specific Premier League appearance count using an independent source.
"""
import argparse,csv,collections,unicodedata,re,json,pathlib,urllib.request
SOURCE="https://raw.githubusercontent.com/AhmeddGaballah/premier_league_24_25_player_stats/main/epl_player_stats_24_25.csv"
def norm(x):
 x=unicodedata.normalize("NFKD",x).encode("ascii","ignore").decode().lower()
 return re.sub(r"[^a-z ]"," ",x).strip()
def words(x):return set(norm(x).split())
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--queue",type=pathlib.Path,required=True)
 p.add_argument("--output",type=pathlib.Path,default=pathlib.Path("output/season_2024_25/alias_candidates.csv"))
 a=p.parse_args()
 with a.queue.open(encoding="utf-8-sig",newline="") as f:queue=list(csv.DictReader(f))
 with urllib.request.urlopen(urllib.request.Request(SOURCE,headers={"User-Agent":"FootballBowls/1.0"}),timeout=60) as f:
  others=list(csv.DictReader(f.read().decode("utf-8-sig").splitlines()))
 output=[]
 for r in queue:
  key=words(r["player_name"])
  candidates=[]
  for o in others:
   if norm(o["Club"])!=norm(r["club"]):continue
   ow=words(o["Player Name"])
   if key and (key<=ow or ow<=key or len(key&ow)>=2):
    candidates.append(o)
  for o in candidates:
   output.append({"extracted_name":r["player_name"],"club":r["club"],
    "extracted_appearances":r["appearances"],"candidate_name":o["Player Name"],
    "candidate_appearances":o["Appearances"],
    "count_matches":str(r["appearances"]==o["Appearances"]).lower(),
    "source":SOURCE,"verification_status":"identity_and_count_require_manual_review"})
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("w",encoding="utf-8",newline="") as f:
  fields=["extracted_name","club","extracted_appearances","candidate_name","candidate_appearances","count_matches","source","verification_status"]
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(output)
 print(json.dumps({"unmatched_queue":len(queue),"candidate_links":len(output),
   "count_agreeing_candidates":sum(x["count_matches"]=="true" for x in output),
   "caution":"Alias matches are suggestions only, not independently verified records."},indent=2))
if __name__=="__main__":main()
