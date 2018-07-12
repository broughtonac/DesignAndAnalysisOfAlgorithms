import random
import matplotlib.pyplot as plt
from collections import deque
import math

def randomPoints(size, xRange, yRange):
    """Generates random (x, y)-coordinates.
    A point's x-coordinate has lower bound 0 and upper bound xRange; its
    y-coordinate has lower bound 0 and upper bound yRange.
    Args:
        size: The number of points to generate.
        xRange: The upper bound for the x-coordinates.
        yRange: The upper bound for the y-coordinates.
    Returns:
        A set of size tuples, each of which is an (x, y)-coordinate.
    """
    # assumptions: no two points are the same and no 3 points fall on a vertical line
    points = {} # keys = coordinates, values = repeat counts
    while len(points) < size:
        x = random.random() * xRange
        y = random.random() * yRange
        if x != y:
            if x not in points:
                points[(x, y)] = 1
            elif points[x] < 3:
                points[(x, y)] += 1
    return list(points.keys())

def plotPoints(points):
    """Plots (x, y)-coordinates in the plane using matplotlib.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    """
    for i in range(len(points)):
        x = points[i][0]
        y = points[i][1]
        plt.plot(x, y, 'bo')
        plt.text(x * 1.01, y * 1.01, i, fontsize = 10)
    plt.show()

def initialize(points):
    """Sorts a list of (x, y)-coordinates by x-coordinate.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    """
    # sorting necessary for balanced divisions
    points.sort(key = lambda p: p[0]) # sort once and for all
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
    leftSub = points[ : m]
    rightSub = points[m : ]
    return (leftSub, rightSub)

def computeVertical(leftSub, rightSub):
    """Finds an x-coordinate that separates the two subproblems.
    Args:
        leftSub: The first element of the tuple in the output of divide. It's a
            list of points sorted by ascending x-coordinate.
        rightSub: The second element of the tuple in the output of divide. It's
            a list of points sorted by ascending x-coordinate.
    Returns:
        An x-coordinate halfway between the right-most point of leftSub and the
        left-most point of rightSub.
    """
    vertical = (leftSub[-1][0] + rightSub[0][0]) / 2
    return vertical

def polarSort(points, reverse = False):
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
        deltaY = p[1] - center[1]
        deltaX = p[0] - center[0]
        angle = math.atan2(deltaY, deltaX)
        if angle < 0:
            angle += 2 * math.pi
        return angle
    points.sort(key = theta, reverse = not reverse)
    return points

def bruteForce(points): # O(n^3) base case
    """Computes the convex hull of points, but naively.
    This algorithm is used as the base case for the O(n lg n) solution.
    Args:
        points: A list of (x, y)-coordinates, each of which is a tuple.
    Returns:
        A subset of points sorted in clockwise order. The subset begins with
        the right-most point if points is a left subhull. It begins with the
        left-most point if it's a right subhull.
    """
    def isTangent(segment): # segment = ((x1, y1), (x2, y2))
        # checks if points are all on one side (left or right) of segment
        def invLineEqn(seg): # x = (y - b) / m
            def x(y):
                m = (seg[1][1] - seg[0][1]) / (seg[1][0] - seg[0][0])
                b = -m * seg[1][0] + seg[1][1]
                return (y - b) / m
            return x # note the closure
        g = invLineEqn(segment) # g(y) = (y - b) / m
        sides = set()
        for p in points:
            if segment[0] != p and segment[1] != p:
                if g(p[1]) > p[0]: # applying the closured function
                    sides.add('left')
                else:
                    sides.add('right')
                if len(sides) == 2:
                    return False
        return True
    def findTangents():
        subhull = []
        addedPoints = set()
        for i in range(len(points) - 1):
            p1 = points[i]
            for p2 in points[i + 1 : ]: # avoids checking segments repetitively
                segment = (p1, p2)
                if isTangent(segment):
                    if segment[0] not in addedPoints:
                        addedPoints.add(segment[0])
                        subhull.append(segment[0])
                    if segment[1] not in addedPoints:
                        addedPoints.add(segment[1])
                        subhull.append(segment[1])
        orderedHull = deque(polarSort(subhull))
        return orderedHull
    return findTangents()

def twoFinger(leftSub, rightSub, vert):
    """Finds the upper and lower tangents for the hull formed by merging left
    and right subhulls.
    Args:
        leftSub: A list of points for the left subhull (clockwise order).
        rightSub: A list of points for the right subhull (clockwise order).
        vert: An x-coordinate specifying the vertical divider.
    Returns:
        A tuple containing the upper and lower tangents, each of which is a
        tuple of 2 points.
    """
    def vertIntercept(p1, p2, vertical): # p1 = (x1, y1) and p2 = (x2, y2)
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
    upperTangent = None
    i = 0
    j = 0
    while True:
        y1 = vertIntercept(leftSub[i], rightSub[(j + 1) % len(rightSub)], vert)
        y2 = vertIntercept(leftSub[i], rightSub[j], vert)
        y3 = vertIntercept(leftSub[(i - 1) % len(leftSub)], rightSub[j], vert)
        if y1 > y2:
            j = (j + 1) % len(rightSub)
        elif y3 > y2:
            i = (i - 1) % len(leftSub)
        else:
            upperTangent = (leftSub[i], rightSub[j])
            break
    lowerTangent = None
    i = 0
    j = 0
    while True:
        y1 = vertIntercept(leftSub[i], rightSub[(j - 1) % len(rightSub)], vert)
        y2 = vertIntercept(leftSub[i], rightSub[j], vert)
        y3 = vertIntercept(leftSub[(i + 1) % len(leftSub)], rightSub[j], vert)
        if y1 < y2:
            j = (j - 1) % len(rightSub)
        elif y3 < y2:
            i = (i + 1) % len(leftSub)
        else:
            lowerTangent = (leftSub[i], rightSub[j])
            break
    return (upperTangent, lowerTangent)
        
def cutAndPaste(leftSub, rightSub, upperTangent, lowerTangent):
    """Merges the left and right subhulls.
    Args:
        leftSub: A list of points for the left subhull (clockwise order).
        rightSub: A list of points for the right subhull (clockwise order).
        upperTangent: A segment to be the new upper tangent of the merged hull.
        lowerTangent: A segment to be the new lower tangent of the merged hull.
    Returns:
        A new hull (with points ordered clockwise) formed by merging leftSub
        and rightSub.
    """
    hull = deque([upperTangent[0]])
    j = rightSub.index(upperTangent[1])
    while rightSub[j] != lowerTangent[1]:
        hull.append(rightSub[j])
        j = (j + 1) % len(rightSub)
    hull.append(rightSub[j])
    i = leftSub.index(lowerTangent[0])
    while leftSub[i] != upperTangent[0]:
        hull.append(leftSub[i])
        i = (i + 1) % len(leftSub)
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
            return bruteForce(points)
        else:
            # DIVIDE
            divided = divide(points)
            leftPoints = divided[0]
            rightPoints = divided[1]
            vertical = computeVertical(leftPoints, rightPoints)
            leftHull = recurse(leftPoints, vertical)
            rightHull = recurse(rightPoints, vertical)
            # CONQUER
            while leftHull[0] != leftPoints[-1]:
                # points[-1] = right most point of subproblem
                leftHull.rotate(1)
            while rightHull[0] != rightPoints[0]:
                # points[0] = left most point of subproblem
                rightHull.rotate(1)
            tangents = twoFinger(leftHull, rightHull, vertical)
            upperTangent = tangents[0]
            lowerTangent = tangents[1]
            return cutAndPaste(leftHull, rightHull, upperTangent, lowerTangent)
    divided = divide(points)
    return recurse(points, computeVertical(divided[0], divided[1]))