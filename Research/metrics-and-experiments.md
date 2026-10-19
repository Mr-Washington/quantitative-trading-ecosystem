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

## What each experiment stores

- Configuration
- Random seed
- Software version
- Event log
- Summary metrics

A named scenario must be runnable, inspectable, replayable, and explainable once that milestone is reached. Changing a parameter must change behavior in an explainable way.
