# Importing verified appearances into Supabase

**The current CSV is empty. Do not import synthetic/demo appearance counts.**

1. Populate `data/appearance_candidates.csv` with independently checked Premier League-only player-by-club totals. Include substitute appearances and exclude lower-division, cup and unused-bench matches.
2. Run `python scripts/validate_appearances.py data/appearance_candidates.csv`. This checks structure, **not** whether the football statistics are true.
3. Dry-run `python scripts/import_verified.py data/appearance_candidates.csv`.
4. Only after manual source review, set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as local environment variables and run `python scripts/import_verified.py data/appearance_candidates.csv --apply`.

The service-role key is a privileged secret. **Never paste it into a GitHub file, HTML page, chat message, or browser app.** This importer intentionally does not run in GitHub Actions yet; a controlled secret-backed workflow can be added after the source pipeline is validated.

Import order is clubs, players, appearances. Upsert updates records with matching player/club IDs. Club names must be consistent across rows.

This importer does not create the historical master list or automatically refresh active players. Those require a trustworthy source feed, identity reconciliation, change detection, and exception handling.
