# Exchange rulebook

Baseline rules for the Project 1 simulated exchange. This is the behavior document.

If a rule is in [Rules already decided](#rules-already-decided), an implementation must do that, and a reader should be able to predict the result. If it is in [Not permitted in v1](#not-permitted-in-v1), do not build it in this project. If it is in [Deferred to a later milestone](#deferred-to-a-later-milestone), it is planned and not specified. If it is in [Open questions](#open-questions), it is not decided, and this rulebook does not answer it.

Implementation has not started. Project-level defaults live in [Config](../Config/README.md). The engine does not read them yet.

## Predicting one order

A participant submits an order. The gateway validates it and assigns an ID.

Validation rejects an off-tick price and a non-positive price before the book changes. Off-tick means the price is not a multiple of the configured tick size. An invalid order does not change the book. The valid path is different: the matching engine matches the order, then the residual rule is applied, then accounts are updated, then events are published.

The incoming order matches eligible opposite-side orders until it cannot match further. A match may be a full fill, a partial fill, or a trade against more than one counterparty. The execution price is the resting order's price.

A buy limit may trade with a resting sell at or below the buyer's limit. A sell limit may trade with a resting buy at or above the seller's limit. Among eligible resting orders, a better price takes precedence. At the same price, the earlier arrival ranks first. On the bid side a higher price is better. On the ask side a lower price is better.

If the incoming taking order would trade with that participant's own resting order, self-trade prevention cancels the resting order. The incoming order then continues to match against other liquidity.

Unfilled residual quantity of a limit order rests in the book. Unfilled residual quantity of a market order is cancelled and does not rest. After that, the live resting book must not contain prices that could immediately cross. This assumes every book change passes through the matching engine. Two resting orders that could trade with each other must not both remain in the book.

Decreasing an order's quantity keeps its FIFO queue position. Any other modification is a cancel plus a new order, so that order loses time priority.

Cancelling an order removes its remaining quantity from the book. A repeated cancel of an unknown or already-dead order is a rejection.

A trade decreases buyer cash and increases buyer holdings. It increases seller cash and decreases seller holdings. That is the pre-fee transfer. Buyer and seller position changes offset. Buyer and seller cash transfers offset before fees.

The account is a cash account. Buying power is 1:1 with equity, and there is no margin. Equity's exact composition is not specified, so the numeric buying-power check is not yet predictable. Short sales are not represented.

The instrument is the stock `JPM`. Prices are integer ticks. Tick size defaults to 1 and is configurable. Price bands use limit-up limit-down. The limit-state length, reference window, and band width have defaults. What happens when a limit state ends is not decided, so this walkthrough states no resume action.

The remaining gaps are the [open questions](#open-questions). In particular, which resting orders a market order may hit is not decided.

## Rules already decided

### Venue

- One centralized electronic exchange.
- The instrument is a stock. The symbol is `JPM`.
- The session stays continuous only. There is no opening or closing auction in this version.
- Local simulation only.

### Prices, bands, quantities, and identity

- Prices are integer ticks, not floating-point dollar values.
- Tick size defaults to 1 and is a configurable parameter.
- Off-tick means not a multiple of the configured tick size. Off-tick prices are rejected during order validation, before the book changes.
- Non-positive prices are rejected during order validation, before the book changes.
- Price bands use limit-up limit-down (LULD). These defaults are configurable:
  - Limit state: 15 seconds.
  - Reference price: a 5 minute rolling average.
  - Band: 5%.
- How the 5% band rounds onto integer ticks is not specified.
- What happens when a limit state ends and trading resumes is not decided. No resume action is specified.
- Quantities are integer units.
- Minimum quantity and maximum quantity are configurable parameters. No values are chosen, so they do not yet constrain an order.
- An order distinguishes original quantity, executed quantity, and remaining quantity.
- Side and status use enumerations, not free strings. The trading rules use two sides: buy and sell. Status labels are not named.
- The gateway assigns IDs. The identifier format is not chosen.

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
- Self-trade prevention cancels the existing resting order. The incoming taking order continues to match against other liquidity.
- Decreasing quantity keeps FIFO queue position. Any other modification is a cancel plus a new order, and it loses time priority.
- A repeated cancel of an unknown or already-dead order is a rejection.
- The same valid state and the same event sequence always produce the same outcome.

### Residual quantity and the resting book

- Unfilled residual quantity of a limit order rests in the book.
- An unfilled market order is cancelled, not left resting. A partial fill does not change that: the quantity that did not trade is cancelled.
- The live resting book must not contain prices that could immediately cross, assuming every book change passes through the matching engine.
- Cancelling an order removes its remaining quantity.

### Accounts, at the level already fixed

- The account is a cash account. There is no margin.
- Buying power is 1:1 with equity.
- Short sales are not represented. There are no brokers to borrow shares.
- The ledger tracks cash, holdings, and fills.
- A trade decreases buyer cash and increases buyer holdings, and increases seller cash and decreases seller holdings, before fees.
- Buyer and seller position changes offset.
- Buyer and seller cash transfers offset before fees.
- Open orders affect what a participant may submit next.
- Equity's exact composition is not specified. No mark-to-market formula is stated.
- How reserved funds are calculated is not specified.
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
- Short sales. There are no brokers to borrow shares.

## Deferred to a later milestone

These are intentionally later. No schedule or table is filled in here.

- Participant and account creation rules. Review later.
- Fees and position limits. They are configurable parameters and should closely follow NYSE. No NYSE fee table is copied, and no values are chosen. They still wait until the accounting path is correct. Until then, cash and position changes are the pre-fee transfers above, with no fee and no position-limit check.
- Opening or closing auctions. The session stays continuous only. Auctions stay out of scope until a later review.

Latency is named only as a later study topic. No latency model is deferred into a specified rule, because none was chosen.

## Open questions

Do not answer these in code unless Michael decides them.

- Which labels the status enumeration uses. The rules require an enumeration and do not name the values.
- Which resting orders a market order may hit. Limit eligibility is decided. A market order is only required to match until it cannot match further, and any unfilled remainder is cancelled rather than rested.
- Whether `OrderAccepted` is published before `TradeExecuted`. The valid path publishes events after matching, the residual rule, and the account update. The invalid path rejects. The relative order of the valid-path events is not fixed.
- Identifier format. Orders, trades, events, and participants have IDs. How those IDs are formed is not chosen.
- Equity's exact composition. Buying power is 1:1 with equity, and no mark-to-market formula is stated.
- How reserved funds are calculated.
- How the 5% LULD band rounds onto integer ticks.
- What happens when an LULD limit state ends and trading resumes. The limit-state length is 15 seconds by default. No resume action is specified. Behavior while a limit state is in effect was not stated, so none is implied.
