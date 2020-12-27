from enum import Enum
import random
import abc


class Suit(Enum):
    CLUB = 0
    HEART = 1
    SPADE = 2
    DIAMOND = 3
    JOKER = 4


class Card:
    def __init__(self, suit: Suit, value: int):
        self.suit = suit
        self.value = value

    def print(self):
        if self.suit == Suit.JOKER:
            print(self.suit.name)
        elif self.value == 1:
            tmp = "Ace"
            print(tmp, "of", self.suit.name, end="")
            print("S")
        elif self.value > 10:
            if self.value == 11:
                tmp = "Jack"
            elif self.value == 12:
                tmp = "Queen"
            else:
                tmp = "King"
            print(tmp, "of", self.suit.name, end="")
            print("S")
        else:
            print(self.value, "of", self.suit.name, end="")
            print("S")

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit


class CustomCard:
    def __init__(self, custom_type: str, value: int):
        self.suit = custom_type
        self.value = value

    def get_type(self):
        return self.suit

    def get_value(self):
        return self.value

    def print(self):
        print(self.suit, self.value)


class BaseDeck:
    def __init__(self):
        self.deck = []
        self.position = 0

    @abc.abstractmethod
    def __fill_deck(self):
        pass

    def __clear_deck(self):
        self.deck.clear()
        self.position = 0

    def is_empty(self):
        return self.position == len(self.deck)

    def get_len(self):
        return len(self.deck[self.position:])

    def shuffle(self):
        if not self.is_empty():
            if self.position == 0:
                random.shuffle(self.deck)
            else:
                tmp = self.deck[:self.position]
                self.deck = self.deck[self.position:]
                random.shuffle(self.deck)
                self.deck = tmp + self.deck

    def get_card(self):
        if not self.is_empty():
            tmp = self.deck[self.position]
            self.position += 1
            return tmp
        return None

    def get_cards(self, size: int):
        if self.is_empty():
            return None
        if len(self.deck) > size:
            tmp = self.deck[self.position: self.position + size]
            self.position += size
        else:
            tmp = self.deck[self.position:]
            self.position = len(self.deck)
        return tmp

    def restart(self):
        self.position = 0

    def get_position(self):
        return self.position

    def get_deck(self):
        return self.deck

    def reset(self):
        self.__clear_deck()
        self.__fill_deck()


class Deck(BaseDeck):
    def __init__(self):
        super().__init__()
        self.__fill_deck()

    def __fill_deck(self):
        for i in range(52):
            self.deck.append(Card(Suit(i % 4), (i % 13) + 1))

    def add_joker(self):
        self.deck.append(Card(Suit.JOKER, 0))


def card_value(card):
    return card.get_value()


def sort_cards(cards: list):
    suits = [[] for x in range(5)]
    tmp = []
    for j in cards:
        suits[j.suit.value].append(j)
    for k in suits:
        k.sort(key=card_value)
        tmp.extend(k)
    return tmp


class Hand:
    def __init__(self):
        self.cards = []

    def move(self, x, y):
        if y == x or y == x+1:
            return 0
        elif y == len(self.cards):
            tmp = self.cards.pop(x)
            self.cards.append(tmp)
            return 0
        tmp = self.cards.pop(x)
        if y < x:
            self.cards = self.cards[:y] + [tmp] + self.cards[y:]
        elif y > x:
            self.cards = self.cards[:y-1] + [tmp] + self.cards[y-1:]

    def look(self):
        for i in self.cards:
            i.print()

    def get_len(self):
        return len(self.cards)

    def insert_card(self, card: Card):
        self.cards.append(card)

    def insert_multiple(self, li: list):
        self.cards.extend(li)

    def get_all(self):
        tmp = self.cards.copy()
        self.clear()
        return tmp

    def peek_all(self):
        return self.cards

    def clear(self):
        self.cards.clear()

    def peek_card(self, index: int):
        return self.cards[index]

    def get_card(self, index: int):
        return self.cards.pop(index)

    def get_cards(self, indexes: list):
        tmp = []
        indexes.sort()
        for i in range(len(indexes)):
            tmp.append(self.cards.pop(indexes[i]-i))
        return tmp

    def sort(self):
        self.cards = sort_cards(self.cards)


class CardGame(metaclass=abc.ABCMeta):
    def __init__(self):
        self.deck = Deck()
        self.players = []

    @abc.abstractclassmethod
    def add_player(self, name: str):
        pass

    @abc.abstractclassmethod
    def start_game(self):
        pass

    def reset(self):
        self.__init__()


"""
action() will ask for an input and search for its corresponding command in the actions or views dictionary
the views dictionary contains actions that can be repeated and will not end a turn
the actions dictionary will return a value to the game class for processing and end its turn
values:
1 - stand : (marks split as done, increments split)
0 - hit: deal a card (if over 21 finishes hand with loss and removes split, if 21 
                                                increments split)
-1 - fold : (removes split)
-2 - double : deal a card, increment split
-3 - split : deal a card to both splits (if split is ace both marked done, if any get 21 finishes split with a normal 
        win and removes split, else increment split, if not ace continue normally)
-4 - indicates that there are no more hands to check : end_turn, check if player is done
player will skip over done splits on action, no need to check

when each player is done, dealer plays until at or over 17, do correct actions for each stand of each player
- call get_value until -4 is returned
"""


class BlackJack(CardGame):
    def __init__(self, starting_money: int = 0):
        super().__init__()
        self.start_money = starting_money
        self.dealer = []
        self.players = []

    def add_player(self, name: str):
        tmp = BlackJackPlayer(name)
        tmp.give_points(self.start_money)
        self.players.append(tmp)

    def start_game(self):
        self.dealer.append(self.deck.get_card())
        self.dealer.append(self.deck.get_card())
        x = blackjack_value(self.dealer)
        for i in self.players:
            i.insert_card(self.deck.get_card())
            i.insert_card(self.deck.get_card())
        if x == 21:
            print("Dealer Natural 21")
            for i in self.players:
                if i.get_value() != 21:
                    i.finish_hand(0)
                else:
                    i.finish_hand(1)
            return
        else:
            for i in self.players:
                print(i.get_name())
                i.place_bet()
                act = i.begin_turn()
                while act != -4:
                    if act == 0:
                        i.insert_card(self.deck.get_card())
                    elif act == -2:
                        i.insert_card(self.deck.get_card())
                        i.inc_split()
                    elif act == -3:
                        i.insert_card_split(self.deck.get_card(), self.deck.get_card())
                    act = i.begin_turn()
                i.end_turn()

        # dealer's turn
        self.peek()
        self.dealer[1].print()
        x = blackjack_value(self.dealer)
        while x < 17:
            tmp = self.deck.get_card()
            tmp.print()
            self.dealer.append(tmp)
            x = blackjack_value(self.dealer)
        if x > 21:
            print("Dealer Bust")
            for i in self.players:
                while i.get_value() != -4:
                    if i.get_value() == 21 and i.get_len() == 2:
                        i.finish_hand(1.5)
                    else:
                        i.finish_hand(2)
        elif x == 21:
            print("Dealer 21")
            for i in self.players:
                while i.get_value() != -4:
                    if i.get_value() == 21:
                        i.finish_hand(1)
                    else:
                        i.finish_hand(0)
        else:
            print("Dealer", x)
            for i in self.players:
                while i.get_value() != -4:
                    if i.get_value() == 21 and i.get_len() == 2:
                        i.finish_hand(1.5)
                    elif i.get_value() > x:
                        i.finish_hand(2)
                    elif i.get_value() == x:
                        i.finish_hand(1)
                    else:
                        i.finish_hand(0)
        for i in self.players:
            print(i.get_name(), i.get_points())

    def peek(self):
        self.dealer[0].print()


class Player(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.name = name
        self.hand = Hand()
        self.points = 0
        self.wins = 0
        self.rounds = 0
        self.done = False
        self.view = {
            'm': self.move_cards,
            'l': self.look,
            's': self.sort
        }
        self.actions = {
            'p': self.play
        }

    @abc.abstractclassmethod
    def begin_turn(self):
        pass

    def action(self):
        print("Your hand:")
        self.look()
        print("options: ", end=" ")
        for i in self.view:
            print(i, end=" ")
        for j in self.actions:
            print(j, end=" ")
        act = input("\nChoose an action: ")
        while act not in self.actions:
            if act in self.view:
                self.view[act]()
            else:
                print("Invalid input, try again.")
            act = input("Choose an action: ")
        return self.actions[act]()

    @staticmethod
    def play():
        return 0

    def give_points(self, pts: int):
        self.points += pts

    def get_name(self):
        return self.name

    def get_points(self):
        return self.points

    def look(self):
        self.hand.look()

    def move_cards(self):
        x = int(input("Choose a card to move: "))
        if x not in range(self.hand.get_len()):
            return "ERROR: x not in range"
        y = int(input("Choose where to move it: "))
        if y not in range(self.hand.get_len()+1):
            return "ERROR: y not in range"
        self.hand.move(x, y)

    def sort(self):
        self.hand.sort()

    def set_done(self):
        self.done = True

    def is_done(self):
        return self.done


# returns the blackjack value of a list of cards
def blackjack_value(cards: list):
    value = 0
    ace = False
    for i in cards:
        if i.value == 1:
            ace = True
        if i.value > 10:
            value += 10
        else:
            value += i.value
    if ace:
        if value + 10 <= 21:
            value += 10
    return value


class Split:
    def __init__(self):
        self.hand = Hand()
        self.doubles = 1
        self.value = 0
        self.done = False

    def clear(self):
        self.value = 0
        self.hand.clear()

    def is_done(self):
        return self.done

    def set_done(self):
        self.done = True

    def can_split(self):
        return self.hand.get_len() == 2 and self.hand.peek_card(0).get_value() == self.hand.peek_card(1).get_value()

    def pop(self):
        tmp = self.hand.get_card(-1)
        self.value = blackjack_value(self.hand.peek_all())
        return tmp

    def insert_card(self, card: Card):
        self.hand.insert_card(card)
        self.value = blackjack_value(self.hand.peek_all())

    def get_value(self):
        return self.value

    def inc_doubles(self):
        self.doubles += 1


class BlackJackPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.bet = 0
        self.total_splits = 0
        self.current_split = 0
        self.splits = [Split()]
        self.view = {
            'm': self.bj_move_cards,
            'l': self.bj_look
        }
        self.actions = {
            'h': self.hit,
            's': self.stay,
            'f': self.fold,
        }

    def begin_turn(self):
        if self.current_split >= len(self.splits):
            return -4
        while self.splits[self.current_split].is_done():
            self.current_split += 1
            if self.current_split >= len(self.splits):
                return -4
        if self.points >= self.bet * (2 ** (self.splits[self.current_split].doubles - 1)):
            self.actions['d'] = self.double
            if self.splits[self.current_split].can_split() and self.total_splits < 3:
                    self.actions['sp'] = self.split
                    act = self.action()
                    self.actions.pop('sp')
            else:
                act = self.action()
            self.actions.pop('d')
        else:
            act = self.action()
        return act

    def rm_split(self):
        self.total_splits -= 1
        self.splits.pop(self.current_split)

    def inc_split(self):
        self.current_split += 1

    def end_turn(self):
        self.current_split = 0

    def insert_card(self, card: Card):
        self.splits[self.current_split].insert_card(card)
        if self.splits[self.current_split].get_value() > 21:
            print("BUST")
            self.finish_hand(0)
        elif self.splits[self.current_split].get_value() == 21:
            self.inc_split()

    def insert_card_split(self, card1: Card, card2: Card):
        if self.get_value() == 1:
            self.splits[self.current_split].set_done()
            self.insert_card(card1)
            if self.get_value() == 21:
                self.finish_hand(2)
        else:
            self.insert_card(card1)

        tmp = self.current_split
        self.current_split = len(self.splits) - 1

        if self.get_value() == 1:
            self.splits[self.current_split].set_done()
            self.insert_card(card2)
            if self.get_value() == 21:
                self.finish_hand(2)
        else:
            self.insert_card(card2)

        self.current_split = tmp
        if self.get_value() == 21:
            self.inc_split()

    def bj_look(self):
        print("look")
        print("current split:", self.current_split)
        print("cards in split:", self.get_len())
        print("number of splits:", len(self.splits))
        self.splits[self.current_split].hand.look()

    def bj_move_cards(self):
        x = int(input("Choose a card to move: "))
        if x not in range(self.splits[self.current_split].hand.get_len()):
            return "ERROR: x not in range"
        y = int(input("Choose where to move it: "))
        if y not in range(self.splits[self.current_split].hand.get_len() + 1):
            return "ERROR: y not in range"
        self.splits[self.current_split].hand.move(x, y)

    def stay(self):
        self.splits[self.current_split].set_done()
        self.inc_split()
        return 1

    def get_value(self):
        if len(self.splits) == 0:
            return -4
        return self.splits[self.current_split].get_value()

    def get_len(self):
        return self.splits[self.current_split].hand.get_len()

    @staticmethod
    def hit():
        return 0

    def fold(self):
        self.finish_hand(0.5)
        return -1

    def double(self):
        self.splits[self.current_split].set_done()
        self.points -= self.bet * (2 ** (self.splits[self.current_split].doubles - 1))
        self.splits[self.current_split].inc_doubles()
        print("Total Cash:", self.points)
        return -2

    def split(self):
        tmp = Split()
        tmp.insert_card(self.splits[self.current_split].pop())
        self.total_splits += 1
        self.splits.append(tmp)
        self.points -= self.bet * (2 ** (self.splits[self.current_split].doubles - 1))
        print("Total Cash:", self.points)
        return -3

    def place_bet(self):
        print("Total Cash:", self.points)
        while True:
            try:
                amt = int(input("Bet amount: "))
                break
            except:
                print("Invalid input, try again.")
        while amt < 2 or amt > self.points:
            if amt > self.points:
                print("Not enough cash, try again.")
            if amt < 2:
                print("Must bet at least 2.")
            try:
                amt = int(input("Bet amount: "))
            except:
                print("Invalid input, try again.")

        self.bet += amt
        self.points -= amt
        print("Total Cash:", self.points)
        print("Current bet:", self.bet)

    def finish_hand(self, multiplier):
        self.points += multiplier * self.bet * (2 ** (self.splits[self.current_split].doubles - 1))
        self.rm_split()
        print("Total Cash:", self.points)
