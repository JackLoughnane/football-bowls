# 2024/25 unmatched player verification: independent club-level source

The first independent dataset matched 521 of 574 appearance-positive rows. Its 53 unmatched/ambiguous rows are not necessarily errors. The comparison source is incomplete and has transfer aggregation issues.

## Priority sources

- Leicester City 2024/25 **Premier League** statistics: https://fbref.com/en/squads/a2d435b3/2024-2025/ — use the **Playing Time** table's **MP** (matches played) and **Starts** columns.
- Liverpool 2024/25 **Premier League** statistics: https://fbref.com/en/squads/822bd0ba/2024-2025/Liverpool-Stats — same columns.
- Official PL 2024/25 squad list (identity support only, **not evidence of appearances**): https://www.premierleague.com/en/news/4110099

**Critical:** Do not use the FBref pages marked **All Competitions**; they include cups and European matches. In the Premier League Playing Time table, `MP` is appearances, `Starts` is starting appearances, and `Subs` is substitute appearances. Thus `MP = Starts + Subs` for each player.

## Verification procedure

1. Open `unmatched_review_queue.csv` from the previous workflow.
2. Start with Leicester City (17 unmatched) and Liverpool (13 unmatched).
3. Compare each player against the correct **Premier League-only** FBref club page; verify club, season, name, MP, Starts, and Subs.
4. Mark each row `verified`, `disputed`, or `not_found`; record source URL and the exact independent figures.
5. Where names differ, confirm identity independently before merging.
6. Repeat for the remaining 23 unmatched rows across other clubs.
7. **Do not** write any of these rows to Supabase until all discrepancies are resolved and the club-season dataset has a reviewed provenance trail.

The original extracted handbook remains the primary source. Independent agreement strengthens confidence, but is not a license to silently change it.
