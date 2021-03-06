import random


def random_intervals(size, time_bounds, weight_bounds, period):
    """Generates a list of random intervals (for testing).
    Args:
        size: An int indicating the length of the output.
        time_bounds: A tuple of floats indicating the min and max amount of time
            to allow for each interval.
        weight_bounds: A tuple of float indicating the min and max bounds for
            generating the weights of each interval.
        period: A float specifying the time elapsed for all requests to be
            submitted.
    Returns:
        A list of tuples of 3 elements representing intervals as (start time,
        finish time, weight).
    """
    intervals = []
    for dummy in range(size):
        s = random.uniform(0.0, period)
        f = random.uniform(s, s + time_bounds[1] - time_bounds[0])
        w = random.uniform(weight_bounds[0], weight_bounds[1])
        interval = (s, f, w)
        intervals.append(interval)
    return intervals


def find_pci(intervals, curr, a, b):  # PCI = previous compatible interval
    """Finds the previous compatible interval for a given interval.
    Args:
        intervals: A list of intervals sorted by finish time.
        curr: An interval to compare against.
        a: The first index of the subproblem wrt intervals.
        b: The last index of the subproblem wrt intervals.
    Returns:
        The index of the most previous interval in intervals compatible with
        curr.
    """
    # modified binary search - O(lg n)
    curr_start = curr[0]
    m = (a + b) // 2
    mid_finish = intervals[m][1]
    if intervals[b][1] <= curr_start:
        # if the subproblem's last element is compatible with curr
        return b
    elif a > b:
        # if there are no intervals compatible with curr
        return 0
    elif curr_start < mid_finish:
        return find_pci(intervals, curr, a, m - 1)
    else:
        return find_pci(intervals, curr, m + 1, b)


def optimize_wis(intervals):  # WIS = weighted interval scheduling
    """Tabulates WIS solutions to WIS subproblems.
    Args:
        intervals: A list of intervals.
    Returns:
        A tuple containing a list of maximal weights of subproblems and
        memoized find_pci results.
    """  # dynamic programming - O(n lg n)
    intervals.sort(key=lambda x: x[1])
    # sort intervals by increasing finish time - O(n lg n)
    arr = [0.0]
    memo = {}  # memoize find_pci calls since they're made again in traceback
    for j in range(1, len(intervals)):
        curr = intervals[j]
        p = find_pci(intervals[: j], curr, 0, j - 1)
        w = curr[2]
        arr.append(max(w + arr[p], arr[j - 1]))
        memo[j] = p
    return (arr, memo)  # last element of arr = max combined weight of solution


def traceback(intervals, arr, memo, j):
    """Finds the subset of compatible intervals with maximal combined weight.
    Args:
        intervals: A list of intervals.
        arr: The first element of the tuple returned by optimize_wis.
        memo: The second element of the tuple returned by optimize_wis.
        j: The last index of intervals.
    Returns:
        The subset of compatible intervals with maximal combined weight.
    """
    # recursion with less than n calls; better than for loop
    if j == 0:
        return set()
    else:
        curr = intervals[j]
        w = curr[2]
        p = memo[j]
        if w + arr[p] > arr[j - 1]:
            return traceback(intervals, arr, memo, p).add(intervals[j])
        else:
            return traceback(intervals, arr, memo, j - 1)


def solve_wis(intervals):
    """Solves the weighted interval scheduling problem via dynamic programming.
    Finds the maximal combined weight that can be obtained, as well as the
    subset that corresponds to that weight.
    Args:
        intevals: A list of intervals.
    Returns:
        A tuple containing the solution subset and its combined weight.
    """
    res = optimize_wis(intervals)
    maxWeight = res[0][-1]
    subset = traceback(intervals, res[0], res[1], len(intervals) - 1)
    return (maxWeight, subset)
