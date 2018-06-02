from enum import Enum
from uno_objs import Deck
from ui import Groups, UI
import curses
import threading
import time
import random

class Modes(Enum):
    LOCAL = 0
    JOIN = 1
    HOST = 2

class Match:
    INITIAL_CARD_COUNT = 7
    EXPAND_FRAMES = 12
    CARDS_IN_HAND = 14

    def __init__(self, mode, ui, settings, players, clientSockets=None, clientManager=None, hostSocket=None):
        self.mode = mode
        self.players = players
        self.clientSockets = clientSockets
        self.clientManager = clientManager
        self.hostSocket = hostSocket
        self.ui = ui
        self.lock = threading.RLock()

        # Game Objects
        self.deck = Deck()
        self.pile = Deck()

        # Results
        self.complete = False
        self.abort = False

        # Data
        self.turn = -1
        self.winner = -1
        self.forceDraw = 0
        self.cardPointer = -1
        self.offset = 0
        #self.currentHand = None
        #self.turnComplete = False
        self.reverse = False
        self.currentColor = None
        self.currentValue = None
        #self.viewingTop = True
        self.consecutivePasses = 0
        self.maxPasses = len(self.players)

        # Settings
        self.displayEffects = settings[0]
        self.computerSpeed = settings[1]
        self.showComputerHands = settings[2]
        self.doesNothing = settings[3]

    def drawCardFromDeck(self):
        card = self.deck.drawCard()
        self.sync(self.ui.setDeckLength, len(self.deck))
        return card

    def dealCards(self):
        for i, player in enumerate(self.players):
            for j in range(Match.INITIAL_CARD_COUNT):
                card = self.drawCardFromDeck()
                player.addCard(card)
                if i == len(self.players) - 1:
                    self.ui.setHand(player.hand, player.name, False, 0)
                self.sync(self.ui.updateCardCount, i, len(player.hand))
                if self.displayEffects:
                    time.sleep(.1)

    def placeCardInPile(self, card):
        self.pile.insertCard(card)
        self.sync(self.ui.pushCard, card, False, self.reverse)
        if self.displayEffects:
            for i in range(Match.EXPAND_FRAMES):
                self.sync(self.ui.expandTopCard, i, self.reverse)
        self.currentColor = card.color
        self.currentValue = card.value

    def eventBegin(self):
        """Deal out Cards to Players"""
        if self.mode != Modes.JOIN:
            if self.mode == Modes.HOST:
                self.sync(self.ui.console, "Press Enter to Begin Match")
                self.ui.getInput(True)
                # Send Message To Sockets to Begin Match
            elif self.mode == Modes.LOCAL:
                self.sync(self.ui.console, "Beginning Match! Press Enter")
                self.ui.getInput(True)

            self.dealCards()
            self.turn = random.randrange(0,len(self.players))
            self.ui.console("First Turn will be {}, Press Enter".format(self.players[self.turn].name))
            self.ui.getInput(True)

            card = self.drawCardFromDeck()
            self.placeCardInPile(card)

    def setCardPointer(self, cardNum):
        if self.cardPointer != -1:
            self.sync(self.ui.lowerCard, self.cardPointer)
        self.cardPointer = cardNum
        self.offset = self.cardPointer // Match.CARDS_IN_HAND
        if self.cardPointer != -1:
            self.sync(self.ui.raiseCard, self.cardPointer)


    def nextTurnLocal(self):
        turnComplete = False
        player = self.players[self.turn]
        isHuman = player.isHuman
        self.cardPointer = 0
        self.offset = 0

        if isHuman:
            self.ui.importHand(self.players[self.turn].hand.getUIData(), player.name, False, False)
            self.ui.setCardPointer(self.cardPointer)
        else:
            self.ui.importHand(self.players[self.turn].hand.getUIData(), player.name, self.hideComputerHands, False)
            self.ui.setCardPointer(-1)
        self.ui.emphasizePlayer(self.turn)
        #self.viewingTop = True
        turnComplete = False
        wildColorChange = None
        legalCards = player.getAllLegalCards(self.currentColor, self.currentValue)



    def play(self):
        """Start Game"""
        self.setupInterface()
        self.startReadThreads()
        if self.mode != Modes.JOIN:
            self.initializeCards()
            self.eventBegin()
            while not self.complete:
                self.nextTurnLocal()
        else:
            pass
        '''
        if self.mode == Modes.LOCAL:
            while not self.complete:
                self.nextTurn()
        else:
            self.networkPlay()
        return self.eventEnd()
        '''
        self.sync(self.ui.clearAllTiles)
        self.sync(self.ui.closeGroup, Groups.MATCH)
        return self.players

    def initializeCards(self):
        if self.mode != Modes.JOIN:
            self.deck.populate()
        else:
            self.receiveDeckFromHost()
        self.sync(self.ui.setDeckLength, len(self.deck))

    def receiveDeckFromHost(self):
        pass

    def setupInterface(self):
        """Show all the appropriate ui windows"""
        self.sync(self.ui.openGroup, Groups.MATCH)
        for i, player in enumerate(self.players):
            self.sync(self.ui.setTileWithPlayer, i, player)
        self.sync(self.ui.hideAllCards)
        self.sync(self.ui.hidePile)
        if self.mode == Modes.JOIN:
            self.sync(self.ui.console, "Waiting For Host To Start...")
        else:
            self.sync(self.ui.console, "Hello World")

    def startReadThreads(self):
        pass

    def sync(self, func, *args):
        with self.lock:
            func(*args)

if __name__ == '__main__':
    pass