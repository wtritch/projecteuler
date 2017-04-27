import AGStopwatch = require("agstopwatch/AGStopwatch");
/**
 Largest palindrome product
 Problem 4
 A palindromic number reads the same both ways. The largest palindrome made
 from the product of two 2-digit numbers is 9009 = 91 × 99.

 Find the largest palindrome made from the product of two 3-digit numbers.
 */
export class Problem4 {

    private static maxValue: number = 999;

    static bruteForce() {
        let stopWatch:AGStopwatch = new AGStopwatch();
        stopWatch.start();

        let maxPalindrome = 0;

        outerLoop:
        for (let i of decendingGenerator(this.maxValue)) {
            for (let j of decendingGenerator(i)) {
                let value = i * j;
                if (this.isPalindrome(value)) {
                    maxPalindrome = value;
                    break outerLoop;
                }
            }
        }

        stopWatch.stop();
        console.log(`Problem 4 brute force: ${maxPalindrome} Time: ${stopWatch.elapsed}ms`);
    }

    static isPalindrome(value: number) :boolean {
        let strValue :String = value.toString(10);
        for (let i = 0; i <= Math.floor(strValue.length / 2); i++) {
            if (strValue[i] != strValue[strValue.length - i - 1]) { return false; }
        }
        return true;
    }
}

function* decendingGenerator(maxValue: number) {
    while (maxValue > 0) {
        yield maxValue;
        maxValue--;
    }
}