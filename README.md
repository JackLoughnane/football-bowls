# Football Bowls

Historical Premier League player appearance data infrastructure.

## Current status
The initial database schema and validation workflow are installed. **No complete player list or verified appearance totals have been imported yet.** The existing game's synthetic figures must not be treated as real.

## Supabase setup
In the existing Supabase project, open SQL Editor and run [sql/001_player_database.sql](sql/001_player_database.sql). It adds `fb_clubs`, `fb_players`, `fb_player_club_appearances`, and `fb_data_updates` without changing the multiplayer room table.

The new player tables allow public reads but no public writes under row-level security. Do not commit database secrets to GitHub.

## Validation
Edit [data/appearance_candidates.csv](data/appearance_candidates.csv) using these fields:

`player_id,player_name,club_id,club_name,appearances,source_url,verification_status`

Run `python scripts/validate_appearances.py data/appearance_candidates.csv`. Outputs are in `output/`. A row marked `verified` passes only structural checks; the script **does not independently establish that the football statistic is correct**.

The [GitHub Actions workflow](.github/workflows/validate-appearance-data.yml) runs validation on Mondays and Thursdays and on changes to the candidate data. It **does not yet scrape Wikipedia, update active-player totals, or write to Supabase**.

## Next steps
1. Identify and deduplicate every historical Premier League player with a confirmed match appearance.
2. Establish accurate Premier League-only appearances by player and club.
3. Add independent cross-source validation and exception reports.
4. Add authenticated Supabase import and scheduled refresh.
5. Update Football Bowls to load a frozen verified dataset snapshot.
