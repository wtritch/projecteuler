import {isNullOrUndefined} from "util";

/**
 * This class represents a sorted linked list implementation with sorting on insert.
 */
export class SortedLinkedList<T> {
    private value: T;
    private comparator: Comparator<T>;
    private next: SortedLinkedList<T>;

    private constructor(comparator: Comparator<T>, value: T) {
        this.comparator = comparator;
        this.value = value;
    }

    /**
     * Insert a new value into the linked list in sorted order and return the new linked list.
     * @param newValue                  The new value
     * @returns {SortedLinkedList<T>}   The new linked list
     */
    insert(newValue: T) : SortedLinkedList<T> {
        let newNode = new SortedLinkedList(this.comparator, newValue);
        if (this.comparator.compare(this.getValue(), newValue) > 0) {
            newNode.setNext(this);
            return newNode;
        }

        let previous :SortedLinkedList<T> = this;
        let current :SortedLinkedList<T> = this.getNext();
        while (!isNullOrUndefined(current) && this.comparator.compare(current.getValue(), newValue) < 0) {
            previous = current;
            current = current.getNext();
        }
        if (!isNullOrUndefined(current)) {
            newNode.setNext(current);
        }
        previous.setNext(newNode);
        return this;
    }

    /**
     * @returns {T} The value of this node.
     */
    getValue() :T {
        return this.value;
    }

    /**
     * @returns {SortedLinkedList<T>} The next node in the linked list, may be undefined.
     */
    getNext() :SortedLinkedList<T> {
        return this.next;
    }

    /**
     * @param next The next node in the linked list
     */
    private setNext(next: SortedLinkedList<T>) {
        this.next = next;
    }

    /**
     * Create a sorted linked list containing the given values.
     *
     * @param comparator    The ordering comparator
     * @param values        The initial linked list values
     * @returns {SortedLinkedList<T>}   The sorted linked list
     */
    public static create<T>(comparator: Comparator<T>, ...values: T[]) {
        values.sort(comparator.compare);
        let head :SortedLinkedList<T> = new SortedLinkedList(comparator, values.shift());
        let current = head;
        for (let value of values) {
            current.setNext(new SortedLinkedList(comparator, value));
            current = current.getNext();
        }
        return head;
    }
}

/**
 * This interface represents a standard Comparator.
 */
export interface Comparator<T> {

    /**
     * Implementations of this method must return:
     *   A value less than zero if valueA is less than valueB
     *   A value equal to zero if valueA is equivalent to valueB
     *   A value greater than zero if valueA is greater than valueB
     *
     * @param valueA    A test value
     * @param valueB    A test value
     */
    compare(valueA :T, valueB :T) : number;
}