"""
Various forms of geometry and geometry related classes used throughout
qfconvert.
"""

from math import sqrt


class Point:
    """
    Simple representation of an (x, y) Cartesian coordinate.

    In QF, the coordinate plane has an origin of (0, 0) at the top-left or
    northwest corner. All coordinates are positive integers. This
    arrangement corresponds with how cells are addressed in DF's user
    interface.
    """
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __cmp__(self, other):
        if self.x == other.x and self.y == other.y:
            return 0
        elif self.x > other.x or self.y > other.y:
            return 1
        else:
            return -1

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, Point):    # multiply two Points' coords together
            return Point(self.x * other.x, self.y * other.y)
        elif isinstance(other, int):    # multiply self coords by other int
            return Point(self.x * other, self.y * other)
        else:
            raise

    def __str__(self):
        return "(%d, %d)" % (self.x, self.y)

    def get_coord_of_axis(self, direction):
        """
        Treating the line traced along direction as an axis,
        return that axis's coordinate from our coords.
        """
        return self.x if direction.compass in ('n', 's') else self.y

    def get_coord_crossing_axis(self, direction):
        """
        Treating the line traced along direction as an axis,
        return the perpendicular axis's coordinate from our coords.
        """
        return self.y if direction.compass in ('n', 's') else self.x

    def distance_to(self, other):
        """Returns straight-line distance between self and other."""
        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

    def midpoint(self, other):
        """
        Returns integer midpoint of straight line connecting self and
        other (rounds down to work well with how DF does it).
        """
        return Point(
            self.x + (other.x - self.x + 1) // 2,
            self.y + (other.y - self.y + 1) // 2
            )

    def is_at_origin(self):
        return self.x == 0 and self.y == 0


DIRECTIONS = {
    'n':  {'index': 0, 'delta': Point(0, -1)},
    'ne': {'index': 1, 'delta': Point(1, -1)},
    'e':  {'index': 2, 'delta': Point(1,  0)},
    'se': {'index': 3, 'delta': Point(1,  1)},
    's':  {'index': 4, 'delta': Point(0,  1)},
    'sw': {'index': 5, 'delta': Point(-1,  1)},
    'w':  {'index': 6, 'delta': Point(-1,  0)},
    'nw': {'index': 7, 'delta': Point(-1, -1)}
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
        Returns offset as a Point.
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
        Returns the direction which is `steps` away from self in in a
        clockwise order around the compass rose.
        """
        return Direction(DIRECTIONS_ORDERED[(self.index() + steps) % 8])

    @staticmethod
    def get_direction(frompos, topos):
        """
        Returns the compass direction point from frompos to topos with
        nw/ne/sw/se taking priority over n/s/e/w
        """
        d = ""
        if frompos.y < topos.y:
            d += "s"
        elif frompos.y > topos.y:
            d += "n"

        if frompos.x < topos.x:
            d += "e"
        elif frompos.x > topos.x:
            d += "w"

        if d == "":
            return None
        else:
            return Direction(d)


class Area:
    """Represents a rectangular area defined on the cartesian grid."""

    def __init__(self, corner, opposite_corner):
        # Get lists of the 2 x coords and 2 y coords
        xs = [corner.x, opposite_corner.x]
        ys = [corner.y, opposite_corner.y]

        # Sort coords so the northernmost and westernmost coordinate is first
        xs.sort()
        ys.sort()

        # Ordered clockwise from NW corner:
        # NW, NE, SE, SW
        self.corners = [
            Point(xs[0], ys[0]),
            Point(xs[1], ys[0]),
            Point(xs[1], ys[1]),
            Point(xs[0], ys[1])
        ]

    def __cmp__(self, other):
        return cmp(self.size(), other.size())

    def __str__(self):
        return '[' + ','.join([str(c) for c in self.corners]) + \
            '] size:' + str(self.size())

    def width(self):
        """Returns width of area, min 1."""
        return self.corners[1].x - self.corners[0].x + 1

    def height(self):
        """Returns height of area, min 1."""
        return self.corners[2].y - self.corners[0].y + 1

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
