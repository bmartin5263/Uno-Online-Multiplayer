import sys
import time
import socket
import threading
import curses
from curses import wrapper
from ui2 import UI
from player import Player, ComputerPlayer

class Game:
    PORT = 22000
    MOVEMENT = (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT, curses.KEY_LEFT)
    SELECT = (ord(' '), ord('\n'))
    COMPUTER_NAMES = ('Watson', 'SkyNet', 'Hal 9000', 'Metal Gear')

    MOVEMENT_MAPS = {
        'mode' : {
            0: [3, 1, 0, 0],
            1: [0, 2, 1, 1],
            2: [1, 3, 2, 2],
            3: [2, 0, 3, 3],
        },
        'lobby' : {
            0: [5, 1, 0, 0],
            1: [0, 3, 2, 2],
            2: [0, 3, 1, 1],
            3: [1, 4, 3, 3],
            4: [3, 5, 4, 4],
            5: [4, 0, 5, 5],
        },
        'stage' : {
            0: [2, 2, 1, 1],
            1: [3, 3, 0, 0],
            2: [0, 0, 3, 3],
            3: [1, 1, 2, 2],
        },
        'settings' : {
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
        self.directory = 'mode'

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
        #self.lock = threading.RLock()

        #self.activeButtons = {
        #    'mode': [],
        #    'lobby': [],
        #    'settings': [],
        #}

        #self.pointers = {
        #    'lobby': self.lobbyPointer,
        #    'mode': self.modePointer,
        #    'settings': self.settingsPointer
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
        self.ui.setStageWithPlayer(self.numPlayers, player)
        self.ui.console("TEST")
        self.numPlayers += 1

    def beginLocal(self):
        self.addPlayer(self.myPlayer)

    def beginHost(self):
        self.addPlayer(self.myPlayer)

    def cleanLobby(self):
        for i in range(self.numPlayers):
            self.removePlayer(0)

    def enterLobby(self):
        self.ui.openGroup('lobby')
        self.ui.openGroup('settings')
        self.ui.updateSettings(self.settings)

        if self.local:
            self.beginLocal()

        self.pointer = self.getDefaultPointer('lobby')
        self.updateButtons('lobby')
        self.setPointer('lobby', self.pointer, None)
        while self.directory == 'lobby':

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer('lobby', k)
                if newPointer != self.pointer:
                    self.setPointer('lobby', newPointer, self.pointer)
                    self.pointer = newPointer
            if k in Game.SELECT:
                self.pressButton('lobby')
                self.updateButtons('lobby')
                self.setPointer('lobby', self.pointer, None)

        self.cleanLobby()
        self.updateButtons('lobby')
        self.ui.closeGroup('lobby')
        self.ui.closeGroup('settings')

    def enterMode(self):
        self.ui.openGroup('lobby')
        self.ui.openGroup('settings')
        self.ui.openGroup('mode')

        self.pointer = self.getDefaultPointer('mode')
        self.updateButtons('mode')
        self.setPointer('mode', self.pointer, None)
        while self.directory == 'mode':

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer('mode', k)
                if newPointer != self.pointer:
                    self.setPointer('mode', newPointer, self.pointer)
                    self.pointer = newPointer
            if k in Game.SELECT:
                self.pressButton('mode')

        self.ui.closeGroup('mode')
        self.ui.closeGroup('settings')
        self.ui.closeGroup('lobby')

    def enterSettings(self):
        self.ui.pressSettings()

        settings = list(self.settings)
        pointer = 0
        self.ui.setButtonPointer('settings', pointer)
        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                self.ui.resetButtonPointer('settings', pointer)
                pointer = self.moveSettingsPointer(k, pointer)
                self.ui.setButtonPointer('settings', pointer)

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

        self.ui.resetButtonPointer('settings', pointer)
        self.ui.restoreSettings()
        return settings


    def enterStage(self):
        self.ui.cancelStage()

        pointer = 0
        self.ui.setStagePointer(pointer)

        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.moveStagePointer(k, pointer)
                if newPointer != pointer:
                    self.ui.restoreStagePointer(pointer)
                    self.ui.setStagePointer(newPointer)
                    pointer = newPointer
            if k in Game.SELECT:
                break

        self.ui.setStageWithPlayer(0, self.myPlayer)
        return pointer

    def getDefaultPointer(self, directory):
        if directory == 'mode':
            return 0
        elif directory == 'lobby':
            if self.local:
                return 1
            else:
                if self.hosting:
                    return 2
                else:
                    return 4

    def movePointer(self, directory, movement):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[directory]
        if directory == 'mode':
            newPointer = moveMap[self.pointer][moveNum]
            while not self.active[newPointer]:
                newPointer = moveMap[newPointer][moveNum]
            return newPointer
        elif directory == 'lobby':
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

    def moveStagePointer(self, movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS['stage']
        newPointer = moveMap[pointer][moveNum]
        return newPointer

    def moveSettingsPointer(self, movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS['settings']
        newPointer = moveMap[pointer][moveNum]
        return newPointer

    def pressButton(self, directory):
        if directory == 'mode':
            if self.pointer == 0:                # Local
                self.directory = 'lobby'
                self.local = True
            elif self.pointer == 1:              # Host
                self.directory = 'lobby'
                self.local = False
                self.hosting = True
            elif self.pointer == 2:              # Join
                self.directory = 'lobby'
                self.local = False
                self.hosting = False
            elif self.pointer == 3:              # Exit
                self.gameActive = False
                self.directory = None
        elif directory == 'lobby':
            if self.pointer == 0:                # Begin Match
                pass
            elif self.pointer == 1:              # Add AI
                if self.numPlayers < 4:
                    self.newAI()
                    if self.numPlayers == 4:
                        self.pointer = self.movePointer('lobby', curses.KEY_DOWN)
            elif self.pointer == 2:              # Search
                self.searching = not self.searching
            elif self.pointer == 3:              # Kick
                if self.numPlayers > 1:
                    num = self.enterStage()
                    if num != 0:
                        self.removePlayer(num)
                        if self.numPlayers == 1:
                            self.pointer = self.movePointer('lobby', curses.KEY_UP)
            elif self.pointer == 4:              # Leave
                self.directory = 'mode'
                self.local = False
                self.hosting = False
            elif self.pointer == 5:              # Settings
                settings = self.enterSettings()
                if settings != self.settings:
                    self.settings = settings

    def removePlayer(self, playerNum):
        del self.playerStaging[playerNum]
        for i, player in enumerate(self.playerStaging):
            self.ui.setStageWithPlayer(i, player)
        self.numPlayers -= 1
        self.ui.clearStage(self.numPlayers)
        self.updateButtons('lobby')

    def setPointer(self, directory, pointer, old):
        if old is not None:
            self.ui.resetButtonPointer(directory, old)
        if pointer is not None:
            self.ui.setButtonPointer(directory, pointer)

    def start(self):
        self.gameActive = True
        self.directory = 'mode'
        self.ui.setStageWithPlayer(-1, self.myPlayer)
        while self.gameActive:
            if self.directory == 'mode':
                self.enterMode()
            elif self.directory == 'lobby':
                self.enterLobby()

    def updateButtons(self, directory):
        data = {}
        if directory == 'mode':
            data = {
                'buttonHost' : { 'start': 8, 'length': 32, 'label': 'Host Multiplayer', 'active' : self.canHost, 'color':None},
                'buttonJoin' : { 'start': 8, 'length': 32, 'label': 'Join Multiplayer', 'active' : True, 'color':None},
                'buttonLocal' : { 'start': 7, 'length': 32, 'label': 'Local Singleplayer', 'active' : True, 'color':None},
                'buttonExit' : { 'start': 14, 'length': 32, 'label': 'Exit', 'active' : True, 'color':None},
            }
        elif directory == 'lobby':
            canStart = self.directory == 'lobby' and (self.local or self.hosting) and self.numPlayers > 1
            canSearch = self.directory == 'lobby' and (self.hosting and self.numPlayers < 4)
            canAddAI = self.directory == 'lobby' and not self.searching and ((self.local and self.numPlayers < 4) or (self.hosting and self.numPlayers < 4))
            canKick = self.directory == 'lobby' and ((self.local and self.numPlayers > 1) or (self.hosting and self.numPlayers > 1))
            canSettings = self.directory == 'lobby' and (self.local or self.hosting)
            canLeave = self.directory == 'lobby'
            data = {
                'buttonStart': {'start': 11, 'length': 32, 'label': 'Start Game', 'active' : canStart, 'color':None},
                'buttonAddAI': {'start': 5, 'length': 15, 'label': 'Add AI', 'active' : canAddAI, 'color':None},
                'buttonSearch' : {'start': 4, 'length': 15, 'label': 'Search', 'active' : canSearch, 'color':None},
                'buttonKick' : {'start': 11, 'length': 32, 'label': 'Kick Player', 'active' : canKick, 'color':None},
                'buttonClose': {'start': 11, 'length': 32, 'label': 'Close Room', 'active' : canLeave, 'color':None},
                'buttonSettings': {'start': 12, 'length': 32, 'label': 'Settings', 'active' : canSettings, 'color':None},
            }
            if self.searching:
                data['buttonSearch']['label'] = "Stop Search"
                data['buttonSearch']['start'] = 2
        self.ui.updateButtons(data)
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