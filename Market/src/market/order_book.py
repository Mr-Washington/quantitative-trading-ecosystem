"""Bids, asks, and price levels.

The book stores resting limit orders. It does not decide which orders trade.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from market.models import Order, OrderId, OrderType, Side


class OrderBookError(Exception):
    """Base error for order book operations."""


class OrderNotFoundError(OrderBookError):
    """Cancel or mutate of an unknown or already-dead order."""


class InvalidOrderError(OrderBookError):
    """Order cannot be added to the resting book."""


class InvalidQuantityError(OrderBookError):
    """Quantity change is not a pure decrease of remaining quantity."""


@dataclass(frozen=True)
class PriceLevelSnapshot:
    price: int
    quantity: int
    order_count: int


class OrderBook:
    """Price-time resting book for limit orders.

    Authoritative store of resting order state. Market residuals never rest.
    """

    def __init__(self) -> None:
        self._orders_by_id: dict[OrderId, Order] = {}
        self._bids: dict[int, deque[OrderId]] = {}
        self._asks: dict[int, deque[OrderId]] = {}
        self._best_bid: int | None = None
        self._best_ask: int | None = None

    def add(self, order: Order) -> None:
        """Rest a limit order at the tail of its price queue."""
        if order.order_type is not OrderType.LIMIT:
            raise InvalidOrderError("only limit orders may rest in the book")
        if order.order_id in self._orders_by_id:
            raise InvalidOrderError(f"order {order.order_id} already rests in the book")
        if order.price <= 0:
            raise InvalidOrderError("resting limit price must be positive")
        if order.remaining_quantity <= 0:
            raise InvalidOrderError("remaining quantity must be positive to rest")
        if order.remaining_quantity > order.original_quantity:
            raise InvalidOrderError("remaining quantity cannot exceed original quantity")
        if order.executed_quantity < 0 or order.original_quantity <= 0:
            raise InvalidOrderError("quantities must be non-negative with positive original")
        if order.executed_quantity + order.remaining_quantity != order.original_quantity:
            raise InvalidOrderError(
                "original quantity must equal executed plus remaining quantity"
            )

        levels = self._levels_for(order.side)
        queue = levels.setdefault(order.price, deque())
        queue.append(order.order_id)
        self._orders_by_id[order.order_id] = order
        self._update_best_on_add(order.side, order.price)

    def cancel(self, order_id: OrderId) -> Order:
        """Remove remaining quantity. Rejects unknown or already-dead orders."""
        order = self._orders_by_id.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"order {order_id} is unknown or already dead")
        self._remove_from_level(order)
        del self._orders_by_id[order_id]
        return order

    def reduce_quantity(self, order_id: OrderId, new_remaining: int) -> Order:
        """Decrease remaining quantity only. Keeps FIFO queue position.

        Reducing to zero removes the order from the book.
        """
        order = self._orders_by_id.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"order {order_id} is unknown or already dead")
        if new_remaining < 0:
            raise InvalidQuantityError("remaining quantity cannot be negative")
        if new_remaining >= order.remaining_quantity:
            raise InvalidQuantityError(
                "reduce_quantity requires a strictly smaller remaining quantity"
            )

        if new_remaining == 0:
            return self.cancel(order_id)

        # Downsize is not a fill: executed stays put; original shrinks with remaining.
        delta = order.remaining_quantity - new_remaining
        order.remaining_quantity = new_remaining
        order.original_quantity -= delta
        return order

    def apply_fill(self, order_id: OrderId, quantity: int) -> Order:
        """Decrease remaining quantity by a fill. Does not change time priority.

        A fill that consumes the remaining quantity removes the order from the book.
        Original quantity stays unchanged.
        """
        order = self._orders_by_id.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"order {order_id} is unknown or already dead")
        if quantity <= 0:
            raise InvalidQuantityError("fill quantity must be positive")
        if quantity > order.remaining_quantity:
            raise InvalidQuantityError("fill quantity exceeds remaining quantity")

        order.remaining_quantity -= quantity
        order.executed_quantity += quantity
        if order.remaining_quantity == 0:
            self._remove_from_level(order)
            del self._orders_by_id[order_id]
        return order

    def best_resting(self, side: Side) -> Order | None:
        """Earliest order at the best price on one side."""
        price = self.best_bid() if side is Side.BUY else self.best_ask()
        if price is None:
            return None
        queue = self._levels_for(side).get(price)
        if not queue:
            return None
        return self._orders_by_id[queue[0]]

    def get(self, order_id: OrderId) -> Order | None:
        return self._orders_by_id.get(order_id)

    def best_bid(self) -> int | None:
        return self._best_bid

    def best_ask(self) -> int | None:
        return self._best_ask

    def depth_at(self, side: Side, price: int) -> int:
        """Total remaining quantity at one price level."""
        levels = self._levels_for(side)
        queue = levels.get(price)
        if not queue:
            return 0
        return sum(self._orders_by_id[oid].remaining_quantity for oid in queue)

    def level_snapshot(self, side: Side, price: int) -> PriceLevelSnapshot | None:
        levels = self._levels_for(side)
        queue = levels.get(price)
        if not queue:
            return None
        quantity = sum(self._orders_by_id[oid].remaining_quantity for oid in queue)
        return PriceLevelSnapshot(price=price, quantity=quantity, order_count=len(queue))

    def levels(self, side: Side) -> list[PriceLevelSnapshot]:
        """Price levels for one side, best price first."""
        levels = self._levels_for(side)
        prices = sorted(levels.keys(), reverse=(side is Side.BUY))
        snapshots: list[PriceLevelSnapshot] = []
        for price in prices:
            snap = self.level_snapshot(side, price)
            if snap is not None:
                snapshots.append(snap)
        return snapshots

    def __contains__(self, order_id: OrderId) -> bool:
        return order_id in self._orders_by_id

    def __len__(self) -> int:
        return len(self._orders_by_id)

    def _levels_for(self, side: Side) -> dict[int, deque[OrderId]]:
        if side is Side.BUY:
            return self._bids
        if side is Side.SELL:
            return self._asks
        raise InvalidOrderError(f"unsupported side: {side}")

    def _remove_from_level(self, order: Order) -> None:
        levels = self._levels_for(order.side)
        queue = levels.get(order.price)
        if queue is None:
            raise OrderBookError(
                f"order {order.order_id} missing from price level {order.price}"
            )
        try:
            queue.remove(order.order_id)
        except ValueError as exc:
            raise OrderBookError(
                f"order {order.order_id} missing from price level {order.price}"
            ) from exc
        if not queue:
            del levels[order.price]
            self._update_best_on_level_removed(order.side, order.price)

    def _update_best_on_add(self, side: Side, price: int) -> None:
        if side is Side.BUY:
            if self._best_bid is None or price > self._best_bid:
                self._best_bid = price
            return
        if self._best_ask is None or price < self._best_ask:
            self._best_ask = price

    def _update_best_on_level_removed(self, side: Side, removed_price: int) -> None:
        if side is Side.BUY:
            if self._best_bid == removed_price:
                self._best_bid = max(self._bids.keys()) if self._bids else None
            return
        if self._best_ask == removed_price:
            self._best_ask = min(self._asks.keys()) if self._asks else None
