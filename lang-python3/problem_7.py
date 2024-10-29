"""
<p>By listing the first six prime numbers: $2, 3, 5, 7, 11$, and $13$, we can see that the $6$th prime is $13$.</p>
<p>What is the $10,001$st prime number?</p>
"""
import time
import math
from typing import List, Generator


def get_nth_prime_div_test(prime_idx: int) -> int:
    primes: List[int] = [2]
    test_num: int = 3
    while len(primes) < prime_idx:
        max_prime = math.sqrt(test_num)
        for prime in primes:
            if prime > max_prime:
                primes.append(test_num)
                break
            if test_num % prime == 0:
                break
        test_num += 2

    return primes[-1]

def get_nth_prime_sieve_of_eratosthenes(prime_idx: int) -> int:
    for idx, prime in enumerate(segmented_eratosthanes_prime_generator()):
        if idx == prime_idx - 1:
            return prime

def segmented_eratosthanes_prime_generator(segment_size: int = 100000) -> Generator[int, None, None]:
    primes: List[int] = []
    generator_index: int = 0
    offset: int = 2

    # Generate the first segment normally
    prime_test = [True for _ in range(segment_size)]
    i = 2
    while i - offset < segment_size:
        if prime_test[i - offset]:
            j = i*i
            while j - offset < segment_size:
                prime_test[j - offset] = False
                j += i
        i += 1
    for idx, is_prime in enumerate(prime_test):
        if is_prime:
            primes.append(idx + offset)
    del prime_test
    offset += segment_size

    while True:
        while generator_index == len(primes):
            primes = primes + primes_in_next_eratosthanes_segment(primes, offset, segment_size)
            offset += segment_size

        yield primes[generator_index]
        generator_index += 1

def primes_in_next_eratosthanes_segment(primes, offset, segment_size) -> List[int]:
    prime_test: List[bool] = [True for _ in range(segment_size)]
    i: int = offset
    sqrt_max_value: float = math.sqrt(i + segment_size)
    for prime in primes:
        if prime > sqrt_max_value:
            break
        j: int = (i // prime) * prime
        while j - offset < segment_size:
            if j - offset < 0:
                j += prime
                continue
            prime_test[j - offset] = False
            j += prime

    segment_primes = []
    for idx, is_prime in enumerate(prime_test):
        if is_prime:
            segment_primes.append(idx + offset)
    return segment_primes


if __name__ == "__main__":
    start_time = time.time()
    # result = get_nth_prime_div_test(1000001)
    result = get_nth_prime_sieve_of_eratosthenes(1000001)
    end_time = time.time()

    print(f"Result: {result}\nTime: {end_time-start_time}")