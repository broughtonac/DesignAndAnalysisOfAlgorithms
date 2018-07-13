import numpy as np
import math

def randomMatrix(n):
    """Generates a random n by n matrix.
    Formed from numpy array objects.
    Args:
        n: The number of rows/columns.
    Returns:
        A numpy array consisting of n numpy arrays, each n elements long.
    """
    return np.random.random((n, n))

def fill(matrix):
    """If necessary, increases matrix size and fills with 0's.
    If the number of rows/columns is not a member of the base 2 geometric
    progression, then increase the number of rows/columns to the next member of
    the progression and fill those positions with 0's. 0's are filled towards
    the bottom right.
    Args:
        matrix: A numpy array of numpy arrays.
    Returns:
        The original matrix if the size doesn't need to be increased. A larger
        matrix filled with zeros if the size does need to be increased.
    """
    n = len(matrix)
    if math.log(n, 2) - math.floor(math.log(n, 2)) != 0:
        k = math.floor(math.log(n, 2)) + 1
        newN = 2 ** k
        padding = newN - n
        matrix = np.pad(matrix, [(0, padding), (0, padding)], 'constant')
    return matrix

def partition(matrix):
    """Divides matrix into 4 submatrices, represented as a tiled matrix.
    Args:
        matrix: a numpy array of numpy arrays.
    Returns:
        A numpy array of 4 submatrices.
    """
    n = len(matrix)
    newN = int(2 ** (math.log(n, 2) - 1))
    upperLeft = matrix[ : newN, : newN]
    upperRight = matrix[ : newN, newN : ]
    lowerLeft = matrix[newN : , : newN]
    lowerRight = matrix[newN : , newN : ]
    tiledMatrix = np.array([
            [upperLeft, upperRight],
            [lowerLeft, lowerRight]
        ])
    return tiledMatrix

def strassenMultiplyGeo(a, b):
    """Apply Strassen algorithm to two square matrices.
    Assumes number of rows/columns for a and b is a member of the base 2
    geometric progression.
    Args:
        a: The matrix on the left of a * b.
        b: The matrix on the right of a * b.
    Returns:
        The matrix product of a and b.
    """
    if len(a) <= 8:
        return np.dot(a, b)
    a = partition(a)
    b = partition(b)
    m1 = strassenMultiplyGeo(a[0, 0] + a[1, 1], b[0, 0] + b[1, 1])
    m2 = strassenMultiplyGeo(a[1, 0] + a[1, 1], b[0, 0])
    m3 = strassenMultiplyGeo(a[0, 0], b[0, 1] - b[1, 1])
    m4 = strassenMultiplyGeo(a[1, 1], b[1, 0] - b[0, 0])
    m5 = strassenMultiplyGeo(a[0, 0] + a[0, 1], b[1, 1])
    m6 = strassenMultiplyGeo(a[1, 0] - a[0, 0], b[0, 0] + b[0, 1])
    m7 = strassenMultiplyGeo(a[0, 1] - a[1, 1], b[1, 0] + b[1, 1])
    upperLeft = m1 + m4 - m5 + m7
    upperRight = m3 + m5
    lowerLeft = m2 + m4
    lowerRight = m1 - m2 + m3 + m6    
    upper = np.concatenate((upperLeft, upperRight), axis = 1)
    lower = np.concatenate((lowerLeft, lowerRight), axis = 1)
    return np.concatenate((upper, lower), axis = 0)

def strassenMultiply(a, b):
    """Apply Strassen algorithm to two square matrices.
    Runs fill on a and b to ensure their number of rows/columns is a member of
    the base 2 geometric progression.
    Args:
        a: The matrix on the left of a * b.
        b: The matrix on the right of a * b.
    Returns:
        The matrix product of a and b.
    Raises:
        ValueError: Matrices a and b were not square and of equal size.
    """ 
    if len(a) != len(a[1]):
        raise ValueError('a is not a square matrix.')
    if len(b) != len(b[1]):
        raise ValueError('b is not a square matrix.')
    if len(a) != len(b):
        raise ValueError('Matrices are not aligned.')
    n = len(a)
    a = fill(a)
    b = fill(b)
    geoProduct = strassenMultiplyGeo(a, b)
    product = [row[ : n] for row in geoProduct[ : n]] # strip 0's
    return np.array(product)