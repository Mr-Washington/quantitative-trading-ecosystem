"""Price-time fills, limit constraints, and trade quantity reconciliation."""

from __future__ import annotations

import pytest

from market.matching_engine import MatchingEngine, MatchingError
from market.models import Order, OrderId, OrderType, ParticipantId, Side
from market.order_book import OrderBook


def _limit(
    order_id: int,
    side: Side,
    price: int,
    quantity: int,
    *,
    participant_id: int = 1,
    arrival_sequence: int = 0,
) -> Order:
    return Order(
        order_id=OrderId(order_id),
        participant_id=ParticipantId(participant_id),
        side=side,
        order_type=OrderType.LIMIT,
        price=price,
        original_quantity=quantity,
        executed_quantity=0,
        remaining_quantity=quantity,
        arrival_sequence=arrival_sequence,
    )


def _market(
    order_id: int,
    side: Side,
    quantity: int,
    *,
    participant_id: int = 1,
    arrival_sequence: int = 0,
) -> Order:
    return Order(
        order_id=OrderId(order_id),
        participant_id=ParticipantId(participant_id),
        side=side,
        order_type=OrderType.MARKET,
        price=0,
        original_quantity=quantity,
        executed_quantity=0,
        remaining_quantity=quantity,
        arrival_sequence=arrival_sequence,
    )


def _rest(book: OrderBook, *orders: Order) -> None:
    for order in orders:
        book.add(order)


def test_limit_buy_rests_when_it_does_not_cross() -> None:
    book = OrderBook()
    _rest(book, _limit(1, Side.SELL, price=105, quantity=10, participant_id=2, arrival_sequence=1))
    incoming = _limit(2, Side.BUY, price=100, quantity=10, participant_id=1, arrival_sequence=2)

    result = MatchingEngine().match(book, incoming, simulated_timestamp=5)

    assert result.trades == []
    assert result.rested is True
    assert book.best_bid() == 100
    assert book.best_ask() == 105
    assert book.get(OrderId(2)) is incoming


def test_full_fill_at_resting_price() -> None:
    book = OrderBook()
    _rest(book, _limit(1, Side.SELL, price=100, quantity=10, participant_id=2))
    incoming = _limit(2, Side.BUY, price=100, quantity=10, participant_id=1)

    result = MatchingEngine().match(book, incoming, simulated_timestamp=3)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.execution_price == 100
    assert trade.quantity == 10
    assert trade.resting_order_id == OrderId(1)
    assert trade.incoming_order_id == OrderId(2)
    assert trade.simulated_timestamp == 3
    assert result.rested is False
    assert incoming.executed_quantity == 10
    assert incoming.remaining_quantity == 0
    assert len(book) == 0


def test_incoming_partial_fill_rests_residual() -> None:
    # Ask 4 @ 100. Buy 10 @ 105. Trade 4 @ 100. Residual buy 6 rests at 105.
    book = OrderBook()
    _rest(book, _limit(1, Side.SELL, price=100, quantity=4, participant_id=2))
    incoming = _limit(2, Side.BUY, price=105, quantity=10, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.quantity, t.execution_price) for t in result.trades] == [(4, 100)]
    assert result.rested is True
    assert incoming.remaining_quantity == 6
    assert incoming.executed_quantity == 4
    assert incoming.original_quantity == 10
    assert book.best_bid() == 105
    assert book.best_ask() is None
    assert book.depth_at(Side.BUY, 105) == 6


def test_resting_partial_fill_keeps_queue_position() -> None:
    # Ask 10 @ 100. Buy 4 @ 100. Trade 4 @ 100. Ask keeps 6 at the same price.
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=100, quantity=10, participant_id=2, arrival_sequence=1),
        _limit(3, Side.SELL, price=100, quantity=7, participant_id=3, arrival_sequence=2),
    )
    incoming = _limit(2, Side.BUY, price=100, quantity=4, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(1), 4, 100)
    ]
    resting = book.get(OrderId(1))
    assert resting is not None
    assert resting.remaining_quantity == 6
    assert resting.executed_quantity == 4
    assert resting.original_quantity == 10
    assert book.best_resting(Side.SELL) is resting
    assert book.depth_at(Side.SELL, 100) == 13
    assert result.rested is False


def test_better_price_executes_before_worse_price() -> None:
    # Asks 3 @ 98, 3 @ 99, 10 @ 101. Buy 6 @ 100.
    # Eligible: 98 then 99. 101 is above the limit and stays.
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=99, quantity=3, participant_id=2, arrival_sequence=1),
        _limit(2, Side.SELL, price=98, quantity=3, participant_id=3, arrival_sequence=2),
        _limit(3, Side.SELL, price=101, quantity=10, participant_id=4, arrival_sequence=3),
    )
    incoming = _limit(4, Side.BUY, price=100, quantity=6, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(2), 3, 98),
        (OrderId(1), 3, 99),
    ]
    assert incoming.remaining_quantity == 0
    assert result.rested is False
    assert book.best_ask() == 101
    assert book.depth_at(Side.SELL, 101) == 10
    assert sum(t.quantity for t in result.trades) == incoming.executed_quantity


def test_same_price_earlier_order_executes_first() -> None:
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=100, quantity=4, participant_id=2, arrival_sequence=1),
        _limit(2, Side.SELL, price=100, quantity=4, participant_id=3, arrival_sequence=2),
    )
    incoming = _limit(3, Side.BUY, price=100, quantity=6, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity) for t in result.trades] == [
        (OrderId(1), 4),
        (OrderId(2), 2),
    ]
    later = book.get(OrderId(2))
    assert later is not None
    assert later.remaining_quantity == 2
    assert book.get(OrderId(1)) is None


def test_sell_limit_hits_bids_at_or_above_limit() -> None:
    # Bids 5 @ 101 and 5 @ 99. Sell 7 @ 100. Only the 101 bid is eligible.
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.BUY, price=99, quantity=5, participant_id=2, arrival_sequence=1),
        _limit(2, Side.BUY, price=101, quantity=5, participant_id=3, arrival_sequence=2),
    )
    incoming = _limit(3, Side.SELL, price=100, quantity=7, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(2), 5, 101)
    ]
    assert result.rested is True
    assert incoming.remaining_quantity == 2
    assert book.best_bid() == 99
    assert book.best_ask() == 100


def test_self_trade_cancels_resting_order_and_continues() -> None:
    # Own ask 5 @ 100, then another participant's ask 5 @ 100.
    # Incoming buy 5 @ 100 from the same participant cancels the first ask
    # and trades the second at 100.
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=100, quantity=8, participant_id=1, arrival_sequence=1),
        _limit(2, Side.SELL, price=100, quantity=5, participant_id=2, arrival_sequence=2),
    )
    incoming = _limit(3, Side.BUY, price=100, quantity=5, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert result.self_trade_cancels == [OrderId(1)]
    assert book.get(OrderId(1)) is None
    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(2), 5, 100)
    ]
    assert result.rested is False
    assert len(book) == 0


def test_self_trade_then_ineligible_price_rests_residual() -> None:
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=100, quantity=5, participant_id=1, arrival_sequence=1),
        _limit(2, Side.SELL, price=102, quantity=5, participant_id=2, arrival_sequence=2),
    )
    incoming = _limit(3, Side.BUY, price=101, quantity=5, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert result.trades == []
    assert result.self_trade_cancels == [OrderId(1)]
    assert result.rested is True
    assert book.best_bid() == 101
    assert book.best_ask() == 102


def test_fill_quantity_does_not_exceed_either_remaining() -> None:
    book = OrderBook()
    _rest(book, _limit(1, Side.SELL, price=100, quantity=10, participant_id=2))
    incoming = _limit(2, Side.BUY, price=110, quantity=3, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert result.trades[0].quantity == 3
    resting = book.get(OrderId(1))
    assert resting is not None
    assert resting.remaining_quantity == 7
    assert incoming.executed_quantity == 3


def test_same_book_and_order_produce_the_same_trades() -> None:
    def run() -> list[tuple[int, int, int]]:
        book = OrderBook()
        _rest(
            book,
            _limit(1, Side.SELL, price=100, quantity=2, participant_id=2, arrival_sequence=1),
            _limit(2, Side.SELL, price=101, quantity=2, participant_id=3, arrival_sequence=2),
        )
        incoming = _limit(3, Side.BUY, price=101, quantity=3, participant_id=1)
        result = MatchingEngine().match(book, incoming, simulated_timestamp=9)
        return [
            (int(t.trade_id), t.execution_price, t.quantity) for t in result.trades
        ]

    assert run() == run() == [(1, 100, 2), (2, 101, 1)]


def test_market_buy_walks_asks_at_several_prices() -> None:
    # Asks 3 @ 100, 4 @ 101, 10 @ 105. Market buy 6.
    # Trades 3 @ 100 then 3 @ 101. Residual does not rest. 105 remains.
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.SELL, price=100, quantity=3, participant_id=2, arrival_sequence=1),
        _limit(2, Side.SELL, price=101, quantity=4, participant_id=3, arrival_sequence=2),
        _limit(3, Side.SELL, price=105, quantity=10, participant_id=4, arrival_sequence=3),
    )
    incoming = _market(4, Side.BUY, quantity=6, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(1), 3, 100),
        (OrderId(2), 3, 101),
    ]
    assert result.rested is False
    assert OrderId(4) not in book
    assert incoming.executed_quantity == 6
    assert incoming.remaining_quantity == 0
    assert book.best_ask() == 101
    assert book.depth_at(Side.SELL, 101) == 1
    assert book.depth_at(Side.SELL, 105) == 10


def test_market_order_cancels_unfilled_residual() -> None:
    book = OrderBook()
    _rest(book, _limit(1, Side.SELL, price=100, quantity=4, participant_id=2))
    incoming = _market(2, Side.BUY, quantity=10, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.quantity, t.execution_price) for t in result.trades] == [(4, 100)]
    assert result.rested is False
    assert OrderId(2) not in book
    assert incoming.executed_quantity == 4
    assert incoming.remaining_quantity == 6
    assert book.best_bid() is None
    assert book.best_ask() is None


def test_market_sell_walks_bids_in_price_time_order() -> None:
    book = OrderBook()
    _rest(
        book,
        _limit(1, Side.BUY, price=99, quantity=2, participant_id=2, arrival_sequence=1),
        _limit(2, Side.BUY, price=101, quantity=2, participant_id=3, arrival_sequence=2),
        _limit(3, Side.BUY, price=101, quantity=2, participant_id=4, arrival_sequence=3),
    )
    incoming = _market(4, Side.SELL, quantity=5, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert [(t.resting_order_id, t.quantity, t.execution_price) for t in result.trades] == [
        (OrderId(2), 2, 101),
        (OrderId(3), 2, 101),
        (OrderId(1), 1, 99),
    ]
    assert result.rested is False
    assert OrderId(4) not in book
    assert incoming.remaining_quantity == 0
    assert book.depth_at(Side.BUY, 99) == 1


def test_market_order_on_empty_book_does_not_rest() -> None:
    book = OrderBook()
    incoming = _market(1, Side.BUY, quantity=5, participant_id=1)

    result = MatchingEngine().match(book, incoming)

    assert result.trades == []
    assert result.rested is False
    assert len(book) == 0
    assert incoming.remaining_quantity == 5


def test_invalid_incoming_order_does_not_change_the_book() -> None:
    book = OrderBook()
    resting = _limit(1, Side.SELL, price=100, quantity=5, participant_id=2)
    _rest(book, resting)
    incoming = _limit(1, Side.BUY, price=100, quantity=5, participant_id=1)

    with pytest.raises(MatchingError):
        MatchingEngine().match(book, incoming)

    assert book.get(OrderId(1)) is resting
    assert len(book) == 1
