import random
import matplotlib.pyplot as plt
from collections import deque
import math


def random_points(size, x_range, y_range):
    """Generates random (x, y)-coordinates.
    A point's x-coordinate has lower bound 0 and upper bound x_range; its
    y-coordinate has lower bound 0 and upper bound y_range.
    Args:
        size: The number of points to generate.
        x_range: The upper bound for the x-coordinates.
        y_range: The upper bound for the y-coordinates.
    Returns:
        A set of size tuples, each of which is an (x, y)-coordinate.
    """
    # assumptions: no two points are the same and no 3 points fall on a
    #     vertical line
    points = {}  # keys = coordinates, values = repeat counts
    while len(points) < size:
        x = random.random() * x_range
        y = random.random() * y_range
        if x != y:
            if x not in points:
                points[(x, y)] = 1
            elif points[x] < 3:
                points[(x, y)] += 1
    return list(points.keys())


def plot_points(points):
    """Plots (x, y)-coordinates in the plane using matplotlib.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    """
    for i in range(len(points)):
        x = points[i][0]
        y = points[i][1]
        plt.plot(x, y, 'bo')
        plt.text(x * 1.01, y * 1.01, i, fontsize=10)
    plt.show()


def initialize(points):
    """Sorts a list of (x, y)-coordinates by x-coordinate.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    """
    # sorting necessary for balanced divisions
    points.sort(key=lambda p: p[0])  # sort once and for all
    return points


def divide(points):
    """Divides a list of points into left and right subproblems.
    Points to the left of the medial x-coordinate make up the left subproblem,
    and they're ordered clockwise. Points on the right of the medial
    x-coordinate  make up the right subproblem, and they're ordered
    anti-clockwise.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    Returns:
        A tuple of the left and right subproblems.
    """
    m = len(points) // 2
    left_sub = points[: m]
    right_sub = points[m:]
    return (left_sub, right_sub)


def compute_vertical(left_sub, right_sub):
    """Finds an x-coordinate that separates the two subproblems.
    Args:
        left_sub: The first element of the tuple in the output of divide. It's a
            list of points sorted by ascending x-coordinate.
        right_sub: The second element of the tuple in the output of divide. It's
            a list of points sorted by ascending x-coordinate.
    Returns:
        An x-coordinate halfway between the right-most point of left_sub and the
        left-most point of right_sub.
    """
    vertical = (left_sub[-1][0] + right_sub[0][0]) / 2
    return vertical


def polar_sort(points, reverse=False):
    """Sorts points by theta.
    Theta is the angle made between x-axis and a vector from the origin to a
    point in the plane.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
        reverse: A Boolean flag where False = clockwise and True =
            anti-clockwise.
    Returns:
        A list of points sorted by theta.
    """
    center = [0, 0]
    for p in points:
        center[0] += p[0]
        center[1] += p[1]
    center[0] /= len(points)
    center[1] /= len(points)

    def theta(p):
        # computes theta for the point p
        delta_y = p[1] - center[1]
        delta_x = p[0] - center[0]
        angle = math.atan2(delta_y, delta_x)
        if angle < 0:
            angle += 2 * math.pi
        return angle

    points.sort(key=theta, reverse=not reverse)
    return points


def brute_force(points):  # O(n^3) base case
    """Computes the convex hull of points, but naively.
    This algorithm is used as the base case for the O(n lg n) solution.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    Returns:
        A subset of points sorted in clockwise order. The subset begins with
        the right-most point if points is a left subhull. It begins with the
        left-most point if it's a right subhull.
    """

    def is_tangent(segment):  # segment = ((x1, y1), (x2, y2))
        # checks if points are all on one side (left or right) of segment
        def inv_line_eqn(seg):  # x = (y - b) / m
            def x(y):
                m = (seg[1][1] - seg[0][1]) / (seg[1][0] - seg[0][0])
                b = -m * seg[1][0] + seg[1][1]
                return (y - b) / m

            return x  # note the closure

        g = inv_line_eqn(segment)  # g(y) = (y - b) / m
        sides = set()
        for p in points:
            if segment[0] != p and segment[1] != p:
                if g(p[1]) > p[0]:  # applying the closure
                    sides.add('left')
                else:
                    sides.add('right')
                if len(sides) == 2:
                    return False
        return True

    def findTangents():
        subhull = []
        added_points = set()
        for i in range(len(points) - 1):
            p1 = points[i]
            for p2 in points[i + 1:]:  # avoids checking segments repetitively
                segment = (p1, p2)
                if is_tangent(segment):
                    if segment[0] not in added_points:
                        added_points.add(segment[0])
                        subhull.append(segment[0])
                    if segment[1] not in added_points:
                        added_points.add(segment[1])
                        subhull.append(segment[1])
        ordered_hull = deque(polar_sort(subhull))
        return ordered_hull

    return findTangents()


def two_finger(left_sub, right_sub, vert):
    """Finds the upper and lower tangents for the hull formed by merging left
    and right subhulls.
    Args:
        left_sub: A list of points for the left subhull (clockwise order).
        right_sub: A list of points for the right subhull (clockwise order).
        vert: An x-coordinate specifying the vertical divider.
    Returns:
        A tuple containing the upper and lower tangents, each of which is a
        tuple of 2 points.
    """

    def vert_intercept(p1, p2, vertical):  # p1 = (x1, y1) and p2 = (x2, y2)
        # Takes p1 from the left subproblem and p2 from the right subproblem.
        # Takes vertical, the x-coordinate specifying the vertical divider.
        # Returns y-coordinate at intersection between line formed by p1 and
        # p2, and vertical.
        x1, y1 = float(p1[0]), float(p1[1])
        x2, y2 = float(p2[0]), float(p2[1])
        x_v = vertical
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        y_v = (m * x_v) + b
        return y_v

    upper_tangent = None
    i = 0
    j = 0
    while True:
        y1 = vert_intercept(left_sub[i], right_sub[(j + 1) % len(right_sub)], vert)
        y2 = vert_intercept(left_sub[i], right_sub[j], vert)
        y3 = vert_intercept(left_sub[(i - 1) % len(left_sub)], right_sub[j], vert)
        if y1 > y2:
            j = (j + 1) % len(right_sub)
        elif y3 > y2:
            i = (i - 1) % len(left_sub)
        else:
            upper_tangent = (left_sub[i], right_sub[j])
            break
    lower_tangent = None
    i = 0
    j = 0
    while True:
        y1 = vert_intercept(left_sub[i], right_sub[(j - 1) % len(right_sub)], vert)
        y2 = vert_intercept(left_sub[i], right_sub[j], vert)
        y3 = vert_intercept(left_sub[(i + 1) % len(left_sub)], right_sub[j], vert)
        if y1 < y2:
            j = (j - 1) % len(right_sub)
        elif y3 < y2:
            i = (i + 1) % len(left_sub)
        else:
            lower_tangent = (left_sub[i], right_sub[j])
            break
    return (upper_tangent, lower_tangent)


def cut_and_paste(left_sub, right_sub, upper_tangent, lower_tangent):
    """Merges the left and right subhulls.
    Args:
        left_sub: A list of points for the left subhull (clockwise order).
        right_sub: A list of points for the right subhull (clockwise order).
        upper_tangent: A segment to be the new upper tangent of the merged hull.
        lower_tangent: A segment to be the new lower tangent of the merged hull.
    Returns:
        A new hull (with points ordered clockwise) formed by merging left_sub
        and right_sub.
    """
    hull = deque([upper_tangent[0]])
    j = right_sub.index(upper_tangent[1])
    while right_sub[j] != lower_tangent[1]:
        hull.append(right_sub[j])
        j = (j + 1) % len(right_sub)
    hull.append(right_sub[j])
    i = left_sub.index(lower_tangent[0])
    while left_sub[i] != upper_tangent[0]:
        hull.append(left_sub[i])
        i = (i + 1) % len(left_sub)
    return hull


def solve(points, n):
    """Computes the convex hull of a list of points via divide and conquer.
    Args:
        points: The list of points for which to compute the complex hull.
        n: The desired size of base case subproblems.
    Returns:
        The convex hull for points as a list of tuples representing
        coordinates.
    """
    points = initialize(points)

    def recurse(points, vertical):
        if len(points) <= n:
            return brute_force(points)
        else:
            # DIVIDE
            divided = divide(points)
            left_points = divided[0]
            right_points = divided[1]
            vertical = compute_vertical(left_points, right_points)
            left_hull = recurse(left_points, vertical)
            right_hull = recurse(right_points, vertical)
            # CONQUER
            while left_hull[0] != left_points[-1]:
                # points[-1] = right most point of subproblem
                left_hull.rotate(1)
            while right_hull[0] != right_points[0]:
                # points[0] = left most point of subproblem
                right_hull.rotate(1)
            tangents = two_finger(left_hull, right_hull, vertical)
            upper_tangent = tangents[0]
            lower_tangent = tangents[1]
            return cut_and_paste(left_hull, right_hull, upper_tangent, lower_tangent)

    divided = divide(points)
    return recurse(points, compute_vertical(divided[0], divided[1]))
