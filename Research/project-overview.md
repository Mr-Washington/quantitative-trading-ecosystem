# Project overview

Owner: Michael Washington.

The Quantitative Trading Ecosystem is a long-running place to learn market microstructure, quantitative finance, and agentic development. It will change over time. Project 1 does not build that whole ecosystem. It builds one simulated financial exchange that later projects can share.

## Guiding principle

First build a market whose behavior can be explained. Then build agents whose behavior can be investigated. Then use AI to discover which strategies and workflows work.

AI belongs in participants and in development workflows. It does not belong in the exchange's core execution rules. The matching engine must be ordinary deterministic code: the same valid state and the same event sequence always produce the same outcome.

## What Project 1 is

One stock, symbol `JPM`, on one centralized electronic exchange, with a continuous limit order book. The simulation is small and internally consistent. It will not replicate every feature of a real exchange. Rules must be documented and testable.

Priority is correctness, observability, and extensibility. Speed and realism come after those.

This setup step is documentation and a folder skeleton. Participants are not part of this step. The exchange is not implemented.

## What a completed Project 1 must show

- How an order travels from a participant to the exchange and becomes a trade.
- An order book and matching engine that preserve the market rules.
- Simulated time, competing events, and deterministic execution.
- Cash, positions, open orders, and executions with no accounting discrepancies.
- Market data that downstream trading agents can consume.
- Reconstruction of a simulation from its event log.
- Correctness tests and performance measurement under different workloads.

Done means all of the following:

- The simulation runs without order-book, matching, or accounting invariant violations.
- The run can be replayed.
- The market's evolution can be explained.
- Changing a parameter changes behavior in an explainable way.

After that, do not add many sophisticated order types. The next project is a serious market participant.

## Illustrative completion command

The following is an example of a finished run from the original brief. It is not a performance target, and it does not override the [rulebook](exchange-rulebook.md). The instrument is the stock `JPM`.

- Scenario: baseline_market
- Instrument: SIM1
- Seed: 42
- Duration: 10,000 events
- Participants: 1 scripted buyer, 1 scripted seller, 10 noise traders
- Outputs: order book and trade history, participant account ledger, market data snapshots, market quality metrics, validation and replay report

`SIM1` appears only in that example. It is not the symbol.
