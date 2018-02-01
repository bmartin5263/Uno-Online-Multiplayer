from curses import wrapper
import sys
from ui import UI
from player import Player, ComputerPlayer
#from match import Match
import curses
import time
import threading
import socket

class Game():

    PORT = 22000
    MOVEMENT = (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT, curses.KEY_LEFT)
    SELECT = (ord(' '), ord('\n'))
    COMPUTER_NAMES = ('Watson', 'SkyNet', 'Hal 9000', 'Metal Gear')

    MV_MAP_MODE = {
        0 : [3, 1, 0, 0],
        1 : [0, 2, 1, 1],
        2 : [1, 3, 2, 2],
        3 : [2, 0, 3, 3],
    }

    MV_MAP_LOBBY = {
        0: [5, 1, 0, 0],
        1: [0, 3, 2, 2],
        2: [0, 3, 1, 1],
        3: [1, 4, 3, 3],
        4: [3, 5, 4, 4],
        5: [4, 0, 5, 5],
    }

    MV_MAP_STAGE = {
        0: [2, 2, 1, 1],
        1: [3, 3, 0, 0],
        2: [0, 0, 3, 3],
        3: [1, 1, 2, 2],
    }

    MESSAGE_FORMAT = "('{}',{})"

    def __init__(self, screen, playerName):
        self.screen = screen
        self.screen.box()
        self.screen.refresh()
        self.ui = UI(screen, 'elements.txt')
        self.myPlayer = self.createPlayer(playerName, 'human')
        self.gameActive = True
        self.canHost = True

        self.hostSocket = None
        self.serverSocket = None
        self.tryingToConnect = False

        self.inputDirectory = None
        self.gameMode = None

        self.searching = False
        self.abortRoom = False
        self.matchQueue = False
        self.stayInRoom = False
        self.searchThread = None
        self.twirlThread = None

        self.lobbyPointer = -1
        self.stagePointer = -1
        self.settingsPointer = -1
        self.modePointer = -1

        self.playerStaging = []
        self.players = []
        self.hSockets = []
        self.hListenThreads = []
        self.hThreadActive = []

        self.numPlayers = 0
        self.lock = threading.RLock()

        self.activeButtons = {
            'mode' : [],
            'lobby' : [],
        }

        self.pointers = {
            'lobby' : self.lobbyPointer,
            'mode' : self.modePointer
        }

        self.settings = [True, False, 'Normal', False]

        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set Options
        try:
            _s.bind(('', Game.PORT))  # Bind Socket to Port
            _s.close()
        except OSError:
            self.canHost = False

    def addPlayer(self, player, s=None):
        self.playerStaging.append(player)
        self.hSockets.append(s)
        self.hListenThreads.append(None)
        self.hThreadActive.append(False)
        if s is not None:
            s.send(self.getPlayerSummary().encode())
            self.titleConsole("Your IP is {}. Welcome {}!".format(self.getIP(), player.name))
            t = threading.Thread(target=self.t_receivePlayerLobby, args=(s,))
            self.hListenThreads[self.numPlayers] = t
            self.hThreadActive[self.numPlayers] = True
            t.start()
        self.updateStage(player, self.numPlayers)
        self.numPlayers += 1
        self.titleConsole("added {}, {}, {}, {}".format(len(self.playerStaging),len(self.hThreadActive), len(self.hListenThreads),
                                                        len(self.hSockets)))
        self.updateButtons('lobby')

    def createPlayer(self, name, type, points=0):
        if type == 'human':
            p = Player(name, points)
        else:
            p = ComputerPlayer(name, points)
        return p

    def drawButtons(self, directory):
        pointer = -1
        if directory == 'lobby':
            pointer = self.lobbyPointer
        elif directory == 'mode':
            pointer = self.modePointer
        self.ui.updateButtons(directory, pointer, {'active':self.activeButtons[directory]})

    def getComputerName(self):
        complete = False
        index = self.numPlayers
        while not complete:
            name = Game.COMPUTER_NAMES[index]
            complete = True
            for player in self.playerStaging:
                if player.name == name:
                    index += 1
                    if index >= len(Game.COMPUTER_NAMES):
                        index = 0
                        complete = False

        return Game.COMPUTER_NAMES[index]

    def getIP(self):
        try:
            name = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            name = "Unknown"
        return name

    def getPlayerSummary(self):
        out = '('
        for p in self.playerStaging:
            out += p.getString()
        out += ')'
        return out

    def interpretMessage(self, message):
        tup = eval(str(message, encoding='utf-8'))
        self.titleConsole(str(tup))
        if tup[0] == 'add':
            p = self.createPlayer(tup[1][0], tup[1][2], int(tup[1][1]))
            self.addPlayer(p)
        elif tup[0] == 'remove':
            self.removePlayer(int(tup[1]))

    def joinServer(self):
        self.ui.prepareJoinButton('getIP')
        self.ui.console(False, "Enter Host IP Address")
        success, text = self.ui.getLineText('buttonNetworkJoin', 1, 10, 16)
        if success:
            self.tryingToConnect = True
            self.ui.prepareJoinButton('connecting')
            self.hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            t = threading.Thread(target=self.t_twirlConnect)
            t.start()
            time.sleep(1)
            try:
                self.hostSocket.connect(('localhost', Game.PORT))
                connectSuccess = True
            except ConnectionRefusedError:
                self.ui.console(False, "Failed To Join Host", True)
                connectSuccess = False
                self.hostSocket = None
            except socket.timeout:
                self.ui.console(False, "Connection Timed Out", True)
                connectSuccess = False
                self.hostSocket = None
            self.tryingToConnect = False
            t.join()
            if connectSuccess:
                self.ui.prepareJoinButton("waiting")
                time.sleep(1)
                myInfo = "({})".format(self.myPlayer.getString())
                self.hostSocket.send(myInfo.encode())
                self.ui.prepareJoinButton("finished")
                return True
            else:
                self.ui.prepareJoinButton("finished")
                return False
        else:
            self.ui.prepareJoinButton('finished')
            return False

    def kickPlayer(self, num):
        if num == -1:
            total = self.numPlayers
            for i in range(total-1, -1, -1):
                if self.hSockets[i] is not None:
                    self.hSockets[i].shutdown(socket.SHUT_RDWR)
                    self.hSockets[i].close()
                else:
                    self.removePlayer(i)
        else:
            if self.hSockets[num] is not None:
                self.hSockets[num].shutdown(socket.SHUT_RDWR)
                self.hSockets[num].close()
            else:
                self.removePlayer(num)

    def listenServer(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set Options
        self.serverSocket.bind(('', Game.PORT))  # Bind Socket to Port
        self.serverSocket.listen(5)  # Listen for Connections

    def movePointer(self, directory, movement):
        moveNum = Game.MOVEMENT.index(movement)
        if directory == 'mode':
            newPointer = Game.MV_MAP_MODE[self.modePointer][moveNum]
            while newPointer not in self.activeButtons['mode']:
                newPointer = Game.MV_MAP_MODE[newPointer][moveNum]
            self.modePointer = newPointer
        if directory == 'lobby':
            newPointer = Game.MV_MAP_LOBBY[self.lobbyPointer][moveNum]
            if newPointer == 1 and self.searching:
                newPointer = 2
            while newPointer not in self.activeButtons['lobby']:
                newPointer = Game.MV_MAP_LOBBY[newPointer][moveNum]
                if newPointer == 1 and self.searching:
                    newPointer = 2
            self.lobbyPointer = newPointer
        if directory == 'stage':
            newPointer = Game.MV_MAP_STAGE[self.stagePointer][moveNum]
            while newPointer >= self.numPlayers:
                newPointer = Game.MV_MAP_STAGE[newPointer][moveNum]
            self.stagePointer = newPointer

    def newAI(self):
        p = ComputerPlayer(self.getComputerName())
        return p

    def pressButton(self, directory):
        if directory == 'mode':
            if self.modePointer == 0:
                self.gameMode = 'local'
                self.inputDirectory = 'lobby'
            elif self.modePointer == 1:
                self.gameMode = 'host'
                self.listenServer()
                self.matchQueue = True
                self.abortRoom = False
                self.inputDirectory = 'lobby'
            elif self.modePointer == 2:
                joined = self.joinServer()
                if joined:
                    self.stayInRoom = True
                    self.gameMode = 'join'
                    self.inputDirectory = 'lobby'
            elif self.modePointer == 3:
                self.gameActive = False
        elif directory == 'lobby':
            if self.lobbyPointer == 0:
                self.matchQueue = False
            elif self.lobbyPointer == 1:
                if self.numPlayers < 4:
                    p = self.newAI()
                    self.addPlayer(p)
            elif self.lobbyPointer == 2:
                if self.searching:
                    self.searchStop()
                else:
                    self.searchStart()
                self.updateButtons('lobby')
            elif self.lobbyPointer == 3:
                self.selectStage()
                if self.stagePointer != 0:
                    self.kickPlayer(self.stagePointer)
                self.stagePointer = -1
            elif self.lobbyPointer == 4:
                if self.gameMode == 'host':
                    self.abortRoom = True
                    #self.serverSocket = None
                elif self.gameMode == 'join':
                    try:
                        self.hostSocket.shutdown(socket.SHUT_RDWR)
                        self.hostSocket.close()
                    except OSError:
                        pass
                    self.hostSocket = None
                self.gameMode = None
                if self.searching:
                    self.searchStop()
                self.kickPlayer(-1)
                self.inputDirectory = 'mode'

    def removePlayer(self, num, all=False):
        self.lock.acquire()
        if all:
            for i in range(self.numPlayers):
                del self.playerStaging[0]
                del self.hListenThreads[0]
                if self.hSockets[0] is not None:
                    try:
                        self.hSockets[0].shutdown(socket.SHUT_RDWR)
                        self.hSockets[0].close()
                    except OSError:
                        pass
                    self.hThreadActive[0] = False
                else:
                    del self.hThreadActive[0]
                del self.hSockets[0]
                self.updateStage(None, i)
                self.numPlayers = 0
            return

        self.titleConsole("{}, {}".format(str(num),len(self.playerStaging)))
        del self.playerStaging[num]
        if self.hSockets[num] is not None:
            try:
                self.hSockets[num].shutdown(socket.SHUT_RDWR)
                self.hSockets[num].close()
            except OSError:
                pass
            self.hThreadActive[num] = False
        else:
            del self.hThreadActive[num]
        del self.hListenThreads[num]
        del self.hSockets[num]
        for i, player in enumerate(self.playerStaging):
            self.updateStage(player, i)
        self.numPlayers -= 1
        self.updateStage(None, self.numPlayers, isSearching=self.searching)
        self.updateButtons('lobby')
        self.titleConsole(
            "removed {}, {}, {}, {}".format(len(self.playerStaging), len(self.hThreadActive), len(self.hListenThreads),
                                          len(self.hSockets)))
        self.lock.release()

    def searchStart(self):
        if self.numPlayers < 4:
            self.titleConsole("Your IP is {}. Searching for Players...".format(self.getIP()))
            for i in range(self.numPlayers, 4):
                self.updateStage(None, i, isSearching=True)
            self.searching = True
            self.searchThread = threading.Thread(target=self.t_searchForPlayers)
            self.twirlThread = threading.Thread(target=self.t_twirlSearch)
            self.searchThread.start()
            self.twirlThread.start()

    def searchStop(self, threadKill=True):
        self.searching = False
        self.serverSocket.close()
        if threadKill:
            self.searchThread.join()
            self.twirlThread.join()
            self.searchThread = None
            self.twirlThread = None
        for i in range(self.numPlayers, 4):
            self.updateStage(None, i)
        self.listenServer()
        if self.numPlayers == 4:
            self.titleConsole("Maximum Players Reached")
        else:
            self.titleConsole("Your IP is {}. Press Search to Find Players".format(self.getIP()))

    def selectStage(self):
        self.stagePointer = 0
        self.updateStage(None, self.stagePointer, isSelected=True, customMessage="Cancel")
        while True:
            k = self.ui.getInput()

            if k in Game.MOVEMENT:
                if self.stagePointer != 0:
                    self.updateStage(self.playerStaging[self.stagePointer], self.stagePointer)
                else:
                    self.updateStage(None, self.stagePointer, isSelected=False, customMessage="Cancel")
                self.movePointer('stage', k)
                if self.stagePointer != 0:
                     self.updateStage(self.playerStaging[self.stagePointer], self.stagePointer, isSelected=True)
                else:
                    self.updateStage(None, self.stagePointer, isSelected=True, customMessage="Cancel")
            if k in Game.SELECT:
                self.updateStage(self.myPlayer, 0)
                #self.updateStage(self.playerStaging[self.stagePointer], self.stagePointer + 1)
                return

    def sendMessage(self, messageType, playerNum=None, ignoreSocket=None):
        message = ''
        if messageType == 'add':
            message = Game.MESSAGE_FORMAT.format('add', self.playerStaging[self.numPlayers-1].getString()[:-1])
        elif messageType == 'remove':
            message = Game.MESSAGE_FORMAT.format('remove', playerNum)
        for s in self.hSockets:
            if s is not None and s != ignoreSocket:
                curses.beep()
                s.send(message.encode())

    def setActiveButtons(self, directory):
        if directory == 'mode':
            if self.canHost:
                self.activeButtons['mode'] = [0, 1, 2, 3]
            else:
                self.activeButtons['mode'] = [0, 2, 3]
        elif directory == 'lobby':
            active = []
            if self.lobbyPointer >= 0:
                if self.numPlayers < 4:
                    if self.gameMode == 'local' or (self.gameMode == 'host' and not self.searching):
                        active.append(1)
                if self.numPlayers > 1 and self.gameMode != 'join':
                    active.append(3)
                    if not self.searching:
                        active.append(0)
                if self.gameMode == 'host' and self.numPlayers < 4:
                    active.append(2)
                active.append(4)
                if self.gameMode != 'join':
                    active.append(5)
            self.activeButtons['lobby'] = list(active)

    def start(self):
        self.ui.openWindow('title')
        self.ui.openWindow('lobby')
        self.ui.openWindow('settings')
        self.ui.console(False, "Welcome to Uno! Select a Mode")
        self.inputDirectory = 'mode'
        self.updateStage(self.myPlayer, None)
        while self.gameActive:

            if self.inputDirectory == 'mode':
                self.ui.openWindow('mode')
                self.modePointer = 0
                self.updateButtons('mode')
                while self.gameActive and self.inputDirectory == 'mode':

                    k = self.ui.getInput()

                    if k in Game.MOVEMENT:
                        self.movePointer('mode', k)
                        self.drawButtons('mode')
                    if k in Game.SELECT:
                        self.pressButton('mode')

                self.ui.closeWindow('mode')
                self.modePointer = -1

            if self.inputDirectory == 'lobby':

                # Initialize Lobby

                if self.gameMode == 'local':
                    self.lobbyPointer = 1
                    self.addPlayer(self.myPlayer)
                elif self.gameMode == 'host':
                    self.titleConsole("Your IP is {}. Press Search to Find Players".format(self.getIP()))
                    self.lobbyPointer = 2
                    self.addPlayer(self.myPlayer)
                elif self.gameMode == 'join':
                    playersInfo = eval(str(self.hostSocket.recv(1024), encoding='utf-8'))
                    for info in playersInfo:
                        p = self.createPlayer(info[0], info[2], info[1])
                        self.addPlayer(p)
                    #self.addPlayer(self.myPlayer)
                    self.lobbyPointer = 4

                self.updateButtons('lobby')
                while self.gameActive and self.inputDirectory == 'lobby':

                    if self.gameMode == 'join':

                        inputThread = threading.Thread(target=self.t_getInput)
                        inputThread.start()
                        while self.stayInRoom:
                            try:
                                hostMessage = self.hostSocket.recv(1024)
                                if hostMessage:
                                    self.interpretMessage(hostMessage)
                                else:
                                    self.stayInRoom = False
                            except OSError:
                                self.stayInRoom = False

                        self.pressButton('lobby')

                    else:

                        k = self.ui.getInput()

                        if k in Game.MOVEMENT:
                            self.movePointer('lobby', k)
                            self.drawButtons('lobby')
                        if k in Game.SELECT:
                            self.pressButton('lobby')

                for i in range(4):
                    self.updateStage(None, i)
                self.lobbyPointer = -1
                self.updateButtons('lobby')

    def t_getInput(self):
        while self.stayInRoom:
            k = self.ui.getInput()
            if k in Game.SELECT:
                try:
                    self.hostSocket.shutdown(socket.SHUT_RDWR)
                    self.hostSocket.close()
                except:
                    pass

    def t_twirlConnect(self):
        while self.tryingToConnect:
            for i in range(4):
                self.ui.twirlConnect(i)
                time.sleep(.1)
                if not self.tryingToConnect:
                    break

    def t_twirlSearch(self):
        while self.searching:
            for i in range(4):
                for j in range(self.numPlayers, 4):
                    self.ui.twirlSearch(j, i)
                curses.doupdate()
                time.sleep(.1)
                if not self.searching:
                    break

    def t_receivePlayerLobby(self, s):
        while self.matchQueue and self.hThreadActive[self.hSockets.index(s)]:
            playerNum = self.hSockets.index(s)
            try:
                message = s.recv(1024)
                if message:
                    pass
                else:
                    self.removePlayer(playerNum)
                    del self.hThreadActive[playerNum]
                    curses.beep()
                    if not self.abortRoom:
                        self.sendMessage('remove', playerNum=playerNum)
                    return
            except OSError:
                self.removePlayer(playerNum)
                del self.hThreadActive[playerNum]
                curses.beep()
                if not self.abortRoom:
                    self.sendMessage('remove', playerNum=playerNum)
                return

    def t_searchForPlayers(self):
        while self.searching:
            try:
                s, addr = self.serverSocket.accept()
            except OSError:
                return

            clientInfo = eval(str(s.recv(1024), encoding='utf-8'))[0]
            p = self.createPlayer(clientInfo[0], clientInfo[2], clientInfo[1])
            self.addPlayer(p, s)
            self.sendMessage('add', ignoreSocket=s)
            if self.numPlayers == 4:
                self.searching = False

    def titleConsole(self, text, warning=False):
        self.ui.console(True, text, warning)

    def updateButtons(self, directory):
        self.setActiveButtons(directory)
        data = {'active' : self.activeButtons[directory]}
        pointer = -1
        if directory == 'lobby':
            pointer = self.lobbyPointer
            if self.gameMode == 'local':
                data['labels'] = [{'name': 'buttonStop', 'start': 4, 'length': 15, 'label': 'Search'}]
            elif self.gameMode == 'join':
                data['labels'] = [{'name': 'buttonClose', 'start': 11, 'length': 32, 'label': 'Leave Room'}]
            elif self.gameMode == 'host':
                if self.searching:
                    data['labels'] = [{'name': 'buttonStop', 'start': 2, 'length': 15, 'label': 'Stop Search'}]
                else:
                    data['labels'] = [{'name': 'buttonStop', 'start': 4, 'length': 15, 'label': 'Search'}]
            else:
                data['labels'] = [{'name': 'buttonStop', 'start': 2, 'length': 15, 'label': 'Stop Search'},
                                  {'name': 'buttonClose', 'start': 11, 'length': 32, 'label': 'Close Room'}]
        elif directory == 'mode':
            pointer = self.modePointer
        if pointer != -1 and pointer not in data['active']:
            self.movePointer(directory, curses.KEY_DOWN)
        self.ui.updateButtons(directory, pointer, data)
        self.drawButtons(directory)

    def updateStage(self, player, stageNum, isSearching=False, isEntering=False, isSelected=False, customMessage=None):
        if player is not None:
            if player.type == 'human':
                self.ui.updatePlayerStage(stageNum, False, player.name, player.points, isSearching, isEntering, isSelected)
            else:
                self.ui.updatePlayerStage(stageNum, False, player.name+' AI', player.points, isSearching, isEntering,
                                          isSelected)
        else:
            if customMessage is None:
                self.ui.updatePlayerStage(stageNum, True, None, None, isSearching, isEntering, isSelected)
            else:
                self.ui.updatePlayerStage(stageNum, False, customMessage, None, isSearching, isEntering, isSelected)


def main(stdscreen, playerName):
    g = Game(stdscreen, playerName)
    g.start()

if __name__ == '__main__':
    try:
        name = sys.argv[1]
        name = name.replace(' ','')
        name = name.replace('"', '')
        name = name.replace("'", '')
        name = name.replace("\n", '')
        if len(name) == 0:
            print("'{}' Is Too Short".format(name))
            exit()
        else:
            name = name[0:12]
    except IndexError:
        print("Error")
        exit()
    sys.stdout.write("\x1b[8;33;70t")
    sys.stdout.flush()
    time.sleep(.05)
    #ui = UI(None, 'elements.txt')
    wrapper(main, name)