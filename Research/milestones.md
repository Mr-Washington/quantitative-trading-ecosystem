# Milestones

Plan only. Do not implement the exchange from this document. Each milestone is done only when its completion line is true.

1. **Write the exchange rulebook.** A reader can predict the exchange's behavior on a defined order sequence. That document is [exchange-rulebook.md](exchange-rulebook.md). Unanswered items stay listed there as open questions.
2. **Order book only.** No execution. Add, find, cancel, and report best bid and ask.
3. **Matching engine.** Hand-calculated scenarios match the expected trades and the remaining book.
4. **Gateway and account ledger.** No invalid order changes the book. Balances and positions reconcile to the trade ledger. Fees and position limits come after accounting is correct.
5. **Simulation controller.** The same configuration, seed, and initial conditions reproduce the same event history and final state.
6. **Market data feed and replay.** Start with complete snapshots. Add incremental updates only if needed. A consumer can rebuild the book from a snapshot plus updates.
7. **Scripted participants.** A buyer, a seller, and a noise trader with documented distributions. A simulated fundamental value may drift. The market runs for a defined event count or simulated duration, with statistics and with no accounting or matching violations.
8. **Diagnostics, visualization, and stress tests.** Plots and summaries. Stress covers heavy submission, cancellation bursts, repeated partial fills, price shocks, and low liquidity. Profile before optimizing. A named scenario can be run, inspected, replayed, and explained.
