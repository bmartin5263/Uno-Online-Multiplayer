import curses
import curses.panel

class UI:

    ELEMENT_DEFAULTS = {
        'title': {'border': 'box', 'tether': None, 'color': 'white', 'location': (0, 0), 'dimensions': (70, 7)},
        'windowMode': {'border': 'box', 'tether': None, 'color': 'white', 'location': (17, 7), 'dimensions': (36, 21)},
        'mainStage': {'border': 'box', 'tether': "windowMode", 'color': 'white', 'location': (1, 1),
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
        self._openGroup('default')
        self._openGroup('lobby')
        self._openGroup('settings')
        self._openGroup('mode')

    def _createElement(self, element):
        """Creates an element with initial values."""
        #name = UI.ELEMENT_DEFAULTS[element]['name']
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
            window.attrset(self.TEXT_COLORS['white'])
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

    def _colorElement(self, color):
        """Color an element."""

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

        curses.doupdate()

        for element in self.e:
            if element != 'main':
                self.e[element]['panel'].hide()

        UI._updatePanels()

    def _closeGroup(self, group):
        for element in UI.GROUPS:
            self.e[element]['panel'].hide()
        UI._updatePanels()


    def _lowerCard(self, index):
        """Lower Card, Restoring its Border Color"""

    def _openGroup(self, group):
        for element in UI.GROUPS[group]:
            self.e[element]['panel'].show()
        UI._updatePanels()

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

    def clearStage(self, num):
        """Clears the stage of any players"""

    def console(self, message):
        """Print a yellow message to game's console"""

    def highlightButton(self, button):
        """Colors a button yellow."""

    def restoreButton(self, button):
        """Restore the color of a button to its default."""

    def searchStage(self, num):
        """Set stage to for searching."""

    def setCardPointer(self, index):
        """Lower the current card, Raise the card specified by index."""

    def setDeckLength(self, num):
        """Sets length of deck to num"""

    def setDirectory(self, directory):
        """Sets the directory and reveals all of its elements"""

    def setHand(self, hand):
        """Sets the current hand in UI memory to the hand provided and draws it."""

    def showHand(self, offset):
        """Show the hand at the offset provided"""

    def setStageWithPlayer(self, num, player):
        """Add Player Details to Lobby Stage. Use -1 for main stage"""

    def updateButtons(self, data):
        """Updates buttons based on data (text, color, etc)"""

    def warning(self, message):
        """Print a red message to the game's console"""

if __name__ == '__main__':
    pass