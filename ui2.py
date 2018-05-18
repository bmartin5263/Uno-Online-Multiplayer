import curses
import curses.panel
from enum import Enum

class Elements(Enum):
    MAIN = 0
    TITLE = 1
    WINDOW_MODE = 2
    MAIN_STAGE = 3
    BUTTON_LOCAL = 4
    BUTTON_HOST = 5
    BUTTON_JOIN = 6
    BUTTON_EXIT = 7
    WINDOW_LOBBY = 8
    PLAYER_STAGE_0 = 9
    PLAYER_STAGE_1 = 10
    PLAYER_STAGE_2 = 11
    PLAYER_STAGE_3 = 12
    BUTTON_START = 13
    BUTTON_ADD_AI = 14
    BUTTON_SEARCH = 15
    BUTTON_KICK = 16
    BUTTON_CLOSE = 17
    BUTTON_SETTINGS = 18
    WINDOW_SETTINGS = 19
    BUTTON_DISPLAY_EFFECTS = 20
    BUTTON_COMPUTER_SPEED = 21
    BUTTON_SHOW_HANDS = 22
    BUTTON_DOES_NOTHING = 23
    WINDOW_HAND = 24
    WINDOW_MATCH = 25

class Groups(Enum):
    MODE = 0
    LOBBY = 1
    SETTINGS = 3
    DEFAULT = 4
    STAGE = 5

class Colors(Enum):
    BLUE = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    WHITE = 4
    GRAY = 5
    INVERT = 6
    DEEP_RED = 7

class UI:

    ELEMENT_DEFAULTS = {
        Elements.TITLE : {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (0, 0), 'dimensions': (70, 7)},
        Elements.WINDOW_MODE: {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (17, 7), 'dimensions': (36, 21)},
        Elements.MAIN_STAGE: {'border': 'box', 'tether': Elements.WINDOW_MODE, 'color': Colors.BLUE, 'location': (1, 1),
                      'dimensions': (34, 4)},
        Elements.BUTTON_LOCAL: {'border': 'box', 'tether': Elements.WINDOW_MODE, 'color': Colors.WHITE, 'location': (1, 8),
                        'dimensions': (34, 3)},
        Elements.BUTTON_HOST: {'border': 'box', 'tether': Elements.WINDOW_MODE, 'color': Colors.WHITE, 'location': (1, 11),
                       'dimensions': (34, 3)},
        Elements.BUTTON_JOIN: {'border': 'box', 'tether': Elements.WINDOW_MODE, 'color': Colors.WHITE, 'location': (1, 14),
                       'dimensions': (34, 3)},
        Elements.BUTTON_EXIT: {'border': 'box', 'tether': Elements.WINDOW_MODE, 'color': Colors.WHITE, 'location': (1, 17),
                       'dimensions': (34, 3)},
        Elements.WINDOW_LOBBY: {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (0, 6), 'dimensions': (70, 26)},
        Elements.PLAYER_STAGE_0: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.BLUE, 'location': (1, 1),
                         'dimensions': (34, 4)},
        Elements.PLAYER_STAGE_1: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.RED, 'location': (35, 1),
                         'dimensions': (34, 4)},
        Elements.PLAYER_STAGE_2: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.GREEN, 'location': (1, 5),
                         'dimensions': (34, 4)},
        Elements.PLAYER_STAGE_3: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.YELLOW, 'location': (35, 5),
                         'dimensions': (34, 4)},
        Elements.BUTTON_START: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.BLUE, 'location': (1, 10),
                         'dimensions': (34, 3)},
        Elements.BUTTON_ADD_AI: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.WHITE, 'location': (1, 13),
                         'dimensions': (17, 3)},
        Elements.BUTTON_SEARCH: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.WHITE, 'location': (18, 13),
                        'dimensions': (17, 3)},
        Elements.BUTTON_KICK: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.WHITE, 'location': (1, 16),
                        'dimensions': (34, 3)},
        Elements.BUTTON_CLOSE: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.WHITE, 'location': (1, 19),
                       'dimensions': (34, 3)},
        Elements.BUTTON_SETTINGS: {'border': 'box', 'tether': Elements.WINDOW_LOBBY, 'color': Colors.WHITE, 'location': (1, 22),
                       'dimensions': (34, 3)},
        Elements.WINDOW_SETTINGS: {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (35, 16), 'dimensions': (34, 15)},
        Elements.BUTTON_DISPLAY_EFFECTS: {'border': None, 'tether': Elements.WINDOW_SETTINGS, 'color': Colors.WHITE, 'location': (1, 3),
                           'dimensions': (32, 1)},
        Elements.BUTTON_COMPUTER_SPEED: {'border': None, 'tether': Elements.WINDOW_SETTINGS, 'color': Colors.WHITE, 'location': (1, 6),
                                 'dimensions': (32, 1)},
        Elements.BUTTON_SHOW_HANDS: {'border': None, 'tether': Elements.WINDOW_SETTINGS, 'color': Colors.WHITE, 'location': (1, 9),
                                 'dimensions': (32, 1)},
        Elements.BUTTON_DOES_NOTHING: {'border': None, 'tether': Elements.WINDOW_SETTINGS, 'color': Colors.WHITE, 'location': (1, 12),
                                 'dimensions': (32, 1)},
    }

    GROUPS = {
        Groups.LOBBY : (Elements.WINDOW_LOBBY, Elements.PLAYER_STAGE_0, Elements.PLAYER_STAGE_1, Elements.PLAYER_STAGE_2, Elements.PLAYER_STAGE_3, Elements.BUTTON_START,
                   Elements.BUTTON_ADD_AI, Elements.BUTTON_SEARCH, Elements.BUTTON_KICK, Elements.BUTTON_CLOSE, Elements.BUTTON_SETTINGS),
        Groups.MODE : (Elements.WINDOW_MODE, Elements.MAIN_STAGE, Elements.BUTTON_LOCAL, Elements.BUTTON_HOST, Elements.BUTTON_JOIN, Elements.BUTTON_EXIT),
        Groups.DEFAULT : (Elements.TITLE,),
        Groups.SETTINGS : (Elements.WINDOW_SETTINGS, Elements.BUTTON_DISPLAY_EFFECTS, Elements.BUTTON_COMPUTER_SPEED, Elements.BUTTON_SHOW_HANDS,
                      Elements.BUTTON_DOES_NOTHING)
    }

    BUTTON_GROUPS = {
        Groups.MODE : (Elements.BUTTON_LOCAL, Elements.BUTTON_HOST, Elements.BUTTON_JOIN, Elements.BUTTON_EXIT),
        Groups.LOBBY : (Elements.BUTTON_START, Elements.BUTTON_ADD_AI, Elements.BUTTON_SEARCH, Elements.BUTTON_KICK, Elements.BUTTON_CLOSE, Elements.BUTTON_SETTINGS),
        Groups.SETTINGS : (Elements.BUTTON_DISPLAY_EFFECTS, Elements.BUTTON_COMPUTER_SPEED, Elements.BUTTON_SHOW_HANDS, Elements.BUTTON_DOES_NOTHING)
    }

    COLORS = (Colors.BLUE, Colors.RED, Colors.GREEN, Colors.YELLOW)
    TWIRL = ('|', '/', '-', '\\')
    STAGES = (Elements.PLAYER_STAGE_0, Elements.PLAYER_STAGE_1, Elements.PLAYER_STAGE_2, Elements.PLAYER_STAGE_3)

    def __init__(self, screen):

        self.directory = None
        self.currentHand = None
        self.currentCard = -1

        self.e = {
            Elements.MAIN : {'window': screen, 'panel': None, 'location': (0,0)},
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
            Colors.WHITE: curses.color_pair(1),
            Colors.BLUE: curses.color_pair(2),
            Colors.RED: curses.color_pair(3),
            Colors.GREEN: curses.color_pair(4),
            Colors.YELLOW: curses.color_pair(5),
            Colors.INVERT: curses.color_pair(6),
            Colors.GRAY: curses.color_pair(11),
            Colors.DEEP_RED: curses.color_pair(12)
        }

        self.BACK_COLORS = {
            Colors.BLUE: curses.color_pair(7),
            Colors.RED: curses.color_pair(8),
            Colors.GREEN: curses.color_pair(9),
            Colors.YELLOW: curses.color_pair(10),
        }

        for e in UI.ELEMENT_DEFAULTS:
            self._createElement(e)

        self._initializeElements()
        self.openGroup(Groups.DEFAULT)

        self.clearStage(0)
        self.clearStage(1)
        self.clearStage(2)
        self.clearStage(3)

        #self.openGroup(Groups.LOBBY)
        #self.openGroup(Groups.SETTINGS)
        #self.openGroup(Groups.MODE)

    @staticmethod
    def blank(length):
        return ' ' * length

    def getInput(self):
        curses.flushinp()
        k = self.e[Elements.MAIN]['window'].getch()
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
            window.attrset(self.TEXT_COLORS[Colors.INVERT])
        else:
            window.bkgd(ord(' ') | curses.color_pair(1))
            window.attrset(self.TEXT_COLORS[color])
        if border == 'box':
            if element == Elements.TITLE:
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_ULCORNER,
                              curses.ACS_URCORNER, curses.ACS_LTEE, curses.ACS_RTEE)
            elif element in (Elements.WINDOW_LOBBY, Elements.WINDOW_HAND):
                window.border(curses.ACS_VLINE, curses.ACS_VLINE, curses.ACS_HLINE, curses.ACS_HLINE,
                              curses.ACS_LTEE,
                              curses.ACS_RTEE, curses.ACS_LLCORNER, curses.ACS_LRCORNER)
            elif element == Elements.WINDOW_MATCH:
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
        self._putText(Elements.TITLE, 25, 1, "|| ||", Colors.BLUE)
        self._putText(Elements.TITLE, 31, 1, "||\\ ||", Colors.GREEN)
        self._putText(Elements.TITLE, 39, 1, "// \\\\", Colors.RED)
        self._putText(Elements.TITLE, 25, 2, "|| ||", Colors.BLUE)
        self._putText(Elements.TITLE, 31, 2, "||\\\\||", Colors.GREEN)
        self._putText(Elements.TITLE, 38, 2, "((   ))", Colors.RED)
        self._putText(Elements.TITLE, 25, 3, "\\\\ //", Colors.BLUE)
        self._putText(Elements.TITLE, 31, 3, "|| \\||", Colors.GREEN)
        self._putText(Elements.TITLE, 39, 3, "\\\\ //", Colors.RED)
        self._putChar(Elements.TITLE, 0, 4, curses.ACS_LTEE, Colors.WHITE)

        for i in range(1, 69):
            self._putChar(Elements.TITLE, i, 4, curses.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.TITLE, 69, 4, curses.ACS_RTEE, Colors.WHITE)

        self._putChar(Elements.WINDOW_LOBBY, 0, 9, curses.ACS_LTEE, Colors.WHITE)
        for i in range(1, 69):
            self._putChar(Elements.WINDOW_LOBBY, i, 9, curses.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_LOBBY, 69, 9, curses.ACS_RTEE, Colors.WHITE)

        """
        self.putChar('handWindow', 0, 2, curses.ACS_LTEE, Colors.WHITE, False)
        for i in range(1, 69):
            self.putChar('handWindow', i, 2, curses.ACS_HLINE, Colors.WHITE, False)
        self.putChar('handWindow', 69, 2, curses.ACS_RTEE, Colors.WHITE, True)
        """

        self._putChar(Elements.WINDOW_MODE, 0, 5, curses.ACS_LTEE, Colors.WHITE)
        self._putChar(Elements.WINDOW_MODE, 0, 7, curses.ACS_LTEE, Colors.WHITE)
        for i in range(1, 35):
            self._putChar(Elements.WINDOW_MODE, i, 5, curses.ACS_HLINE, Colors.WHITE)
            self._putChar(Elements.WINDOW_MODE, i, 7, curses.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_MODE, 35, 5, curses.ACS_RTEE, Colors.WHITE)
        self._putChar(Elements.WINDOW_MODE, 0, 7, curses.ACS_LTEE, Colors.WHITE)

        self._putText(Elements.WINDOW_SETTINGS, 13, 1, "Settings", Colors.WHITE)
        self._putChar(Elements.WINDOW_SETTINGS, 0, 2, curses.ACS_LTEE, Colors.WHITE)
        for i in range(1, 33):
            self._putChar(Elements.WINDOW_SETTINGS, i, 2, curses.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_SETTINGS, 33, 2, curses.ACS_RTEE, Colors.WHITE)

        data = {
            Elements.BUTTON_START: {'start': 11, 'length': 32, 'label': 'Start Game', 'active': False, 'color': None},
            Elements.BUTTON_ADD_AI: {'start': 5, 'length': 15, 'label': 'Add AI', 'active': False, 'color': None},
            Elements.BUTTON_SEARCH: {'start': 4, 'length': 15, 'label': 'Search', 'active': False, 'color': None},
            Elements.BUTTON_KICK: {'start': 11, 'length': 32, 'label': 'Kick Player', 'active': False, 'color': None},
            Elements.BUTTON_CLOSE: {'start': 11, 'length': 32, 'label': 'Close Room', 'active': False, 'color': None},
            Elements.BUTTON_SETTINGS: {'start': 12, 'length': 32, 'label': 'Settings', 'active': False, 'color': None},
        }

        sdata = {
            Elements.BUTTON_DISPLAY_EFFECTS : {'start':0, 'length': 32, 'label': '- Display Effects', 'active': False, 'color': None},
            Elements.BUTTON_COMPUTER_SPEED : {'start': 0, 'length': 32, 'label': '- Computer Speed', 'active': False, 'color': None},
            Elements.BUTTON_SHOW_HANDS : {'start': 0, 'length': 32, 'label': '- Show Computer Hands', 'active': False, 'color': None},
            Elements.BUTTON_DOES_NOTHING : {'start': 0, 'length': 32, 'label': '- Does Nothing', 'active': False, 'color': None},
        }

        self.updateButtons(data)
        self.updateSettingButtons(sdata)
        self.updateSettings([True, 'Normal', False, False])

        curses.doupdate()

        for element in self.e:
            if element != Elements.MAIN:
                self.e[element]['panel'].hide()

        UI._updatePanels()

    def _console(self, title, text, warning=False):
        color = Colors.YELLOW
        if warning:
            color = Colors.RED
        if title:
            self._putText(Elements.TITLE, 1, 5, UI.blank(68), color)
            self._putText(Elements.TITLE, 1, 5, text, color)
        else:
            self._putText(Elements.WINDOW_MODE, 1, 6, UI.blank(34), color)
            self._putText(Elements.WINDOW_MODE, 1, 6, text, color)
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
        self._putText(Elements.PLAYER_STAGE_0, 1, 1, UI.blank(32))
        self._putText(Elements.PLAYER_STAGE_0, 1, 2, UI.blank(32))
        self._putText(Elements.PLAYER_STAGE_0, 1, 1, "Cancel")
        curses.doupdate()

    def clearStage(self, num):
        """Clears the stage of any players"""
        if num < 0:
            stage = Elements.MAIN_STAGE
        else:
            stage = UI.STAGES[num]
        self._colorElement(stage, Colors.GRAY)
        self._putText(stage, 1, 1, UI.blank(32))
        self._putText(stage, 1, 2, UI.blank(32))
        self._putText(stage, 1, 1, "No Player", Colors.GRAY)
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
        """Set stage to for searching. Does not update"""
        stageName = UI.STAGES[num]
        self._putText(stageName, 1, 1, UI.blank(32))
        self._putText(stageName, 1, 2, UI.blank(32))
        self._putText(stageName, 1, 1, "Searching", Colors.GRAY)

    def setButtonPointer(self, directory, num):
        color = Colors.YELLOW
        if directory == Groups.SETTINGS:
            color = Colors.BLUE
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
        self._highlightButton(Elements.BUTTON_SETTINGS, Colors.GREEN)

    def restoreSettings(self):
        self._highlightButton(Elements.BUTTON_SETTINGS, Colors.YELLOW)

    def setStagePointer(self, num):
        """Highlight a stage white."""
        self._colorElement(UI.STAGES[num], Colors.WHITE)
        curses.doupdate()

    def restoreStagePointer(self, num):
        """Return stage to original color"""
        self._colorElement(UI.STAGES[num], None)
        curses.doupdate()

    def setStageWithPlayer(self, num, player):
        """Add Player Details to Lobby Stage. Use -1 for main stage"""
        if num < 0:
            stage = Elements.MAIN_STAGE
        else:
            stage = UI.STAGES[num]
        self._colorElement(stage, None)
        self._putText(stage, 1, 1, UI.blank(32))
        self._putText(stage, 1, 1, player.name)
        self._putText(stage, 1, 2, UI.blank(32))
        self._putText(stage, 1, 2, 'Points: {}'.format(str(player.points)))
        curses.doupdate()

    def twirlSearch(self, num, i):
        stage = UI.STAGES[num]
        self._putChar(stage, 11, 1, ' ', Colors.GRAY)
        if i is not None:
            ch = UI.TWIRL[i]
            self._putChar(stage, 11, 1, ch, Colors.GRAY)

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
                color = Colors.GRAY
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
            color = Colors.WHITE
            self._colorElement(buttonName, color)
            self._putText(buttonName, 0, 0, ' ' * int(length), color)
            self._putText(buttonName, start + 1, 0, label, color)
        curses.doupdate()

    def updateSettings(self, settings):
        # [displayEffects(True,False), computerSpeed(Slow, Normal, Fast), showComputerHands(True, False), Does Nothing
        self._putText(Elements.WINDOW_SETTINGS, 8, 4, UI.blank(25), None)
        self._putText(Elements.WINDOW_SETTINGS, 8, 7, UI.blank(25), None)
        self._putText(Elements.WINDOW_SETTINGS, 8, 10, UI.blank(25), None)
        self._putText(Elements.WINDOW_SETTINGS, 8, 13, UI.blank(25), None)

        if settings[0] is True:
            self._putText(Elements.WINDOW_SETTINGS, 8, 4, 'True', Colors.GREEN)
        else:
            self._putText(Elements.WINDOW_SETTINGS, 8, 4, 'False', Colors.RED)
        if settings[1] == 'Slow':
            self._putText(Elements.WINDOW_SETTINGS, 8, 7, 'Slow', Colors.RED)
        elif settings[1] == 'Normal':
            self._putText(Elements.WINDOW_SETTINGS, 8, 7, 'Normal', Colors.YELLOW)
        elif settings[1] == 'Fast':
            self._putText(Elements.WINDOW_SETTINGS, 8, 7, 'Fast', Colors.GREEN)
        if settings[2] is True:
            self._putText(Elements.WINDOW_SETTINGS, 8, 10, 'True', Colors.GREEN)
        else:
            self._putText(Elements.WINDOW_SETTINGS, 8, 10, 'False', Colors.RED)
        if settings[3] is True:
            self._putText(Elements.WINDOW_SETTINGS, 8, 13, 'True', Colors.GREEN)
        else:
            self._putText(Elements.WINDOW_SETTINGS, 8, 13, 'False', Colors.RED)
        curses.doupdate()

    def warning(self, message):
        """Print a red message to the game's console"""
        self._console(True, message, True)

if __name__ == '__main__':
    pass