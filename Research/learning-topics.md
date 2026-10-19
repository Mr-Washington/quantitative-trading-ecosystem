# Learning topics

Study notes for Project 1. None of this is implemented code.

## Market microstructure

Bid, ask, spread, limit versus market, partial fills, price-time priority, depth, tick size, liquidity, slippage, and market impact.

The baseline rules that fix some of these words are in the [rulebook](exchange-rulebook.md). Tick size is still an open question. Slippage and market impact are concepts to study, not measured behaviors of this exchange yet.

## Order-book structures

Price-indexed sides, a FIFO queue at each price, and an order-ID index for cancellation.

Practical check: several orders at one price, a partial fill, cancel one order, and the remaining priority is preserved.

## Event-driven simulation

Event queue, simulated time versus wall clock, timestamps, sequence numbers, causal order, and seeded random number generators. Latency is a later topic. No latency rule is decided.

Practical check: two traders at specified times, and the replay is identical.

## Accounts

Cash and position ledgers, buyer and seller accounting, reservations and buying power, and realized versus unrealized P&L.

A trade decreases buyer cash and increases buyer holdings. It increases seller cash and decreases seller holdings. That statement is before fees. Fees and rebates are deferred. Inventory and position limits are deferred.

Open orders affect what a participant may submit next. The buying-power formula and the reservation rule are open questions.

## Market data

Best bid and offer, trades, quotes, depth snapshots, incremental updates, event sourcing, and replay. Separate internal state from what a participant observes.

Record accepted orders, rejected orders, cancellations, executions, book changes, and simulation events. Records use stable IDs and simulated timestamps. Simulated timestamps stay separate from real processing timestamps.

The feed starts with complete snapshots. Incremental updates are added only if needed. A consumer must be able to rebuild the book from a snapshot plus updates.

## Reliability

Unit and integration tests, invariants, property-based tests, deterministic fixtures, randomized sequences, profiling, stress tests, and experiment configuration with reproducibility.

The invariants to enforce are listed in [data models and invariants](data-models-and-invariants.md).
