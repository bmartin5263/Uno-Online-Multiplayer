import sys
import time
import socket
import threading
import curses
from curses import wrapper
from ui2 import UI, Groups, Elements
from player import Player, ComputerPlayer

class Game:
    PORT = 22000
    MOVEMENT = (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT, curses.KEY_LEFT)
    SELECT = (ord(' '), ord('\n'))
    COMPUTER_NAMES = ('Watson', 'SkyNet', 'Hal 9000', 'Metal Gear')

    MOVEMENT_MAPS = {
        Groups.MODE : {
            0: [3, 1, 0, 0],
            1: [0, 2, 1, 1],
            2: [1, 3, 2, 2],
            3: [2, 0, 3, 3],
        },
        Groups.LOBBY : {
            0: [5, 1, 0, 0],
            1: [0, 3, 2, 2],
            2: [0, 3, 1, 1],
            3: [1, 4, 3, 3],
            4: [3, 5, 4, 4],
            5: [4, 0, 5, 5],
        },
        Groups.STAGE : {
            0: [2, 2, 1, 1],
            1: [3, 3, 0, 0],
            2: [0, 0, 3, 3],
            3: [1, 1, 2, 2],
        },
        Groups.SETTINGS : {
            0: [3, 1, 0, 0],
            1: [0, 2, 1, 1],
            2: [1, 3, 2, 2],
            3: [2, 0, 3, 3],
        }
    }

    NEXT_SPEED = {
        'Slow': 'Normal',
        'Normal': 'Fast',
        'Fast': 'Slow'
    }


    def __init__(self, stdscreen, name):
        # User Interface
        self.screen = stdscreen
        self.screen.box()
        self.screen.refresh()
        self.ui = UI(stdscreen)         # Primary UI Object
        self.pointer = -1
        self.active = []

        # Local Data
        self.myPlayer = Game.createPlayer(name, True, 0)
        self.gameActive = False          # Exit Program?
        self.canHost = True             # Do you have a network connection?
        self.directory = Groups.MODE

        # Match Data
        self.local = False              # is this a local game
        self.hosting = False            # are you hosting?
        self.settings = [True, 'Normal', False, False]
        self.playerStaging = []
        self.numPlayers = 0

        # Network Sockets
        self.hostSocket = None              # Client Only, socket to the Host
        self.playerSockets = []             # Host Only, list of sockets associated to players in playerStaging
        self.listeningSocket = None         # Host Only, socket listening for connections
        self.clientManager = None           # Host Only, collection of sockets

        # Hosting Data
        self.searching = False              # Are we searching for players
        self.twirlThread = None             # Thread for updating UI twirls

        #self.inputDirectory = None
        #self.gameMode = None

        #self.searching = False
        #self.abortRoom = False
        #self.matchQueue = False
        #self.stayInRoom = False
        #self.searchThread = None
        #self.twirlThread = None

        #self.lobbyPointer = -1
        #self.stagePointer = -1
        #self.settingsPointer = -1
        #self.modePointer = -1

        #self.players = []
        #self.hSockets = []
        #self.hListenThreads = []
        #self.hThreadActive = []

        #self.numPlayers = 0
        self.lock = threading.RLock()

        #self.activeButtons = {
        #    Groups.MODE: [],
        #    'lobby': [],
        #    Groups.SETTINGS: [],
        #}

        #self.pointers = {
        #    'lobby': self.lobbyPointer,
        #    Groups.MODE: self.modePointer,
        #    Groups.SETTINGS: self.settingsPointer
        #}

        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set Options
        try:
            _s.bind(('', Game.PORT))  # Bind Socket to Port
            _s.close()
        except OSError:
            self.canHost = False

    @staticmethod
    def createPlayer(name, isHuman, points):
        if isHuman:
            p = Player(name, points)
        else:
            p = ComputerPlayer(name, points)
        return p

    def newAI(self):
        name = Game.COMPUTER_NAMES[self.numPlayers]
        p = Game.createPlayer(name, False, 0)
        self.addPlayer(p)

    def addPlayer(self, player, sock=None):
        self.playerStaging.append(player)
        #self.playerSockets.append(sock)
        #self.hListenThreads.append(None)
        #self.hThreadActive.append(False)
        #if sock is not None:
        #    s.send(self.getPlayerSummary().encode())
        #    self.titleConsole("Your IP is {}. Welcome {}!".format(self.getIP(), player.name))
        #    t = threading.Thread(target=self.t_receivePlayerLobby, args=(s,))
        #    self.hListenThreads[self.numPlayers] = t
        #    self.hThreadActive[self.numPlayers] = True
        #    t.start()
        self.modifyUI(self.ui.setStageWithPlayer, self.numPlayers, player)
        self.modifyUI(self.ui.console, "TEST")
        self.numPlayers += 1

    def beginLocal(self):
        self.addPlayer(self.myPlayer)

    def beginHost(self):
        self.addPlayer(self.myPlayer)

    def cleanLobby(self):
        if self.twirlThread is not None:
            self.twirlThread.join()
            self.twirlThread = None
        for i in range(self.numPlayers):
            self.removePlayer(0)

    def enterLobby(self):
        self.modifyUI(self.ui.openGroup, Groups.LOBBY)
        self.modifyUI(self.ui.openGroup, Groups.SETTINGS)
        #self.modifyUI(self.ui.updateSettings, self.settings)

        if self.local:
            self.beginLocal()

        self.pointer = self.getDefaultPointer(Groups.LOBBY)
        self.updateButtons(Groups.LOBBY)
        self.setPointer(Groups.LOBBY, self.pointer, None)
        while self.directory == Groups.LOBBY:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer(Groups.LOBBY, k)
                if newPointer != self.pointer:
                    self.setPointer(Groups.LOBBY, newPointer, self.pointer)
                    self.pointer = newPointer
            if k in Game.SELECT:
                self.pressButton(Groups.LOBBY)
                self.updateButtons(Groups.LOBBY)
                self.setPointer(Groups.LOBBY, self.pointer, None)

        self.cleanLobby()
        self.updateButtons(Groups.LOBBY)
        self.modifyUI(self.ui.closeGroup, Groups.LOBBY)
        self.modifyUI(self.ui.closeGroup, Groups.SETTINGS)

    def enterMode(self):
        self.modifyUI(self.ui.openGroup, Groups.LOBBY)
        self.modifyUI(self.ui.openGroup, Groups.SETTINGS)
        self.modifyUI(self.ui.openGroup, Groups.MODE)

        self.modifyUI(self.ui.modeConsole, "Welcome to Uno! Select a Mode")

        self.pointer = self.getDefaultPointer(Groups.MODE)
        self.updateButtons(Groups.MODE)
        self.setPointer(Groups.MODE, self.pointer, None)
        while self.directory == Groups.MODE:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer(Groups.MODE, k)
                if newPointer != self.pointer:
                    self.setPointer(Groups.MODE, newPointer, self.pointer)
                    self.pointer = newPointer
            if k in Game.SELECT:
                self.pressButton(Groups.MODE)

        self.modifyUI(self.ui.closeGroup, Groups.MODE)
        self.modifyUI(self.ui.closeGroup, Groups.SETTINGS)
        self.modifyUI(self.ui.closeGroup, Groups.LOBBY)

    def enterSettings(self):
        self.modifyUI(self.ui.pressSettings)

        settings = list(self.settings)
        pointer = 0
        self.modifyUI(self.ui.setButtonPointer, Groups.SETTINGS, pointer)
        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                self.modifyUI(self.ui.resetButtonPointer, Groups.SETTINGS, pointer)
                pointer = Game.moveSettingsPointer(k, pointer)
                self.modifyUI(self.ui.setButtonPointer, Groups.SETTINGS, pointer)

            elif k == ord(' '):
                if pointer == 0:
                    settings[0] = not settings[0]
                elif pointer == 1:
                    settings[1] = Game.NEXT_SPEED[settings[1]]
                elif pointer == 2:
                    settings[2] = not settings[2]
                elif pointer == 3:
                    settings[3] = not settings[3]
                self.ui.updateSettings(settings)

            elif k in (ord('\n'), 27):
                break

        self.modifyUI(self.ui.resetButtonPointer, Groups.SETTINGS, pointer)
        self.modifyUI(self.ui.restoreSettings)
        return settings


    def enterStage(self):
        self.modifyUI(self.ui.cancelStage)

        pointer = 0
        self.modifyUI(self.ui.setStagePointer, pointer)

        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = Game.moveStagePointer(k, pointer)
                if newPointer != pointer:
                    self.ui.restoreStagePointer(pointer)
                    self.ui.setStagePointer(newPointer)
                    pointer = newPointer
            if k in Game.SELECT:
                break

        self.modifyUI(self.ui.setStageWithPlayer, 0, self.myPlayer)
        return pointer

    def getDefaultPointer(self, directory):
        if directory == Groups.MODE:
            return 0
        elif directory == Groups.LOBBY:
            if self.local:
                return 1
            else:
                if self.hosting:
                    return 2
                else:
                    return 4

    def modifyUI(self, func, *args):
        with self.lock:
            func(*args)

    def movePointer(self, directory, movement):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[directory]
        if directory == Groups.MODE:
            newPointer = moveMap[self.pointer][moveNum]
            while not self.active[newPointer]:
                newPointer = moveMap[newPointer][moveNum]
            return newPointer
        elif directory == Groups.LOBBY:
            newPointer = moveMap[self.pointer][moveNum]
            if newPointer == 1 and not self.active[1]:
                newPointer = 2
            elif newPointer == 2 and not self.active[2]:
                curses.beep()
                newPointer = 1
            while not self.active[newPointer]:
                newPointer = moveMap[newPointer][moveNum]
                if newPointer == 1 and not self.active[1]:
                    newPointer = 2
                elif newPointer == 2 and not self.active[2]:
                    newPointer = 1
            return newPointer

    @staticmethod
    def moveStagePointer(movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[Groups.STAGE]
        newPointer = moveMap[pointer][moveNum]
        return newPointer

    @staticmethod
    def moveSettingsPointer(movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[Groups.SETTINGS]
        newPointer = moveMap[pointer][moveNum]
        return newPointer

    def pressButton(self, directory):
        if directory == Groups.MODE:
            if self.pointer == 0:                # Local
                self.directory = Groups.LOBBY
                self.local = True
            elif self.pointer == 1:              # Host
                self.directory = Groups.LOBBY
                self.local = False
                self.hosting = True
            elif self.pointer == 2:              # Join
                self.directory = Groups.LOBBY
                self.local = False
                self.hosting = False
            elif self.pointer == 3:              # Exit
                self.gameActive = False
                self.directory = None
        elif directory == Groups.LOBBY:
            if self.pointer == 0:                # Begin Match
                pass
            elif self.pointer == 1:              # Add AI
                if self.numPlayers < 4:
                    self.newAI()
                    if self.numPlayers == 4:
                        self.pointer = self.movePointer(Groups.LOBBY, curses.KEY_DOWN)
            elif self.pointer == 2:              # Search
                self.searching = not self.searching
                if self.searching:
                    self.twirlThread = threading.Thread(target=self.t_twirlSearch)
                    self.twirlThread.start()
                else:
                    self.twirlThread.join()
            elif self.pointer == 3:              # Kick
                if self.numPlayers > 1:
                    num = self.enterStage()
                    if num != 0:
                        self.removePlayer(num)
                        if self.numPlayers == 1:
                            self.pointer = self.movePointer(Groups.LOBBY, curses.KEY_UP)
            elif self.pointer == 4:              # Leave
                self.directory = Groups.MODE
                self.local = False
                self.hosting = False
                self.searching = False
            elif self.pointer == 5:              # Settings
                settings = self.enterSettings()
                if settings != self.settings:
                    self.settings = settings

    def removePlayer(self, playerNum):
        del self.playerStaging[playerNum]
        for i, player in enumerate(self.playerStaging):
            self.modifyUI(self.ui.setStageWithPlayer, i, player)
        self.numPlayers -= 1
        self.modifyUI(self.ui.clearStage, self.numPlayers)
        self.updateButtons(Groups.LOBBY)

    def setPointer(self, directory, pointer, old):
        if old is not None:
            self.modifyUI(self.ui.resetButtonPointer, directory, old)
        if pointer is not None:
            self.modifyUI(self.ui.setButtonPointer, directory, pointer)

    def start(self):
        self.gameActive = True
        self.directory = Groups.MODE
        self.modifyUI(self.ui.setStageWithPlayer, -1, self.myPlayer)
        while self.gameActive:
            if self.directory == Groups.MODE:
                self.enterMode()
            elif self.directory == Groups.LOBBY:
                self.enterLobby()

    def t_twirlSearch(self):
        for i in range(self.numPlayers, 4):
            self.modifyUI(self.ui.searchStage, i)
        curses.doupdate()
        while self.searching:
            for i in range(4):
                for j in range(self.numPlayers, 4):
                    self.modifyUI(self.ui.twirlSearch, j, i)
                curses.doupdate()
                time.sleep(.1)
                if not self.searching:
                    break
        for i in range(self.numPlayers, 4):
            self.modifyUI(self.ui.clearStage, i)

    def updateButtons(self, directory):
        data = {}
        if directory == Groups.MODE:
            data = {
                Elements.BUTTON_HOST : { 'start': 8, 'length': 32, 'label': 'Host Multiplayer', 'active' : self.canHost, 'color':None},
                Elements.BUTTON_JOIN : { 'start': 8, 'length': 32, 'label': 'Join Multiplayer', 'active' : True, 'color':None},
                Elements.BUTTON_LOCAL : { 'start': 7, 'length': 32, 'label': 'Local Singleplayer', 'active' : True, 'color':None},
                Elements.BUTTON_EXIT : { 'start': 14, 'length': 32, 'label': 'Exit', 'active' : True, 'color':None},
            }
        elif directory == Groups.LOBBY:
            canStart = self.directory == Groups.LOBBY and (self.local or self.hosting) and self.numPlayers > 1
            canSearch = self.directory == Groups.LOBBY and (self.hosting and self.numPlayers < 4)
            canAddAI = self.directory == Groups.LOBBY and not self.searching and ((self.local and self.numPlayers < 4) or (self.hosting and self.numPlayers < 4))
            canKick = self.directory == Groups.LOBBY and ((self.local and self.numPlayers > 1) or (self.hosting and self.numPlayers > 1))
            canSettings = self.directory == Groups.LOBBY and (self.local or self.hosting)
            canLeave = self.directory == Groups.LOBBY
            data = {
                Elements.BUTTON_START: {'start': 11, 'length': 32, 'label': 'Start Game', 'active' : canStart, 'color':None},
                Elements.BUTTON_ADD_AI: {'start': 5, 'length': 15, 'label': 'Add AI', 'active' : canAddAI, 'color':None},
                Elements.BUTTON_SEARCH : {'start': 4, 'length': 15, 'label': 'Search', 'active' : canSearch, 'color':None},
                Elements.BUTTON_KICK : {'start': 11, 'length': 32, 'label': 'Kick Player', 'active' : canKick, 'color':None},
                Elements.BUTTON_CLOSE: {'start': 11, 'length': 32, 'label': 'Close Room', 'active' : canLeave, 'color':None},
                Elements.BUTTON_SETTINGS: {'start': 12, 'length': 32, 'label': 'Settings', 'active' : canSettings, 'color':None},
            }
            if self.searching:
                data[Elements.BUTTON_SEARCH]['label'] = "Stop Search"
                data[Elements.BUTTON_SEARCH]['start'] = 2
        self.modifyUI(self.ui.updateButtons, data)
        self.active = []
        for button in UI.BUTTON_GROUPS[directory]:
            self.active.append(data[button]['active'])


def main(stdscreen, playerName):
    g = Game(stdscreen, playerName)
    g.start()

def program():
    name = ''
    try:
        name = sys.argv[1]
        name = name.replace(' ', '')
        name = name.replace('"', '')
        name = name.replace("'", '')
        name = name.replace("\n", '')
        if len(name) == 0:
            print("'{}' Is Too Short".format(name))
            exit()
        else:
            name = name[0:12]
    except IndexError:
        print("Error, Please Provide a Name")
        exit()
    sys.stdout.write("\x1b[8;33;70t")
    sys.stdout.flush()
    time.sleep(.05)
    # ui = UI(None, 'elements.txt')
    wrapper(main, name)

if __name__ == '__main__':
    program()