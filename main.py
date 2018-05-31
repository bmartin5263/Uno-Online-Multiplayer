import sys
import time
import socket
import threading
import curses
from curses import wrapper
from ui import UI, Groups, Elements
from player import Player, ComputerPlayer
from network_util import SocketManager, FixedMessage, Message, Notification
from match import Match, Modes

class Game:
    PORT = 24600
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
        self.pointers = {
            Groups.LOBBY : -1,
            Groups.MODE : -1,
            Groups.STAGE : -1
        }
        self.actives = {
            Groups.LOBBY : [],
            Groups.MODE : [],
            Groups.STAGE : []
        }

        # Local Data
        if name != '':
            self.myPlayer = Game.createPlayer(name, True, 0)
        else:
            self.myPlayer = None

        self.gameActive = False          # Exit Program?
        self.canHost = True             # Do you have a network connection?
        self.directory = Groups.MODE

        # Match Data
        self.mode = None
        self.settings = [True, 'Normal', False, False]
        self.playerStaging = []
        self.numPlayers = 0
        self.enterMatch = False

        # Network Sockets
        self.hostSocket = None              # Client Only, socket to the Host
        self.playerSockets = []             # Host Only, list of sockets associated to players in playerStaging
        #self.listeningSocket = None         # Host Only, socket listening for connections
        self.clientManager = None           # Host Only, collection of sockets

        # Hosting Data
        self.searching = False              # Are we searching for players
        self.twirlThread = None             # Thread for updating UI twirls
        self.readThread = None

        # Join Data
        self.connectedToHost = False
        self.tryingToConnect = False

        self.lock = threading.RLock()

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
        if self.mode == Modes.HOST:
            self.sendLobby()

    def addPlayer(self, player, sock=None):
        with self.lock:
            self.numPlayers += 1
            self.playerStaging.append(player)
            if self.mode == Modes.HOST:
                    self.playerSockets.append(sock)
            self.sync(self.ui.setStageWithPlayer, self.numPlayers - 1, player)
            #self.modifyUI(self.ui.console, "Added = {} / {}".format(str(len(self.playerSockets)), str(len(self.playerStaging))))
            if self.mode == Modes.HOST:
                if self.searching:
                    self.sync(self.ui.console, "Your IP is {}. Welcome {}!".format(Game.getIP(), player.name))
                else:
                    self.sync(self.ui.console, "Welcome {}!".format(player.name))

    def beginLocal(self):
        self.addPlayer(self.myPlayer)

    def beginHost(self):
        self.addPlayer(self.myPlayer, None)
        self.clientManager = SocketManager.actAsServer(Game.PORT)
        self.readThread = threading.Thread(target=self.hostReader)
        self.readThread.start()
        self.sync(self.ui.console, "Press Search to Find Players")

    def connectToHost(self, address):
        self.tryingToConnect = True
        self.sync(self.ui.joinButtonConnecting)
        twirlThread = threading.Thread(target=self.t_twirlConnect)
        twirlThread.start()
        self.hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostSocket.settimeout(10)
        try:
            self.hostSocket.connect((address, Game.PORT))
            self.connectedToHost = True
            payload = Message.compile(Message.GENERAL, type='lobby', action='greeting', data=(self.myPlayer.getSummary(),))
            greeting = FixedMessage(data=payload)
            greeting.sendTo(self.hostSocket)
            self.connectedToHost = True
            return True
        except socket.timeout:
            self.sync(self.ui.modeWarning, "Connection Timed Out")
            return False
        except (ConnectionRefusedError, OSError):
            self.sync(self.ui.modeWarning, "Could Not Connect To Host IP")
            return False
        except KeyboardInterrupt:
            self.sync(self.ui.modeWarning, "Connection Interrupted")
            return False
        finally:
            self.tryingToConnect = False
            twirlThread.join()

    def cleanLobby(self):
        for i in range(self.numPlayers):
            self.removePlayer(0)
        self.mode = None
        self.searching = False
        self.connectedToHost = False
        self.enterMatch = False
        if self.twirlThread is not None:
            self.twirlThread.join()
            self.twirlThread = None
        if self.readThread is not None:
            self.readThread.join()
            self.readThread = None
        self.hostSocket = None
        self.clientManager = None
        self.sync(self.ui.console, "")

    def enterLobby(self):
        self.sync(self.ui.openGroup, Groups.LOBBY)
        self.sync(self.ui.openGroup, Groups.SETTINGS)
        #self.modifyUI(self.ui.updateSettings, self.settings)

        if self.mode == Modes.LOCAL:
            self.beginLocal()
        elif self.mode == Modes.HOST:
            self.beginHost()
        elif self.mode == Modes.JOIN:
            self.getLobbyFromHost()

        self.pointers[Groups.LOBBY] = self.getDefaultPointer(Groups.LOBBY)
        self.updateButtons(Groups.LOBBY)
        self.setPointer(Groups.LOBBY, self.pointers[Groups.LOBBY], None)
        while self.directory == Groups.LOBBY:

            try:
                k = self.ui.getInput()
            except KeyboardInterrupt:
                self.directory = Groups.MODE

            if k in Game.MOVEMENT:
                newPointer = self.movePointer(Groups.LOBBY, k)
                if newPointer != self.pointers[Groups.LOBBY]:
                    self.setPointer(Groups.LOBBY, newPointer, self.pointers[Groups.LOBBY])
                    self.pointers[Groups.LOBBY] = newPointer

            elif k in Game.SELECT:
                self.pressButton(Groups.LOBBY)
                self.updateButtons(Groups.LOBBY)
                self.setPointer(Groups.LOBBY, self.pointers[Groups.LOBBY], None)

            elif k == -1:
                if self.mode == Modes.JOIN:
                    self.pingHost()
                    if not self.connectedToHost:
                        self.directory = Groups.MODE

            if self.enterMatch:
                self.playMatch()


        self.cleanLobby()
        self.updateButtons(Groups.LOBBY)
        self.sync(self.ui.closeGroup, Groups.LOBBY)
        self.sync(self.ui.closeGroup, Groups.SETTINGS)

    def enterMode(self):
        self.sync(self.ui.openGroup, Groups.LOBBY)
        self.sync(self.ui.openGroup, Groups.SETTINGS)
        self.sync(self.ui.openGroup, Groups.MODE)

        if not self.myPlayer:
            self.sync(self.ui.modeConsole, "Please Enter Your Name")
            name = self.getPlayerName()
            while name == "":
                name = self.getPlayerName()
            self.myPlayer = Game.createPlayer(name, True, 0)

        self.sync(self.ui.setStageWithPlayer, -1, self.myPlayer)

        self.sync(self.ui.modeConsole, "Welcome to Uno! Select a Mode")

        self.pointers[Groups.MODE] = self.getDefaultPointer(Groups.MODE)
        self.updateButtons(Groups.MODE)
        self.setPointer(Groups.MODE, self.pointers[Groups.MODE], None)
        while self.directory == Groups.MODE:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer(Groups.MODE, k)
                if newPointer != self.pointers[Groups.MODE]:
                    self.setPointer(Groups.MODE, newPointer, self.pointers[Groups.MODE])
                    self.pointers[Groups.MODE] = newPointer
            if k in Game.SELECT:
                self.pressButton(Groups.MODE)

        self.sync(self.ui.closeGroup, Groups.MODE)
        self.sync(self.ui.closeGroup, Groups.SETTINGS)
        self.sync(self.ui.closeGroup, Groups.LOBBY)

    def enterSettings(self):
        self.sync(self.ui.pressSettings)

        settings = list(self.settings)
        pointer = 0
        self.sync(self.ui.setButtonPointer, Groups.SETTINGS, pointer)
        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                self.sync(self.ui.resetButtonPointer, Groups.SETTINGS, pointer)
                pointer = Game.moveSettingsPointer(k, pointer)
                self.sync(self.ui.setButtonPointer, Groups.SETTINGS, pointer)

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

        self.sync(self.ui.resetButtonPointer, Groups.SETTINGS, pointer)
        self.sync(self.ui.restoreSettings)
        return settings


    def enterStage(self):
        self.directory = Groups.STAGE
        self.sync(self.ui.cancelStage)

        self.pointers[Groups.STAGE] = self.getDefaultPointer(Groups.STAGE)
        self.sync(self.ui.setStagePointer, self.pointers[Groups.STAGE])

        while True:

            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                newPointer = self.movePointer(Groups.STAGE, k)
                if newPointer != self.pointers[Groups.STAGE]:
                    self.ui.restoreStagePointer(self.pointers[Groups.STAGE])
                    self.ui.setStagePointer(newPointer)
                    self.pointers[Groups.STAGE] = newPointer
            if k in Game.SELECT:
                break
            if k == -1:
                pass

        finalPointer = self.pointers[Groups.STAGE]
        #self.pointers[Groups.MODE] = 0
        self.sync(self.ui.setStageWithPlayer, 0, self.myPlayer)
        self.directory = Groups.LOBBY
        return finalPointer

    def getDefaultPointer(self, directory):
        if directory == Groups.MODE:
            return 0
        elif directory == Groups.LOBBY:
            if self.mode == Modes.LOCAL:
                return 1
            else:
                if self.mode == Modes.HOST:
                    return 2
                else:
                    return 4
        elif directory == Groups.STAGE:
            return 0

    def getHostIP(self):
        success, address = self.ui.getIPJoinButton()
        if success:
            return address
        else:
            return "localhost"

    def getPlayerName(self):
        success, text = self.ui.getNameFromMainStage()
        while not success:
            success, text = self.ui.getNameFromMainStage()
        return text

    def getLobbyFromHost(self):
        self.playerStaging = []
        self.settings = []
        data = eval(FixedMessage.receive(self.hostSocket))
        self.sync(self.ui.console, "Joined Lobby, Waiting for Host To Start Game")
        if data['type'] == 'lobby':
            if data['action'] == 'update':
                playerSummaries = data['data'][0]
                settings = data['data'][1]
                self.settings = settings
                self.ui.updateSettings(self.settings)
                for tup in playerSummaries:
                    if tup[2]:
                        p = Player(tup[0], tup[1])
                    else:
                        p = ComputerPlayer(tup[0], tup[1])
                    self.addPlayer(p)
        self.readThread = threading.Thread(target=self.clientReader)
        self.readThread.start()

    @staticmethod
    def getIP():
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            ip = "Unknown"
        return ip

    def sendLobby(self):
        data = []
        playerList = []
        for player in self.playerStaging:
            playerList.append(player.getSummary())
        data.append(playerList)
        data.append(list(self.settings))
        payload = Message.compile(Message.GENERAL, type='lobby', action='update', data=data)
        self.clientManager.writeAll(payload)
        if self.searching:
            payload = Message.compile(Message.GENERAL, type='lobby', action='search', data=True)
            self.clientManager.writeAll(payload)
        else:
            payload = Message.compile(Message.GENERAL, type='lobby', action='search', data=False)
            self.clientManager.writeAll(payload)

    def sendMessage(self, message, exclude):
        payload = Message.compile(Message.GENERAL, type='lobby', action='message', data=(message,))
        self.clientManager.writeAll(payload, exclude)

    def sync(self, func, *args):
        with self.lock:
            func(*args)

    def movePointer(self, directory, movement):
        with self.lock:
            moveNum = Game.MOVEMENT.index(movement)
            moveMap = Game.MOVEMENT_MAPS[directory]
            if directory == Groups.MODE:
                newPointer = moveMap[self.pointers[directory]][moveNum]
                while not self.actives[directory][newPointer]:
                    newPointer = moveMap[newPointer][moveNum]
                return newPointer
            elif directory == Groups.LOBBY:
                newPointer = moveMap[self.pointers[directory]][moveNum]
                if newPointer == 1 and not self.actives[directory][1]:
                    newPointer = 2
                elif newPointer == 2 and not self.actives[directory][2]:
                    newPointer = 1
                while not self.actives[directory][newPointer]:
                    newPointer = moveMap[newPointer][moveNum]
                    if newPointer == 1 and not self.actives[directory][1]:
                        newPointer = 2
                    elif newPointer == 2 and not self.actives[directory][2]:
                        newPointer = 1
                return newPointer
            elif directory == Groups.STAGE:
                moveNum = Game.MOVEMENT.index(movement)
                moveMap = Game.MOVEMENT_MAPS[Groups.STAGE]
                newPointer = moveMap[self.pointers[directory]][moveNum]
                if newPointer < self.numPlayers:
                    return newPointer
                else:
                    return self.pointers[directory]


    def moveStagePointer(self, movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[Groups.STAGE]
        newPointer = moveMap[pointer][moveNum]
        if newPointer < self.numPlayers:
            return newPointer
        else:
            return pointer

    @staticmethod
    def moveSettingsPointer(movement, pointer):
        moveNum = Game.MOVEMENT.index(movement)
        moveMap = Game.MOVEMENT_MAPS[Groups.SETTINGS]
        newPointer = moveMap[pointer][moveNum]
        return newPointer

    def pingHost(self):
        #curses.flash()
        try:
            ping = Message.compile(Message.GENERAL, type='ping', action='ping', data=("ping",))
            greeting = FixedMessage(data=ping)
            greeting.sendTo(self.hostSocket)
        except OSError:
            self.connectedToHost = False

    def pauseThreads(self):
        if self.mode != Modes.LOCAL:
            self.readThread.join()
            self.readThread = None

    def resumeThreads(self):
        if self.mode == Modes.JOIN:
            self.readThread = threading.Thread(target=self.clientReader)
            self.readThread.start()
        elif self.mode == Modes.HOST:
            self.readThread = threading.Thread(target=self.hostReader)
            self.readThread.start()


    def playMatch(self):
        self.sync(self.ui.closeGroup, Groups.LOBBY)
        self.sync(self.ui.closeGroup, Groups.SETTINGS)

        self.pauseThreads()

        m = Match(self.mode, self.ui, self.settings, self.playerStaging, self.playerSockets, self.hostSocket)
        self.playerStaging = m.play()

        for i, player in enumerate(self.playerStaging):
            self.sync(self.ui.setStageWithPlayer, i, player)

        self.resumeThreads()

        self.enterMatch = False
        self.sync(self.ui.openGroup, Groups.LOBBY)
        self.sync(self.ui.openGroup, Groups.SETTINGS)

    def pressButton(self, directory):
        if directory == Groups.MODE:
            if self.pointers[directory] == 0:                # Local
                self.directory = Groups.LOBBY
                self.mode = Modes.LOCAL
            elif self.pointers[directory] == 1:              # Host
                self.directory = Groups.LOBBY
                self.mode = Modes.HOST
            elif self.pointers[directory] == 2:              # Join
                address = self.getHostIP()
                if address != "":
                    success = self.connectToHost(address)
                    if success:
                        self.directory = Groups.LOBBY
                        self.mode = Modes.JOIN
                self.sync(self.ui.restoreJoinButton)
            elif self.pointers[directory] == 3:              # Exit
                self.gameActive = False
                self.directory = None
        elif directory == Groups.LOBBY:
            if self.pointers[directory] == 0:                # Begin Match
                self.enterMatch = True
            elif self.pointers[directory] == 1:              # Add AI
                if self.numPlayers < 4:
                    self.newAI()
                    if self.numPlayers == 4:
                        self.pointers[Groups.LOBBY] = self.movePointer(Groups.LOBBY, curses.KEY_UP)
            elif self.pointers[directory] == 2:              # Search
                if self.mode == Modes.HOST:
                    if not self.searching:
                        self.startSearching()
                        payload = Message.compile(Message.GENERAL, type='lobby', action='search', data=True)
                        self.clientManager.writeAll(payload)
                    else:
                        self.stopSearching()
                        payload = Message.compile(Message.GENERAL, type='lobby', action='search', data=False)
                        self.clientManager.writeAll(payload)
            elif self.pointers[directory] == 3:              # Kick
                if self.numPlayers > 1:
                    num = self.enterStage()
                    if num != 0:
                        self.removePlayer(num)
                    if self.numPlayers == 1:
                        self.pointers[Groups.LOBBY] = self.movePointer(Groups.LOBBY, curses.KEY_UP)
            elif self.pointers[directory] == 4:              # Leave
                self.directory = Groups.MODE
                if self.connectedToHost:
                    self.hostSocket.shutdown(socket.SHUT_RDWR)
                    self.hostSocket.close()
                elif self.mode == Modes.HOST:
                    self.clientManager.terminateManager()
            elif self.pointers[directory] == 5:              # Settings
                settings = self.enterSettings()
                if settings != self.settings:
                    self.settings = settings
                    if self.mode == Modes.HOST:
                        self.sendLobby()

    def removePlayer(self, playerNum):
        with self.lock:
            del self.playerStaging[playerNum]
            if self.mode == Modes.HOST:
                self.clientManager.removeSocket(self.playerSockets[playerNum])
                del self.playerSockets[playerNum]
                self.sendLobby()
            for i, player in enumerate(self.playerStaging):
                self.sync(self.ui.setStageWithPlayer, i, player)
            if self.mode == Modes.HOST and self.directory == Groups.STAGE:
                if self.pointers[Groups.STAGE] > 0:
                    curses.beep()
                    self.pointers[Groups.STAGE] -= 1
                    self.sync(self.ui.cancelStage)
                    self.sync(self.ui.setStagePointer, self.pointers[Groups.STAGE])

            self.numPlayers -= 1
            #self.modifyUI(self.ui.console,
            #              "Removed = {} / {}".format(str(len(self.playerSockets)), str(len(self.playerStaging))))
            if self.searching:
                self.sync(self.ui.searchStage, self.numPlayers)
            else:
                self.sync(self.ui.clearStage, self.numPlayers)

    def startSearching(self, interfaceOnly=False):
        if not self.searching:
            self.searching = True
            self.twirlThread = threading.Thread(target=self.t_twirlSearch)
            self.twirlThread.start()
            if not interfaceOnly:
                self.sync(self.ui.console, "Your IP is {}. Searching for Players...".format(Game.getIP()))
                self.clientManager.startListener()

    def stopSearching(self, interfaceOnly=False):
        if self.searching:
            self.searching = False
            if not interfaceOnly:
                self.clientManager.stopListener()
            self.twirlThread.join()

    def setPointer(self, directory, pointer, old):
        if old is not None:
            self.sync(self.ui.resetButtonPointer, directory, old)
        if pointer is not None:
            self.sync(self.ui.setButtonPointer, directory, pointer)

    def clientReader(self):
        while True:
            try:
                message = eval(FixedMessage.receive(self.hostSocket, 1.0))
                if message['type'] == 'lobby':
                    if message['action'] == 'update':
                        self.sync(self.ui.clearAllStages)
                        self.playerStaging = []
                        self.numPlayers = 0
                        playerSummaries = message['data'][0]
                        settings = message['data'][1]
                        self.settings = settings
                        self.sync(self.ui.updateSettings, self.settings)
                        for tup in playerSummaries:
                            if tup[2]:
                                p = Player(tup[0], tup[1])
                            else:
                                p = ComputerPlayer(tup[0], tup[1])
                            self.addPlayer(p)
                    elif message['action'] == 'search':
                        if message['data']:
                            self.startSearching(True)
                        else:
                            self.stopSearching(True)
                    elif message['action'] == 'message':
                        self.sync(self.ui.console, message['data'][0])

            except socket.timeout:
                if self.enterMatch:
                    break
            except BrokenPipeError:
                self.connectedToHost = False
                #self.modifyUI(self.ui.warning, "BROKEN PIPE")
                return
            except OSError:
                #self.modifyUI(self.ui.warning, "OS ERROR")
                return

    def hostReader(self):
        while self.mode == Modes.HOST and not self.enterMatch:
            inbox = self.clientManager.read()
            for isMessage, sock, message in inbox:
                if isMessage:
                    #self.modifyUI(self.ui.console, str(message))
                    message = eval(message)
                    #self.modifyUI(self.ui.console, "Got a Message!")
                    if message['type'] == 'lobby':
                        if message['action'] == 'greeting':
                            p = Player(message['data'][0][0], message['data'][0][1])
                            self.addPlayer(p, sock)
                            self.sendLobby()
                            self.sendMessage("Welcome {}!".format(p.name), [sock])
                            if self.numPlayers >= 4 and self.searching:
                                self.stopSearching()
                                self.updateButtons(Groups.LOBBY)
                                self.pointers[Groups.LOBBY] = self.movePointer(Groups.LOBBY, curses.KEY_DOWN)
                                self.setPointer(Groups.LOBBY, self.pointers[Groups.LOBBY], None)
                else:
                    if message == Notification.CLIENT_DISCONNECTED:
                        try:
                            self.removePlayer(self.playerSockets.index(sock))
                            if self.directory != Groups.STAGE:
                                self.updateButtons(Groups.LOBBY)
                                if self.pointers[Groups.LOBBY] == 3:
                                    self.pointers[Groups.LOBBY] = self.movePointer(Groups.LOBBY, curses.KEY_DOWN)
                                self.setPointer(Groups.LOBBY, self.pointers[Groups.LOBBY], None)
                        except ValueError:
                            pass
            time.sleep(.1)

    def start(self):
        """Starts the game in the Mode directory."""
        self.gameActive = True
        self.directory = Groups.MODE
        while self.gameActive:
            if self.directory == Groups.MODE:
                self.enterMode()
            elif self.directory == Groups.LOBBY:
                self.enterLobby()

    def t_twirlConnect(self):
        """Thread function to create a twirl effect on the join button."""
        while self.tryingToConnect:
            for i in range(4):
                self.sync(self.ui.twirlConnect, i)
                curses.doupdate()
                time.sleep(.1)
                if not self.tryingToConnect:
                    break

    def t_twirlSearch(self):
        """Thread function to create a twirl effect for all stages without players."""
        for i in range(self.numPlayers, 4):
            self.sync(self.ui.searchStage, i)
        curses.doupdate()
        while self.searching:
            for i in range(4):
                for j in range(self.numPlayers, 4):
                    self.sync(self.ui.twirlSearch, j, i)
                curses.doupdate()
                time.sleep(.1)
                if not self.searching:
                    break
        for i in range(self.numPlayers, 4):
            self.sync(self.ui.clearStage, i)

    def updateButtons(self, directory):
        """Uses current state data to set the data and active buttons in a directory."""
        data = {}
        if directory == Groups.MODE:
            data = {
                Elements.BUTTON_HOST : { 'start': 8, 'length': 32, 'label': 'Host Multiplayer', 'active' : self.canHost, 'color':None},
                Elements.BUTTON_JOIN : { 'start': 8, 'length': 32, 'label': 'Join Multiplayer', 'active' : True, 'color':None},
                Elements.BUTTON_LOCAL : { 'start': 7, 'length': 32, 'label': 'Local Singleplayer', 'active' : True, 'color':None},
                Elements.BUTTON_EXIT : { 'start': 14, 'length': 32, 'label': 'Exit', 'active' : True, 'color':None},
            }
        elif directory == Groups.LOBBY:
            canStart = self.directory == Groups.LOBBY and (self.mode == Modes.LOCAL or (self.mode == Modes.HOST and not self.searching)) and self.numPlayers > 1
            canSearch = self.directory == Groups.LOBBY and (self.mode == Modes.HOST and self.numPlayers < 4)
            canAddAI = self.directory == Groups.LOBBY and not self.searching and ((self.mode == Modes.LOCAL and self.numPlayers < 4) or (self.mode == Modes.HOST and self.numPlayers < 4))
            canKick = self.directory == Groups.LOBBY and not self.searching and ((self.mode == Modes.LOCAL and self.numPlayers > 1) or (self.mode == Modes.HOST and self.numPlayers > 1))
            canSettings = self.directory == Groups.LOBBY and not self.searching and (self.mode == Modes.LOCAL or self.mode == Modes.HOST)
            canLeave = self.directory == Groups.LOBBY and not self.searching
            data = {
                Elements.BUTTON_START: {'start': 11, 'length': 32, 'label': 'Start Game', 'active' : canStart, 'color':None},
                Elements.BUTTON_ADD_AI: {'start': 5, 'length': 15, 'label': 'Add AI', 'active' : canAddAI, 'color':None},
                Elements.BUTTON_SEARCH : {'start': 4, 'length': 15, 'label': 'Search', 'active' : canSearch, 'color':None},
                Elements.BUTTON_KICK : {'start': 11, 'length': 32, 'label': 'Kick Player', 'active' : canKick, 'color':None},
                Elements.BUTTON_CLOSE: {'start': 11, 'length': 32, 'label': 'Close Room', 'active' : canLeave, 'color':None},
                Elements.BUTTON_SETTINGS: {'start': 12, 'length': 32, 'label': 'Settings', 'active' : canSettings, 'color':None},
            }
            if self.mode == Modes.JOIN:
                data[Elements.BUTTON_CLOSE]['label'] = "Leave Room"
            if self.searching:
                data[Elements.BUTTON_SEARCH]['label'] = "Stop Search"
                data[Elements.BUTTON_SEARCH]['start'] = 2
        self.sync(self.ui.updateButtons, data)
        self.actives[directory] = []
        for button in UI.BUTTON_GROUPS[directory]:
            self.actives[directory].append(data[button]['active'])


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
        pass
    sys.stdout.write("\x1b[8;33;70t")
    sys.stdout.flush()
    time.sleep(.05)
    # ui = UI(None, 'elements.txt')
    wrapper(main, name)

if __name__ == '__main__':
    program()