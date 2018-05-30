from enum import Enum
from uno_objs import Deck
from ui2 import Groups, UI
import curses
import threading
import time

class Modes(Enum):
    LOCAL = 0
    JOIN = 1
    HOST = 2

class Match:

    def __init__(self, mode, ui, settings, players, clientSockets=None, hostSocket=None):
        self.mode = mode
        self.players = players
        self.clientSockets = clientSockets
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

    def play(self):
        """Start Game"""
        self.setupInterface()
        '''
        self.initializeCards()
        self.eventBegin()
        if self.mode == Modes.LOCAL:
            while not self.complete:
                self.nextTurn()
        else:
            self.networkPlay()
        return self.eventEnd()
        '''
        del self.players[1]
        self.ui.console(str(len(self.players)))
        return self.players

    def setupInterface(self):
        """Show all the appropriate ui windows"""
        self.sync(self.ui.openGroup, Groups.MATCH)
        time.sleep(5)
        curses.beep()
        self.sync(self.ui.closeGroup, Groups.MATCH)

    def sync(self, func, *args):
        with self.lock:
            func(*args)

if __name__ == '__main__':
    pass