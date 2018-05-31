import random
from enum import Enum
from ui2 import Colors

class Card:

    COLORS = (Colors.BLUE, Colors.RED, Colors.GREEN, Colors.YELLOW)
    VALUES = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R', 'X', '+2')
    WILD = ('W', '+4')

    def __init__(self, color, value):
        self.color = color
        self.value = value

        if value in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
            self.points = int(value)
        elif value in ("W", "+4"):
            self.points = 50
        else:
            self.points = 20

        if value in Card.WILD:
            self.wild = True
            self.color = Colors.WHITE
        else:
            self.wild = False

    def getSummary(self):
        return self.color, self.value

class Hand:

    def __init__(self):
        self.hand = []

    def __iter__(self):
        return iter(self.hand)

    def __len__(self):
        return len(self.hand)

    def __getitem__(self, item):
        return self.hand[item]

    def getSummary(self):
        output = []
        for card in self.hand:
            output.append(card.getSummary())
        return output

    def addCard(self, card):
        self.hand.append(card)

    def removeCard(self, index):
        return self.hand.pop(int(index))

    def discard(self):
        self.hand = []

    def getCard(self, index):
        return self.hand[index]

    def indexCard(self, card):
        return self.hand.index(card)

class Deck:

    def __init__(self):
        self.deck = []

    def __getitem__(self, index):
        return self.deck[index]

    def __iter__(self):
        return iter(self.deck)

    def __len__(self):
        return len(self.deck)

    def populate(self):
        for color in Card.COLORS:
            for value in Card.VALUES:
                self.deck.append(Card(color, value))
                if value != '0':
                    self.deck.append(Card(color, value))
        for i in range(4):
            self.deck.append(Card(Colors.WILD, '+4'))
            self.deck.append(Card(Colors.WILD, 'W'))
        self.shuffle()

    def drawCard(self):
        return self.deck.pop()

    def addCard(self, card):
        self.deck.append(card)

    def insertCard(self, card):
        self.deck.insert(0, card)

    def shuffle(self):
        random.shuffle(self.deck)

    def getSummary(self):
        output = []
        for card in self.deck:
            output.append(card.getSummary())
        return output