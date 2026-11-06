"""Book invariants: no negative remaining quantity; cancel removes remaining quantity."""

from __future__ import annotations

import pytest

from market.models import Order, OrderId, OrderType, ParticipantId, Side
from market.order_book import (
    InvalidOrderError,
    InvalidQuantityError,
    OrderBook,
    OrderNotFoundError,
)


def _limit(
    order_id: int,
    side: Side,
    price: int,
    quantity: int,
    *,
    participant_id: int = 1,
    arrival_sequence: int = 0,
    executed: int = 0,
) -> Order:
    return Order(
        order_id=OrderId(order_id),
        participant_id=ParticipantId(participant_id),
        side=side,
        order_type=OrderType.LIMIT,
        price=price,
        original_quantity=quantity,
        executed_quantity=executed,
        remaining_quantity=quantity - executed,
        arrival_sequence=arrival_sequence,
    )


def test_add_and_best_bid_ask() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=10, arrival_sequence=1))
    book.add(_limit(2, Side.BUY, price=101, quantity=5, arrival_sequence=2))
    book.add(_limit(3, Side.SELL, price=105, quantity=7, arrival_sequence=3))
    book.add(_limit(4, Side.SELL, price=104, quantity=3, arrival_sequence=4))

    assert book.best_bid() == 101
    assert book.best_ask() == 104
    assert len(book) == 4


def test_fifo_order_at_same_price_via_level_queue() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=10, arrival_sequence=1))
    book.add(_limit(2, Side.BUY, price=100, quantity=20, arrival_sequence=2))

    snap = book.level_snapshot(Side.BUY, 100)
    assert snap is not None
    assert snap.order_count == 2
    assert snap.quantity == 30
    assert book.depth_at(Side.BUY, 100) == 30

    # First cancel removes the earlier arrival; later order stays at the level.
    book.cancel(OrderId(1))
    assert book.get(OrderId(1)) is None
    assert book.get(OrderId(2)) is not None
    assert book.depth_at(Side.BUY, 100) == 20
    assert book.best_bid() == 100


def test_cancel_removes_remaining_quantity() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.SELL, price=50, quantity=15))
    assert book.depth_at(Side.SELL, 50) == 15

    cancelled = book.cancel(OrderId(1))
    assert cancelled.remaining_quantity == 15
    assert OrderId(1) not in book
    assert book.depth_at(Side.SELL, 50) == 0
    assert book.best_ask() is None
    assert book.level_snapshot(Side.SELL, 50) is None


def test_repeated_cancel_of_dead_order_is_rejected() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=10, quantity=1))
    book.cancel(OrderId(1))

    with pytest.raises(OrderNotFoundError):
        book.cancel(OrderId(1))

    with pytest.raises(OrderNotFoundError):
        book.cancel(OrderId(99))


def test_reduce_quantity_keeps_fifo_position() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=10, arrival_sequence=1))
    book.add(_limit(2, Side.BUY, price=100, quantity=10, arrival_sequence=2))

    book.reduce_quantity(OrderId(1), 4)
    order = book.get(OrderId(1))
    assert order is not None
    assert order.remaining_quantity == 4
    assert order.original_quantity == 4
    assert order.executed_quantity == 0
    assert book.depth_at(Side.BUY, 100) == 14

    # Order 1 is still ahead of order 2 at the same price.
    book.cancel(OrderId(1))
    assert book.get(OrderId(2)) is not None
    assert book.depth_at(Side.BUY, 100) == 10


def test_reduce_quantity_rejects_increase_and_negative() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=10))

    with pytest.raises(InvalidQuantityError):
        book.reduce_quantity(OrderId(1), 10)
    with pytest.raises(InvalidQuantityError):
        book.reduce_quantity(OrderId(1), 11)
    with pytest.raises(InvalidQuantityError):
        book.reduce_quantity(OrderId(1), -1)


def test_reduce_to_zero_removes_order() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=10))
    book.reduce_quantity(OrderId(1), 0)
    assert OrderId(1) not in book
    assert book.best_bid() is None


def test_remaining_quantity_never_negative() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=5))
    with pytest.raises(InvalidQuantityError):
        book.reduce_quantity(OrderId(1), -1)
    order = book.get(OrderId(1))
    assert order is not None
    assert order.remaining_quantity >= 0


def test_market_order_cannot_rest() -> None:
    book = OrderBook()
    market = Order(
        order_id=OrderId(1),
        participant_id=ParticipantId(1),
        side=Side.BUY,
        order_type=OrderType.MARKET,
        price=100,
        original_quantity=5,
        executed_quantity=0,
        remaining_quantity=5,
        arrival_sequence=1,
    )
    with pytest.raises(InvalidOrderError):
        book.add(market)
    assert len(book) == 0


def test_duplicate_order_id_rejected() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=100, quantity=1))
    with pytest.raises(InvalidOrderError):
        book.add(_limit(1, Side.SELL, price=110, quantity=1))


def test_empty_book_bests_are_none() -> None:
    book = OrderBook()
    assert book.best_bid() is None
    assert book.best_ask() is None
    assert book.levels(Side.BUY) == []
    assert book.levels(Side.SELL) == []


def test_best_updates_when_best_level_depletes() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=101, quantity=1))
    book.add(_limit(2, Side.BUY, price=100, quantity=1))
    assert book.best_bid() == 101
    book.cancel(OrderId(1))
    assert book.best_bid() == 100


def test_levels_sorted_best_first() -> None:
    book = OrderBook()
    book.add(_limit(1, Side.BUY, price=98, quantity=1))
    book.add(_limit(2, Side.BUY, price=100, quantity=2))
    book.add(_limit(3, Side.SELL, price=105, quantity=3))
    book.add(_limit(4, Side.SELL, price=103, quantity=4))

    bids = book.levels(Side.BUY)
    asks = book.levels(Side.SELL)
    assert [level.price for level in bids] == [100, 98]
    assert [level.price for level in asks] == [103, 105]
