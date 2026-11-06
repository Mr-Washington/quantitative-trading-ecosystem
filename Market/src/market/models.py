"""Orders and related types for the exchange.

Identifier format is not chosen in the rulebook. IDs are opaque ints for now.
Status enumeration labels are not named yet, so this module does not define them.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

OrderId = NewType("OrderId", int)
ParticipantId = NewType("ParticipantId", int)


class Side(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Limit residuals may rest. Market residuals do not."""

    LIMIT = "limit"
    MARKET = "market"


@dataclass
class Order:
    """Resting or incoming order fields required by the book.

    Original, executed, and remaining quantity stay distinct.
    """

    order_id: OrderId
    participant_id: ParticipantId
    side: Side
    order_type: OrderType
    price: int
    original_quantity: int
    executed_quantity: int
    remaining_quantity: int
    arrival_sequence: int
