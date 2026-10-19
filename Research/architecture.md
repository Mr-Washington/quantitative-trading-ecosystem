# Architecture

Exchange logic stays independent from simulation orchestration and visualization. Order state has one authoritative source of truth.

The matching engine is deterministic code, not a language model. Given the same valid state and the same event sequence, it produces the same outcome.

## Components

| Component | Responsibility |
| --- | --- |
| Market participants | Generate orders and react to market data |
| Exchange gateway and validation | Validate orders, assign IDs, reject invalid requests |
| Matching engine | Price-time priority and executions |
| Order book | Resting bids and asks |
| Account ledger | Cash, holdings, and fills |
| Market data and event log | Quotes, depth updates, trades, replay, and metrics |
| Simulation controller | Schedule events, control simulated time, and coordinate participants |

## Technology boundaries that are already chosen

- Python, with typed interfaces and automated tests.
- Persistence is structured event logs and experiment configurations.
- The execution environment is a local simulation. There is no live order routing.
- The clock is a discrete-event simulated clock, not wall-clock polling.

How those pieces are built is the milestone plan, not this skeleton. Module files under [Market](../Market/README.md) name a future responsibility and contain no behavior.
