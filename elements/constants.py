from enum import Enum


Tuple2Int = tuple[int, int]
Tuple4Int = tuple[int, int, int, int]


class _Alignment(Enum):
    """
    CLass for representing text and image alignment on a widget
    """
    TOP = -1
    BOTTOM = 1
    CENTER = 0
    LEFT = -1
    RIGHT = 1


TOP_ALIGN = _Alignment.TOP
BOTTOM_ALIGN = _Alignment.BOTTOM
CENTER_ALIGN = _Alignment.CENTER
LEFT_ALIGN = _Alignment.LEFT
RIGHT_ALIGN = _Alignment.RIGHT


class _Value(Enum):
    """
    Class for representing arguments value for object initialization or function call
    """
    NULL = "null"
    DEFAULT = "default"
    AUTO = "auto"
    ZERO = "zero"


NULL_VALUE = _Value.NULL  # Has no value
DEFAULT_VALUE = _Value.DEFAULT  # Use default value of the object
AUTO_VALUE = _Value.AUTO  # Value calculated based on other attributes
ZERO_VALUE = _Value.ZERO  # Value is 0
