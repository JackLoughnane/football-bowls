#!/usr/bin/env python3
"""Parse positional word CSVs extracted from official 2024/25 PL handbook.
Input: downloaded workflow artifact, extracted into --input-dir.
Review only; not career totals or approved for Supabase import.
"""
import argparse,csv,collections,pathlib,re
HEADERS={389:{'left':[(98,'AFC Bournemouth'),(323,'Arsenal')],'right':[(98,'Aston Villa'),(304,'Brentford')]},390:{'left':[(75,'Brighton & Hove Albion'),(321,'Chelsea')],'right':[(75,'Crystal Palace'),(301,'Everton')]},391:{'left':[(75,'Fulham'),(250,'Ipswich Town')],'right':[(75,'Leicester City'),(301,'Liverpool')]},392:{'left':[(75,'Manchester City'),(291,'Manchester United')],'right':[(75,'Newcastle United'),(257,'Nottingham Forest')]},393:{'left':[(75,'Southampton'),(301,'Tottenham Hotspur')],'right':[(75,'West Ham United'),(260,'Wolverhampton Wanderers')]}}
COLS=[(47,215,'left'),(218,400,'left'),(467,635,'right'),(637,806,'right')]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-dir',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,default=pathlib.Path('output/season_2024_25/parsed_player_rows.csv'))
    args=ap.parse_args()
    records=[]
    for page in HEADERS:
        path=args.input_dir/f'page_{page}_words.csv'
        with path.open(newline='',encoding='utf-8') as f:
            words=list(csv.DictReader(f))
        groups=collections.defaultdict(list)
        for w in words:
            x=float(w['x0']);y=round(float(w['top']))
            for ci,(lo,hi,side) in enumerate(COLS):
                if lo<=x<hi:
                    groups[(y,ci)].append((x,w['text']))
                    break
        for (y,ci),ws in sorted(groups.items()):
            side=COLS[ci][2]
            eligible=[(start,name) for start,name in HEADERS[page][side] if y>start+7]
            if not eligible:continue
            club=eligible[-1][1]
            tokens=[t for _,t in sorted(ws)]
            if len(tokens)<5 or not all(re.fullmatch(r'\d+',t) for t in tokens[-4:]):continue
            name=' '.join(tokens[:-4])
            if not re.search('[A-Za-zÀ-ÿ]',name):continue
            p,sub,unused,goals=map(int,tokens[-4:])
            if p>38 or sub>38 or p+sub>38:
                raise ValueError(f'Impossible appearances on PDF page {page}: {club}, {name}, {p}+{sub}')
            records.append([club,name,p,sub,unused,goals,p+sub,page,y])
    keys=[(r[0],r[1]) for r in records]
    if len(set(keys))!=len(keys):raise ValueError('Duplicate player-club names')
    if len(set(r[0] for r in records))!=20:raise ValueError('Not all 20 clubs found')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow(['club','player_name','starts','sub_appearances','unused_sub','goals','total_appearances','source_pdf_page','row_y'])
        writer.writerows(records)
    print(f'Extracted {len(records)} player-club rows; {sum(r[6]>0 for r in records)} played; {sum(r[6]==0 for r in records)} unused-only')
    print('Review-only data: NOT approved for career totals or automatic import.')
if __name__=='__main__':main()
