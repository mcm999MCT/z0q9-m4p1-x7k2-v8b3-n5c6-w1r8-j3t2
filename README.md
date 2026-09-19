# Crypto Intelligence Bot

A multi-chain cryptocurrency **intelligence and Discord alerting** system.

**This bot never trades, buys, sells, or touches your wallet.** It only reads
public blockchain and market data, scores tokens, and sends alerts to
Discord. See `PROJECT_SPEC.md` and `AGENTS.md` for the full rules this
project follows.

---

## Project status

This project is being built stage by stage. See `STATUS.md` for exactly
what is done and what's next.

**Current stage: Stage 3 — Solana Provider.** The bot can now make
real, read-only connections to the Solana network (checking connectivity,
reading token supply, and reading a token's largest holder accounts).
Nothing trades, signs, or touches a private key. EVM chains
(Ethereum/Base/BNB/Arbitrum/Robinhood) are not connected yet — that's
Stage 4.

---

## Requirements

* Python 3.10 or newer
* pip (comes with Python)

---

## Setup (step by step)

1. **Install the dependencies.** Open a terminal in this folder and run:

   ```bash
   pip install -r requirements.txt
   ```

2. **Create your local settings file.** Copy the example file:

   ```bash
   cp .env.example .env
   ```

   You don't need to fill anything into `.env` yet for Stage 1 — the bot
   will run fine with everything blank. Later stages will tell you exactly
   which values to add and how to get them (for example, RPC URLs and a
   Discord webhook).

   **Never share your `.env` file or commit it to Git.** It's already
   excluded via `.gitignore`.

3. **Run the bot once, safely:**

   ```bash
   python run.py --dry-run --once
   ```

   * `--dry-run` means no real Discord alerts will ever be sent.
   * `--once` means it runs a single check and exits, instead of running
     forever.

   You should see log messages ending in:
   `Crypto Intelligence Bot finished this run cleanly.`

   This also creates a local database file at `data/crypto_bot.db`.

---

## Running the tests

To check that everything is working correctly:

```bash
python -m pytest -v
```

All tests should show `PASSED`.

---

## Command-line options

| Flag         | What it does                                              |
|--------------|------------------------------------------------------------|
| `--dry-run`  | Never sends real Discord alerts, even if configured.        |
| `--demo`     | Uses safe demo/test data where applicable (clearly labeled). |
| `--once`     | Runs a single scan and exits, instead of running continuously. |

---

## Project documents

* `PROJECT_SPEC.md` — the full technical specification for this project.
* `AGENTS.md` — the permanent development rules this project follows.
* `STATUS.md` — current progress, what's done, and what's next.

---

## Project structure (through Stage 3)

```text
crypto-intelligence-bot/
├── app/
│   ├── main.py              # wires everything together
│   ├── config.py            # reads settings from environment variables
│   ├── logging_setup.py     # sets up safe, consistent logging
│   ├── models/
│   │   ├── chain.py          # the 6 supported chains and their IDs
│   │   ├── token.py          # token identity: (chain, token_address)
│   │   └── wallet.py         # wallet identity: (chain, wallet_address)
│   ├── chains/
│   │   ├── base.py            # shared blueprint every chain connection follows
│   │   ├── registry.py        # lookup table connecting chains to real providers
│   │   ├── solana.py          # REAL Solana connection (read-only)
│   │   └── solana_address.py  # Solana address format validation
│   ├── providers/             # (empty — added in Stage 5)
│   ├── analysis/              # (empty — added in later stages)
│   ├── alerts/                 # (empty — added in Stage 11)
│   ├── database/
│   │   ├── db.py             # database connection & schema setup
│   │   └── repository.py     # (empty — filled in as tables are added)
│   └── services/               # (empty — added in later stages)
├── tests/                     # automated tests
├── data/                      # local SQLite database lives here
├── .env.example                # template for your local settings
├── .gitignore
├── requirements.txt
├── pytest.ini                  # test configuration
├── run.py                      # start here
├── PROJECT_SPEC.md
├── AGENTS.md
└── STATUS.md
```
