import curses
import curses.panel
import time

def parse(filename):
    filelines = open(filename, 'r').readlines()
    output = []
    currentElement = {}
    for line in filelines:
        split = line.split()
        if len(split) > 0:
            sigil = split[0][0]
            sigilName = split[0][1:].lower()
            if sigil == '!':
                if currentElement != {}:
                    output.append(currentElement)
                    currentElement = {}
                try:
                    currentElement['name'] = split[1]
                except IndexError:
                    pass
            elif sigil == '$':
                value = split[1]
                currentElement[sigilName] = value
            elif sigil == '#':
                pass
    if currentElement != {}:
        output.append(currentElement)
    return output

class UI:

    IGNORE_INPUT = (127, 260, 259, 261, 258)

    DIR_MATCH = ('matchWindow', 'deck', 'topCard', 'bottomCard', 'p1Tile', 'p2Tile', 'p3Tile', 'p4Tile')
    DIR_HAND = ('handWindow', 'previousCard', 'card0', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6', 'card7',
                'card8', 'card9', 'card10', 'card11', 'card12', 'card13', 'nextCard')
    DIR_LOBBY = ('lobbyWindow', 'player0Stage', 'player1Stage', 'player2Stage', 'player3Stage', 'buttonStart',
                 'buttonStop','buttonAddAI', 'buttonKick', 'buttonClose', 'buttonSettings')
    DIR_SETTINGS = ('settingsWindow', 'buttonDisplayEffects', 'buttonComputerSpeed', 'buttonShowHands',
                    'buttonDoesNothing')
    DIR_TITLE = ('title',)
    DIR_MODE = ('modeWindow', 'mainStage', 'buttonLocal', 'buttonNetworkHost','buttonNetworkJoin', 'buttonExit')

    BUT_MODE = ('buttonLocal', 'buttonNetworkHost','buttonNetworkJoin', 'buttonExit')
    BUT_LOBBY = ('buttonStart', 'buttonAddAI', 'buttonStop', 'buttonKick', 'buttonClose', 'buttonSettings')
    BUT_SETTINGS = ('buttonDisplayEffects', 'buttonComputerSpeed', 'buttonShowHands', 'buttonDoesNothing')

    BUT_MAP = {
        'mode': BUT_MODE,
        'lobby': BUT_LOBBY,
        'settings': BUT_SETTINGS
    }

    TWIRL = ('|','/','-','\\')

    COLORS = ('blue', 'red', 'green', 'yellow')

    FRMT_STAGE = 'player{}Stage'

    def __init__(self, screen, filename):
        self.screen = screen
        self.e = {
            'main' : {'window': screen, 'panel': None, 'location': None},
        }
        self.g = {}

        #'''
        curses.curs_set(0)
        curses.init_pair(1, 15, curses.COLOR_BLACK)
        curses.init_pair(2, 39, curses.COLOR_BLACK)
        curses.init_pair(3, 199, curses.COLOR_BLACK)
        curses.init_pair(4, 82, curses.COLOR_BLACK)
        curses.init_pair(5, 226, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, 15)
        curses.init_pair(7, 39, 17)
        curses.init_pair(8, 199, 52)
        curses.init_pair(9, 82, 22)
        curses.init_pair(10, 226, 58)
        curses.init_pair(11, 8, curses.COLOR_BLACK)
        curses.init_pair(12, 9, curses.COLOR_BLACK)

        self.TEXT_COLORS = {
            'white': curses.color_pair(1),
            'blue': curses.color_pair(2),
            'red': curses.color_pair(3),
            'green': curses.color_pair(4),
            'yellow': curses.color_pair(5),
            'invert': curses.color_pair(6),
            'gray': curses.color_pair(11),
            'deepRed': curses.color_pair(12)
        }

        self.BACK_COLORS = {
            'blue': curses.color_pair(7),
            'red': curses.color_pair(8),
            'green': curses.color_pair(9),
            'yellow': curses.color_pair(10),
        }
        elements = parse(filename)
        for e in elements:
            self.createElement(e)

        for element in self.e:
            if element != 'main':
                self.e[element]['panel'].hide()
        UI.refreshPanels()


        self.updateButtons('mode', -1, {'labels': [
            {'name': 'buttonNetworkHost', 'start': 8, 'length': 32, 'label': 'Host Multiplayer'},
            {'name': 'buttonNetworkJoin', 'start': 8, 'length': 32, 'label': 'Join Multiplayer'},
            {'name': 'buttonLocal', 'start': 7, 'length': 32, 'label': 'Local Singleplayer'},
            {'name': 'buttonExit', 'start': 14, 'length': 32, 'label': 'Exit'},
        ],
        })

        self.updateButtons('settings', -1, {'labels': [
            {'name': 'buttonDisplayEffects', 'start':0, 'length': 32, 'label': '- Display Effects'},
            {'name': 'buttonComputerSpeed', 'start': 0, 'length': 32, 'label': '- Computer Speed'},
            {'name': 'buttonShowHands', 'start': 0, 'length': 32, 'label': '- Show Computer Hands'},
            {'name': 'buttonDoesNothing', 'start': 0, 'length': 32, 'label': '- Does Nothing'}
        ], 'active':[0,1,2,3]
        })

        self.updateButtons('lobby', -1, {'labels': [
            {'name': 'buttonStart', 'start': 11, 'length': 32, 'label': 'Start Game'},
            {'name': 'buttonAddAI', 'start': 5, 'length': 15, 'label': 'Add AI'},
            {'name': 'buttonStop', 'start': 4, 'length': 15, 'label': 'Search'},
            {'name': 'buttonKick', 'start': 11, 'length': 32, 'label': 'Kick Player'},
            {'name': 'buttonClose', 'start': 11, 'length': 32, 'label': 'Close Room'},
            {'name': 'buttonSettings', 'start': 12, 'length': 32, 'label': 'Settings'},
        ],
        })

        self.console(False, "Welcome to Uno! Select a Mode")
        self.updatePlayerStage(None, True)
        self.updatePlayerStage(0, True)
        self.updatePlayerStage(1, True)
        self.updatePlayerStage(2, True)
        self.updatePlayerStage(3, True)
        self.updateSettings([True, 'Normal', False, False])

    def createElement(self, e):
        name = e['name']
        location = eval(e['location'])
        dimensions = eval(e['dimensions'])
        border = e['border']
        try:
            group = e['group']
            if group in self.g:
                self.g[group].append(name)
            else:
                self.g[group] = [name]
        except KeyError:
            pass
        try:
            tether = e['tether']
            tetheredLocation = self.e[tether]['location']
            location = (location[0]+tetheredLocation[0],location[1]+tetheredLocation[1])
        except KeyError:
            pass
        window = curses.newwin(dimensions[1], dimensions[0], location[1], location[0])
        if name == 'controls':
            window.bkgd(ord(' ') | curses.color_pair(6))
            window.attrset(self.TEXT_COLORS['invert'])
        else:
            window.bkgd(ord(' ') | curses.color_pair(1))
            window.attrset(self.TEXT_COLORS['white'])
        if border == 'box':
            if name == 'title':
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE, curses.ACS_ULCORNER,
                              curses.ACS_URCORNER, curses.ACS_LTEE, curses.ACS_RTEE)
            elif name in ('lobbyWindow', 'handWindow'):
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_LTEE,
                              curses.ACS_RTEE, curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            elif name == 'matchWindow':
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_LTEE,
                              curses.ACS_RTEE, curses.ACS_LTEE, curses.ACS_RTEE)
            else:
                window.box()
        panel = curses.panel.new_panel(window)
        self.e[name] = {'window':window, 'panel':panel, 'location':location}

        ######### INITIALIZE #############

        if name == 'title':
            self.putText('title', 1, 25, "|| ||", 'blue', False)
            self.putText('title', 1, 31, "||\\ ||", 'green', False)
            self.putText('title', 1, 39, "// \\\\", 'red', False)
            self.putText('title', 2, 25, "|| ||", 'blue', False)
            self.putText('title', 2, 31, "||\\\\||", 'green', False)
            self.putText('title', 2, 38, "((   ))", 'red', False)
            self.putText('title', 3, 25, "\\\\ //", 'blue', False)
            self.putText('title', 3, 31, "|| \\||", 'green', False)
            self.putText('title', 3, 39, "\\\\ //", 'red', False)
            self.putChar('title', 4, 0, curses.ACS_LTEE, 'white', False)
            for i in range(1, 69):
                self.putChar('title', 4, i, curses.ACS_HLINE, 'white', False)
            self.putChar('title', 4, 69, curses.ACS_RTEE, 'white', True)
        if name == 'lobbyWindow':
            self.putChar('lobbyWindow', 9, 0, curses.ACS_LTEE, 'white', False)
            for i in range(1,69):
                self.putChar('lobbyWindow', 9, i, curses.ACS_HLINE, 'white', False)
            self.putChar('lobbyWindow', 9, 69, curses.ACS_RTEE, 'white', True)
        if name == 'handWindow':
            self.putChar('handWindow', 2, 0, curses.ACS_LTEE, 'white', False)
            for i in range(1, 69):
                self.putChar('handWindow', 2, i, curses.ACS_HLINE, 'white', False)
            self.putChar('handWindow', 2, 69, curses.ACS_RTEE, 'white', True)
        if name == 'modeWindow':
            self.putChar(name, 5, 0, curses.ACS_LTEE, 'white', False)
            self.putChar(name, 7, 0, curses.ACS_LTEE, 'white', False)
            for i in range(1, 35):
                self.putChar(name, 5, i, curses.ACS_HLINE, 'white', False)
                self.putChar(name, 7, i, curses.ACS_HLINE, 'white', False)
            self.putChar(name, 5, 35, curses.ACS_RTEE, 'white', False)
            self.putChar(name, 7, 0, curses.ACS_LTEE, 'white', True)
        if name == 'settingsWindow':
            self.putText(name,1,13,"Settings",'white',False)
            self.putChar(name, 2, 0, curses.ACS_LTEE, 'white', False)
            for i in range(1, 33):
                self.putChar(name, 2, i, curses.ACS_HLINE, 'white', False)
            self.putChar(name, 2, 33, curses.ACS_RTEE, 'white', True)

    def checkHidden(self, name, checkPhase):
        try:
            panel = self.e[name]['panel']
            hidden = panel.hidden()
        except:
            return False
        if checkPhase:
            if hidden:
                panel.show()
        else:
            panel.hide()
            UI.refreshPanels()


    def colorWindow(self, name, color, update):
        restoreHidden = self.checkHidden(name, True)
        self.e[name]['window'].bkgd(0, self.TEXT_COLORS[color])
        self.e[name]['window'].attrset(self.TEXT_COLORS[color])
        self.e[name]['window'].noutrefresh()
        if update:
            self.e[name]['window'].refresh()
        if restoreHidden:
            self.checkHidden(name, False)

    @staticmethod
    def blank(length):
        return ' '*length

    @staticmethod
    def refreshPanels():
        curses.panel.update_panels()
        curses.doupdate()

    def putText(self, elementName, y, x, text, color, refresh):
        restoreHidden = self.checkHidden(elementName, True)
        if color:
            try:
                self.e[elementName]['window'].addstr(y, x, text, self.TEXT_COLORS[color])
            except:
                pass
        else:
            try:
                self.e[elementName]['window'].addstr(y, x, text)
            except:
                pass
        if refresh:
            self.e[elementName]['window'].refresh()
        if restoreHidden:
            self.checkHidden(elementName, False)

    def putChar(self, elementName, y, x, character, color, refresh):
        restoreHidden = self.checkHidden(elementName, True)
        if color:
            try:
                self.e[elementName]['window'].addch(y, x, character, self.TEXT_COLORS[color])
            except:
                pass
        else:
            try:
                self.e[elementName]['window'].addch(y, x, character)
            except:
                pass
        if refresh:
            self.e[elementName]['window'].refresh()
        else:
            self.e[elementName]['window'].noutrefresh()
        if restoreHidden:
            self.checkHidden(elementName, False)



    ################################################################

    def closeWindow(self, window):
        if window == 'lobby':
            for element in self.DIR_LOBBY:
                self.e[element]['panel'].hide()
        elif window == 'title':
            for element in self.DIR_TITLE:
                self.e[element]['panel'].hide()
        elif window == 'hand':
            for element in self.DIR_HAND:
                self.e[element]['panel'].hide()
        elif window == 'match':
            for element in self.DIR_MATCH:
                self.e[element]['panel'].hide()
        elif window == 'mode':
            for element in self.DIR_MODE:
                self.e[element]['panel'].hide()
        elif window == 'settings':
            for element in self.DIR_SETTINGS:
                self.e[element]['panel'].hide()
        UI.refreshPanels()

    def console(self, title, text, warning=False):
        color = 'yellow'
        if warning:
            color = 'red'
        if title:
            restoreHidden = self.checkHidden('title', True)
            self.e['title']['window'].addstr(5, 1, ' ' * 68)
            self.e['title']['window'].addstr(5, 1, text, self.TEXT_COLORS[color])
            self.e['title']['window'].refresh()
            if restoreHidden:
                self.checkHidden('title', False)
        else:
            restoreHidden = self.checkHidden('modeWindow', True)
            self.e['modeWindow']['window'].addstr(6, 1, ' ' * 34)
            self.e['modeWindow']['window'].addstr(6, 1, text, self.TEXT_COLORS[color])
            self.e['modeWindow']['window'].refresh()
            if restoreHidden:
                self.checkHidden('modeWindow', False)

    def getInput(self):
        curses.flushinp()
        k = self.e['main']['window'].getch()
        return k

    def getLineText(self, elementName, y, x, length, color=None):
        curses.curs_set(1)
        element = self.e[elementName]['window']
        element.move(y, x)
        element.refresh()
        text = []
        c = self.getInput()
        while chr(c) != '\n':
            if c not in UI.IGNORE_INPUT and len(text) < length:
                text.append(chr(c))
            elif c == 127 and len(text) > 0:
                text.pop()
            for i, character in enumerate(text):
                self.putChar(elementName, y, x + i, character, color, False)
            element.move(y, x+len(text))
            element.refresh()
            c = self.getInput()
            self.putText(elementName, y, x, UI.blank(length), None, False)
        curses.curs_set(0)
        text = ''.join(text)
        self.putText(elementName, y, x, UI.blank(length), None, True)
        if text is '' or text.replace(' ','') is '':
            return True, ''
        return True, text

    def openWindow(self, window):
        if window == 'lobby':
            for element in self.DIR_LOBBY:
                self.e[element]['panel'].show()
        elif window == 'title':
            for element in self.DIR_TITLE:
                self.e[element]['panel'].show()
        elif window == 'hand':
            for element in self.DIR_HAND:
                self.e[element]['panel'].show()
        elif window == 'match':
            for element in self.DIR_MATCH:
                self.e[element]['panel'].show()
        elif window == 'mode':
            for element in self.DIR_MODE:
                self.e[element]['panel'].show()
        elif window == 'settings':
            for element in self.DIR_SETTINGS:
                self.e[element]['panel'].show()
        self.e['controls']['panel'].show()
        self.e['controls']['panel'].top()
        UI.refreshPanels()

    def prepareJoinButton(self, phase):
        if phase == 'getIP':
            self.updateButtons('mode', -1, {'labels': [
                {'name': 'buttonNetworkJoin', 'start': 0, 'length': 32, 'label': 'Host IP:'},
            ], 'pressed':[2]
            })
        elif phase == 'connecting':
            self.updateButtons('mode', -1, {'labels': [
                {'name': 'buttonNetworkJoin', 'start': 10, 'length': 32, 'label': 'Connecting X'},
            ], 'pressed': [2]
            })
        elif phase == 'waiting':
            self.updateButtons('mode', -1, {'labels': [
                {'name': 'buttonNetworkJoin', 'start': 9, 'length': 32, 'label': 'Joining Game...'},
            ], 'pressed': [2]
            })
        elif phase == 'finished':
            self.updateButtons('mode', 2, {'active':[0,1,2,3], 'labels': [
                {'name': 'buttonNetworkJoin', 'start': 8, 'length': 32, 'label': 'Join Multiplayer'},
            ],
            })


    def updateButtons(self, group, pointer, data=None):
        # data = {'active':[], 'labels':[{'name':str, 'start':int, 'length':int, 'label':str}], pressed:[]}

        grp = UI.BUT_MAP[group]
        for i, e in enumerate(grp):
            self.colorWindow(e,'gray',False)
        if data is not None:
            if 'active' in data:
                for a in data['active']:
                    name = grp[a]
                    if name == 'buttonStart':
                        self.colorWindow(name, 'blue', False)
                    else:
                        self.colorWindow(name, 'white', False)
            if 'labels' in data:
                for l in data['labels']:
                    name = l['name']
                    start = l['start']
                    label = l['label']
                    length = l['length']
                    restoreHidden = self.checkHidden(name, False)
                    if group == 'settings':
                        try:
                            self.e[name]['window'].addstr(0, 0, ' ' * int(length))
                        except:
                            pass
                        self.e[name]['window'].addstr(0, start + 1, str(label))
                    else:
                        self.e[name]['window'].addstr(1, 1, ' ' * int(length))
                        self.e[name]['window'].addstr(1, start + 1, str(label))
                    self.e[name]['window'].noutrefresh()
                    if restoreHidden:
                        self.checkHidden(name, False)
            if 'pressed' in data:
                for a in data['pressed']:
                    name = grp[a]
                    if name == 'buttonNetworkJoin':
                        self.colorWindow(name, 'red', False)
                    else:
                        self.colorWindow(name, 'green', False)
        if pointer >= 0:
            if group == 'settings':
                self.colorWindow(grp[pointer], 'blue', True)
            else:
                self.colorWindow(grp[pointer], 'yellow', True)

        curses.doupdate()

    def updatePlayerStage(self, num, empty, name=None, points=None, searching=False, entering=False, select=False):
        if num is None:
            stageName = 'mainStage'
        else:
            stageName = UI.FRMT_STAGE.format(str(num))
        if not empty:
            if num is not None:
                color = UI.COLORS[num]
            else:
                color = 'blue'
            if select:
                color = 'white'
        else:
            color = 'gray'
            self.e[stageName]['window'].addstr(1, 1, ' ' * 32)
            if searching:
                self.putText(stageName, 1, 1, "Searching", color, True)
            else:
                if not entering:
                    self.putText(stageName, 1, 1, "No Player", color, True)
        self.colorWindow(stageName, color, False)
        #time.sleep(1)
        if name is not None:
            self.putText(stageName, 1, 1, UI.blank(32), None, False)
            self.putText(stageName, 1, 1, name, color, True)
        if points is not None:
            self.putText(stageName, 2, 1, UI.blank(32), None, False)
            self.putText(stageName, 2, 1, 'Points: {}'.format(str(points)), None, True)
        else:
            self.putText(stageName, 2, 1, UI.blank(32), None, True)

    def updateSettings(self, settings):
        # [displayEffects(True,False), computerSpeed(Slow, Normal, Fast), showComputerHands(True, False), Does Nothing
        self.putText('settingsWindow', 4, 8, UI.blank(25), None, False)
        self.putText('settingsWindow', 7, 8, UI.blank(25), None, False)
        self.putText('settingsWindow', 10, 8, UI.blank(25), None, False)
        self.putText('settingsWindow', 13, 8, UI.blank(25), None, False)

        if settings[0] is True:
            self.putText('settingsWindow', 4, 8, 'True', 'green', False)
        else:
            self.putText('settingsWindow', 4, 8, 'False', 'red', False)
        if settings[1] == 'Slow':
            self.putText('settingsWindow', 7, 8, 'Slow', 'red', False)
        elif settings[1] == 'Normal':
            self.putText('settingsWindow', 7, 8, 'Normal', 'yellow', False)
        elif settings[1] == 'Fast':
            self.putText('settingsWindow', 7, 8, 'Fast', 'green', False)
        if settings[2] is True:
            self.putText('settingsWindow', 10, 8, 'True', 'green', False)
        else:
            self.putText('settingsWindow', 10, 8, 'False', 'red', False)
        if settings[3] is True:
            self.putText('settingsWindow', 13, 8, 'True', 'green', True)
        else:
            self.putText('settingsWindow', 13, 8, 'False', 'red', True)

    def twirlSearch(self, num, i):
        stageName = UI.FRMT_STAGE.format(str(num))
        self.putChar(stageName, 1, 11, ' ', None, False)
        if i is not None:
            ch = UI.TWIRL[i]
            self.putChar(stageName, 1, 11, ch, None, False)

    def twirlConnect(self, i):
        self.putChar('buttonNetworkJoin', 1, 22, ' ', None, False)
        if i is not None:
            ch = UI.TWIRL[i]
            self.putChar('buttonNetworkJoin', 1, 22, ch, None, True)