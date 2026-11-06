# Milestones

Plan only. Do not implement the exchange from this document. Each milestone is done only when its completion line is true.

Component placement: [architecture.md](architecture.md). Order lifecycle: [exchange-operations.md](exchange-operations.md). Book structure: [data-models-and-invariants.md](data-models-and-invariants.md#order-book-structure).

1. **Write the exchange rulebook.** A reader can predict the exchange's behavior on a defined order sequence. That document is [exchange-rulebook.md](exchange-rulebook.md). Unanswered items stay listed there as open questions.
2. **Order book only.** Done. No execution. Add, find, cancel, reduce quantity, and report best bid and ask. Structure and APIs: [order book structure](data-models-and-invariants.md#order-book-structure). Code: `Market/src/market/order_book.py`.
3. **Matching engine.** Hand-calculated scenarios match the expected trades and the remaining book. Valid-path match and residual steps: [exchange operations](exchange-operations.md).
4. **Gateway and account ledger.** No invalid order changes the book. Balances and positions reconcile to the trade ledger. Fees and position limits come after accounting is correct. They will be configurable and NYSE-aligned. No values are chosen. Validation and account steps: [exchange operations](exchange-operations.md).
5. **Simulation controller.** The same configuration, seed, and initial conditions reproduce the same event history and final state.
6. **Market data feed and replay.** Start with complete snapshots. Add incremental updates only if needed. A consumer can rebuild the book from a snapshot plus updates.
7. **Scripted participants.** A buyer, a seller, and a noise trader with documented distributions. A simulated fundamental value may drift. The market runs for a defined event count or simulated duration, with statistics and with no accounting or matching violations.
8. **Diagnostics, visualization, and stress tests.** Plots and summaries. Stress covers heavy submission, cancellation bursts, repeated partial fills, price shocks, and low liquidity. Profile before optimizing. A named scenario can be run, inspected, replayed, and explained.
