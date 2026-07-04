# Toolbench — autonomous build-loop rules

The owner's directive: **build the store, then keep building genuinely useful
apps into it, nonstop, autonomously.** These rules keep that from repeating the
old "15 apps, 0 AZN" mistake. They adapt the money-first engine in
`/Users/mac/Documents/Claude/AUTONOMOUS-ENGINE.md` to a build loop.

## What the loop does each iteration
1. **Read `BACKLOG.md` and `LEDGER.md` first.** Take the top backlog item that
   passes the gates below. If the backlog is empty, do fresh, skeptical research
   and add 3–5 new vetted ideas (never filler to hit a number).
2. **Build ONE tool** as its own `Emin-dev/<name>` repo — vanilla JS ES modules,
   zero dependencies, no build step, deploy to GitHub Pages. It runs client-side
   (private by default; nothing uploaded).
3. **Verify for real, both layers**, before deploy:
   - Node tests for every pure-logic module (`node test/*.test.mjs`).
   - A real interactive pass in **Preview MCP only** (never the owner's Safari /
     claude-in-chrome / computer-use) — click the core flow, check console is
     clean, and take a **mobile-viewport screenshot** before deploying.
4. **Deploy + verify live** — `curl` the live files, confirm 200s and that the
   real new code is served (not a stale build). Fix Pages flakiness with
   disable+re-enable if needed.
5. **List it in the store** — add the entry to `js/products.js` (status `live`),
   commit + push the hub, confirm the live hub picked it up.
6. **Log honestly in `LEDGER.md`** — what shipped, what was verified at both
   layers, real bugs found + fixed. Record that a ship is **not revenue**;
   distribution and a paying buyer are separate, still-missing steps.

## Binding gates — a tool is only built if ALL pass
- **Useful gate:** it solves a real, specific, nameable job for a nameable
  person. If the honest description is "a small random toy", it is CUT.
- **Defensibility gate:** a random person could not reproduce it in an
  afternoon with ChatGPT (real engine, real data, real domain logic, or real
  polish). No thin GPT-wrappers.
- **No-backend gate:** it works fully client-side with no paid API and no
  server cost hidden behind a "Phase 2". If it genuinely needs a backend, note
  that honestly and pick a different item.
- **Payment honesty gate:** monetization is only `free`, `buy`, `rent`, or
  `sell` — **never ads**. Any paid tier is a clearly-labelled sandbox until the
  owner sets up real payment. Wiring a real payment account or live charging is
  a **stop-and-ask**, never automatic.

## Hard constraints (never violated)
- **No ads, ever.** No brainrot / low-effort filler apps.
- **Never delete shipped work** — freeze/archive only. The old 15 repos stay
  untouched.
- **Never use the owner's real browser** to test — Preview MCP only, stated
  explicitly in any subagent prompt.
- **Screenshot at mobile size before every deploy.**
- **Stop and ask** before: real payment/business-account setup, going live with
  real charging, or anything hard to reverse (deleting/renaming a shipped
  product).
- **Be honest in every ledger entry:** shipping more tools does not by itself
  create revenue. That needs real distribution + a paying customer, which the
  loop cannot fabricate — it can only prepare (drafts, target lists) for the
  owner to act on.

## Pacing
Self-paced, ~20–30 minutes between iterations (`ScheduleWakeup`). Quality over
speed — one solid, verified tool per iteration beats three rushed ones.
