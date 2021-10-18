from enum import Enum


class EventType(Enum):
    """
    Enum class for Event Type
    """
    PREPLAY = 0
    INPLAY = 1


class Status(Enum):
    """
    Enum class for Event Status
    """
    PENDING = 0
    STARTED = 1
    ENDED = 2
    CANCELLED = 3


class Outcome(Enum):
    """
    Enum class for Selection Outcome
    """
    UNSETTLED = 0
    VOID = 1
    LOSE = 2
    WIN = 3
