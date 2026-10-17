# Phase 2: Real Premier League appearance statistics

The historical roster contains **6,880 candidate players**, not 6,880 confirmed Premier League players. The source contains squad membership but **no appearances field** (see https://github.com/Samoilov2004/premier_league_dataset).

## Input data contract

Create a CSV with these columns:
`player_id,player_name,club_id,club_name,season_start,appearances,source_url`

Each row must represent the **number of Premier League matches played** for one player, one club, one season (including appearances as a substitute). Zero is allowed in the season file, but a zero-total player must not enter the game's master list. Exclude cup games, Championship games, unused substitute listings, and starts-only figures.

Use stable player identifiers from the candidate roster where identities match; avoid merging namesakes. Source URLs should identify the actual statistic, not merely a club squad.

Run `python scripts/aggregate_season_appearances.py data/pl_season_appearances.csv`. The output `output/appearance_review/club_totals_UNVERIFIED.csv` aggregates seasons by player and club, with `verification_status=pending` and no final source URL. It cannot pass the Supabase importer until independently checked and promoted.

**Validation plan:** check coverage by season and club; verify a representative sample against official Premier League statistics; reconcile player identities, club transfers, substitute appearances, duplicate seasons, and active player updates; investigate discrepancies before publishing.

**Source caution:** the existing squad dataset is sourced from Transfermarkt and does not supply appearance counts. FootyStats offers player-season statistics for some seasons, but availability, licensing, and coverage require checking. The Premier League's own historical appearance statistics are a benchmark. Do not import guessed or simulated numbers.
