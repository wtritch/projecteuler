import re
import time
from abc import ABCMeta
from enum import Enum
from typing import Literal, List, Set, Any, cast, Iterable, Tuple, Dict


# In the card game poker, a hand consists of five cards and are ranked, from lowest to highest, in the following way:
#
# High Card: Highest value card.
# One Pair: Two cards of the same value.
# Two Pairs: Two different pairs.
# Three of a Kind: Three cards of the same value.
# Straight: All cards are consecutive values.
# Flush: All cards of the same suit.
# Full House: Three of a kind and a pair.
# Four of a Kind: Four cards of the same value.
# Straight Flush: All cards are consecutive values of same suit.
# Royal Flush: Ten, Jack, Queen, King, Ace, in same suit.
# The cards are valued in the order:
# 2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King, Ace.
#
# If two players have the same ranked hands then the rank made up of the highest value wins; for example, a pair of
# eights beats a pair of fives (see example 1 below). But if two ranks tie, for example, both players have a pair of
# queens, then highest cards in each hand are compared (see example 4 below); if the highest cards tie then the next
# highest cards are compared, and so on.
#
# Consider the following five hands dealt to two players:
#
# Hand	 	Player 1	 	                                Player 2	 	                                    Winner
# 1	 	5H 5C 6S 7S KD  Pair of Fives                       2C 3S 8S 8D TD  Pair of Eights                      Player 2
# 2	 	5D 8C 9S JS AC  Highest card Ace                    2C 5C 7D 8S QH  Highest card Queen                  Player 1
# 3	 	2D 9C AS AH AC  Three Aces                          3D 6D 7D TD QD  Flush with Diamonds                 Player 2
# 4	 	4D 6S 9H QH QC  Pair of Queens Highest card Nine    3D 6D 7H QD QS  Pair of Queens Highest card Seven   Player 1
# 5	 	2H 2D 4C 4D 4S  Full House With Three Fours         3C 3D 3S 9S 9D  Full House with Three Threes        Player 1
# The file, poker.txt, contains one-thousand random hands dealt to two players. Each line of the file contains ten cards
# (separated by a single space): the first five are Player 1's cards and the last five are Player 2's cards. You can
# assume that all hands are valid (no invalid characters or repeated cards), each player's hand is in no specific order,
# and in each hand there is a clear winner.
#
# How many hands does Player 1 win?

class HandType(Enum):
    HighCard = 0
    OnePair = 1
    TwoPairs = 2
    ThreeOfAKind = 3
    Straight = 4
    Flush = 5
    FullHouse = 6
    FourOfAKind = 7
    StraightFlush = 8
    RoyalFlush = 9


Suit = Literal["Heart", "Diamond", "Club", "Spade"]


class Card(metaclass=ABCMeta):
    value: int
    suit: Suit

    def __init__(self, value: int, suit: Suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        value_str: str = str(self.value)
        match self.value:
            case 14:
                value_str = "A"
            case 13:
                value_str = "K"
            case 12:
                value_str = "Q"
            case 11:
                value_str = "J"

        return f"{value_str} {self.suit}"


class Hand(metaclass=ABCMeta):
    """
    Abstract base class for a Hand composed of 5 cards.  Each hand has a type and the ability to compare
    itself to other hands to determine which, if either, has higher value.
    """

    type: HandType

    def __init__(self, type: HandType):
        super().__init__()
        self.type = type

    def compare_to(self, other: Any) -> int:
        """
        Determine if this hand is of higher value than the given hand.

        :param other:   The hand to compare
        :return: a positive value if this hand has greater value, 0 if equal, and negative if the other hand has higher value
        """
        if not isinstance(other, Hand):
            raise AssertionError("Cannot compare to non-hand")

        other_hand: Hand = cast(Hand, other)
        return self.type.value - other_hand.type.value


class HighCardHand(Hand):
    cards: List[Card]

    def __init__(self, cards: List[Card]):
        super().__init__(HandType.HighCard)
        assert len(cards) == 5
        self.cards = cards

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_high_card = cast(HighCardHand, other)
        return compare_kickers(self.cards, other_high_card.cards)


class OnePairHand(Hand):
    pair: List[Card]
    kickers: List[Card]

    def __init__(self, pair: List[Card], kickers: List[Card]):
        super().__init__(HandType.OnePair)
        assert len(pair) == 2
        assert len(kickers) == 3
        self.pair = pair
        self.kickers = kickers

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_pair = cast(OnePairHand, other)
        pair_comparison = compare_cards(self.pair[0], other_pair.pair[0])
        if pair_comparison != 0:
            return pair_comparison
        return compare_kickers(self.kickers, other_pair.kickers)


class TwoPairsHand(Hand):
    high_pair: List[Card]
    low_pair: List[Card]
    kicker: Card

    def __init__(self, high_pair: List[Card], low_pair: List[Card], kicker: Card):
        super().__init__(HandType.TwoPairs)
        assert len(high_pair) == 2
        assert len(low_pair) == 2
        assert kicker is not None
        self.high_pair = high_pair
        self.low_pair = low_pair
        self.kicker = kicker

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_two_pair = cast(TwoPairsHand, other)
        high_pair_comparison = compare_cards(self.high_pair[0], other_two_pair.high_pair[0])
        if high_pair_comparison != 0:
            return high_pair_comparison
        low_pair_comparison = compare_cards(self.low_pair[0], other_two_pair.low_pair[0])
        if low_pair_comparison != 0:
            return low_pair_comparison
        return compare_cards(self.kicker, other_two_pair.kicker)


class ThreeOfAKindHand(Hand):
    triple: List[Card]
    kickers: List[Card]

    def __init__(self, triple: List[Card], kickers: List[Card]):
        super().__init__(HandType.ThreeOfAKind)
        assert len(triple) == 3
        assert len(kickers) == 2
        self.triple = triple
        self.kickers = kickers

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_three_of_a_kind = cast(ThreeOfAKindHand, other)
        triple_comparison = compare_cards(self.triple[0], other_three_of_a_kind.triple[0])
        if triple_comparison != 0:
            return triple_comparison
        return compare_kickers(self.kickers, other_three_of_a_kind.kickers)


class StraightHand(Hand):
    cards: List[Card]

    def __init__(self, cards: List[Card]):
        super().__init__(HandType.Straight)
        assert len(cards) == 5
        self.cards = cards

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_straight = cast(StraightHand, other)
        return compare_cards(self.cards[0], other_straight.cards[0])


class FlushHand(Hand):
    cards: List[Card]

    def __init__(self, cards: List[Card]):
        super().__init__(HandType.Flush)
        assert len(cards) == 5
        self.cards = cards

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_flush = cast(FlushHand, other)
        return compare_kickers(self.cards, other_flush.cards)


class FullHouseHand(Hand):
    triple: List[Card]
    pair: List[Card]

    def __init__(self, triple: List[Card], pair: List[Card]):
        super().__init__(HandType.FullHouse)
        assert len(triple) == 3
        assert len(pair) == 2
        self.triple = triple
        self.pair = pair

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_full_house = cast(FullHouseHand, other)
        triple_comparison = compare_cards(self.triple[0], other_full_house.triple[0])
        if triple_comparison != 0:
            return triple_comparison
        return compare_cards(self.pair[0], other_full_house.pair[0])


class FourOfAKindHand(Hand):
    quadruple: List[Card]
    kicker: Card

    def __init__(self, quadruple: List[Card], kicker: Card):
        super().__init__(HandType.FourOfAKind)
        assert len(quadruple) == 4
        assert kicker is not None
        self.quadruple = quadruple
        self.kicker = kicker

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_four_of_a_kind = cast(FourOfAKindHand, other)
        return compare_cards(self.quadruple[0], other_four_of_a_kind.quadruple[0])


class StraightFlushHand(Hand):
    cards: List[Card]

    def __init__(self, cards: List[Card]):
        super().__init__(HandType.StraightFlush)
        assert len(cards) == 5
        self.cards = cards

    def compare_to(self, other: Hand) -> int:
        type_comparison = super().compare_to(other)
        if type_comparison != 0:
            return type_comparison

        other_straight_flush = cast(StraightFlushHand, other)
        return compare_cards(self.cards[0], other_straight_flush.cards[0])


def group_by_value(cards: Iterable[Card]) -> Tuple[
    Set[Suit], List[Card] | None, List[Card] | None, List[List[Card]], List[Card]]:
    """
    Utility method for grouping cards by value and returning any four-of-a-kind, three-of-a-kind, pairs, and/or kickers
    represented by the given 5 cards.

    :param cards: A set of 5 unique cards
    :return: A Tuple containing the suits, four-of-a-kind, three-of-a-kind, pairs, and/or kickers from the 5 cards
    """
    suits: Set[Suit] = set()

    quadruple: List[Card] | None = None
    triple: List[Card] | None = None
    pairs: List[List[Card]] = []
    kickers: List[Card] = []

    by_value: Dict[int, List[Card]] = {}
    for card in cards:
        if card.value not in by_value:
            by_value.setdefault(card.value, [])
        by_value.get(card.value).append(card)

    for cards_with_same_value in by_value.values():
        for card in cards_with_same_value:
            suits.add(card.suit)
        if len(cards_with_same_value) == 4:
            quadruple = cards_with_same_value
        elif len(cards_with_same_value) == 3:
            triple = cards_with_same_value
        elif len(cards_with_same_value) == 2:
            pairs.append(cards_with_same_value)
        else:
            kickers.append(cards_with_same_value[0])

    kickers.sort(key=lambda x: x.value, reverse=True)
    pairs.sort(key=lambda x: x[0].value, reverse=True)

    return suits, quadruple, triple, pairs, kickers


def to_hand(cards: Iterable[Card]) -> Hand:
    """
    Factory method for converting a set of 5 cards into the best possible hand.

    :param cards:   A set of 5 unique suited cards
    :return: The best hand that can be made from the given cards
    """
    suits, quadruple, triple, pairs, kickers = group_by_value(cards)

    if is_straight(kickers):
        if len(suits) == 1:
            return StraightFlushHand(kickers)
        return StraightHand(kickers)

    if len(suits) == 1:
        return FlushHand(kickers)

    if quadruple is not None:
        return FourOfAKindHand(quadruple=quadruple, kicker=kickers[0])

    if triple is not None:
        if len(pairs) == 1:
            return FullHouseHand(triple=triple, pair=pairs[0])
        return ThreeOfAKindHand(triple=triple, kickers=kickers)

    if len(pairs) == 2:
        return TwoPairsHand(high_pair=pairs[0], low_pair=pairs[1], kicker=kickers[0])

    if len(pairs) == 1:
        return OnePairHand(pair=pairs[0], kickers=kickers)

    return HighCardHand(cards=kickers)


def is_straight(cards_desc: List[Card]) -> bool:
    """
    Helper utility to determine if the list of cards represents a 5-card Straight

    :param cards_desc:  The cards in descending value order
    :returns:   True if the cards represent a 5-card straight
    """
    if len(cards_desc) != 5:
        return False

    last_value: int | None = None
    for card in cards_desc:
        if last_value is not None and last_value != card.value + 1:
            return False
        last_value = card.value
    return True


def compare_kickers(a: List[Card], b: List[Card]) -> int:
    """
    Helper utility to compare two ordered "kicker" card lists to determine which has higher value.

    :param a: a list of cards in descending value order
    :param b: a list of cards in descending value order
    :return: value greater than 0 if a has a higher value kicker, less than 0 if b has a higher value kicker, 0 if kickers are equal value
    """
    if len(a) != len(b):
        raise AssertionError("Cannot compare kickers with unequal lengths")

    for idx, a_kicker in enumerate(a):
        b_kicker: Card = b[idx]
        difference: int = compare_cards(a_kicker, b_kicker)
        if difference != 0:
            return difference

    return 0


def compare_cards(a: Card, b: Card) -> int:
    """
    Helper utility to determine which card has a higher face value.

    :param a:   the first comparison card
    :param b:   the second comparison card
    :return: value greater than 0 if a is higher value, less than 0 if b is higher value, 0 if cards are equal value
    """
    return a.value - b.value


def to_card(serialized_card: str) -> Card:
    match: re.Match = re.match(r"^(\w+)(\w)$", serialized_card)
    if not match:
        raise AssertionError(f"Unable to parse card: {serialized_card}")

    value: int
    match match.group(1):
        case 'A':
            value = 14
        case 'K':
            value = 13
        case 'Q':
            value = 12
        case 'J':
            value = 11
        case 'T':
            value = 10
        case _:
            value = int(match.group(1))

    match match.group(2):
        case 'H':
            return Card(value, 'Heart')
        case 'D':
            return Card(value, 'Diamond')
        case 'C':
            return Card(value, 'Club')
        case 'S':
            return Card(value, 'Spade')
        case _:
            raise AssertionError(f"Cannot parse suit from serialized card: {serialized_card}")


if __name__ == "__main__":

    player_1_victories = 0
    start_time = time.time()

    #     cards = """
    # 5H 5C 6S 7S KD 2C 3S 8S 8D TD
    # 5D 8C 9S JS AC 2C 5C 7D 8S QH
    # 2D 9C AS AH AC 3D 6D 7D TD QD
    # 4D 6S 9H QH QC 3D 6D 7H QD QS
    # 2H 2D 4C 4D 4S 3C 3D 3S 9S 9D
    #     """
    #     lines = cards.split("\n")
    #     for line in lines:

    with open("0054_poker.txt", "r") as source_file:
        for line in source_file:
            line = line.strip()
            serialized_cards = line.split(" ")
            if len(serialized_cards) != 10:
                continue
            player_1 = to_hand(map(to_card, serialized_cards[0:5]))
            player_2 = to_hand(map(to_card, serialized_cards[5:10]))
            result = player_1.compare_to(player_2)
            if result > 0:
                player_1_victories += 1
            elif result == 0:
                raise AssertionError("There must not be poker ties")
            else:
                continue

    end_time = time.time()

    print(f"Result: {player_1_victories}\nTime: {end_time - start_time}")
