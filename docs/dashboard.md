# Bob Progress Dashboard

Last updated (UTC): 2026-02-15

## Mission
Build a safe, reliable SPY swing-trading bot for IBKR, paper-first.

## Current Focus
- Reliability hardening
- Risk controls persistence
- Execution correctness
- Observability and alerting

## Now / Next / Blocked

### Now
- Review and merge PR #4 (risk-state persistence)
- Prepare reconnection hardening slice (IBKR resilience)

### Next
1. IBKR disconnect/reconnect handling with bounded retries
2. Order-state reconciliation after restart
3. Telegram run summaries + risk alerts
4. Expand tests for execution edge cases

### Blocked
- None at the moment

## Active PRs
- #4 Persist risk state across restarts
  - https://github.com/asistantbob-glitch/spy-swing-bot/pull/4

## Active Issues
- #1 Roadmap: Production hardening
  - https://github.com/asistantbob-glitch/spy-swing-bot/issues/1
- #2 Research: open-source IBKR patterns
  - https://github.com/asistantbob-glitch/spy-swing-bot/issues/2
- #3 Research: Solana ecosystem primer (research-only)
  - https://github.com/asistantbob-glitch/spy-swing-bot/issues/3

## Risks / Watchouts
- Restart safety gaps if risk state is not persisted (addressed by PR #4)
- API session drops can cause inconsistent execution if not reconciled
- Need clear, rate-limited alerting to avoid noise fatigue

## Decision Log
- Use 1H bars with 4H primary timeframe for SPY swing logic
- Keep paper-only mode as default until explicit go-live approval
- No direct pushes to `main`; use PRs for all structural changes

## Weekly Improvement Cycle
Each week:
1. Review recent commits and PRs
2. Pick one engineering skill to improve
3. Apply improvement in code
4. Document in `lessons.md`

## Communication Cadence (A + C)
- GitHub-native dashboard updates in this file
- Telegram summaries:
  - quick progress updates on major milestones
  - end-of-day summary when meaningful progress is made
