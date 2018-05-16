import sys
import time
import socket
import threading
from curses import wrapper

class Game:

    def __init__(self, stdscreen, name):
        self.screen = screen
        self.screen.box()
        self.screen.refresh()
        self.ui = UI(screen)

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
            'mode': [],
            'lobby': [],
            'settings': [],
        }

        self.pointers = {
            'lobby': self.lobbyPointer,
            'mode': self.modePointer,
            'settings': self.settingsPointer
        }

        self.settings = [True, 'Normal', False, False]

        _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Set Options
        try:
            _s.bind(('', Game.PORT))  # Bind Socket to Port
            _s.close()
        except OSError:
            self.canHost = False


def main(stdscreen, playerName):
    g = Game(stdscreen, playerName)
    g.start()
    time.sleep(5)

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