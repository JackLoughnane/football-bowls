#!/usr/bin/env python3
"""Extract 2024/25 official PL handbook statistics into REVIEW-ONLY files.

Page layouts are complex. Output is not verified or import-ready.
"""
import csv
import io
import json
import pathlib
import re
import urllib.request
import pdfplumber

URL="https://resources.premierleague.pulselive.com/premierleague/document/2025/07/24/99839920-d274-42aa-a2ac-e5612b4f6c61/PL_Handbook_25-26_Digital_24.07.pdf"
OUT=pathlib.Path("output/season_2024_25")
CLUBS=["AFC Bournemouth","Arsenal","Aston Villa","Brentford","Brighton & Hove Albion",
"Chelsea","Crystal Palace","Everton","Fulham","Ipswich Town","Leicester City",
"Liverpool","Manchester City","Manchester United","Newcastle United",
"Nottingham Forest","Southampton","Tottenham Hotspur","West Ham United","Wolverhampton Wanderers"]
# The PL tables occupy PDF pages 389-393 (1-indexed); detect by heading instead of assuming indices.
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(URL,headers={"User-Agent":"FootballBowls/0.1"})
    with urllib.request.urlopen(req,timeout=120) as response:
        raw=response.read()
    (OUT/"source.json").write_text(json.dumps({"source_url":URL,"season":"2024/25",
        "bytes":len(raw),"status":"extraction_for_review_only"},indent=2),encoding="utf-8")
    page_count=0
    rows=[]
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for index,page in enumerate(pdf.pages):
            text=page.extract_text(x_tolerance=2,y_tolerance=3) or ""
            if "Premier League Appearances and Goals" not in text or "Season 2024/25" not in text and not (388<=index<=392):
                continue
            # Retain raw text and positional words for reconstructing multi-column tables.
            page_count+=1
            (OUT/f"page_{index+1:03d}.txt").write_text(text,encoding="utf-8")
            words=page.extract_words(x_tolerance=2,y_tolerance=3)
            with (OUT/f"page_{index+1:03d}_words.csv").open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=["text","x0","top","x1","bottom"])
                writer.writeheader()
                writer.writerows([{k:w.get(k) for k in writer.fieldnames} for w in words])
            rows.append({"pdf_page":index+1,"detected_clubs":"; ".join(c for c in CLUBS if c in text),
                         "word_count":len(words)})
    with (OUT/"page_manifest.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["pdf_page","detected_clubs","word_count"])
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"pages_extracted":page_count,"page_manifest":rows},indent=2))
    if page_count<5:
        raise SystemExit("Expected at least five statistics pages; extraction needs review")

if __name__=="__main__":
    main()
