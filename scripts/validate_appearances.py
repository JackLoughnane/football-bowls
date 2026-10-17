#!/usr/bin/env python3
"""Structural validation only. This does not establish statistical accuracy."""
import csv
import json
import pathlib
import sys

FIELDS = ("player_id","player_name","club_id","club_name","appearances","source_url","verification_status")

def validate(path):
    accepted, rejected, seen = [], [], set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        for row_number, row in enumerate(reader, 2):
            errors = []
            for field in FIELDS:
                if not (row.get(field) or "").strip():
                    errors.append(f"missing {field}")
            try:
                apps = int((row.get("appearances") or "").strip())
                if apps < 1:
                    errors.append("appearances must be positive")
            except ValueError:
                errors.append("appearances must be an integer")
            if row.get("verification_status","").strip().lower() != "verified":
                errors.append("not independently verified")
            url = row.get("source_url","").strip()
            if url and not url.startswith("https://"):
                errors.append("source_url must use https")
            key = (row.get("player_id","").strip(), row.get("club_id","").strip())
            if key in seen:
                errors.append("duplicate player-club pair")
            seen.add(key)
            if errors:
                rejected.append({**row, "row_number": row_number, "errors": "; ".join(errors)})
            else:
                accepted.append(row)
    return accepted, rejected

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/validate_appearances.py input.csv")
    path = pathlib.Path(sys.argv[1])
    accepted, rejected = validate(path)
    output = pathlib.Path("output")
    output.mkdir(exist_ok=True)
    write_csv(output / "accepted.csv", accepted, FIELDS)
    write_csv(output / "rejected.csv", rejected, (*FIELDS,"row_number","errors"))
    summary = {"accepted": len(accepted), "rejected": len(rejected),
               "note": "Structural validation is not independent statistical verification"}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))
    if rejected:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
