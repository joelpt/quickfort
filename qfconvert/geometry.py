"""
Various forms of geometry and geometry related classes used throughout
qfconvert.
"""

from math import sqrt


def compare_points((x1, y1), (x2, y2)):
    """
    Returns 0 if the two points are equal.
    Returns 1 if x1>x2 or y1>y2.
    Returns -1 otherwise.
    """
    if x1 == x2 and y1 == y2:
        return 0
    elif x1 > x2 or y1 > y2:
        return 1
    else:
        return -1


def add_points((x1, y1), (x2, y2)):
    """
    Adds (translates) the points returning (x1+x2, y1+y2).
    """
    return (x1 + x2, y1 + y2)


def multiply_points((x1, y1), (x2, y2)):
    """
    Multiplies (scales) the points returning (x1*x2, y1*y2).
    """
    return (x1 * x2, y1 * y2)


def scale_point((x, y), m):
    """
    Scales (multiplies) the given point by magnitude m.
    """
    return (x * m, y * m)


def get_coord_along_axis((x, y), direction):
    """
    Treating the line passing through (x, y) in the provided
    direction as an axis, return that axis's coordinate.
    """
    return x if direction.compass in ('n', 's') else y


def get_coord_crossing_axis((x, y), direction):
    """
    Treating the line passing through (x, y) in the provided
    direction as an axis, return the perpendicular axis's coordinate.
    """
    return y if direction.compass in ('n', 's') else x


def distance((x1, y1), (x2, y2)):
    """Returns straight-line distance between provided points."""
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def midpoint((x1, y1), (x2, y2)):
    """
    Returns integer midpoint of straight line connecting provided
    points (rounds down to work well with how DF does it).
    """
    return (
        x1 + (x2 - x1 + 1) // 2,
        y1 + (y2 - y1 + 1) // 2
        )


DIRECTIONS = {
    'n':  {'index': 0, 'delta': (0, -1)},
    'ne': {'index': 1, 'delta': (1, -1)},
    'e':  {'index': 2, 'delta': (1,  0)},
    'se': {'index': 3, 'delta': (1,  1)},
    's':  {'index': 4, 'delta': (0,  1)},
    'sw': {'index': 5, 'delta': (-1,  1)},
    'w':  {'index': 6, 'delta': (-1,  0)},
    'nw': {'index': 7, 'delta': (-1, -1)}
    }

DIRECTIONS_ORDERED = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']


class Direction:
    """Direction represents one of the 8 compass directions: n, ne, e, .."""

    def __init__(self, compass_dir):
        self.compass = compass_dir

    def __str__(self):
        return "{compass:%s}" % self.compass

    def index(self):
        """
        Return index of given direction from DIRECTIONS.
        Kinda hacky but Python dicts are unordered :(
        """
        return DIRECTIONS[self.compass]['index']

    def axis(self):
        """
        Returns 'x' for e|w directions and 'y' for n|s directions.
        Returns 'xy' for other directions.
        """
        if self.compass in ('n', 's'):
            return 'y'
        if self.compass in ('e', 'w'):
            return 'x'
        return 'xy'

    def delta(self):
        """
        Get the x/y coordinate offset needed to move one unit on the
        cartesian grid towards self.compass.
        Returns offset as a point.
        """
        return DIRECTIONS[self.compass]['delta']

    def opposite(self):
        """Returns the direction opposite this one (e -> w; ne -> sw)"""
        return self.clockwise(4)

    def right_turn(self):
        """Returns the direction 90 degrees right of this one (n -> e)"""
        return self.clockwise(2)

    def left_turn(self):
        """Returns the direction 90 degrees left of this one (n -> w)"""
        return self.clockwise(6)

    def clockwise(self, steps):
        """
        Returns the direction which is `steps` away from self in a
        clockwise order around the compass rose.
        """
        return Direction(DIRECTIONS_ORDERED[(self.index() + steps) % 8])

    @staticmethod
    def get_direction((x1, y1), (x2, y2)):
        """
        Returns the compass direction point from (x1, y1) to (x2, y2) with
        nw/ne/sw/se taking priority over n/s/e/w
        """
        d = ""
        if y1 < y2:
            d += "s"
        elif y1 > y2:
            d += "n"

        if x1 < x2:
            d += "e"
        elif x1 > x2:
            d += "w"

        if d == "":
            return None
        else:
            return Direction(d)


class Area:
    """Represents a rectangular area defined on the cartesian grid."""

    def __init__(self, (x, y), (x_opposite, y_opposite)):
        # Get lists of the 2 x coords and 2 y coords

        xs = [x, x_opposite]
        ys = [y, y_opposite]

        # Sort coords so the northernmost and westernmost coordinate is first
        xs.sort()
        ys.sort()

        # Ordered clockwise from NW corner:
        # NW, NE, SE, SW
        self.corners = [
            (xs[0], ys[0]),
            (xs[1], ys[0]),
            (xs[1], ys[1]),
            (xs[0], ys[1])
        ]

    def __cmp__(self, other):
        return cmp(self.size(), other.size())

    def __str__(self):
        return '[' + ','.join([str(c) for c in self.corners]) + \
            '] size:' + str(self.size())

    def width(self):
        """Returns width of area, min 1."""
        return self.corners[1][0] - self.corners[0][0] + 1

    def height(self):
        """Returns height of area, min 1."""
        return self.corners[2][1] - self.corners[0][1] + 1

    def size(self):
        """Returns size (geometric area) of area, min 1."""
        return self.width() * self.height()

    def diagonal_length(self):
        """Returns corner-to-opposite-corner distance of area."""
        return sqrt(self.width() ** 2 + self.height() ** 2)

    def opposite_corner(self, corner):
        """Returns the opposite corner of area given param `corner`."""
        for i in xrange(0, 4):
            if corner == self.corners[i]:
                return self.corners[(i + 2) % 4]
        return None
