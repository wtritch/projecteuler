import bisect
import time
from typing import Generator, Dict, Iterable, List, Tuple


def solve_with_brute_force(max_value: int) -> int:
    total = 0
    for i in range(max_value):
        if i % 13 == 0 or i % 17 == 0:
            total += i
    return total

def solve_with_dictionary_generator(max_value: int) -> int:
    total = 0
    for i in generate_next_multiple_with_dictionary([13, 17]):
        if (i >= max_value):
            break
        total += i
    return total

def generate_next_multiple_with_dictionary(numbers: Iterable[int]) -> Generator[int, None, None]:
    multiples: Dict[int, int] = {number:number for number in numbers}
    while True:
        next_multiple = min(multiples.values())
        for base, value in multiples.items():
            if next_multiple == value:
                multiples[base] += base
        yield next_multiple


def solve_with_another_dictionary_generator(max_value: int) -> int:
    total = 0
    for i in generate_next_multiple_with_another_dictionary([13, 17]):
        if (i >= max_value):
            break
        total += i
    return total

def generate_next_multiple_with_another_dictionary(numbers: Iterable[int]) -> Generator[int, None, None]:
    multiples: Dict[int, int] = {number:number for number in numbers}
    while True:
        next_min: int | None = None
        next_values = {}
        for base, value in multiples.items():
            if next_min is None or value < next_min:
                next_min = value
                next_values = {base: value+base}
            elif next_min == value:
                next_values[base] = value+base
        for base, value in next_values.items():
            multiples[base] = value
        yield next_min

def solve_with_sorted_list_generator(max_value: int) -> int:
    total = 0
    for i in generate_next_multiple_sorted_list([13, 17]):
        if (i >= max_value):
            break
        total += i
    return total

def generate_next_multiple_sorted_list(numbers: Iterable[int]) -> Generator[int, None, None]:
    multiples: List[Tuple[int, int]] = []
    for base in numbers:
        bisect.insort(multiples, (base, base), key=lambda x: x[1])

    while True:
        next_value = multiples[0][1]
        while multiples[0][1] == next_value:
            multiple = multiples.pop(0)
            bisect.insort(multiples, (multiple[0], multiple[1]+multiple[0]), key=lambda x: x[1])

        yield next_value


if __name__ == "__main__":
    start = time.time()
    result = solve_with_sorted_list_generator(10000000)
    end = time.time()

    print(f"Result: {result}\nTime: {end-start}")
