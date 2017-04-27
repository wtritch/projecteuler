import {isNullOrUndefined} from "util";
import {Comparator, SortedLinkedList} from "./sorted-linked-list";
import AGStopwatch = require("agstopwatch/AGStopwatch");

/**
 Largest prime factor
 Problem 3
 The prime factors of 13195 are 5, 7, 13 and 29.

 What is the largest prime factor of the number 600851475143 ?

 Output:
 Problem 3 brute force: 6857 Time: 110002ms
 Problem 3 prime factor tree: 6857 Time: 3ms
 */
export class Problem3 {

    private static value :number = 600851475143;

    /**
     * Solve by streaming primes looking for modulo 0.
     */
    static bruteForce() :void {
        let stopWatch:AGStopwatch = new AGStopwatch();
        stopWatch.start();

        let maxFactor: number = Math.floor(Math.sqrt(this.value));
        let lastFactor: number = 0;

        for (let prime of primeGenerator(maxFactor)) {
            if (this.value % prime == 0) {
                lastFactor = prime;
            }
        }

        stopWatch.stop();
        console.log(`Problem 3 brute force: ${lastFactor} Time: ${stopWatch.elapsed}ms`);
    }

    /**
     * Solve by factor tree - continually divide the number by primes, checking if the
     * result is prime.
     */
    static primeFactorTree() :void {
        let stopWatch:AGStopwatch = new AGStopwatch();
        stopWatch.start();

        let factors: number[] = primeFactors(this.value, [] as number[]);

        stopWatch.stop();
        console.log(`Problem 3 prime factor tree: ${factors.pop()} Time: ${stopWatch.elapsed}ms`);
    }

}

/**
 * Calculate the prime factors for a number.
 *
 * @param value             A number
 * @param existingFactors   The existing ordered list of prime factors.
 * @returns {number[]}      An ordered list of prime factors for the given number.
 */
export function primeFactors(value: number, existingFactors: number[]) :number[] {
    if (value == 1) return existingFactors;

    let result :number[] = Array.from(existingFactors);

    // If the value is prime, append it to the existing list and return
    if (isPrime(value)) {
        if (result.length == 0 || result[result.length - 1] != value) {
            result.push(value);
        }

        return result;
    }

    // Attempt to divide the value by prime numbers.  If it is divisible by a prime,
    // add the prime to the list of prime factors, and continue factoring the quotient.
    for (let prime of primeGenerator(Math.floor(Math.sqrt(value)))) {
        if (value % prime == 0) {
            if (result.length == 0 || result[result.length - 1] != value) {
                result.push(prime);
            }

            return primeFactors(value / prime, result);
        }
    }
}

/**
 * Test if a number is prime.
 *
 * @param value         The value to test
 * @returns {boolean}   True if the value is prime
 */
export function isPrime(value: number) {
    if (value < 2) { return false; }
    if (value == 2) { return true; }
    if (value % 2 == 0 || value % 3 == 0) { return false; }

    let sqrt = Math.sqrt(value);
    for (let i = 5; i <= sqrt; i += 6) {
        if (value % i == 0 || value % (i + 2) == 0) { return false; }
    }
    return true;
}

/**
 * Infinite prime generator using sorted rotating prime multiple generators.
 *
 * @param maxValue      OPTIONAL exclusive maximum prime value
 * @returns {number}    A ascending, ordered set of prime numbers
 */
export function* primeGenerator(maxValue: number) {
    let value = 11;

    // Define the multiple generator comparator, sorting on current value
    let comparator :Comparator<ValuedIterator> = {
        compare(valueA: ValuedIterator, valueB: ValuedIterator) :number {
            // console.log(`Comparing ${valueA.current()} to ${valueB.current()} => ${valueA.current() - valueB.current()}`)
            return valueA.current() - valueB.current();
        }
    };

    /**
     * Define a sorted linked list of prime multiple generators.
     *
     * @type {SortedLinkedList<ValuedIterator>}
     */
    let primeMultipleGenerators :SortedLinkedList<ValuedIterator> =
        SortedLinkedList.create(comparator,
            new ValuedIterator(multipleGenerator(3, null)),
            new ValuedIterator(multipleGenerator(5, null)),
            new ValuedIterator(multipleGenerator(7, null)));

    //Yield the first primes
    yield 2;
    yield 3;
    yield 5;
    yield 7;

    while (true) {
        let currentGenerator = primeMultipleGenerators.getValue();
        while (currentGenerator.current() < value) {
            //Bump the prime multiple generators to or past the test value
            currentGenerator.next();
            primeMultipleGenerators = primeMultipleGenerators.getNext().insert(currentGenerator);
            currentGenerator = primeMultipleGenerators.getValue();

            if (currentGenerator.current() == value) {
                //Value is not prime, try the next number;
                value += 2;
            }
        }

        //Value is prime
        if (!isNullOrUndefined(maxValue) && value >= maxValue) {
            //We've passed the max value, abort.
            break;
        }

        yield value;

        //Add a new multiple generator for this prime value
        let newGenerator = new ValuedIterator(multipleGenerator(value, null));
        primeMultipleGenerators = primeMultipleGenerators.insert(newGenerator);

        //Try the next number
        value += 2;
    }
}

/**
 * Generate multiples of a number optionally less than a max value.
 *
 * @param value A value
 * @param max   [optional] A maximum value
 */
function* multipleGenerator(value: number, max: number) {
    let multiple = value;
    while (isNullOrUndefined(max) || multiple < max) {
        yield multiple;
        multiple += value;
    }
}

/**
 * Wrapper class that holds a generator and the last-generated value.
 */
class ValuedIterator {
    private iter:IterableIterator<number>;
    private currentValue: number;

    constructor(iter :IterableIterator<number>) {
        this.iter = iter;
        this.currentValue = iter.next().value;
    }

    next(): number {
        this.currentValue = this.iter.next().value;
        return this.currentValue;
    }

    current(): number {
        return this.currentValue;
    }
}