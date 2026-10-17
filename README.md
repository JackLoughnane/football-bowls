# Football Bowls — playable prototype

## Play locally
Open `index.html` in a browser and choose **Pass & play**. No server or installation needed.

## Enable online rooms
1. Create a Supabase project at supabase.com.
2. Run `supabase.sql` in the project's SQL editor.
3. Host `index.html` on a static host (Netlify, Vercel, GitHub Pages) with HTTPS.
4. On each device, choose **Play online** and enter the **same** Supabase project URL and publishable/anon key. Do **not** enter a service-role/secret key.
5. Player 1 creates a room and shares the code/link. Player 2 joins using that code.

Online state is synchronised using REST polling about every 1.8 seconds. Both players must remain connected. The prototype does not include accounts, reconnection guarantees, server-side anti-cheat, secure private rooms, or automated room cleanup.

## IMPORTANT: data accuracy
Bundled appearance totals come from the provisional epldata 1992/93–2017/18 Premier League match extract, not synthetic placeholders. These are not necessarily complete career totals, especially for players active after 2017/18. Replace `DATA` in `index.html` with verified, licensed club-specific Premier League appearance totals before publishing as a trivia game. Real records must aggregate all spells at a club and include substitute appearances. Prefer a fixed season-end snapshot.

## IMPORTANT: security
The SQL policies intentionally permit public reads/writes to simplify prototyping. Anyone with the project URL and anon key can tamper with game rooms. **Do not deploy these policies for a public competitive game.** For production, move game rules, player eligibility, room authorization, turn enforcement and appearance checks into trusted server-side functions and restrict table permissions. Add rate limits, authentication/guest tokens, input validation, expiration and replay protection.

## Rules
Two players alternate 3 guesses each. Each name may only be used once per round. Closest individual guess to the target wins 1 point; equal distance is a draw. After the chosen number of rounds, most points wins. Invalid players are prevented by autocomplete.

## Known prototype limitations
- Provisional historical match data, not fully audited, with deterministic target generation.
- No live licensed data feed.
- Online mode requires your own Supabase configuration and hosting.
- Race protection is best-effort optimistic version checking, not authoritative server-side validation.
- The bowls pitch clips guesses far outside the target range for readability.

## Updated scoring rules (v2)
- Each player has three turns per round.
- A surviving bowl scores one point if its distance from the target is strictly less than the closest surviving bowl of the opposing player. This can award 0–3 placement points to a player.
- An exact target earns an additional bonus point for each surviving exact bowl.
- If a later guess has the same appearance count as an earlier surviving opponent guess, the earlier guess is knocked out and cannot score. This applies regardless of whether the later guess is closer to the target (they are equally distant).
- Duplicate player names are not allowed within a round, but distinct players with the same appearance count are allowed.
- Tied distances do not count as closer. If an opponent has no surviving bowls, every surviving bowl counts as closer.
- The match lasts the configured number of rounds; highest cumulative points wins. Draws are possible.
- These rules apply to local play and the client-side online prototype. Online play still needs server-side authoritative validation before public competitive release.
