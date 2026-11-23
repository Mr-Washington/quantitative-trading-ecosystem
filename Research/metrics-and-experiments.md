# Metrics and experiments

Future scope. Nothing here is collected yet, and no scenario is runnable.

## Market quality

- Bid-ask spread
- Midprice
- Depth at the best quotes
- Trading volume
- Price volatility

## Exchange performance

- Events per second
- Matching operations per event
- Memory
- Runtime by scenario

Real processing latency is recorded separately from simulated time. That separation is decided. A latency model of the market is not.

## Order outcomes

- Accepted and rejected orders
- Cancellation rate
- Fill rate
- Partial fills
- Order-to-trade ratio

## Scenarios to compare later

- Baseline liquidity
- A sudden fundamental-value shock
- A cancellation burst
- Sparse trading

`Market/configs/baseline.yaml` and `Market/configs/low_liquidity.yaml` reserve names for the baseline and sparse-trading comparisons. They do not store parameter values.

Stress coverage, when diagnostics exist, adds heavy submission, cancellation bursts, repeated partial fills, price shocks, and low liquidity. Profile before optimizing.

## Strategy evaluation across seeds

A single seed fixes wake permute and other RNG draws, so one run is replayable but not enough to rank strategies. Future experiment harnesses should:

- Sweep **many seeds** under the same configuration and scenario
- Report a **distribution of P&amp;L** (and supporting order/market metrics) per strategy
- Keep each individual run fully replayable from its stored seed

Same-timestamp agent wake order is a seeded random permute (milestone 5); multi-seed spreads are how strategy comparison stays honest about that randomness.

## What each experiment stores

- Configuration
- Random seed (per run; the sweep records the seed set)
- Software version
- Event log
- Summary metrics (per run; aggregate distribution across the seed sweep)

A named scenario must be runnable, inspectable, replayable, and explainable once that milestone is reached. Changing a parameter must change behavior in an explainable way.
