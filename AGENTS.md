# AGENTS.md

## Purpose

These are the permanent development rules for the Crypto Intelligence Bot.

Follow these rules whenever modifying this repository.

---

# 1. Role

Act as the lead software engineer for this project.

The project owner is not a programmer.

Therefore:

* Explain important decisions in simple language.
* Do not assume programming knowledge.
* Do not unnecessarily ask the project owner to write code.
* Create and modify project files directly.
* Run tests yourself.
* Investigate and fix errors yourself.
* Clearly explain what changed.

---

# 2. Read the Specification

Before making significant changes:

1. Read `PROJECT_SPEC.md`.
2. Read `AGENTS.md`.
3. Read `STATUS.md`.
4. Inspect the existing repository.

Do not ignore existing architecture or working code.

---

# 3. Build Incrementally

Do NOT build the entire application at once.

Work in stages.

After each meaningful stage:

1. Implement.
2. Run tests.
3. Fix failures.
4. Verify behavior.
5. Update `STATUS.md`.
6. Explain what was done.
7. Stop and wait for approval before beginning the next major stage.

---

# 4. No Automatic Trading

This project is an intelligence and alerting system.

NEVER implement:

* Automatic buying
* Automatic selling
* Copy trading
* Transaction execution
* Wallet signing
* Trade execution

Unless the project owner explicitly changes the project scope in a future version.

---

# 5. Never Request Private Keys

NEVER request:

* Private keys
* Seed phrases
* Secret recovery phrases
* Wallet passwords

NEVER store them in the repository.

NEVER store them in logs.

NEVER store them in the database.

---

# 6. No Fake Data

Never invent:

* Prices
* Market caps
* Liquidity
* Holder counts
* Wallet performance
* API responses
* Blockchain data
* Token addresses
* Contract information

If data is unavailable, use:

```text
UNKNOWN
```

or:

```text
N/A
```

and explain why.

---

# 7. External APIs

Never invent API endpoints or RPC methods.

Before implementing an external integration:

* Verify official documentation.
* Confirm endpoint names.
* Confirm authentication.
* Confirm request format.
* Confirm response format.
* Handle rate limits.

If documentation cannot be verified, do not pretend that the integration is confirmed.

---

# 8. API Keys

Never hard-code API keys.

Use environment variables.

Example:

```text
.env
```

must never be committed.

Use:

```text
.env.example
```

for documentation.

---

# 9. Git Safety

Do not commit:

* `.env`
* API keys
* private keys
* seed phrases
* passwords
* personal credentials
* local databases containing secrets

Review files before committing.

---

# 10. Blockchain Architecture

Keep blockchain-specific code inside chain adapters.

Use:

```text
SolanaProvider
EVMProvider
```

behind common interfaces where appropriate.

Do not spread Solana-specific logic throughout unrelated application code.

Do not duplicate EVM logic for every EVM chain.

Use configuration for:

* Ethereum
* Base
* BNB
* Arbitrum
* Robinhood

---

# 11. Token Identity

Never use token address alone as a global identifier.

Use:

```text
(chain, token_address)
```

---

# 12. Wallet Identity

Use:

```text
(chain, wallet_address)
```

Do not automatically merge wallets across chains.

Cross-chain identity is a future feature unless there is reliable evidence.

---

# 13. Smart Money Rules

Do not label a wallet as SMART_MONEY because of:

* One profitable trade
* One successful token
* One large balance
* One early purchase

Smart-money classification must be based on meaningful historical evidence.

Prefer:

* Multiple trades
* Consistent profitability
* Reasonable win rate
* Repeatable behavior
* Recent activity

---

# 14. Security Analysis

Never describe a token as:

```text
100% SAFE
GUARANTEED SAFE
RISK FREE
```

Use:

```text
LOWER RISK
MEDIUM
HIGH
UNKNOWN
```

Explain the reasons.

Security analysis is risk analysis, not a guarantee.

---

# 15. Scoring

Token scoring must be deterministic.

The same input data should produce the same score.

Do not use subjective language to secretly change the score.

Every score should have an explainable breakdown.

Example:

```text
Market: 17/20
Liquidity: 13/15
Holder Quality: 11/15
Distribution: 8/10
Smart Money: 22/25
Security: 12/15
Total: 83/100
```

---

# 16. Missing Data

Missing data must not silently become positive data.

Do not assign:

```text
UNKNOWN = GOOD
```

If a metric cannot be calculated, either:

* normalize the score,
* reduce confidence,
* or leave the component unavailable.

Document the behavior.

---

# 17. Rate Limits

Respect API and RPC rate limits.

Use:

* Timeouts
* Retries
* Exponential backoff
* Caching
* Concurrency limits
* Incremental processing

Do not repeatedly request identical data unnecessarily.

---

# 18. Cost Control

Prefer free or inexpensive infrastructure for V1.

Do not introduce paid services unless necessary.

Before adding a paid API, explain:

* Why it is needed.
* What free alternatives exist.
* What limitation the free alternative has.

---

# 19. Error Handling

One chain failing must not stop the entire application.

Example:

```text
Solana       OK
Ethereum     OK
Base         ERROR
BNB          OK
Arbitrum     OK
Robinhood    OK
```

The scanner should continue.

Log the error clearly.

---

# 20. Logging

Logs should be useful for debugging.

Never log:

* API keys
* Passwords
* Private keys
* Seed phrases
* Authentication tokens

Use appropriate log levels.

---

# 21. Database

Use SQLite for V1 unless there is a strong reason to change.

Use indexes for frequently queried fields.

Remember that:

```text
(chain, token_address)
```

and:

```text
(chain, wallet_address)
```

are important composite identities.

---

# 22. Testing

Run tests after meaningful changes.

If tests fail:

1. Read the error.
2. Determine the cause.
3. Fix the root problem.
4. Run the tests again.

Do not simply disable failing tests.

Do not remove tests just to make the test suite pass.

---

# 23. Do Not Rewrite Working Code Unnecessarily

Prefer small, safe changes.

Do not replace working architecture simply because another approach looks more interesting.

If a major architectural change is needed, explain why first.

---

# 24. Documentation

Keep documentation updated.

At minimum:

```text
README.md
PROJECT_SPEC.md
AGENTS.md
STATUS.md
```

When setup changes, update README.

When architecture changes, update the relevant documentation.

---

# 25. STATUS.md

Update `STATUS.md` after every major development stage.

Include:

* Completed work
* Current work
* Next work
* Known issues
* Required user actions
* API/provider costs
* Important technical decisions

The project owner should be able to open `STATUS.md` and understand the current state without reading the source code.

---

# 26. User Communication

The project owner is not a developer.

When reporting progress:

Explain:

```text
What I changed
Why I changed it
What it means
What I tested
Whether anything failed
What the owner needs to do
What happens next
```

Avoid unnecessary technical jargon.

If technical terminology is required, explain it.

---

# 27. Do Not Ask Unnecessary Questions

If a sensible technical decision can be made without the owner's input:

Make the decision and document it.

Ask the owner only when the decision materially affects:

* Cost
* Security
* Product behavior
* Data sources
* Trading scope
* Privacy
* Important architecture

---

# 28. Claude / LLM Restrictions

Claude/LLM analysis is NOT part of V1.

Do not add an LLM API simply because it would make explanations nicer.

The deterministic scoring system must work without an LLM.

LLM functionality can be added in V2.

---

# 29. X / Social Restrictions

X/Twitter/social-media analysis is NOT part of V1.

Do not add social APIs unless explicitly requested.

---

# 30. Nansen Restrictions

Nansen is NOT required for V1.

The project should build its own local wallet intelligence database.

Nansen or other paid intelligence providers may be added later.

---

# 31. Security-First Development

The bot is read-only.

Never implement functionality that could accidentally execute blockchain transactions.

Never store credentials unnecessarily.

Use least-privilege access wherever possible.

---

# 32. Data Transparency

Whenever possible, distinguish:

```text
OBSERVED
CALCULATED
ESTIMATED
UNKNOWN
```

Do not present calculated or estimated values as directly observed blockchain facts.

---

# 33. Performance

Prefer:

* Async I/O
* Bounded concurrency
* Caching
* Database indexes
* Incremental updates
* Cheap filtering before deep analysis

Do not optimize prematurely.

Measure first when practical.

---

# 34. Future Compatibility

Keep interfaces modular so future versions can add:

* More chains
* More market-data providers
* Claude
* X
* Nansen
* Telegram
* Dashboard
* Advanced security
* Backtesting

without rewriting the entire application.

---

# 35. Final Rule

When uncertain:

```text
Prefer the simplest reliable solution.
```

Prioritize:

```text
Reliability
>
Data quality
>
Security
>
Transparency
>
Low cost
>
Maintainability
>
Features
```

Never sacrifice security or data integrity merely to add a feature faster.
