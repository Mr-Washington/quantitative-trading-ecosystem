# Exchange rulebook

Baseline rules for the Project 1 simulated exchange. This is the behavior document.

If a rule is in [Rules already decided](#rules-already-decided), an implementation must do that, and a reader should be able to predict the result. If it is in [Not permitted in v1](#not-permitted-in-v1), do not build it in this project. If it is in [Deferred to a later milestone](#deferred-to-a-later-milestone), it is planned and not specified. If it is in [Open questions](#open-questions), the brief does not decide it, and this rulebook does not answer it.

Implementation has not started.

## Predicting one order

A participant submits an order. The gateway validates it and assigns an ID.

If the order is invalid, the exchange rejects it. An invalid order does not change the book. The valid path is different: the matching engine matches the order, then the residual rule is applied, then accounts are updated, then events are published.

The incoming order matches eligible opposite-side orders until it cannot match further. A match may be a full fill, a partial fill, or a trade against more than one counterparty. The execution price is the resting order's price.

A buy limit may trade with a resting sell at or below the buyer's limit. A sell limit may trade with a resting buy at or above the seller's limit. Among eligible resting orders, a better price takes precedence. At the same price, the earlier arrival ranks first. On the bid side a higher price is better. On the ask side a lower price is better.

Unfilled residual quantity of a limit order rests in the book. Unfilled residual quantity of a market order is cancelled and does not rest. After that, the live resting book must not contain prices that could immediately cross. This assumes every book change passes through the matching engine. Two resting orders that could trade with each other must not both remain in the book.

A trade decreases buyer cash and increases buyer holdings. It increases seller cash and decreases seller holdings. That is the pre-fee transfer. Buyer and seller position changes offset. Buyer and seller cash transfers offset before fees.

Cancelling an order removes its remaining quantity from the book.

The gaps in that walkthrough are the [open questions](#open-questions). In particular, the brief does not define market-order price eligibility, and it does not define the buying-power check that would make a submit invalid.

## Rules already decided

### Venue

- One centralized electronic exchange.
- One fictional instrument, stock-style or futures-style. The symbol is not chosen.
- The matching model is a continuous limit order book. There is no auction in the chosen model.
- Local simulation only.

### Prices, quantities, and identity

- Prices are integer ticks, not floating-point dollar values.
- Quantities are integer units.
- An order distinguishes original quantity, executed quantity, and remaining quantity.
- Side and status use enumerations, not free strings. The trading rules use two sides: buy and sell. Status labels are not named.
- The gateway assigns IDs. The brief does not choose an ID format.

### Clock and events

- The simulation is discrete-event. The clock is simulated. It is not wall-clock polling.
- The scheduler is a priority queue ordered by simulated timestamp, then a deterministic sequence number.
- The clock advances to the next event.
- Simulated timestamps stay separate from real processing timestamps.
- The explicit events are `SubmitOrder`, `CancelOrder`, `OrderAccepted`, `OrderRejected`, and `TradeExecuted`.

### Lifecycle

1. Submit.
2. Validate.
3. Reject if invalid.
4. Otherwise match.
5. Apply the residual-order rule.
6. Update accounts.
7. Publish events.

No invalid order changes the book.

### Matching

- An incoming order matches eligible opposite-side orders until it cannot match further.
- Full fills, partial fills, and multiple counterparties are in scope.
- Execution price, in this baseline, is the resting order's price.
- A buy limit may trade with a resting sell at or below the buyer's limit.
- A sell limit may trade with a resting buy at or above the seller's limit.
- A better price takes precedence. A higher bid is better than a lower bid. A lower ask is better than a higher ask.
- At the same price, earlier arrival ranks first.
- The same valid state and the same event sequence always produce the same outcome.

### Residual quantity and the resting book

- Unfilled residual quantity of a limit order rests in the book.
- An unfilled market order is cancelled, not left resting. A partial fill does not change that: the quantity that did not trade is cancelled.
- The live resting book must not contain prices that could immediately cross, assuming every book change passes through the matching engine.
- Cancelling an order removes its remaining quantity.

### Accounts, at the level already fixed

- The ledger tracks cash, holdings, and fills.
- A trade decreases buyer cash and increases buyer holdings, and increases seller cash and decreases seller holdings, before fees.
- Buyer and seller position changes offset.
- Buyer and seller cash transfers offset before fees.
- Open orders affect what a participant may submit next. The formula is not decided.
- Remaining quantity is never negative.
- Fill quantity never exceeds either order's remaining quantity.
- Trade quantities reconcile with executed order quantities.

### Participants and data, at the level already fixed

- Participants are basic scripted traders at first. Building them is not part of this setup step. A completed Project 1 includes a buyer, a seller, and a noise trader.
- Order state has one authoritative source of truth.
- Market data starts with complete snapshots. Incremental updates are added only if needed.
- A later consumer must be able to rebuild the book from a snapshot plus updates.
- Replay of the same inputs reproduces the same final state.
- The same configuration, seed, and initial conditions reproduce the same event history and final state.

## Not permitted in v1

- Live order routing, or a connection to a real venue.
- Replicating Nasdaq, or any production rulebook, in full.
- Many sophisticated order types. Iceberg, stop, peg, discretionary, and similar types are out.
- A language model inside the matching engine. Core execution rules stay ordinary deterministic code.
- Optimizing for speed before correctness.
- Building market-maker or execution agents in Project 1. Scripted traders are a later milestone of this project; autonomous trading agents are the next project.

## Deferred to a later milestone

These are intentionally later. They are not specified, so they have no numbers and no formulas here.

- Fees and rebates. They come only after the accounting path is correct.
- Basic position limits, including inventory limits. Same condition: accounting first.

Until those exist, cash and position changes are the pre-fee transfers above, with no fee and no position-limit check.

Latency is named only as a later study topic. No latency model is deferred into a specified rule, because none was chosen.

## Open questions

Do not answer these in code or in a later edit unless Michael decides them.

- Exact instrument: stock-style or futures-style, and its symbol. `SIM1` is only an example in the illustrative completion command.
- Tick size, and any price bands.
- Whether short sales are allowed.
- Buying-power formula, and how reservations work.
- Self-trade prevention.
- Whether an order can be amended or replaced.
- Minimum and maximum quantity.
- How off-tick or non-positive prices are rejected.
- Participant and account creation rules.
- Whether a repeated cancel of an unknown or already-dead order is a rejection or a no-op.
- Fee schedule and position limits. These are also [deferred](#deferred-to-a-later-milestone). No schedule is stated.
- Opening or closing auctions. The chosen model is continuous only. Auctions stay out of scope unless Michael adds them.

### Gaps the brief leaves open

These are the same kind of hole: decided text does not tell a reader what to do.

- Which labels the status enumeration uses. The brief requires an enumeration and does not name the values.
- Which resting orders are eligible for an incoming market order. Limit eligibility is decided. A market order is only required to match until it cannot match further, and any unfilled remainder is cancelled rather than rested.
- The publication order of `OrderAccepted` and `TradeExecuted`. The valid path publishes events after matching, the residual rule, and the account update. The invalid path rejects. The relative order of the valid-path events is not fixed.
- Identifier format. Orders, trades, events, and participants have IDs. The brief does not choose how those IDs are formed.
