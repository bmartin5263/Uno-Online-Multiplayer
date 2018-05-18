import curses
import curses.panel

class UI:

    ELEMENT_DEFAULTS = {
        'title': {'border': 'box', 'tether': None, 'color': 'white', 'location': (0, 0), 'dimensions': (70, 7)},
        'windowMode': {'border': 'box', 'tether': None, 'color': 'white', 'location': (17, 7), 'dimensions': (36, 21)},
        'mainStage': {'border': 'box', 'tether': "windowMode", 'color': 'blue', 'location': (1, 1),
                      'dimensions': (34, 4)},
        'buttonLocal': {'border': 'box', 'tether': "windowMode", 'color': 'white', 'location': (1, 8),
                        'dimensions': (34, 3)},
        'buttonHost': {'border': 'box', 'tether': "windowMode", 'color': 'white', 'location': (1, 11),
                       'dimensions': (34, 3)},
        'buttonJoin': {'border': 'box', 'tether': "windowMode", 'color': 'white', 'location': (1, 14),
                       'dimensions': (34, 3)},
        'buttonExit': {'border': 'box', 'tether': "windowMode", 'color': 'white', 'location': (1, 17),
                       'dimensions': (34, 3)},
        'windowLobby': {'border': 'box', 'tether': None, 'color': 'white', 'location': (0, 6), 'dimensions': (70, 26)},
        'playerStage0': {'border': 'box', 'tether': "windowLobby", 'color': 'blue', 'location': (1, 1),
                         'dimensions': (34, 4)},
        'playerStage1': {'border': 'box', 'tether': "windowLobby", 'color': 'red', 'location': (35, 1),
                         'dimensions': (34, 4)},
        'playerStage2': {'border': 'box', 'tether': "windowLobby", 'color': 'green', 'location': (1, 5),
                         'dimensions': (34, 4)},
        'playerStage3': {'border': 'box', 'tether': "windowLobby", 'color': 'yellow', 'location': (35, 5),
                         'dimensions': (34, 4)},
        'buttonStart': {'border': 'box', 'tether': "windowLobby", 'color': 'blue', 'location': (1, 10),
                         'dimensions': (34, 3)},
        'buttonAddAI': {'border': 'box', 'tether': "windowLobby", 'color': 'white', 'location': (1, 13),
                         'dimensions': (17, 3)},
        'buttonSearch': {'border': 'box', 'tether': "windowLobby", 'color': 'white', 'location': (18, 13),
                        'dimensions': (17, 3)},
        'buttonKick': {'border': 'box', 'tether': "windowLobby", 'color': 'white', 'location': (1, 16),
                        'dimensions': (34, 3)},
        'buttonClose': {'border': 'box', 'tether': "windowLobby", 'color': 'white', 'location': (1, 19),
                       'dimensions': (34, 3)},
        'buttonSettings': {'border': 'box', 'tether': "windowLobby", 'color': 'white', 'location': (1, 22),
                       'dimensions': (34, 3)},
        'windowSettings': {'border': 'box', 'tether': None, 'color': 'white', 'location': (35, 16), 'dimensions': (34, 15)},
        'buttonDisplayEffects': {'border': None, 'tether': "windowSettings", 'color': 'white', 'location': (1, 3),
                           'dimensions': (32, 1)},
        'buttonComputerSpeed': {'border': None, 'tether': "windowSettings", 'color': 'white', 'location': (1, 6),
                                 'dimensions': (32, 1)},
        'buttonShowHands': {'border': None, 'tether': "windowSettings", 'color': 'white', 'location': (1, 9),
                                 'dimensions': (32, 1)},
        'buttonDoesNothing': {'border': None, 'tether': "windowSettings", 'color': 'white', 'location': (1, 12),
                                 'dimensions': (32, 1)},
    }

    GROUPS = {
        'lobby' : ('windowLobby', 'playerStage0', 'playerStage1', 'playerStage2', 'playerStage3', 'buttonStart',
                   'buttonAddAI', 'buttonSearch', 'buttonKick', 'buttonClose', 'buttonSettings'),
        'mode' : ('windowMode', 'mainStage', 'buttonLocal', 'buttonHost', 'buttonJoin', 'buttonExit'),
        'default' : ('title',),
        'settings' : ('windowSettings', 'buttonDisplayEffects', 'buttonComputerSpeed', 'buttonShowHands',
                      'buttonDoesNothing')
    }

    BUTTON_GROUPS = {
        'mode' : ('buttonLocal', 'buttonHost', 'buttonJoin', 'buttonExit'),
        'lobby' : ('buttonStart', 'buttonAddAI', 'buttonSearch', 'buttonKick', 'buttonClose', 'buttonSettings'),
        'settings' : ('buttonDisplayEffects', 'buttonComputerSpeed', 'buttonShowHands', 'buttonDoesNothing')
    }

    COLORS = ('blue', 'red', 'green', 'yellow')
    TWIRL = ('|', '/', '-', '\\')

    def __init__(self, screen):

        self.directory = None
        self.currentHand = None
        self.currentCard = -1

        self.e = {
            'main' : {'window': screen, 'panel': None, 'location': (0,0)},
        }

        curses.curs_set(0)
        curses.init_pair(1, 15, curses.COLOR_BLACK)     # white text
        curses.init_pair(2, 39, curses.COLOR_BLACK)     # blue text
        curses.init_pair(3, 199, curses.COLOR_BLACK)    # red text
        curses.init_pair(4, 82, curses.COLOR_BLACK)     # green text
        curses.init_pair(5, 226, curses.COLOR_BLACK)    # yellow text
        curses.init_pair(6, curses.COLOR_BLACK, 15)     # inverted text
        curses.init_pair(7, 39, 17)
        curses.init_pair(8, 199, 52)
        curses.init_pair(9, 82, 22)
        curses.init_pair(10, 226, 58)
        curses.init_pair(11, 8, curses.COLOR_BLACK) # gray
        curses.init_pair(12, 9, curses.COLOR_BLACK) # deep red

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

        for e in UI.ELEMENT_DEFAULTS:
            self._createElement(e)

        self._initializeElements()
        self.openGroup('default')

        self.clearStage(0)
        self.clearStage(1)
        self.clearStage(2)
        self.clearStage(3)

        #self.openGroup('lobby')
        #self.openGroup('settings')
        #self.openGroup('mode')

    @staticmethod
    def blank(length):
        return ' ' * length

    def getInput(self):
        curses.flushinp()
        k = self.e['main']['window'].getch()
        return k

    def _createElement(self, element):
        """Creates an element with initial values."""
        location = UI.ELEMENT_DEFAULTS[element]['location']
        dimensions = UI.ELEMENT_DEFAULTS[element]['dimensions']
        border = UI.ELEMENT_DEFAULTS[element]['border']
        tether = UI.ELEMENT_DEFAULTS[element]['tether']
        color = UI.ELEMENT_DEFAULTS[element]['color']
        if tether is not None:
            tetheredLocation = UI.ELEMENT_DEFAULTS[tether]['location']
            location = (location[0] + tetheredLocation[0], location[1] + tetheredLocation[1])
        window = curses.newwin(dimensions[1], dimensions[0], location[1], location[0])
        if element == 'controls':
            window.bkgd(ord(' ') | curses.color_pair(6))
            window.attrset(self.TEXT_COLORS['invert'])
        else:
            window.bkgd(ord(' ') | curses.color_pair(1))
            window.attrset(self.TEXT_COLORS[color])
        if border == 'box':
            if element == 'title':
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_ULCORNER,
                              curses.ACS_URCORNER, curses.ACS_LTEE, curses.ACS_RTEE)
            elif element in ('windowLobby', 'windowHand'):
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_LTEE,
                              curses.ACS_RTEE, curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            elif element == 'windowMatch':
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_LTEE,
                              curses.ACS_RTEE, curses.ACS_LTEE, curses.ACS_RTEE)
            else:
                window.box()
        panel = curses.panel.new_panel(window)
        self.e[element] = {'window': window, 'panel': panel, 'location': location}

    def _colorElement(self, name, color):
        """Color an element. Does not update"""
        if color is not None:
            c = self.TEXT_COLORS[color]
        else:
            c = self.TEXT_COLORS[UI.ELEMENT_DEFAULTS[name]['color']]
        self.e[name]['window'].bkgd(0, c)
        self.e[name]['window'].attrset(c)
        self.e[name]['window'].noutrefresh()

    def _initializeElements(self):
        """Put initial text and colors to the elements"""
        self._putText('title', 25, 1, "|| ||", 'blue')
        self._putText('title', 31, 1, "||\\ ||", 'green')
        self._putText('title', 39, 1, "// \\\\", 'red')
        self._putText('title', 25, 2, "|| ||", 'blue')
        self._putText('title', 31, 2, "||\\\\||", 'green')
        self._putText('title', 38, 2, "((   ))", 'red')
        self._putText('title', 25, 3, "\\\\ //", 'blue')
        self._putText('title', 31, 3, "|| \\||", 'green')
        self._putText('title', 39, 3, "\\\\ //", 'red')
        self._putChar('title', 0, 4, curses.ACS_LTEE, 'white')

        for i in range(1, 69):
            self._putChar('title', i, 4, curses.ACS_HLINE, 'white')
        self._putChar('title', 69, 4, curses.ACS_RTEE, 'white')

        self._putChar('windowLobby', 0, 9, curses.ACS_LTEE, 'white')
        for i in range(1, 69):
            self._putChar('windowLobby', i, 9, curses.ACS_HLINE, 'white')
        self._putChar('windowLobby', 69, 9, curses.ACS_RTEE, 'white')

        """
        self.putChar('handWindow', 0, 2, curses.ACS_LTEE, 'white', False)
        for i in range(1, 69):
            self.putChar('handWindow', i, 2, curses.ACS_HLINE, 'white', False)
        self.putChar('handWindow', 69, 2, curses.ACS_RTEE, 'white', True)
        """

        self._putChar("windowMode", 0, 5, curses.ACS_LTEE, 'white')
        self._putChar("windowMode", 0, 7, curses.ACS_LTEE, 'white')
        for i in range(1, 35):
            self._putChar("windowMode", i, 5, curses.ACS_HLINE, 'white')
            self._putChar("windowMode", i, 7, curses.ACS_HLINE, 'white')
        self._putChar("windowMode", 35, 5, curses.ACS_RTEE, 'white')
        self._putChar("windowMode", 0, 7, curses.ACS_LTEE, 'white')

        self._putText("windowSettings", 13, 1, "Settings", 'white')
        self._putChar("windowSettings", 0, 2, curses.ACS_LTEE, 'white')
        for i in range(1, 33):
            self._putChar("windowSettings", i, 2, curses.ACS_HLINE, 'white')
        self._putChar("windowSettings", 33, 2, curses.ACS_RTEE, 'white')

        data = {
            'buttonStart': {'start': 11, 'length': 32, 'label': 'Start Game', 'active': False, 'color': None},
            'buttonAddAI': {'start': 5, 'length': 15, 'label': 'Add AI', 'active': False, 'color': None},
            'buttonSearch': {'start': 4, 'length': 15, 'label': 'Search', 'active': False, 'color': None},
            'buttonKick': {'start': 11, 'length': 32, 'label': 'Kick Player', 'active': False, 'color': None},
            'buttonClose': {'start': 11, 'length': 32, 'label': 'Close Room', 'active': False, 'color': None},
            'buttonSettings': {'start': 12, 'length': 32, 'label': 'Settings', 'active': False, 'color': None},
        }

        sdata = {
            'buttonDisplayEffects' : {'start':0, 'length': 32, 'label': '- Display Effects', 'active': False, 'color': None},
            'buttonComputerSpeed' : {'start': 0, 'length': 32, 'label': '- Computer Speed', 'active': False, 'color': None},
            'buttonShowHands' : {'start': 0, 'length': 32, 'label': '- Show Computer Hands', 'active': False, 'color': None},
            'buttonDoesNothing' : {'start': 0, 'length': 32, 'label': '- Does Nothing', 'active': False, 'color': None},
        }

        self.updateButtons(data)
        self.updateSettingButtons(sdata)
        self.updateSettings([True, 'Normal', False, False])

        curses.doupdate()

        for element in self.e:
            if element != 'main':
                self.e[element]['panel'].hide()

        UI._updatePanels()

    def _console(self, title, text, warning=False):
        color = 'yellow'
        if warning:
            color = 'red'
        if title:
            self._putText('title', 1, 5, UI.blank(68), color)
            self._putText('title', 1, 5, text, color)
        else:
            self._putText('modeWindow', 1, 6, UI.blank(34), color)
            self._putText('modeWindow', 1, 6, text, color)
        curses.doupdate()

    def _highlightButton(self, button, color):
        """Colors a button yellow."""
        self._colorElement(button, color)
        curses.doupdate()

    def _restoreButton(self, button):
        """Restore the color of a button to its default."""
        self._colorElement(button, None)
        curses.doupdate()

    def _lowerCard(self, index):
        """Lower Card, Restoring its Border Color"""

    def _putChar(self, elementName, x, y, character, color=None):
        window = self.e[elementName]['window']
        if color is not None:
            color = self.TEXT_COLORS[color]
        else:
            color = self.TEXT_COLORS[UI.ELEMENT_DEFAULTS[elementName]['color']]
        try:
            window.addch(y, x, character, color)
        except:
            pass
        window.noutrefresh()

    def _putText(self, elementName, x, y, text, color=None):
        """Places text at an element at a location defined by (x,y). Does not update."""
        #restoreHidden = self.checkHidden(elementName, True)
        window = self.e[elementName]['window']
        if color is not None:
            color = self.TEXT_COLORS[color]
        else:
            color = self.TEXT_COLORS[UI.ELEMENT_DEFAULTS[elementName]['color']]
        try:
            window.addstr(y, x, text, color)
        except:
            pass
        window.noutrefresh()

    def _raiseCard(self, index):
        """Raise Card, Setting its Border to White"""

    def _twirlSearch(self, num, phase):
        """Spins search wheel at specified stage using current phase char"""

    @staticmethod
    def _updatePanels():
        curses.panel.update_panels()
        curses.doupdate()

    def cancelStage(self):
        """Set text of stage 0 to 'cancel' for use in kicking players"""
        self._putText('playerStage0', 1, 1, UI.blank(32))
        self._putText('playerStage0', 1, 2, UI.blank(32))
        self._putText('playerStage0', 1, 1, "Cancel")
        curses.doupdate()

    def clearStage(self, num):
        """Clears the stage of any players"""
        if num < 0:
            stageName = 'mainStage'
        else:
            stageName = "playerStage" + str(num)
        self._colorElement(stageName, "gray")
        self._putText(stageName, 1, 1, UI.blank(32))
        self._putText(stageName, 1, 2, UI.blank(32))
        self._putText(stageName, 1, 1, "No Player", "gray")
        curses.doupdate()

    def closeGroup(self, group):
        for element in UI.GROUPS[group]:
            self.e[element]['panel'].hide()
        UI._updatePanels()

    def console(self, message):
        """Print a yellow message to game's console"""
        self._console(True, message, False)

    def modeConsole(self, message):
        self._console(False, message, False)

    def modeWarning(self, message):
        self._console(False, message, True)

    def openGroup(self, group):
        for element in UI.GROUPS[group]:
            self.e[element]['panel'].show()
        UI._updatePanels()

    def resetButtonPointer(self, directory, num):
        self._restoreButton(UI.BUTTON_GROUPS[directory][num])

    def searchStage(self, num):
        """Set stage to for searching."""

    def setButtonPointer(self, directory, num):
        color = 'yellow'
        if directory == 'settings':
            color = 'blue'
        self._highlightButton(UI.BUTTON_GROUPS[directory][num], color)

    def setCardPointer(self, index):
        """Lower the current card, Raise the card specified by index."""

    def setDeckLength(self, num):
        """Sets length of deck to num"""

    def setHand(self, hand):
        """Sets the current hand in UI memory to the hand provided and draws it."""

    def showHand(self, offset):
        """Show the hand at the offset provided"""

    def pressSettings(self):
        self._highlightButton("buttonSettings", "green")

    def restoreSettings(self):
        self._highlightButton("buttonSettings", "yellow")

    def setStagePointer(self, num):
        """Highlight a stage white."""
        self._colorElement("playerStage"+str(num), "white")
        curses.doupdate()

    def restoreStagePointer(self, num):
        """Return stage to original color"""
        self._colorElement("playerStage" + str(num), None)
        curses.doupdate()

    def setStageWithPlayer(self, num, player):
        """Add Player Details to Lobby Stage. Use -1 for main stage"""
        if num < 0:
            stageName = 'mainStage'
        else:
            stageName = "playerStage" + str(num)
        self._colorElement(stageName, None)
        self._putText(stageName, 1, 1, UI.blank(32))
        self._putText(stageName, 1, 1, player.name)
        self._putText(stageName, 1, 2, UI.blank(32))
        self._putText(stageName, 1, 2, 'Points: {}'.format(str(player.points)))
        curses.doupdate()


    def updateButtons(self, data):
        """Updates buttons based on data (text, color, etc)"""
        for buttonName in data:
            innerData = data[buttonName]
            start = innerData['start']
            label = innerData['label']
            length = innerData['length']
            active = innerData['active']
            color = innerData['color']
            if not active:
                color = 'gray'
            else:
                if color is None:
                    color = UI.ELEMENT_DEFAULTS[buttonName]['color']
            self._colorElement(buttonName, color)
            self._putText(buttonName, 1, 1, ' ' * int(length), color)
            self._putText(buttonName, start + 1, 1, label, color)
        curses.doupdate()

    def updateSettingButtons(self, data):
        for buttonName in data:
            innerData = data[buttonName]
            start = innerData['start']
            label = innerData['label']
            length = innerData['length']
            color = "white"
            self._colorElement(buttonName, color)
            self._putText(buttonName, 0, 0, ' ' * int(length), color)
            self._putText(buttonName, start + 1, 0, label, color)
        curses.doupdate()

    def updateSettings(self, settings):
        # [displayEffects(True,False), computerSpeed(Slow, Normal, Fast), showComputerHands(True, False), Does Nothing
        self._putText('windowSettings', 8, 4, UI.blank(25), None)
        self._putText('windowSettings', 8, 7, UI.blank(25), None)
        self._putText('windowSettings', 8, 10, UI.blank(25), None)
        self._putText('windowSettings', 8, 13, UI.blank(25), None)

        if settings[0] is True:
            self._putText('windowSettings', 8, 4, 'True', 'green')
        else:
            self._putText('windowSettings', 8, 4, 'False', 'red')
        if settings[1] == 'Slow':
            self._putText('windowSettings', 8, 7, 'Slow', 'red')
        elif settings[1] == 'Normal':
            self._putText('windowSettings', 8, 7, 'Normal', 'yellow')
        elif settings[1] == 'Fast':
            self._putText('windowSettings', 8, 7, 'Fast', 'green')
        if settings[2] is True:
            self._putText('windowSettings', 8, 10, 'True', 'green')
        else:
            self._putText('windowSettings', 8, 10, 'False', 'red')
        if settings[3] is True:
            self._putText('windowSettings', 8, 13, 'True', 'green')
        else:
            self._putText('windowSettings', 8, 13, 'False', 'red')
        curses.doupdate()

    def warning(self, message):
        """Print a red message to the game's console"""
        self._console(True, message, True)

if __name__ == '__main__':
    pass