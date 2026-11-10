"""Price-time matching for limit and market orders.

Accounts and event publication are later milestones. This module updates the
resting book and returns the trades from one incoming order.

Market orders walk opposite liquidity in price-time order, may fill at several
resting prices, and never rest. Unfilled market residual is cancelled.
"""

from __future__ import annotations

from dataclasses import dataclass

from market.models import Order, OrderId, OrderType, Side, Trade, TradeId
from market.order_book import OrderBook


class MatchingError(Exception):
    """The incoming order cannot be matched."""


@dataclass(frozen=True)
class MatchResult:
    trades: list[Trade]
    incoming: Order
    rested: bool
    self_trade_cancels: list[OrderId]


class MatchingEngine:
    """Match one incoming order against the resting book."""

    def __init__(self) -> None:
        self._next_trade_id = 1

    def match(
        self,
        book: OrderBook,
        incoming: Order,
        *,
        simulated_timestamp: int = 0,
    ) -> MatchResult:
        self._validate_incoming(book, incoming)

        trades: list[Trade] = []
        self_trade_cancels: list[OrderId] = []
        opposite = Side.SELL if incoming.side is Side.BUY else Side.BUY

        while incoming.remaining_quantity > 0:
            resting = book.best_resting(opposite)
            if resting is None or not _price_eligible(incoming, resting):
                break
            if resting.participant_id == incoming.participant_id:
                book.cancel(resting.order_id)
                self_trade_cancels.append(resting.order_id)
                continue

            fill_qty = min(incoming.remaining_quantity, resting.remaining_quantity)
            execution_price = resting.price
            book.apply_fill(resting.order_id, fill_qty)
            incoming.remaining_quantity -= fill_qty
            incoming.executed_quantity += fill_qty
            trades.append(
                Trade(
                    trade_id=TradeId(self._next_trade_id),
                    resting_order_id=resting.order_id,
                    incoming_order_id=incoming.order_id,
                    execution_price=execution_price,
                    quantity=fill_qty,
                    simulated_timestamp=simulated_timestamp,
                )
            )
            self._next_trade_id += 1

        rested = False
        if incoming.remaining_quantity > 0 and incoming.order_type is OrderType.LIMIT:
            book.add(incoming)
            rested = True

        _assert_not_crossed(book)
        return MatchResult(
            trades=trades,
            incoming=incoming,
            rested=rested,
            self_trade_cancels=self_trade_cancels,
        )

    def _validate_incoming(self, book: OrderBook, incoming: Order) -> None:
        if incoming.side not in (Side.BUY, Side.SELL):
            raise MatchingError(f"unsupported side: {incoming.side}")
        if incoming.order_type not in (OrderType.LIMIT, OrderType.MARKET):
            raise MatchingError(f"unsupported order type: {incoming.order_type}")
        if incoming.order_id in book:
            raise MatchingError(f"order {incoming.order_id} already rests in the book")
        if incoming.original_quantity <= 0 or incoming.executed_quantity < 0:
            raise MatchingError("quantities must be non-negative with positive original")
        if incoming.remaining_quantity <= 0:
            raise MatchingError("incoming order has no remaining quantity")
        if incoming.remaining_quantity > incoming.original_quantity:
            raise MatchingError("remaining quantity cannot exceed original quantity")
        if (
            incoming.executed_quantity + incoming.remaining_quantity
            != incoming.original_quantity
        ):
            raise MatchingError(
                "original quantity must equal executed plus remaining quantity"
            )
        if incoming.order_type is OrderType.LIMIT and incoming.price <= 0:
            raise MatchingError("limit price must be positive")


def _price_eligible(incoming: Order, resting: Order) -> bool:
    if incoming.order_type is OrderType.MARKET:
        return True
    if incoming.side is Side.BUY:
        return resting.price <= incoming.price
    return resting.price >= incoming.price


def _assert_not_crossed(book: OrderBook) -> None:
    best_bid = book.best_bid()
    best_ask = book.best_ask()
    if best_bid is not None and best_ask is not None and best_bid >= best_ask:
        raise MatchingError(
            f"resting book crossed after match: bid {best_bid} ask {best_ask}"
        )
