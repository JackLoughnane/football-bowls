#!/usr/bin/env python3
"""epldata historical PL appearance aggregation and cautious 2024/25 candidates."""
import pandas as pd,re,unicodedata,json,pathlib
D=pathlib.Path("output/epldata")
def normalize(s):
 s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode().lower()
 return " ".join(re.findall(r"[a-z0-9]+",s))
def main():
 players=pd.read_csv(D/"players.csv",dtype=str).fillna("")
 pt=pd.read_csv(D/"player_team.csv",dtype=str).fillna("")
 pg=pd.read_csv(D/"player_game.csv",dtype=str).fillna("")
 gt=pd.read_csv(D/"game_team.csv",dtype=str).fillna("")
 games=pd.read_csv(D/"games.csv",dtype=str).fillna("")
 assert players.player_id.is_unique,"Player IDs not unique"
 assert pg.player_game_id.is_unique,"Player-game IDs not unique"
 # Use actual match participations, never squad registration or unused substitute.
 match=pg.merge(pt[["player_team_id","player_id","team"]],on="player_team_id",validate="many_to_one")
 match=match.merge(gt[["team_game_id","game_id","team"]],on="team_game_id",suffixes=("","_match"),validate="many_to_one")
 assert (match.team==match.team_match).all(),"Player stint and match club disagree"
 match=match.merge(games[["game_id","game_date"]],on="game_id",validate="many_to_one")
 match["date"]=pd.to_datetime(match.game_date,errors="coerce")
 assert match.date.notna().all()
 # Season begins in July/August and ends following year; calendar months Jan-Jun belong to previous season.
 year=match.date.dt.year.where(match.date.dt.month>=7,match.date.dt.year-1)
 match["season"]=year.astype(str)+"-"+(year+1).astype(str).str[-2:]
 assert not match.duplicated(["player_id","game_id"]).any(),"Repeated player in one match"
 season=match.groupby(["player_id","team","season"],as_index=False).agg(appearances=("game_id","nunique"))
 season=season.merge(players[["player_id","first_name","last_name","birth_date"]],on="player_id",validate="many_to_one")
 season["name"]=(season.first_name+" "+season.last_name).str.strip()
 season.to_csv(D/"historical_player_club_season.csv",index=False)
 career=season.groupby(["player_id","team","name","birth_date"],as_index=False).agg(career_appearances=("appearances","sum"),seasons=("season","nunique"))
 career.to_csv(D/"historical_career_club_totals_1992_2018.csv",index=False)
 # Candidate identity suggestions are not approvals; no 2024/25 identities are auto-assigned.
 staging=pd.read_csv("/mnt/data/football_bowls_2024_25_identity_staging.csv",dtype=str).fillna("") if pathlib.Path("/mnt/data/football_bowls_2024_25_identity_staging.csv").exists() else None
 if staging is not None:
  names=players.copy()
  names["name"]=(names.first_name+" "+names.last_name).str.strip()
  names["norm"]=names.name.map(normalize)
  rows=[]
  for _,s in staging[staging.total_appearances.astype(int)>0].iterrows():
   key=normalize(s.source_player_name)
   hits=names[names.norm==key]
   for _,h in hits.iterrows():
    rows.append(dict(season=s.season,club=s.club,source_player_name=s.source_player_name,candidate_epldata_id=h.player_id,candidate_name=h["name"],candidate_birth_date=h.birth_date,match_method="exact_normalized_name_only",verification_status="candidate_not_verified",import_ready=False))
  pd.DataFrame(rows,columns=["season","club","source_player_name","candidate_epldata_id","candidate_name","candidate_birth_date","match_method","verification_status","import_ready"]).to_csv(D/"2024_25_identity_candidates_UNVERIFIED.csv",index=False)
 print(json.dumps({"players":len(players),"historical_player_club_seasons":len(season),"historical_career_club_totals":len(career),"note":"Unverified community dataset; not approved for Supabase import."}))
if __name__=="__main__":main()
