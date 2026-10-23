# Football Bowls — appearance-data audit (23 October 2026)

## Scope
The deployed `index.html` contains Premier League player–club appearance totals intended to cover 1992/93–2025/26. The audit checked structural integrity of the deployed data and the eight 2018/19–2025/26 season CSVs, with reference to the project's earlier historical integrity files and selected official Premier League benchmarks. This is **not** an independent row-by-row verification of all 7,697 totals against the Premier League.

## Results
- 51 distinct club labels, 7,697 game player–club rows after fixing Elias Kachunga.
- Eight later season files examined (2018/19–2025/26): 5,097 source player-season rows; 931 zero-appearance rows appropriately omitted from positive-appearance aggregation.
- No non-integer, negative, or greater-than-38 single-season appearance values found in those eight source files.
- No repeated player-name-to-multiple-player-ID or player-ID-to-multiple-name cases within the *same club* in the eight later source files.
- The game's existing duplicate-name entries were:
  - Coventry City — Paul Williams (164 and 16). **Do not merge automatically**: distinct-player identity needs manual confirmation.
  - Everton — Mark Hughes (18 and 1). **Do not merge automatically**: distinct-player identity needs manual confirmation.
  - Huddersfield — Elias Kachunga (16 and 3), plus 20 appearances in the newer source. Corrected to **39** total and deduplicated.
- Selected known benchmarks: Robinho / Manchester City 41; Ryan Giggs / Manchester United 632; James Milner summed across his six clubs 658. These match available official benchmarks, but a sample check is not a full certification.

## Important historical source limitations
The historical extraction's own `historical_integrity_audit.json` explicitly marks **63 potentially valid unlinked appearances** unresolved and says the historical data are **NOT APPROVED**. It also records 76 unlinked player-game rows, 11 registration/match-club disagreements (zero eligible), 31 duplicate player-match rows (zero eligible), and one orphan match record in 1998/99. These need match-level investigation before claiming the old data are fully verified.

## Outstanding risks / next actions
1. Resolve all 63 historical candidate appearances against authoritative match lineups and the relevant club. Do not silently assign them.
2. Replace the game's `[name, appearances]` representation with stable player IDs. Otherwise two distinct players with the same display name cannot be selected unambiguously.
3. Reconcile cross-period player identity (1992–2018 vs 2018–2026), including nicknames, accents, full-name/short-name changes and club aliases. The later source has IDs; the earlier game entries are names only.
4. Compare each of the 7,697 player–club totals against a reliable independent source, or reconcile all season records with independently verified match lineups.
5. Record source version/date and verification status for each number; add automated tests that prevent publishing incomplete or provisional figures as verified.

## Source references
- Official Premier League all-time statistics: https://www.premierleague.com/en/stats/all-time
- Official Robinho record: https://www.premierleague.com/en/players/15107/robinho/career
- Later-season CSVs: https://github.com/imadeddine-belkat/Premier-League-Stats/tree/main/pl_stats/_merged/players
- Historical integrity report: `epldata_checked/historical_integrity_audit.json` in the original project work files (not necessarily committed in this repository).

## Release status
**PROVISIONAL — NOT APPROVED FOR CLAIMS OF FULL STATISTICAL ACCURACY.** Automated structural checks passed for the newer source, but the unresolved historical records and player identity problems remain material.
