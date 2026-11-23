# Future milestones (after local Project 1)

Expansion planning only. This document does **not** replace the eight local milestones in [milestones.md](milestones.md). Those remain the build order for the correctness-first Python exchange.

**Correctness reference:** the current local discrete-event engine (simulated clock, deterministic matching, event log replay) stays the source of truth for market behavior **before any AWS cutover**. An AWS deployment is successful only when it can reproduce, or be proven equivalent to, local runs under the [exchange rulebook](exchange-rulebook.md) and the invariants in [data-models-and-invariants.md](data-models-and-invariants.md). Target shape: [aws-architecture.md](aws-architecture.md).

## Local milestones (unchanged)

Continue and finish [milestones.md](milestones.md) 1–8 first: rulebook, order book, matching, gateway/accounts, simulation controller, market data/replay, scripted participants, diagnostics/stress. Do not skip local replay and invariant tests to chase cloud infrastructure.

## Project 1b — Local hardening and multi-agent controller

Bridge between “exchange works locally” and “ready to think about cloud.”

1. **Invariant and replay gate.** Named scenarios replay to identical final state. Accounting, book, and matching invariants hold under stress from milestone 8.
2. **Richer simulation controller.** Many participants with different strategies in one local run (interfaces and configs first; strategies may still be scripted). Controller sends **wake** commands on the simulated clock; agents submit/cancel through the gateway and do not own the clock. Same-timestamp wakes use the seeded random permute and submit-before-next-wake rules from milestone 5.
3. **Clear process boundaries.** Document which components could become separate processes later (gateway, matcher, ledger persist, market-data publisher, agents) without changing rules. Still local; no AWS required.
4. **Latency measurement hooks.** Record wall-clock processing latency separately from simulated time (study topic only; no latency model in the rulebook yet).

Done when: a multi-strategy local scenario runs, replays, and explains itself; boundaries for a later service split are written down.

## Project 2 — Serious market participants (still local by default)

Aligns with the ecosystem intent: after the exchange is explainable, build participants whose behavior can be investigated.

1. **Market-maker and/or execution-style agents** with documented policies (not LLM-in-the-matcher).
2. **Experiment harness** for comparing strategies under shared seeds and configs ([metrics-and-experiments.md](metrics-and-experiments.md)). Run a **spread of seeds** and report a **distribution of P&amp;L** (and related metrics), not a single-run score, so same-timestamp wake permute and other seeded randomness do not masquerade as model quality.
3. **Optional AI in the participant layer only** — research workflows and strategy search, never inside matching.

Done when: agent P&amp;L distributions and behavior can be separated from exchange bugs using the same replay tools as Project 1.

AWS is still optional here. Prefer keeping agents on the local engine until Project 1b gates pass.

## Project 3 — AWS packaging without cutover

Introduce cloud packaging **alongside** the local reference, not instead of it.

1. **Containerize** gateway, matcher, controller, and a sample agent using the same Python logic as local.
2. **Stand up the default stack in a non-production account** per [aws-architecture.md](aws-architecture.md): NLB + gateway, single active `JPM` matcher, stream + archive + Redis, Aurora for durable ledger/snapshots.
3. **Parity tests.** Feed the same event sequences into local and AWS-hosted matcher paths; require matching trades, residual books, and account deltas (within documented async-persist windows if ledger flush is asynchronous).
4. **Observability baseline.** CloudWatch + OpenTelemetry; X-Ray only with heavy sampling.

Done when: a containerized `JPM` primary can pass parity against local replay for a fixed scenario set. Local remains the authority if they disagree.

## Project 4 — Multi-agent AWS simulation at scale

1. **Agent fleet** on ECS/EKS (or equivalent), heterogeneous strategies, message bus from controller to agents and back through the gateway.
2. **Operational reliability:** matcher active/passive failover for the `JPM` shard, durable event archive to S3, snapshot restore drills.
3. **Load and latency budgets** for the hot path; profile before widening the architecture.

Done when: many agents can run a long scenario on AWS with no invariant violations and with documented latency distributions — and local replay still validates the economic outcome.

## Project 5 — Multi-instrument sharding (only when needed)

1. **Partition by symbol:** one active matcher/book per instrument.
2. **Routing** at the edge by instrument to the correct shard.
3. **Cross-instrument concerns** (portfolio margin, multi-symbol agents) stay outside a single book’s matching loop.

Do not start this phase to “scale” a single `JPM` book. Scale that book with better process affinity and measurement, not multiple writers.

## Explicit non-sequence

- Do not replace milestones 1–8 with cloud work.
- Do not put the hot matcher on Lambda.
- Do not claim multiple active matchers for one continuous price-time book.
- Do not implement Market stubs or deploy AWS as part of writing this plan.
