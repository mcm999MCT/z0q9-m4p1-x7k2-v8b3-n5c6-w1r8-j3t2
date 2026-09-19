# Crypto Intelligence Bot — Project Status

Last updated:

```text
Stage 3 completed and live-verified. Project scope paused at Solana-only.
```

---

# Current Status

## Overall

```text
Project Status: IN PROGRESS — SCOPE PAUSED (Solana-only for now)
Current Stage: Stage 3 COMPLETE AND LIVE-VERIFIED
Stage 4 (EVM chains): ON HOLD — do not start until explicitly requested
```

---

# Completed

* [x] GitHub repository created (project owner's responsibility — files are ready)
* [x] Project specification added
* [x] Development rules added
* [x] Project structure created
* [x] Configuration system
* [x] SQLite database
* [x] Logging
* [x] Blockchain abstraction
* [x] Solana provider
* [ ] EVM provider
* [ ] Ethereum support
* [ ] Base support
* [ ] BNB Smart Chain support
* [ ] Arbitrum support
* [ ] Robinhood Chain support
* [ ] Market-data integration
* [ ] Token discovery
* [ ] Growth tracking
* [ ] Liquidity analysis
* [ ] Solana holder analysis
* [ ] EVM holder analysis
* [ ] Creator/deployer analysis
* [ ] Security analysis
* [ ] Wallet tracking
* [ ] Smart-money scoring
* [ ] Token scoring
* [ ] Discord alerts
* [ ] Alert deduplication
* [ ] Parallel scanning
* [x] Automated tests (Stage 1 scope — more added every stage)
* [x] README
* [x] Dry-run mode (flag recognized; nothing to "dry run" yet)
* [x] Demo mode (flag recognized; no demo data yet since there's no scanning)
* [x] One-scan mode (flag recognized; loop-forever mode not built yet)

---

# What was done in Stage 1

Built the foundational skeleton of the application — the "plumbing" that
every later stage will run on top of. No blockchain scanning exists yet.

**Files created:**

```text
app/config.py            — reads all settings from environment variables
app/logging_setup.py     — sets up safe, consistent logging (with a
                            safeguard against ever printing secret values)
app/database/db.py       — creates/opens the local SQLite database file
app/database/repository.py — placeholder; will be filled in as real
                            data tables are added in later stages
app/main.py               — wires config + logging + database together
run.py                     — the command you run to start the bot
requirements.txt           — the two packages needed so far
.env.example                — template listing every setting, with notes
.gitignore                  — keeps secrets and generated files out of Git
README.md                   — step-by-step setup instructions
tests/test_config.py        — 7 tests for the configuration system
tests/test_database.py      — 5 tests for the database setup
tests/test_logging_setup.py — 4 tests for the logging safeguard
tests/test_main.py          — 2 end-to-end tests that run the whole app
```

**Why it was done this way:**

* Configuration comes from environment variables (a `.env` file), never
  hard-coded, so no secrets end up in the code — this follows AGENTS.md
  rule 8.
* The database uses SQLite (a single local file, no server needed) as
  required by AGENTS.md rule 21 and the spec.
* Logging has a built-in safety net that will hide anything that looks
  like a real secret value (like an actual API key), even if a future
  bug accidentally tried to log one.
* Nothing was built ahead of what Stage 1 needs — for example, the real
  database tables for tokens/wallets/scores come later, once those
  features exist, per AGENTS.md rule 23 ("don't rewrite/over-build").

**What I tested:**

* Ran the full automated test suite: **18 tests, all passed.**
* Ran the bot for real from the command line
  (`python run.py --dry-run --once`) and confirmed it starts up, reports
  its configuration, creates the database file, and exits cleanly.
* **Found and fixed one real bug during this manual testing:** the
  logging safety filter was too aggressive — it was hiding a harmless
  message that just *mentioned* the name "MARKET_DATA_API_KEY" (saying
  it wasn't configured yet), even though no actual secret was in that
  message. I tightened the filter so it only hides messages that contain
  an actual secret-like value, not just a variable name, and added tests
  specifically covering this case so it can't silently come back.

**Whether anything failed:** No — after fixing the logging bug above, all
tests pass and the bot runs cleanly.

---

# What was done in Stage 2

Built the shared "shapes" and rules that every blockchain connection will
plug into later. **No real blockchain connections were built — nothing in
this stage talks to Solana, Ethereum, or any other network.** That starts
in Stage 3 (Solana) and Stage 4 (EVM chains).

**Files created:**

```text
app/models/chain.py    — the official list of the 6 supported chains and
                          their IDs (Ethereum=1, Base=8453, BNB=56,
                          Arbitrum=42161, Robinhood=4663, Solana has none)
app/models/token.py     — the rule that a token is identified by
                          (chain, token_address), never the address alone
app/models/wallet.py    — the same rule for wallets:
                          (chain, wallet_address)
app/chains/base.py       — the common "shape" (BlockchainProvider) that
                          the real Solana and EVM connections must follow
app/chains/registry.py    — the lookup table that will connect a chain
                          name to its real provider, once one exists

tests/test_models_chain.py    — 12 tests
tests/test_models_token.py    — 10 tests
tests/test_models_wallet.py   — 7 tests
tests/test_chains_base.py     — 4 tests
tests/test_chain_registry.py  — 6 tests
```

**Why it was done this way — in plain language:**

* **The chain list (`chain.py`)** is now the single place that says
  "these are the 6 blockchains this bot knows about, and here are their
  ID numbers." Those ID numbers are typed in exactly as they appear in
  `PROJECT_SPEC.md` section 4 — nothing was guessed.
* **The identity rules (`token.py`, `wallet.py`)** enforce something
  important from the spec: a token or wallet is never identified by its
  address alone, only by *(which chain it's on, plus its address)*. This
  matters because the exact same address can exist as a completely
  different, unrelated token or wallet on two different chains. I wrote
  automated tests that specifically prove the same address on two
  different chains is treated as two different things — this is a rule
  that would be easy to accidentally break later, so it's locked in now
  with tests.
* **The common interface (`chains/base.py`)** is the blueprint that the
  real Solana connection (Stage 3) and the real EVM connection (Stage 4)
  will both have to follow. Think of it like a standard electrical
  outlet shape — as long as every chain "plugs in" using the same shape,
  the rest of the bot doesn't need to know or care whether it's talking
  to Solana or Ethereum under the hood. Right now this blueprint only
  requires one thing: a way to check "is this chain reachable right
  now?" That's intentional — it's exactly what's needed to satisfy the
  spec's rule that one broken chain (e.g. Base having an outage) must
  never stop the other chains from being scanned. More requirements will
  be added to this blueprint only once each real capability (reading
  token supply, holder data, etc.) is actually built against verified,
  official documentation — not guessed at ahead of time.
* **The registry (`chains/registry.py`)** is an empty coat-rack right
  now — it's built and tested, but nothing is hung on it yet, because
  there's no real Solana or EVM connection to hang there. Trying to use
  it before Stage 3/4 correctly gives a clear "not built yet" message
  instead of pretending to work.
* I did **not** yet build a shared model for market data (price,
  liquidity, volume, etc.), even though `PROJECT_SPEC.md`'s example
  folder listing shows a `models/market.py` file. That's deliberate: a
  model for market data would be empty and untested until we actually
  pick a market-data provider in Stage 5. Building it now would mean
  guessing at fields we can't verify yet, which goes against AGENTS.md's
  "never invent data" and "build incrementally" rules. I'll build it
  properly in Stage 5, once there's a real provider behind it.

**What I tested:**

* Ran the full automated test suite: **63 tests, all passed** (the
  original 18 from Stage 1, plus 45 new ones for Stage 2).
* Specifically tested the identity rule with real examples: confirmed
  that a token at the same address on Ethereum, Base, and Robinhood
  Chain are correctly treated as three separate tokens, not one.
* Confirmed the blueprint (`BlockchainProvider`) cannot be used directly
  — only a real, finished chain connection can use it, which is enforced
  automatically by Python, not just by convention.
* Confirmed that trying to look up a Solana or EVM connection through the
  registry right now correctly fails with a clear, friendly explanation
  ("not built yet") instead of crashing unexpectedly or silently doing
  nothing.
* Re-ran the Stage 1 startup check (`python run.py --dry-run --once`) to
  confirm none of the new Stage 2 code broke anything that was already
  working — it still starts up and exits cleanly.
* Checked the new code by hand for anything that would violate AGENTS.md:
  no real network/RPC calls, no invented prices or holder counts, no
  hard-coded secrets. None found.

**What I fixed:** Nothing needed fixing — all tests passed on the first
full run.

**Whether anything failed:** No.

---

# What was done in Stage 3

Built the **first real blockchain connection** in the project: a working,
read-only connection to Solana. Before writing any code, I looked up
Solana's official RPC documentation (solana.com/docs/rpc) to confirm the
exact request/response format for every method used — nothing was
guessed.

**Files created:**

```text
app/chains/solana.py          — the real Solana connection (SolanaProvider)
app/chains/solana_address.py   — validates that a string is a properly
                                 formatted Solana address, before ever
                                 sending it to the network

tests/test_chains_solana.py    — 26 tests
tests/test_solana_address.py   — 12 tests
```

**What it can do (all read-only, no exceptions):**

* **Check whether the Solana network is reachable** — used by the future
  scanner to know if Solana is having problems, without crashing the
  whole bot (PROJECT_SPEC.md section 19).
* **Look up a token's total supply.**
* **Look up a token's 20 largest holder accounts** — exactly as
  PROJECT_SPEC.md section 16 asks for. Important: these are the 20
  largest *accounts*, which the spec is explicit are NOT automatically
  human wallets — they can be liquidity pools, programs, or other
  infrastructure. Figuring out which is which is Stage 7's job; Stage 3's
  job is only to fetch the raw, accurate numbers.

**What it can NEVER do, by design — not just by choice:** There is no
method anywhere in this code that accepts a private key or seed phrase,
and no method that signs or sends a transaction. I wrote an automated
test that scans every method on this class and fails the build if any
method name contains a word like "sign", "buy", "sell", "swap", or
"trade", or if any method accepts a parameter with "private", "secret",
or "seed" in its name — so this isn't just a promise, it's continuously
checked.

**Why it was built this way — in plain language:**

* **Real documentation first.** Before writing a single line, I looked up
  Solana's own official docs for `getHealth`, `getTokenSupply`, and
  `getTokenLargestAccounts` and copied their exact example
  requests/responses into the code comments and tests, so the code is
  built against what Solana actually returns — not a guess.
* **The RPC address is never hard-coded.** It's read from
  `SOLANA_RPC_URL`, exactly like Stage 1 set up. I added a comment in
  `.env.example` mentioning that Solana's own free public address
  (`https://api.mainnet-beta.solana.com`) works fine for V1 — but that's
  documentation for you, not something baked into the code.
* **Network problems can't crash the bot.** If the Solana network is
  slow, rate-limits us, or is briefly down, the code automatically
  retries a few times with increasing delays between attempts (this is
  called "exponential backoff" — waiting a little longer each time
  instead of hammering a struggling server). If it still can't get an
  answer after retrying, it reports "this chain isn't working right now"
  instead of crashing — which is exactly what lets the future scanner
  skip a broken chain and keep going with the others.
* **Bad or missing data becomes "I don't know", never a guess.** If you
  ask about a token address that's typed wrong, or a token the network
  has no data for, you get a clear "no data available" rather than a
  fabricated number.
* **No new paid service was needed or added.** Solana's own free,
  official public RPC endpoint covers everything this stage needed.

**What I tested:**

* Ran the full test suite: **96 tests, all passed** (the previous 63,
  plus 33 new ones).
* Verified two real, well-known Solana addresses (the USDC token and
  wrapped SOL) correctly pass address validation, and that garbage input
  never crashes the validator, only returns "not valid."
* Simulated real-world network problems on purpose — a rate limit (too
  many requests), a server error, and a connection failure — and
  confirmed the bot retries with backoff and then fails safely (reports
  "error", doesn't crash) if the problem doesn't go away.
* Confirmed a genuinely bad request (not just a temporary problem) is
  reported immediately, without wasting time retrying something that
  will never succeed.
* Confirmed the new SolanaProvider correctly plugs into the Stage 2
  registry — proving the two stages actually connect together, not just
  that each one works alone.
* Re-ran the Stage 1 startup check — still works, unaffected.
* Made a real network request from this environment to Solana's public
  endpoint. It was blocked by this sandbox's own network rules (this
  development environment only allows connections to a small list of
  software-package sites, not blockchain networks) — but that turned out
  to be a useful test in itself: the code handled that real failure
  exactly as designed, returning a clean "error" result instead of
  crashing. I was not able to complete a fully successful live call to
  Solana from inside this environment, so please run the command below
  on your own computer to confirm a real, successful connection.

**What I fixed:** Nothing needed fixing — all tests passed on the first
full run.

**Whether anything failed:** No test failures. See the one limitation
noted below about live network testing.

---

# Stage 3 Live Verification — CONFIRMED

On 2026-09-17, the project owner ran the real connectivity check below on
their own computer (normal home/office internet, outside this development
sandbox):

```bash
python3 -c "
import asyncio
from app.chains.solana import SolanaProvider

async def main():
    provider = SolanaProvider(rpc_url='https://api.mainnet-beta.solana.com')
    health = await provider.check_health()
    print('Status:', health.status)
    print('Message:', health.message)

asyncio.run(main())
"
```

**Result received:**

```text
Status: HealthStatus.OK
```

This confirms `SolanaProvider` successfully makes a real, live connection
to Solana's public RPC endpoint. Combined with the 96/96 passing
automated tests, Stage 3 is now fully verified — both in isolated tests
and in a real-world environment.

---

# Project Scope Decision — V1 is Solana-only for now

**As of 2026-09-17, the project owner has decided V1 will focus on
Solana only.**

```text
Stage 4 (EVM chains: Ethereum, Base, BNB, Arbitrum, Robinhood) is ON HOLD.
Do NOT start Stage 4 or build any EVM functionality until the project
owner explicitly requests it.
```

What this means in practice:

* No `EVMProvider`, no Ethereum/Base/BNB/Arbitrum/Robinhood code will be
  written until asked for.
* The chain registry (Stage 2) still lists all 6 chains — that costs
  nothing to leave in place, and doesn't require building anything for
  the unused chains.
* Later stages (discovery, holder analysis, wallet tracking, security,
  scoring, Discord alerts, parallel scanning) will be built against
  Solana only, unless/until the project owner reopens EVM chains.
* This is a scope decision, not a technical limitation — the Stage 2
  architecture was deliberately built so EVM chains could be added later
  without reworking anything, if the project owner changes their mind.

---

# Next Stages

```text
Stage 1  → Project foundation                    [DONE]
Stage 2  → Blockchain abstraction                 [DONE]
Stage 3  → Solana                                 [DONE — live verified]
Stage 4  → EVM chains                             [ON HOLD — V1 is Solana-only]
Stage 5  → Market data                            [awaiting instruction]
Stage 6  → Token discovery
Stage 7  → Holder analysis
Stage 8  → Wallet tracking
Stage 9  → Security analysis
Stage 10 → Scoring
Stage 11 → Discord
Stage 12 → Parallel scanning
Stage 13 → Testing/reliability
Stage 14 → Documentation
```

Since V1 is now Solana-only, stages 6 onward (discovery, holder analysis,
wallet tracking, security, scoring, alerts, scanning) will apply to
Solana only, once the project owner is ready to continue. Stage 4 is
skipped entirely unless reopened.

---

# Supported Chains

**V1 scope updated 2026-09-17: Solana only, by the project owner's
decision.** The other chains remain listed below for reference (and
because the architecture already supports adding them later), but none
of them will be built unless the project owner explicitly reopens them.

| Chain           | Chain ID | Status  |
| --------------- | -------: | ------- |
| Solana          |      N/A | **Provider built (Stage 3) and LIVE-VERIFIED** — read-only: health check, token supply, largest holders |
| Ethereum        |        1 | **ON HOLD** — V1 is Solana-only |
| Base            |     8453 | **ON HOLD** — V1 is Solana-only |
| BNB Smart Chain |       56 | **ON HOLD** — V1 is Solana-only |
| Arbitrum One    |    42161 | **ON HOLD** — V1 is Solana-only |
| Robinhood Chain |     4663 | **ON HOLD** — V1 is Solana-only |

---

# API / Provider Costs

Current target:

```text
Claude API: $0 in V1
Nansen: $0 in V1
X/Twitter API: $0 in V1
Trading APIs: $0 in V1
```

No paid services have been introduced. Stage 1 has zero ongoing cost.

---

# Required Environment Variables

Expected configuration (all currently optional — none required for
Stage 1):

```text
SOLANA_RPC_URL=

ETHEREUM_RPC_URL=
BASE_RPC_URL=
BNB_RPC_URL=
ARBITRUM_RPC_URL=
ROBINHOOD_RPC_URL=

DISCORD_WEBHOOK_URL=

MARKET_DATA_API_KEY=

DATABASE_PATH=data/crypto_bot.db

SCAN_INTERVAL_SECONDS=60

ALERT_SCORE_THRESHOLD=80

MAX_TOKENS_PER_CHAIN=100

MAX_CONCURRENT_REQUESTS=10

LOG_LEVEL=INFO

DRY_RUN=true
```

Never put real secrets into this file — use a local `.env` file instead
(never commit `.env`).

---

# Required User Actions

```text
1. Create/confirm the GitHub repository.               [DONE]
2. Add the Stage 1 + Stage 2 + Stage 3 files.           [DONE]
3. Run `pip install -r requirements.txt`.               [DONE]
4. Add SOLANA_RPC_URL to your .env file.                [confirm done]
5. Run the real Solana connectivity check.              [DONE — confirmed OK]
6. Run `python -m pytest -v` to confirm all 96 tests pass.
7. Decide next step: V1 is now Solana-only. Let me know when you're
   ready to continue (e.g. Stage 5 — market data research, or straight
   into Solana-only token discovery/analysis), or if there's anything
   else you'd like adjusted first.
```

Later, the user will need to:

* Create a market-data API account if the chosen provider needs one
  (Stage 5 — will research and present options first)
* Create a Discord webhook (Stage 11 — will explain step by step)

EVM RPC endpoints (Ethereum/Base/BNB/Arbitrum/Robinhood) are **not**
needed — V1 is Solana-only per the project owner's 2026-09-17 decision.

---

# Known Issues

```text
None currently open.
```

**Resolved during Stage 1 testing:**
* The logging safety filter was initially too aggressive and hid a
  harmless configuration message. Fixed and covered by new tests
  (see "What was done in Stage 1" above).

**Stage 2:** No issues found — all tests passed on the first full run.

**Stage 3:** No test failures found. This development environment's own
network rules prevented it from completing a live call to Solana's
public RPC endpoint, so I asked the project owner to run a real
connectivity check on their own computer.

**RESOLVED (2026-09-17):** The project owner ran the live verification
command on their own computer, with a normal internet connection, and
received:

```text
Status: HealthStatus.OK
```

This confirms `SolanaProvider` successfully connects to Solana's real
public RPC endpoint outside this development sandbox. Stage 3 is now
fully verified, both by automated tests (96/96 passing) and by a real
live network connection. No further action needed on this item.

---

# Important Decisions

## V1 is read-only

No automatic trading.

No wallet signing.

No private keys.

No seed phrases.

---

## V1 does not use Claude inside the bot

Claude Code is being used as the developer/building assistant.

The crypto bot itself does not need the Claude API in V1.

---

## V1 does not use Nansen

The bot should build its own local wallet-performance database.

---

## V1 does not use X/Twitter

Social analysis can be added later.

---

## Multi-chain architecture

The bot should support:

```text
Solana
Ethereum
Base
BNB
Arbitrum
Robinhood
```

Solana uses its own provider.

EVM chains share an EVM provider.

---

## Robinhood Chain requires verification

Robinhood Chain (chain ID 4663) will not be implemented until its
official documentation is reviewed to confirm real RPC endpoint behavior
and EVM compatibility. This will happen at Stage 4. Its chain ID is
already recorded in the chain registry (Stage 2) because that number
comes directly from PROJECT_SPEC.md, not from any external source that
needed verification.

---

## Market-data provider not yet chosen

No market-data provider has been selected. Free/cheap options will be
researched and presented for approval before Stage 5 begins. For the same
reason, no shared market-data model (`models/market.py`) was built in
Stage 2 — it will be built in Stage 5 once there's a real provider to
verify its fields against.

---

## The blockchain provider interface will grow gradually

Stage 2's `BlockchainProvider` interface only requires one method so far
(`check_health`). Rather than guessing upfront at every method a chain
provider will eventually need (reading token supply, holder data,
security checks, etc.), those will be added to the interface only once
each capability is actually built and verified against real, official
documentation in Stage 3 onward. This avoids designing against
assumptions that later turn out to be wrong.

---

## Stage 3 database scope

No new database tables were added in Stage 3. Storing token observations
over time (PROJECT_SPEC.md section 14) is a Stage 6/7 concern, once
there's an actual discovery/scanning process generating data worth
storing. Stage 3 only builds the connection itself.

---

## Stage 3 used only Solana's own free public RPC endpoint

No paid Solana RPC provider (e.g. Helius) was needed or added. Solana's
official public endpoint (`https://api.mainnet-beta.solana.com`) covers
everything Stage 3 needed: checking connectivity, reading token supply,
and reading the largest holder accounts. If a future stage needs
something the public endpoint can't reliably provide (e.g. much higher
request volume), that will be raised explicitly before adding anything
paid, per AGENTS.md rule 18.

---

## Stage 1 database scope

Only a minimal `schema_meta` table (tracking schema version) was created
in Stage 1. The full set of tables described in PROJECT_SPEC.md section
30 (chains, tokens, token_observations, holders, wallets,
wallet_transactions, wallet_token_positions, token_scores, alerts) will
be added incrementally as each relevant stage is built, rather than all
at once — this keeps each change small, testable, and easy to review.

---

# Scoring

Target token score:

```text
0–100
```

Initial weighting:

```text
Market / Momentum       20
Liquidity               15
Holder Quality          15
Holder Distribution    10
Smart Money Activity    25
Security / Risk         15
--------------------------------
Total                  100
```

Default alert threshold:

```text
80
```

Not yet implemented — arrives in Stage 10.

---

# Development Notes

This file should be updated throughout development.

Do not delete historical information that is useful for understanding
important decisions.

When a stage is completed, change its checkbox from:

```text
[ ]
```

to:

```text
[x]
```

and update the Current Stage section.

---

# Stage 1 — Independent Verification

A separate verification pass was done after Stage 1 was first delivered,
to double-check everything against `PROJECT_SPEC.md` and `AGENTS.md`
before starting Stage 2.

**Checked:**

* Every expected Stage 1 file/folder exists (28 files checked — all present).
* No `.env` file, database file, or hard-coded secret-like values are
  present anywhere in the code (AGENTS.md rules 5, 8, 9).
* No trading, transaction-signing, wallet-key, or fake market-data code
  exists anywhere (AGENTS.md rules 4, 5, 6).
* `.gitignore` correctly excludes `.env` and local database files.
* Full test suite re-run from a clean state: **18/18 passed.**
* The app was run from a completely fresh copy of the project (simulating
  what happens after you unzip and set it up for the first time):
  installed dependencies, copied `.env.example` to `.env`, ran
  `python run.py --dry-run --once` — started up, logged its
  configuration, created the database, and exited cleanly (exit code 0).
* Confirmed the database file is created correctly with the expected
  `schema_meta` table and version number.
* Tested a malformed setting (`SCAN_INTERVAL_SECONDS=garbage`) — the app
  did not crash; it safely fell back to the default value of 60, as
  designed.
* Tested running with no flags at all (`python run.py`) — completes and
  exits normally rather than hanging.

**Result:** No bugs found. No missing pieces found. Stage 1 matches
`PROJECT_SPEC.md` and `AGENTS.md`.

**One behavior worth understanding (not a bug):** Running the bot with no
flags currently behaves the same as `--once` — it does a single pass and
exits, rather than looping forever. This is expected: the continuous
scanning loop is a Stage 12 feature ("Parallel scanner") that doesn't
exist yet. There's nothing to loop on yet, so this is safe and correct
for where the project is right now.

---

# Stage 2 — Independent Verification

A separate verification pass was done after Stage 2 was uploaded to
GitHub, to confirm the repository actually matches what was delivered,
before starting Stage 3.

**Checked:**

* Read `PROJECT_SPEC.md`, `AGENTS.md`, and `STATUS.md` in full again.
* Confirmed all 36 expected Stage 1 + Stage 2 files/folders are present
  — none missing.
* Confirmed no Stage 1 functionality was lost: re-ran the exact Stage 1
  startup check (`python run.py --dry-run --once`) and it still works
  identically — configuration, logging, and the database all still
  function correctly.
* Re-ran the full automated test suite from a completely clean state:
  **63/63 tests passed.**
* Went a step further than just "tests pass" — manually exercised the
  new Stage 2 code interactively to confirm it's genuinely functional,
  not just present:
  - Printed all 6 chains with their IDs — matched PROJECT_SPEC.md exactly.
  - Confirmed the same token address on two different chains is
    correctly treated as two different tokens.
  - Confirmed the provider registry correctly reports no providers are
    available yet, and gives a clear, friendly error rather than a crash
    when asked for one.
* Re-checked for AGENTS.md violations: no hard-coded secrets, no
  trading/signing code, no fake/invented data anywhere in the new code.
* Confirmed `.gitignore` is still correctly excluding `.env` and local
  database files.

**Found and fixed:** One small issue — a deprecation warning from the
test framework (`pytest-asyncio`) about an unset configuration option.
It wasn't causing any test failures, but left unfixed it could cause
real problems when that testing tool releases a future update. Fixed by
adding one explicit setting to `pytest.ini`. Re-ran the full suite
afterward to confirm: still 63/63 passed, and the warning is gone.

**Result:** Stage 2 is complete, matches `PROJECT_SPEC.md` and
`AGENTS.md`, and no Stage 1 functionality was lost.

---

# Change Log

## 2026-09-17 — Stage 3 Live Verification + Scope Decision

* Project owner ran the real Solana connectivity check on their own
  computer and confirmed `Status: HealthStatus.OK` — Stage 3 is now
  verified against a real, live network connection, not just automated
  tests.
* Project owner decided V1 will focus on Solana only. Stage 4 (EVM
  chains) is on hold and will not be started or built until explicitly
  requested. No code was changed as part of this decision — only this
  status document, to record the decision clearly.

## Stage 3 — Solana Provider (complete)

* Verified official Solana RPC documentation (solana.com/docs/rpc) for
  `getHealth`, `getTokenSupply`, and `getTokenLargestAccounts` before
  writing any code.
* Created `app/chains/solana_address.py` — validates Solana address
  format (base58, 32 bytes) using only the standard library.
* Created `app/chains/solana.py` — the real, read-only `SolanaProvider`:
  connectivity check, token supply lookup, largest-holder-accounts
  lookup. Includes timeouts, retries, exponential backoff, and safe
  handling of rate limits and missing data.
* Added 38 new automated tests (96 total, all passing), including tests
  that specifically prove no trading/signing method or private-key/seed-
  phrase parameter exists anywhere on the provider.
* No paid API was needed — Solana's free public RPC endpoint covers
  everything this stage needed.
* No bugs found during testing. One environment limitation noted: this
  sandbox's own network rules blocked a live call to Solana's public
  endpoint, so full end-to-end connectivity should be confirmed by the
  project owner on their own machine (command provided above).

## Stage 2 — Independent Verification (complete)

* Re-inspected the full repository against PROJECT_SPEC.md and AGENTS.md.
* Confirmed no Stage 1 functionality was lost.
* Re-ran the full test suite from a clean state: 63/63 passed.
* Manually exercised Stage 2 code interactively to confirm real, working
  behavior (not just files existing).
* Found and fixed a pytest-asyncio deprecation warning (not a test
  failure, but a future-proofing fix) by adding one setting to
  `pytest.ini`.

## Stage 2 — Blockchain Abstraction, Common Models, Chain Registry (complete)

* Created `app/models/chain.py` — the official list of 6 supported chains
  and their chain IDs (from PROJECT_SPEC.md section 4).
* Created `app/models/token.py` and `app/models/wallet.py` — enforcing
  the (chain, address) identity rule for tokens and wallets
  (PROJECT_SPEC.md sections 6 and 7).
* Created `app/chains/base.py` — the abstract `BlockchainProvider`
  interface that Solana/EVM providers will implement in Stage 3/4.
* Created `app/chains/registry.py` — the lookup table that will connect
  chain names to real providers once they exist.
* Added 45 new automated tests (63 total). All passing.
* Deliberately did NOT build a shared market-data model yet — deferred to
  Stage 5 when a real provider is chosen, to avoid guessing at fields.
* No bugs found during testing.

## Stage 1 — Independent Verification (complete)

* Re-inspected the full project against PROJECT_SPEC.md and AGENTS.md.
* Re-ran the full test suite from a clean state: 18/18 passed.
* Ran the app from a completely fresh setup to confirm first-time startup
  works.
* Checked for secrets, fake data, and trading/signing code: none found.
* No fixes were needed — Stage 1 was already correct.

## Stage 1 — Project Foundation (complete)

* Created project folder structure.
* Built configuration system reading from environment variables.
* Built SQLite database initialization with schema-version tracking.
* Built structured logging with a secret-redaction safety net.
* Built `run.py` with `--dry-run`, `--demo`, and `--once` flags.
* Wrote and ran 18 automated tests (all passing).
* Found and fixed a false-positive bug in the logging safety filter.
* Wrote README with setup instructions.

## Initial

Project specification created.

Status:

```text
Project not started.
```
