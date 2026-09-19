# Crypto Intelligence Bot — Project Specification

## 1. Project Overview

Build a working V1 multi-chain cryptocurrency intelligence and Discord alert bot.

The purpose of this project is to continuously scan multiple blockchain ecosystems, identify potentially interesting tokens, analyze their market conditions, liquidity, holders, wallet activity, and security risks, calculate a deterministic score, and send high-quality opportunities to Discord.

This is an intelligence and alerting system.

It is NOT an automatic trading bot.

The first version must prioritize:

* Reliability
* Data quality
* Low cost
* Transparent calculations
* Low false positives
* Easy debugging
* Modular architecture
* Security
* Clear Discord alerts

The project should be designed so that more advanced features can be added later without rebuilding the entire application.

---

# 2. V1 Goals

The bot should:

1. Discover new, recent, trending, high-volume, or fast-growing tokens.
2. Scan multiple blockchains.
3. Collect market data.
4. Track token growth.
5. Analyze liquidity.
6. Analyze holder distribution.
7. Identify creator/deployer wallets where possible.
8. Identify suspicious wallet behavior.
9. Track wallet performance over time.
10. Build a local database of potentially good/smart wallets.
11. Detect when historically successful wallets buy or sell tokens.
12. Calculate a deterministic token score from 0–100.
13. Send tokens above a configurable score threshold to Discord.
14. Store historical observations so the bot becomes more intelligent over time.
15. Continue scanning other chains if one chain fails.
16. Operate cheaply using free or low-cost infrastructure where possible.

---

# 3. Explicit V1 Non-Goals

Do NOT implement these features in V1:

* Automatic trading
* Buying tokens
* Selling tokens
* Wallet signing
* Private keys
* Seed phrases
* Transaction execution
* Claude/LLM analysis inside the bot
* X/Twitter integration
* Nansen integration
* Telegram integration
* Complex web dashboard
* Paid smart-money databases
* Copy trading

These may be considered for V2 or later.

---

# 4. Supported Blockchains

V1 must support the following chains:

### Solana

Chain:

```text
Solana
```

Use a dedicated Solana provider.

---

### Ethereum

Chain ID:

```text
1
```

---

### Base

Chain ID:

```text
8453
```

---

### BNB Smart Chain

Chain ID:

```text
56
```

---

### Arbitrum One

Chain ID:

```text
42161
```

---

### Robinhood Chain

Chain ID:

```text
4663
```

Robinhood Chain is EVM-compatible.

Therefore Ethereum, Base, BNB Smart Chain, Arbitrum, and Robinhood should share a reusable EVM provider architecture.

Do NOT create completely separate implementations for every EVM chain unless technically necessary.

---

# 5. Architecture

Use a modular architecture.

The core application should contain a common blockchain interface.

Conceptually:

```text
BlockchainProvider
        |
        +------------------+
        |                  |
SolanaProvider       EVMProvider
                           |
            +--------------+--------------+
            |       |       |       |      |
        Ethereum  Base    BNB   Arbitrum Robinhood
```

The rest of the application should not need to know the low-level details of each blockchain.

The application should work with normalized models.

---

# 6. Chain Identity

Never identify a token only by its address.

The unique token identity must be:

```text
(chain, token_address)
```

For example:

```text
(Solana, ABC...)
(Base, 0xABC...)
(Robinhood, 0xABC...)
```

The same EVM address may exist on multiple chains.

Treat those as different token identities unless there is verified evidence that they represent the same asset.

---

# 7. Wallet Identity

Wallet identity should also be chain-aware.

Use:

```text
(chain, wallet_address)
```

For EVM chains, the same address can technically exist on multiple chains.

Do not automatically assume that activity on different EVM chains represents one identical wallet entity for scoring purposes.

Cross-chain wallet intelligence may be added later.

---

# 8. Project Structure

Create the project approximately as follows:

```text
crypto-intelligence-bot/
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── token.py
│   │   ├── wallet.py
│   │   ├── market.py
│   │   └── chain.py
│   │
│   ├── chains/
│   │   ├── base.py
│   │   ├── solana.py
│   │   ├── evm.py
│   │   └── registry.py
│   │
│   ├── providers/
│   │   ├── market_data.py
│   │   └── rpc.py
│   │
│   ├── analysis/
│   │   ├── market.py
│   │   ├── holders.py
│   │   ├── wallets.py
│   │   ├── security.py
│   │   └── scoring.py
│   │
│   ├── alerts/
│   │   └── discord.py
│   │
│   ├── database/
│   │   ├── db.py
│   │   └── repository.py
│   │
│   └── services/
│       ├── scanner.py
│       ├── wallet_tracker.py
│       └── token_analyzer.py
│
├── tests/
│
├── data/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── run.py
│
├── PROJECT_SPEC.md
├── AGENTS.md
└── STATUS.md
```

The exact structure may be adjusted if there is a strong technical reason.

Do not add unnecessary complexity.

---

# 9. Configuration

Use environment variables.

Never hard-code API keys or secrets.

Expected configuration:

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

Not every value must be required if a feature can operate without it.

The application must clearly report missing configuration.

---

# 10. Market Data

Create a market-data abstraction.

The normalized market model should contain, where available:

```text
chain
token_address
symbol
name
price
market_cap
liquidity
volume_5m
volume_1h
volume_6h
volume_24h
price_change_5m
price_change_1h
price_change_6h
price_change_24h
pair
dex
first_seen
last_updated
```

The exact fields may vary by provider.

If data is unavailable:

```text
N/A
```

or:

```text
UNKNOWN
```

must be used.

Never invent values.

---

# 11. Token Discovery

The discovery system should search for:

* New tokens
* Recently launched tokens
* High-volume tokens
* Fast-growing tokens
* Trending tokens
* Tokens with unusual activity
* Tokens gaining liquidity
* Tokens with interesting wallet activity

Discovery should be configurable.

Do not assume that every newly created token is interesting.

---

# 12. Cheap Filtering

The bot should use a staged analysis pipeline.

Preferred architecture:

```text
DISCOVERY
   ↓
CHEAP MARKET FILTER
   ↓
LIQUIDITY FILTER
   ↓
HOLDER ANALYSIS
   ↓
WALLET ANALYSIS
   ↓
SECURITY ANALYSIS
   ↓
TOKEN SCORE
   ↓
DISCORD ALERT
```

Cheap filters should happen before expensive analysis.

This reduces:

* API usage
* RPC requests
* CPU usage
* database load
* unnecessary processing

---

# 13. Market Analysis

Analyze:

* Market capitalization
* Price
* Price changes
* Volume
* Volume acceleration
* Liquidity
* Liquidity changes
* Market-cap/liquidity relationship
* Token age
* Momentum

The system should distinguish between:

```text
Observed
Calculated
Estimated
Unavailable
```

---

# 14. Growth Tracking

The bot must store token observations over time.

For each token, record observations such as:

```text
timestamp
price
market_cap
liquidity
volume
```

Calculate growth where possible:

```text
Growth since first observed
5 minute growth
1 hour growth
6 hour growth
24 hour growth
```

Important:

"Growth since beginning" should mean:

```text
growth since the bot first observed the token
```

unless reliable launch/initial-price data is available.

Do not pretend that the bot knows the true launch price if it does not.

---

# 15. Liquidity Analysis

Analyze:

* Absolute liquidity
* Liquidity / market cap
* Liquidity growth
* Liquidity decline
* Abnormally low liquidity
* Abnormal volume relative to liquidity
* Potential liquidity-risk situations

Configurable thresholds should include at minimum:

```text
MIN_LIQUIDITY_USD
MAX_MARKETCAP_LIQUIDITY_RATIO
```

Avoid hard-coding assumptions when possible.

---

# 16. Solana Holder Analysis

Use appropriate Solana RPC methods where available.

Potential methods include:

```text
getTokenLargestAccounts
getTokenSupply
getTokenAccountsByOwner
```

Analyze:

* Top 10 concentration
* Top 20 concentration
* Largest holder percentage
* Meaningful holder count
* Holder growth
* Distribution changes

IMPORTANT:

The largest token accounts are NOT automatically human wallets.

They can represent:

* Liquidity pools
* Programs
* Burn addresses
* Lockers
* Infrastructure
* Other contracts/programs

The system must attempt to label known infrastructure.

---

# 17. EVM Holder Analysis

For EVM tokens, analyze where possible:

* Total supply
* Top holders
* Holder balances
* Holder concentration
* Holder count
* Transfer activity
* Creator/deployer holdings
* Contract ownership

Do not assume raw Transfer logs alone are an efficient universal solution for obtaining all historical holders.

Use an indexed provider/API where necessary.

The architecture should allow different data providers later.

---

# 18. Holder Labels

Wallet/entity labels should support:

```text
UNKNOWN
LIKELY_CREATOR
KNOWN_PROGRAM
KNOWN_LP
KNOWN_BURN
KNOWN_LOCKER
INFRASTRUCTURE
NORMAL_WALLET
```

Labels should be based on evidence.

Do not claim an address is a human wallet without sufficient evidence.

---

# 19. Creator / Deployer Analysis

Where possible identify:

* Token creator
* Contract deployer
* Initial distribution
* Creator holdings
* Creator transfers
* Creator selling
* Creator accumulation

Flag suspicious behavior such as:

* Large creator allocation
* Creator dumping
* Repeated transfers to fresh wallets
* Suspicious distribution patterns

If the creator cannot be identified:

```text
UNKNOWN
```

---

# 20. Security Analysis

The bot must NOT describe a token as completely safe.

Security status should use:

```text
LOWER RISK
MEDIUM
HIGH
UNKNOWN
```

---

## Solana Security Checks

Where available analyze:

* Mint authority
* Freeze authority
* Holder concentration
* Creator behavior
* Liquidity
* Distribution
* Suspicious wallet activity

---

## EVM Security Checks

Where available analyze:

* Contract verification
* Owner privileges
* Mint capability
* Pause capability
* Blacklist capability
* Trading restrictions
* Transfer restrictions
* Ownership status
* Proxy/upgradeability
* Creator holdings
* Suspicious transfer behavior

The security system should report the specific reasons for risk.

---

# 21. Smart Wallet Database

The bot should gradually build its own wallet intelligence database.

Do not depend on a paid smart-money database for V1.

Wallet records should include approximately:

```text
wallet_address
chain
first_seen
last_seen
trades_count
winning_trades
losing_trades
realized_pnl_estimate
win_rate
average_return
median_return
tokens_traded
wallet_score
classification
```

Classifications:

```text
UNKNOWN
WATCHLIST
GOOD
SMART_MONEY
```

A wallet must NOT become "SMART_MONEY" based on one lucky trade.

Require sufficient historical evidence.

---

# 22. Wallet Performance

Track wallet activity over time.

Potential metrics:

### Win Rate

```text
winning trades / total closed trades
```

### Profitability

Estimate realized profitability when reliable data is available.

### Consistency

Measure whether profitable performance occurs across multiple trades.

### Trade Count

A wallet with many successful trades is more meaningful than one successful trade.

### Recency

Recent activity should matter.

Do not allow old performance to dominate forever.

---

# 23. Example Wallet Score

Initial wallet score:

```text
Win Rate             25%
Profitability        30%
Consistency          15%
Trade Count          10%
Average Return       10%
Recent Activity      10%
```

Total:

```text
100%
```

These weights must be configurable.

The implementation may improve the formula if there is a strong reason.

---

# 24. Token Wallet Intelligence

For each token determine where possible:

```text
Good wallets holding
Good wallets recently buying
Good wallets recently selling
Smart wallets buying
Smart wallets selling
Smart-wallet concentration
```

A wallet that simply holds a token should not automatically be treated as actively bullish.

Buying activity should be distinguished from holding activity.

---

# 25. Token Scoring

Every analyzed token should receive a deterministic score from:

```text
0–100
```

Initial weighting:

```text
Market / Momentum       20 points
Liquidity               15 points
Holder Quality          15 points
Holder Distribution    10 points
Smart Money Activity    25 points
Security / Risk         15 points
----------------------------------
TOTAL                  100 points
```

The score must be explainable.

Every score should be possible to break down into its components.

Example:

```text
Market/Momentum: 17/20
Liquidity: 13/15
Holder Quality: 11/15
Distribution: 8/10
Smart Money: 22/25
Security: 12/15

TOTAL: 83/100
```

---

# 26. Missing Data

Never create fake points because data is missing.

If a metric is unavailable:

* mark it unavailable
* normalize scoring appropriately
* or reduce confidence

The system must distinguish:

```text
BAD
UNKNOWN
GOOD
```

UNKNOWN must not automatically mean BAD.

---

# 27. Discord Alerts

Send alerts using a Discord webhook.

Only alert when:

```text
token_score >= ALERT_SCORE_THRESHOLD
```

Default:

```text
80
```

The threshold must be configurable.

---

# 28. Discord Alert Format

Example:

```text
🚨 CRYPTO INTELLIGENCE ALERT

🟣 CHAIN: SOLANA

$ABC — Example Token

🎯 SCORE: 86/100

💰 MARKET
Market Cap: $420K
Liquidity: $87K
Price: $0.0042

📈 GROWTH
Since First Seen: +318%
1h: +42%
6h: +187%
24h: +245%

💧 LIQUIDITY
Liquidity/MC: 20.7%
Liquidity Trend: Increasing

👥 HOLDERS
Top 10: 21.4%
Top 20: 32.1%
Good Wallets Holding: 7
Good Wallets Recently Buying: 4

🧠 SMART MONEY
Smart Wallets Buying: 3
Smart Wallets Selling: 0

🛡️ SECURITY
Risk: LOWER RISK

WHY IT SCORED HIGH
• Strong recent momentum
• Healthy liquidity relative to market cap
• Several historically successful wallets buying
• Reasonable holder distribution

RISKS
• Token is very young
• Limited historical data

DATA CONFIDENCE
Medium

Token: [address]
```

Do not use fake links.

Only include links that are actually available.

---

# 29. Alert Deduplication

Do not repeatedly send identical alerts.

Store sent alerts in the database.

Possible re-alert conditions:

```text
Score increases by >= 10
```

or:

```text
Configured cooldown expires
```

Both should be configurable.

---

# 30. Database

Use SQLite for V1.

Database should contain approximately:

```text
chains
tokens
token_observations
holders
wallets
wallet_transactions
wallet_token_positions
token_scores
alerts
```

Use appropriate indexes.

Important indexes should include composite identities such as:

```text
(chain, token_address)
(chain, wallet_address)
```

---

# 31. Parallel Scanning

The bot should scan chains concurrently where practical.

Conceptually:

```text
Solana       ─┐
Ethereum     ─┤
Base         ─┤
BNB          ─┤
Arbitrum     ─┤──> Analysis Pipeline
Robinhood    ─┘
```

Use asynchronous programming where appropriate.

One chain failure must NOT stop the entire scanner.

Example:

```text
Solana       OK
Ethereum     OK
Base         ERROR
BNB          OK
Arbitrum     OK
Robinhood    OK
```

The scanner should continue operating.

---

# 32. Rate Limiting and Reliability

Implement:

* Request timeouts
* Retries
* Exponential backoff
* Concurrency limits
* Caching
* Deduplication
* Logging
* Graceful failure
* Incremental updates

Do not hammer public RPC endpoints.

Respect provider rate limits.

---

# 33. Cost Control

V1 should be designed to run cheaply.

Prioritize:

* Free RPC endpoints
* Free or low-cost APIs
* SQLite
* Local processing
* Discord webhook
* Async requests
* Caching
* Cheap filters
* Incremental database updates

Do not add paid APIs unless necessary.

---

# 34. Security Rules

The bot is read-only.

NEVER:

* Ask for private keys
* Ask for seed phrases
* Store private keys
* Store seed phrases
* Sign transactions
* Execute transactions
* Buy tokens
* Sell tokens
* Connect to a wallet for trading

The bot should only analyze publicly available blockchain and market information.

---

# 35. Operating Modes

Support:

```bash
python run.py
```

Normal mode.

```bash
python run.py --dry-run
```

Run without sending real Discord alerts.

```bash
python run.py --demo
```

Run using safe demo/test data where appropriate.

```bash
python run.py --once
```

Perform one scan and exit.

Do not create fake production data.

Demo data must be clearly identified as demo data.

---

# 36. Logging

Use structured, useful logs.

Example:

```text
[INFO] Starting scanner
[INFO] Scanning Solana
[INFO] Scanning Base
[INFO] Scanning Robinhood
[INFO] Found 42 candidate tokens
[INFO] Analyzing token ABC
[INFO] Token ABC score: 83
[INFO] Discord alert sent
```

Errors should include enough information to debug the problem.

Do not log secrets.

---

# 37. Testing

Create automated tests for:

* Chain configuration
* Token identity
* Wallet identity
* Solana address handling
* EVM address handling
* Liquidity calculations
* Growth calculations
* Holder calculations
* Wallet scoring
* Token scoring
* Alert threshold
* Alert deduplication
* Cross-chain wallet handling
* Configuration validation

Tests should run after meaningful changes.

---

# 38. Development Stages

Build the application incrementally.

### Stage 1

Project structure

Configuration

SQLite database

Basic logging

---

### Stage 2

Blockchain abstraction

Chain registry

Common models

---

### Stage 3

Solana provider

Basic Solana token analysis

---

### Stage 4

EVM provider

Ethereum

Base

BNB

Arbitrum

Robinhood

---

### Stage 5

Market-data integration

---

### Stage 6

Token discovery

---

### Stage 7

Holder analysis

---

### Stage 8

Wallet tracking

---

### Stage 9

Security analysis

---

### Stage 10

Scoring engine

---

### Stage 11

Discord alerts

---

### Stage 12

Parallel scanner

---

### Stage 13

Testing and reliability improvements

---

### Stage 14

README and setup documentation

---

# 39. Development Process

Do NOT build the entire application in one giant step.

For every stage:

1. Read the specification.
2. Inspect the current repository.
3. Explain the plan.
4. Implement the stage.
5. Run tests.
6. Fix errors.
7. Verify the implementation.
8. Update STATUS.md.
9. Explain what was completed.
10. Explain what I need to do, if anything.
11. Wait for approval before starting the next major stage.

I am not a programmer.

Explain technical concepts in simple language.

Do not assume that I know Python, Git, APIs, RPCs, databases, or blockchain development.

---

# 40. External APIs

Never invent:

* API endpoints
* RPC methods
* Request formats
* Response fields
* Authentication requirements

When using an external service, verify the official documentation.

If an API changes or is unavailable:

1. Report the problem.
2. Do not fabricate a workaround.
3. Implement a clean abstraction so another provider can be added later.

---

# 41. Data Quality

Data quality is more important than having many features.

Every important piece of information should ideally be traceable to:

```text
Observed data
Calculated data
Estimated data
Unavailable data
```

Do not present estimates as facts.

Do not claim that a wallet is smart money without sufficient historical evidence.

Do not claim that a token is safe.

Do not claim that a token will increase in price.

The bot is an intelligence system, not a prediction guarantee.

---

# 42. V2 Roadmap

Possible future features:

* Claude API analysis
* X/Twitter sentiment
* Nansen
* Birdeye
* More sophisticated smart-money tracking
* Telegram alerts
* Web dashboard
* More blockchains
* Better contract security analysis
* Wallet clustering
* Cross-chain wallet intelligence
* Historical backtesting
* Advanced anomaly detection
* User-specific alert profiles

These should NOT be implemented unless explicitly requested.

---

# 43. Final Product Principle

The goal is NOT:

> Find every token that might go 100x.

The goal is:

> Build a reliable multi-chain intelligence system that filters thousands of tokens down to a small number of objectively interesting opportunities and clearly explains the evidence and risks behind each alert.

Prioritize:

```text
DATA QUALITY
    >
RELIABILITY
    >
TRANSPARENCY
    >
LOW FALSE POSITIVES
    >
LOW COST
    >
FEATURE COUNT
```

Build a system that can evolve over time.
