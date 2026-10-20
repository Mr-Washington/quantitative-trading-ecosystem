# Possible improvements

Expansion ideas only. None of these is a Project 1 rule. The decided behavior stays in the [exchange rulebook](exchange-rulebook.md).

- Actions when an LULD limit state ends and trading resumes. The limit-state length is configured. The resume action is not.
- How a 5% band rounds onto integer ticks. Prices are integer ticks, and the rounding rule is still unspecified.
- Participant and account creation rules. Review later.
- Penalties for low order-to-execution ratios, and other NYSE-like participant controls. This is a future extension of the rejection for a repeated cancel of an unknown or already-dead order. No penalty is specified.
- Fee schedule and position limits as configurable parameters aligned with NYSE. Values are not chosen. Do not copy a NYSE fee table into this project ahead of that review.
- Opening or closing auctions, to review later. The session stays continuous only until then.

Already implied by the docs, and still explicitly not in v1:

- Live order routing, or a connection to a real venue.
- Replicating Nasdaq, or any production rulebook, in full.
- Sophisticated order types: iceberg, stop, peg, discretionary, and similar.
- A language model inside the matching engine.
- Optimizing for speed before correctness.
- Market-maker or execution agents. Those belong to the next project, not Project 1.
- A latency model. Latency is a later study topic, and no latency rule is decided.
