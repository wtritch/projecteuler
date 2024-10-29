import time
from typing import List, Generator


# In the United Kingdom the currency is made up of pound (£) and pence (p). There are eight coins in general circulation:
#
# 1p, 2p, 5p, 10p, 20p, 50p, £1 (100p), and £2 (200p).
# It is possible to make £2 in the following way:
#
# 1×£1 + 1×50p + 2×20p + 1×5p + 1×2p + 3×1p
# How many different ways can £2 be made using any number of coins?

def get_combinations_brute_force(amount: int, denominations: List[int]) -> int:
    denominations.sort(reverse=False)

    denomination_values = [0] * len(denominations)
    combination_count = 0

    while True:
        combo_count, complete = increment_and_check(amount, 0, denominations, denomination_values)
        combination_count += combo_count
        if complete:
            return combination_count


def increment_and_check(amount: int, idx: int, denominations: List[int], denomination_values: List[int]) -> [int, bool]:
    combination_count = 0
    denomination_values[idx] += denominations[idx]
    total = sum(denomination_values)
    if total >= amount:
        if total == amount:
            combination_count += 1

        if idx + 1 >= len(denominations):
            return combination_count, True

        denomination_values[idx] = 0
        combo_count, complete = increment_and_check(amount, idx + 1, denominations, denomination_values)
        return combination_count + combo_count, complete

    return combination_count, False


def get_combinations_with_tuples(amount: int, denominations: List[int]) -> int:
    combination_count = 0
    denominations.sort(reverse=True)

    for denomination_tuple in get_denomination_tuples(denominations):
        if denomination_tuple is None:
            break
        # Include at least one coin of each denomination
        remainder = amount - sum(denomination_tuple)
        combination_count += get_combination_count(denomination_tuple, remainder)

    return combination_count

def get_denomination_tuples(denominations: List[int]) -> Generator[List[int], None, None]:
    for denomination_count in range(1, len(denominations) + 1):
        try:
            for denomination_tuple in n_choose_r(denominations, denomination_count):
                yield denomination_tuple
        except StopIteration:
            continue

def n_choose_r(values: List[int], r: int) -> Generator[List[int], None, None]:
    """Yield the various combinations of nCr of the given list of values.
    Example: n_choose_r([1, 2, 3], 2) will yield:
    [1, 2], [1, 3], [2, 3]

    :param values:  The n values to choose from
    :param r:       The number of values to choose
    :returns:   The unique combinations of r from the values list
    """
    if r == len(values):
        yield values
        return

    for idx, value in enumerate(values):
        if r == 1:
            # We're only selecting one, just iterate down the list
            yield [value]
            continue

        if r + idx > len(values):
            # Not enough remaining for a sub-list, we're done
            return

        for sub_combination in n_choose_r(values[idx + 1:], r - 1):
            yield [value] + sub_combination

def get_combination_count(denominations: List[int], amount: int) -> int:
    """
    Given a set of coin denominations and a target amount, return the number of unique coin combinations that can
    produce the given amount.

    :param denominations:   A set of coin denominations.  Performs better if ordered descending.
    :param amount:          The target total coin value
    :return:    The number of unique combinations of different coin denominations that sum to the target total coin value
    """
    if amount < 0 or len(denominations) == 0:
        # We've blown past our target amount or are considering an empty set of coin denominations
        return 0

    if len(denominations) == 1:
        # We're only considering one coin, see if there's a way to hit our amount with them
        return 1 if amount % denominations[0] == 0 else 0

    count = 0
    for idx, denomination in enumerate(denominations):
        if amount % denomination == 0:
            count += 1

        remainder = amount - denomination
        while remainder > 0:
            count += get_combination_count(denominations[idx + 1:], remainder)
            remainder -= denomination
    return count

if __name__ == "__main__":
    coin_denominations: List[int] = [200, 100, 50, 20, 10, 5, 2, 1]
    # denominations: List[int] = [100, 50, 10]
    target_amount: int = 200
    start_time = time.time()

    # result = get_combinations_brute_force(target_amount, coin_denominations)
    result = get_combinations_with_tuples(target_amount, coin_denominations)


    end_time = time.time()

    print(f"Result: {result}\nTime: {end_time-start_time}")