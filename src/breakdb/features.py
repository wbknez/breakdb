"""
Contains classes and functions to programmatically represent features
extracted from X-ray imaging data.
"""
from dataclasses import dataclass
from enum import IntEnum, unique


@dataclass(frozen=True)
class Bounds:
    """
    Represents a collection of coordinates that enclose a geometric surface.

    Attributes:
        coords (list): A list of coordinates that comprise a bounded surface.
    """

    coords: list


@dataclass(frozen=True)
class Coordinates:
    """
    Represents a pair of coordinates in two-dimensional Cartesian space.

    Attributes:
        x (int): The x-axis coordinate.
        y (int): The y-axis coordinate.
    """

    x: int
    y: int


@unique
class Presentation(IntEnum):
    """
    Represents whether or not a fracture is present in an image.
    """

    Negative = 0
    """
    Represents an image (X-ray) where a fracture is not present.
    """

    Positive = 1
    """
    Represents an image (X-ray) where at least one fracture is present.
    """
