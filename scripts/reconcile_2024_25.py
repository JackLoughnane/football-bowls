#!/usr/bin/env python3
"""Conservative 2024/25 independent appearance reconciliation.

Exact player+club matching only; unmatched rows require human review.
Independent community dataset is NOT an official PL source and can be incomplete.
"""
import argparse,csv,collections,json,pathlib,unicodedata,urllib.request
URL="https://raw.githubusercontent.com/AhmeddGaballah/premier_league_24_25_player_stats/main/epl_player_stats_24_25.csv"
ALIASES={"man city":"manchester city","man utd":"manchester united","nott'm forest":"nottingham forest",
"wolves":"wolverhampton wanderers","bournemouth":"afc bournemouth","brighton":"brighton & hove albion",
"spurs":"tottenham hotspur","west ham":"west ham united","newcastle":"newcastle united"}
def norm(s):
    s=unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().casefold().strip()
    return " ".join(s.replace(".","").replace("-"," ").split())
def club(s):
    v=norm(s)
    return ALIASES.get(v,v)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--official",required=True,type=pathlib.Path)
    p.add_argument("--output",default="output/season_2024_25/reconciliation",type=pathlib.Path)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"FootballBowlsValidation/1.0"}),timeout=60) as r:
        independent=list(csv.DictReader(r.read().decode("utf-8-sig").splitlines()))
    official=list(csv.DictReader(args.official.open(encoding="utf-8-sig",newline="")))
    idx=collections.defaultdict(list)
    for r in independent:
        idx[(norm(r["Player Name"]),club(r["Club"]))].append(r)
    results=[]
    matched=0;agree=0;disagree=0
    for r in official:
        if int(r["total_appearances"])==0:continue
        key=(norm(r["player_name"]),club(r["club"]))
        candidates=idx.get(key,[])
        status="unmatched"
        comparison=""
        if len(candidates)==1:
            matched+=1
            comparison=candidates[0]["Appearances"]
            if int(comparison)==int(r["total_appearances"]):
                status="agree";agree+=1
            else:
                status="disagree";disagree+=1
        elif len(candidates)>1:status="ambiguous"
        results.append({"player_name":r["player_name"],"club":r["club"],
            "official_extracted_appearances":r["total_appearances"],
            "independent_appearances":comparison,"status":status,
            "source_pdf_page":r["source_pdf_page"],"independent_source_url":URL})
    with (args.output/"row_comparison.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]))
        w.writeheader();w.writerows(results)
    report={"season":"2024/25","official_positive_rows":len(results),
        "independent_dataset_rows":len(independent),"exact_player_club_matches":matched,
        "agreements":agree,"disagreements":disagree,
        "unmatched_or_ambiguous":len(results)-matched,
        "independent_source":URL,
        "caveat":"Community dataset may contain mistakes or omit transfers. Do not automatically correct official handbook values or import to game."}
    (args.output/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if disagree:print("DISCREPANCIES FOUND: inspect row_comparison.csv before any import")
if __name__=="__main__":main()
