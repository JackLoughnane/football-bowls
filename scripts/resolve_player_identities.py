#!/usr/bin/env python3
"""Apply independently reviewed player IDs to season staging, never guess."""
import argparse,csv,json,collections,pathlib
KEY=('season','club_code','source_player_name')
FIELDS=('player_external_id','player_canonical_name','identity_source_url','identity_reviewer','identity_reviewed_at')
def read(path):
 with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 p=argparse.ArgumentParser()
 for x in ('staging','registry','output'):p.add_argument('--'+x,required=True)
 a=p.parse_args();rows=read(a.staging);evidence=read(a.registry);idx={};errors=[]
 for r in evidence:
  k=tuple(r.get(x,'').strip() for x in KEY)
  if not all(k) or k in idx or not all(r.get(x,'').strip() for x in FIELDS) or not r['identity_source_url'].startswith('https://'):
   errors.append('Incomplete, duplicate, or invalid registry row: '+str(k))
  else:idx[k]=r
 known={tuple(r[x].strip() for x in KEY) for r in rows}
 for k in idx:
  if k not in known:errors.append('Unknown staging key: '+str(k))
 names=collections.defaultdict(set)
 for r in idx.values():names[r['player_external_id'].strip()].add(r['player_canonical_name'].strip().casefold())
 for player_id,n in names.items():
  if len(n)>1:errors.append('Conflicting canonical names: '+player_id)
 if errors:raise SystemExit(json.dumps({'errors':errors},indent=2))
 matched=0
 for r in rows:
  k=tuple(r[x].strip() for x in KEY)
  if k in idx:
   for field in FIELDS:r[field]=idx[k][field].strip()
   r['identity_status']='reviewed_external_id_with_evidence';matched+=1
  r['import_ready']='False'
 out=pathlib.Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 print(json.dumps({'rows':len(rows),'reviewed':matched,'unresolved':len(rows)-matched,'import_ready':0},indent=2))
if __name__=='__main__':main()
