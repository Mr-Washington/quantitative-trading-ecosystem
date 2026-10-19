# Data models and invariants

Starting entities only. Add a field when a feature requires it. Do not add fields in advance.

Identifier format is not chosen. See the [rulebook](exchange-rulebook.md).

## Entities

### Order

- Order ID
- Participant ID
- Side
- Price
- Quantity
- Remaining quantity
- Arrival sequence

Original quantity, executed quantity, and remaining quantity stay distinct. Side is an enumeration, not a free string.

### Trade

- Trade ID
- Resting order ID
- Incoming order ID
- Execution price
- Quantity
- Simulated timestamp

The baseline execution price is the resting order's price.

### OrderBook

- Bid levels
- Ask levels
- Active-order index

### Account

- Cash balance
- Position
- Reserved funds
- Open orders

How reserved funds are calculated is an open question.

### MarketEvent

- Event ID
- Event type
- Simulated timestamp
- Sequence number
- Payload

The explicit event types are `SubmitOrder`, `CancelOrder`, `OrderAccepted`, `OrderRejected`, and `TradeExecuted`.

### MarketSnapshot

- Best bid
- Best ask
- Depth
- Recent trades
- Market timestamp

### SimulationConfig

- Random seed
- Starting price
- Tick size
- Session length
- Participant settings

Tick size, the symbol, and the participant settings are not given values. Configuration files under Market keep these as comments only.

## Invariants future tests must enforce

- No negative remaining quantity.
- Fill quantity never exceeds either order's remaining quantity.
- Limit-order price constraints are respected.
- Better-priced eligible orders execute first.
- Earlier eligible orders execute first at the same price.
- Cancelling an order removes its remaining quantity.
- Trade quantities reconcile with executed order quantities.
- Buyer and seller position changes offset.
- Buyer and seller cash transfers offset before fees.
- Replay reproduces the same final state.

Also required later, still without specified cases:

- Rejection paths
- Empty books
- Repeated cancellation requests
- Multiple orders at one price
- Simultaneous events with identical simulated timestamps

The test modules in `Market/tests/` name the invariant they will protect. They do not contain tests yet.
