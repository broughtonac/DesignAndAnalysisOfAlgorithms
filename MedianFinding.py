import random


def random_nums(n, a, b):
    """Generates a list of random ints with no repeats.
    Args:
        n: The amount of numbers to generate.
        a: The lower bound for generating random ints.
        b: The upper bound for generating random ints.
    Returns:
        A list of n random integers, each between a and b inclusive.
    """
    nums = set()
    while len(nums) < n:
        nums.add(random.randint(a, b))
    nums = list(nums)
    random.shuffle(nums)
    return nums


def naive_median(nums):  # O(n lg n)
    """Finds the median of a list of numerics.
    The naive approach sorts nums then selects the value at the middle index
    (or the average of the values at the two middle indexes if there are an
    even number of elements).
    Args:
        nums: A list of numerics.
    Returns:
        The median of nums.
    """
    nums = sorted(nums)
    if len(nums) % 2 == 1:
        return nums[len(nums) // 2]
    else:
        lower = nums[(len(nums) // 2) - 1]
        upper = nums[len(nums) // 2]
        return (lower + upper) * 0.5


def columnize(nums):
    """Chops a list into groups of 5, each sorted in descending order.
    Args:
        nums: A list of numerics.
    Returns:
        A list of lists with inner lists representing sorted columns.
    """
    columns = []
    col = []
    for i in range(len(nums)):
        if i % 5 == 0 and i != 0:
            col.sort(reverse=True)
            columns.append(col)
            col = [nums[i]]
        else:
            col.append(nums[i])
    if col:
        col.sort(reverse=True)
        columns.append(col)
    return columns


def quick_select(nums, k, f):
    """Finds the kth smallest element of a list of numerics.
    Args:
        nums: A list of numerics.
        k: The rank of the element we want to select.
        f: The function we use to select pivots.
    Returns:
        The kth smallest element in nums.
    """
    if len(nums) == 1:
        return nums[0]
    pivot = f(nums)
    lows = []
    highs = []
    pivots = []  # repeats? no problem
    for num in nums:
        if num < pivot:
            lows.append(num)
        elif num > pivot:
            highs.append(num)
        elif num == pivot:
            pivots.append(num)
    if k < len(lows):
        return quick_select(lows, k, f)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return quick_select(highs, k - len(lows) - len(pivots), f)


def quick_select_median(nums, f=random.choice):  # wraps quick_select
    """Finds the median of a list of nuemrics.
    Args:
        nums: A list of numerics.
        f: The function used for pivot selection (set to randomly selecting
            elements of nums by default).
    Returns:
        The median of nums by applying quick_select and f to choose pivots.
    """
    if len(nums) % 2 == 1:
        return quick_select(nums, len(nums) // 2, f)
    else:
        lower = quick_select(nums, len(nums) // 2 - 1, f)
        upper = quick_select(nums, len(nums) // 2, f)
        return (lower + upper) * 0.5


def median_of_medians(nums):  # here we 'pick x cleverly'
    """Finds a new pivot for quick_select as the median of medians.
    The median of medians is found by taking the medians of each column in
    columnize(nums), then taking the median of those medians.
    Args:
        nums: A list of numerics.
    Returns:
        The updated pivot for quick_select as the median of medians.
    """
    if len(nums) <= 5:
        return naive_median(nums)
    columns = columnize(nums)
    medians = []
    for col in columns:
        if len(col) % 2 == 1:
            medians.append(col[len(col) // 2])
        else:
            lower = col[(len(col) // 2) - 1]
            upper = col[len(col) // 2]
            medians.append((lower + upper) * 0.5)
    pivot = quick_select_median(medians, median_of_medians)
    return pivot


def fast_median(nums):  # O(n)
    """Finds the median of a list of numerics.
    This is a fast deterministic algorithm for finding the median which uses
    quick_select with median_of_medians.
    Args:
        nums: A list of numerics.
    Returns:
        The median of nums.
    """
    return quick_select_median(nums, median_of_medians)
