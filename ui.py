import curses
import curses.panel
import _curses
import math
from enum import Enum
import time

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
    TOP_CARD = 26
    BELOW_CARD = 27
    DECK_METER = 28
    DECK_COUNT = 29
    CARD_0 = 30
    CARD_1 = 31
    CARD_2 = 32
    CARD_3 = 33
    CARD_4 = 34
    CARD_5 = 35
    CARD_6 = 36
    CARD_7 = 37
    CARD_8 = 38
    CARD_9 = 39
    CARD_10 = 40
    CARD_11 = 41
    CARD_12 = 42
    CARD_13 = 43
    PLAYER_TILE_0 = 44
    PLAYER_TILE_1 = 45
    PLAYER_TILE_2 = 46
    PLAYER_TILE_3 = 47
    NEXT_CARD = 48
    PREV_CARD = 49


class Groups(Enum):
    MODE = 0
    LOBBY = 1
    SETTINGS = 3
    DEFAULT = 4
    STAGE = 5
    MATCH = 6

class Colors(Enum):
    BLUE = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    WHITE = 4
    GRAY = 5
    INVERT = 6
    DEEP_RED = 7
    WILD = 8

class UI:

    TRANSLATE_COLOR = {
        'blue' : Colors.BLUE,
        'red' : Colors.RED,
        'green' : Colors.GREEN,

    }

    IGNORE_INPUT = (127, 260, 259, 261, 258)

    BIG_NUMBERS = {'0': ["  .d8888b.  ", " d88P  Y88b ", " 888    888 ", " 888    888 ", " 888    888 ", " 888    888 ",
                         " Y88b  d88P ", '  "Y8888P"  '],
                   '1': ['   .d888    ', '  d88888    ', '    8888    ', '    8888    ', '    8888    ', '    8888    ',
                         '    8888    ', '  88888888  '],
                   '2': ['  .d8888b.  ', ' d88P  Y88b ', '        888 ', '      .d88P ', '  .od888P"  ', ' d88P"      ',
                         ' 888"       ', ' 8888888888 '],
                   '3': ['  .d8888b.  ', ' d88P  Y88b ', '      .d88P ', '     8888"  ', '      "Y8b. ', ' 888    888 ',
                         ' Y88b  d88P ', '  "Y8888P"  '],
                   '4': ['     d8888  ', '    d8P888  ', '   d8P 888  ', '  d8P  888  ', ' d88   888  ', ' 8888888888 ',
                         '       888  ', '       888  '],
                   '5': [' 8888888888 ', ' 888        ', ' 888        ', ' 8888888b.  ', '      "Y88b ', '        888 ',
                         ' Y88b  d88P ', '  "Y8888P"  '],
                   '6': ['  .d8888b.  ', ' d88P  Y88b ', ' 888        ', ' 888d888b.  ', ' 888P "Y88b ', ' 888    888 ',
                         ' Y88b  d88P ', '  "Y8888P"  '],
                   '7': [' 8888888888 ', '       d88P ', '      d88P  ', '     d88P   ', '  88888888  ', '   d88P     ',
                         '  d88P      ', ' d88P       '],
                   '8': ['  .d8888b.  ', ' d88P  Y88b ', ' Y88b. d88P ', '  "Y88888"  ', ' .d8P""Y8b. ', ' 888    888 ',
                         ' Y88b  d88P ', '  "Y8888P"  '],
                   '9': ['  .d8888b.  ', ' d88P  Y88b ', ' 888    888 ', ' Y88b. d888 ', '  "Y888P888 ', '        888 ',
                         ' Y88b  d88P ', '  "Y8888P"  '],
                   'X': [' Y8b    d8P ', '  Y8b  d8P  ', '   Y8888P   ', '    Y88P    ', '    d88b    ', '   d8888b   ',
                         '  d8P  Y8b  ', ' d8P    Y8b '],

                   'R9': ['     d88P   ', '    d88P    ', '   d88P     ', '  d88P      ', '  Y88b     ', '   Y88b     ',
                          '    Y88b    ', '     Y88b   '],

                   'R8': ['    d88P   Y', '   d88P     ', '  d88P      ', ' d88P       ', ' Y88b       ',
                          '  Y88b      ',
                          '   Y88b     ', '    Y88b   d'],

                   'R7': ['   d88P   Y8', '  d88P     Y', ' d88P       ', 'd88P        ', 'Y88b        ',
                          ' Y88b       ',
                          '  Y88b     d', '   Y88b   d8'],

                   'R6': ['  d88P   Y88', ' d88P     Y8', 'd88P       Y', '88P         ', '88b         ',
                          'Y88b       d',
                          ' Y88b     d8', '  Y88b   d88'],

                   'R5': [' d88P   Y88b', 'd88P     Y88', '88P       Y8', '8P         Y', '8b         d',
                          '88b       d8',
                          'Y88b     d88', ' Y88b   d88P'],

                   'R4': ['d88P   Y88b ', '88P     Y88b', '8P       Y88', 'P         Y8', 'b         d8',
                          '8b       d88',
                          '88b     d88P', 'Y88b   d88P '],

                   'R3': ['88P   Y88b  ', '8P     Y88b ', 'P       Y88b', '         Y88', '         d88',
                          'b       d88P',
                          '8b     d88P ', '88b   d88P  '],

                   'R2': ['8P   Y88b   ', 'P     Y88b  ', '       Y88b ', '        Y88b', '        d88P',
                          '       d88P ',
                          'b     d88P  ', '8b   d88P   '],

                   'R1': ['P   Y88b    ', '     Y88b   ', '      Y88b  ', '       Y88b ', '       d88P ',
                          '      d88P  ',
                          '     d88P   ', 'b   d88P    '],

                   'R0': ['   Y88b     ', '    Y88b    ', '     Y88b   ', '      Y88b  ', '      d88P  ',
                          '     d88P   ',
                          '    d88P    ', '   d88P     '],

                   'W': [' 88      88 ', ' 88      88 ', ' 88  db  88 ', ' 88 d88b 88 ', ' 88d8888b88 ', ' 88P    Y88 ',
                         ' 8P      Y8 ', ' P        Y '],
                   '+2': ['   db       ', '   88       ', ' C8888D     ', '   88  8888 ', '   VP     8 ',
                          '       8888 ',
                          '       8    ', '       8888 '],
                   '+4': ['   db       ', '   88       ', ' C8888D     ', '   88    d  ', '   VP   d8  ',
                          '       d 8  ',
                          '      d8888 ', '         8  ']
                   }

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
        Elements.WINDOW_MATCH: {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (0, 6), 'dimensions': (70, 18)},
        Elements.WINDOW_HAND: {'border': 'box', 'tether': None, 'color': Colors.WHITE, 'location': (0, 23),
                                       'dimensions': (70, 9)},
        Elements.PREV_CARD: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (2, 4),
                             'dimensions': (4, 4)},
        Elements.CARD_0: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (7, 4),
                               'dimensions': (4, 4)},
        Elements.CARD_1: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (11, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_2: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (15, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_3: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (19, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_4: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (23, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_5: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (27, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_6: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (31, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_7: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (35, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_8: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (39, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_9: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (43, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_10: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (47, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_11: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (51, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_12: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (55, 4),
                          'dimensions': (4, 4)},
        Elements.CARD_13: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (59, 4),
                           'dimensions': (4, 4)},
        Elements.NEXT_CARD: {'border': 'box', 'tether': Elements.WINDOW_HAND, 'color': Colors.WHITE, 'location': (64, 4),
                           'dimensions': (4, 4)},
        Elements.DECK_METER : {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.WHITE, 'location': (2, 5),
                           'dimensions': (5, 11)},
        Elements.DECK_COUNT: {'border': None, 'tether': Elements.WINDOW_MATCH, 'color': Colors.WHITE,
                              'location': (1, 2),
                              'dimensions': (9, 2)},
        Elements.TOP_CARD: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.WHITE,
                              'location': (29, 4),
                              'dimensions': (14, 12)},
        Elements.BELOW_CARD: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.WHITE,
                            'location': (27, 2),
                            'dimensions': (14, 12)},
        Elements.PLAYER_TILE_0: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.BLUE,
                              'location': (55, 1),
                              'dimensions': (14, 4)},
        Elements.PLAYER_TILE_1: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.RED,
                                 'location': (55, 5),
                                 'dimensions': (14, 4)},
        Elements.PLAYER_TILE_2: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.GREEN,
                                 'location': (55, 9),
                                 'dimensions': (14, 4)},
        Elements.PLAYER_TILE_3: {'border': 'box', 'tether': Elements.WINDOW_MATCH, 'color': Colors.YELLOW,
                                 'location': (55, 13),
                                 'dimensions': (14, 4)},
    }

    GROUPS = {
        Groups.LOBBY : (Elements.WINDOW_LOBBY, Elements.PLAYER_STAGE_0, Elements.PLAYER_STAGE_1, Elements.PLAYER_STAGE_2, Elements.PLAYER_STAGE_3, Elements.BUTTON_START,
                   Elements.BUTTON_ADD_AI, Elements.BUTTON_SEARCH, Elements.BUTTON_KICK, Elements.BUTTON_CLOSE, Elements.BUTTON_SETTINGS),
        Groups.MODE : (Elements.WINDOW_MODE, Elements.MAIN_STAGE, Elements.BUTTON_LOCAL, Elements.BUTTON_HOST, Elements.BUTTON_JOIN, Elements.BUTTON_EXIT),
        Groups.DEFAULT : (Elements.TITLE,),
        Groups.SETTINGS : (Elements.WINDOW_SETTINGS, Elements.BUTTON_DISPLAY_EFFECTS, Elements.BUTTON_COMPUTER_SPEED, Elements.BUTTON_SHOW_HANDS,
                      Elements.BUTTON_DOES_NOTHING),
        Groups.MATCH : (Elements.WINDOW_MATCH, Elements.WINDOW_HAND, Elements.CARD_0, Elements.CARD_1, Elements.CARD_2, Elements.CARD_3,
                        Elements.CARD_4, Elements.CARD_5, Elements.CARD_6, Elements.CARD_7, Elements.CARD_8, Elements.CARD_9, Elements.CARD_10,
                        Elements.CARD_11, Elements.CARD_12, Elements.CARD_13, Elements.PLAYER_TILE_0, Elements.PLAYER_TILE_1,
                        Elements.PLAYER_TILE_2, Elements.PLAYER_TILE_3, Elements.TOP_CARD, Elements.BELOW_CARD,
                        Elements.PREV_CARD, Elements.NEXT_CARD, Elements.DECK_COUNT, Elements.DECK_METER)
    }

    BUTTON_GROUPS = {
        Groups.MODE : (Elements.BUTTON_LOCAL, Elements.BUTTON_HOST, Elements.BUTTON_JOIN, Elements.BUTTON_EXIT),
        Groups.LOBBY : (Elements.BUTTON_START, Elements.BUTTON_ADD_AI, Elements.BUTTON_SEARCH, Elements.BUTTON_KICK, Elements.BUTTON_CLOSE, Elements.BUTTON_SETTINGS),
        Groups.SETTINGS : (Elements.BUTTON_DISPLAY_EFFECTS, Elements.BUTTON_COMPUTER_SPEED, Elements.BUTTON_SHOW_HANDS, Elements.BUTTON_DOES_NOTHING)
    }

    COLORS = (Colors.BLUE, Colors.RED, Colors.GREEN, Colors.YELLOW)
    TWIRL = ('|', '/', '-', '\\')
    STAGES = (Elements.PLAYER_STAGE_0, Elements.PLAYER_STAGE_1, Elements.PLAYER_STAGE_2, Elements.PLAYER_STAGE_3)
    CARDS = (Elements.CARD_0, Elements.CARD_1, Elements.CARD_2, Elements.CARD_3, Elements.CARD_4, Elements.CARD_5,
             Elements.CARD_6, Elements.CARD_7, Elements.CARD_8, Elements.CARD_9, Elements.CARD_10, Elements.CARD_11,
             Elements.CARD_12, Elements.CARD_13)
    TILES = (Elements.PLAYER_TILE_0, Elements.PLAYER_TILE_1, Elements.PLAYER_TILE_2, Elements.PLAYER_TILE_3)

    def __init__(self, screen):

        self.directory = None
        self.hand = None
        self.handName = None
        self.topCard = None
        self.currentCard = -1

        self.e = {
            Elements.MAIN : {'window': screen, 'panel': None, 'location': (0,0)},
        }

        self.e[Elements.MAIN]['window'].timeout(600)

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

        # Redefined to Lower Number of Warnings
        self.ACS_VLINE = curses.ACS_VLINE
        self.ACS_HLINE = curses.ACS_HLINE
        self.ACS_RTEE = curses.ACS_RTEE
        self.ACS_LTEE = curses.ACS_LTEE
        self.ACS_URCORNER = curses.ACS_URCORNER
        self.ACS_ULCORNER = curses.ACS_ULCORNER
        self.ACS_LLCORNER = curses.ACS_LLCORNER
        self.ACS_LRCORNER = curses.ACS_LRCORNER

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

        self.clearAllStages()
        self.clearAllTiles()

        #self.openGroup(Groups.LOBBY)
        #self.openGroup(Groups.SETTINGS)
        #self.openGroup(Groups.MODE)

    @staticmethod
    def blank(length):
        return ' ' * length

    def getInput(self, blocking=False):
        if blocking:
            self.noTimeOut()
        curses.flushinp()
        k = self.e[Elements.MAIN]['window'].getch()
        self.timeOut()
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
                window.border(self.ACS_VLINE, self.ACS_VLINE, self.ACS_HLINE, self.ACS_HLINE,
                              self.ACS_ULCORNER,
                              self.ACS_URCORNER, self.ACS_LTEE, self.ACS_RTEE)
            elif element in (Elements.WINDOW_LOBBY, Elements.WINDOW_HAND):
                window.border(self.ACS_VLINE, self.ACS_VLINE, self.ACS_HLINE, self.ACS_HLINE,
                              self.ACS_LTEE,
                              self.ACS_RTEE, self.ACS_LLCORNER, self.ACS_LRCORNER)
            elif element == Elements.WINDOW_MATCH:
                window.border(self.ACS_VLINE, self.ACS_VLINE, self.ACS_HLINE, self.ACS_HLINE,
                              self.ACS_LTEE,
                              self.ACS_RTEE, self.ACS_LTEE, self.ACS_RTEE)
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

        self._putChar(Elements.TITLE, 0, 4, self.ACS_LTEE, Colors.WHITE)
        for i in range(1, 69):
            self._putChar(Elements.TITLE, i, 4, self.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.TITLE, 69, 4, self.ACS_RTEE, Colors.WHITE)

        self._putChar(Elements.WINDOW_LOBBY, 0, 9, self.ACS_LTEE, Colors.WHITE)
        for i in range(1, 69):
            self._putChar(Elements.WINDOW_LOBBY, i, 9, self.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_LOBBY, 69, 9, self.ACS_RTEE, Colors.WHITE)

        self._putChar(Elements.WINDOW_HAND, 0, 2, self.ACS_LTEE, Colors.WHITE)
        for i in range(1, 69):
            self._putChar(Elements.WINDOW_HAND, i, 2, self.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_HAND, 69, 2, self.ACS_RTEE, Colors.WHITE)


        self._putChar(Elements.WINDOW_MODE, 0, 5, self.ACS_LTEE, Colors.WHITE)
        self._putChar(Elements.WINDOW_MODE, 0, 7, self.ACS_LTEE, Colors.WHITE)
        for i in range(1, 35):
            self._putChar(Elements.WINDOW_MODE, i, 5, self.ACS_HLINE, Colors.WHITE)
            self._putChar(Elements.WINDOW_MODE, i, 7, self.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_MODE, 35, 5, self.ACS_RTEE, Colors.WHITE)

        self._putText(Elements.WINDOW_SETTINGS, 13, 1, "Settings", Colors.WHITE)
        self._putChar(Elements.WINDOW_SETTINGS, 0, 2, self.ACS_LTEE, Colors.WHITE)
        for i in range(1, 33):
            self._putChar(Elements.WINDOW_SETTINGS, i, 2, self.ACS_HLINE, Colors.WHITE)
        self._putChar(Elements.WINDOW_SETTINGS, 33, 2, self.ACS_RTEE, Colors.WHITE)

        self._putText(Elements.NEXT_CARD, 1, 1, "->", Colors.WHITE)
        self._putText(Elements.NEXT_CARD, 1, 2, "->", Colors.WHITE)
        self._putText(Elements.PREV_CARD, 1, 1, "<-", Colors.WHITE)
        self._putText(Elements.PREV_CARD, 1, 2, "<-", Colors.WHITE)
        self._putText(Elements.DECK_COUNT, 0, 0, "Deck:", Colors.WHITE)
        self._putText(Elements.DECK_COUNT, 0, 1, "0 Cards", Colors.WHITE)

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

        mdata = {
            Elements.BUTTON_HOST: {'start': 8, 'length': 32, 'label': 'Host Multiplayer', 'active': False,
                                   'color': None},
            Elements.BUTTON_JOIN: {'start': 8, 'length': 32, 'label': 'Join Multiplayer', 'active': False,
                                   'color': None},
            Elements.BUTTON_LOCAL: {'start': 7, 'length': 32, 'label': 'Local Singleplayer', 'active': False,
                                    'color': None},
            Elements.BUTTON_EXIT: {'start': 14, 'length': 32, 'label': 'Exit', 'active': False, 'color': None},
        }

        self.updateButtons(data)
        self.updateButtons(mdata)
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

    def _drawDeckVisual(self, lst):
        for i in range(9):
            self._putText(Elements.DECK_METER, 2, 9 - i, ' ', Colors.WHITE)
        for i, string in enumerate(lst):
            if i < 3:
                self._putText(Elements.DECK_METER, 2, 9 - i, '=', Colors.RED)
            elif i < 6:
                self._putText(Elements.DECK_METER, 2, 9 - i, '=', Colors.YELLOW)
            elif i < 9:
                self._putText(Elements.DECK_METER, 2, 9 - i, '=', Colors.GREEN)

    def _getLineText(self, element, x, y, length):
        """Get a Line of Text From an Element"""
        curses.curs_set(1)
        window = self.e[element]['window']
        window.move(y, x)
        window.refresh()
        text = []
        self.e[Elements.MAIN]['window'].timeout(-1)
        c = self.getInput(True)
        while chr(c) != '\n':
            if c not in UI.IGNORE_INPUT and len(text) < length:
                text.append(chr(c))
            elif c == 127 and len(text) > 0:
                text.pop()
            for i, character in enumerate(text):
                self._putChar(element, x + i, y, character)
            window.move(y, x+len(text))
            window.refresh()
            c = self.getInput(True)
            self._putText(element, x, y, UI.blank(length))
        curses.curs_set(0)
        text = ''.join(text)
        self._putText(element, x, y, UI.blank(length))
        if text is '' or text.replace(' ','') is '':
            self.e[Elements.MAIN]['window'].timeout(600)
            return False, ''
        self.e[Elements.MAIN]['window'].timeout(600)
        return True, text

    def _highlightButton(self, button, color):
        """Colors a button yellow."""
        self._colorElement(button, color)
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
        except _curses.error:
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
        except _curses.error:
            pass
        window.noutrefresh()

    def _raiseCard(self, index):
        """Raise Card, Setting its Border to White"""

    def _restoreButton(self, button):
        """Restore the color of a button to its default."""
        self._colorElement(button, None)
        curses.doupdate()

    def _twirlSearch(self, num, phase):
        """Spins search wheel at specified stage using current phase char"""

    def noTimeOut(self):
        self.e[Elements.MAIN]['window'].timeout(-1)

    def timeOut(self):
        self.e[Elements.MAIN]['window'].timeout(600)

    @staticmethod
    def _updatePanels():
        curses.panel.update_panels()
        curses.doupdate()

    def pushCard(self, card, draw, reverse):
        self.e[Elements.TOP_CARD]['panel'].hide()
        self.e[Elements.BELOW_CARD]['panel'].hide()

        if self.topCard is not None:
            self.e[Elements.BELOW_CARD]['panel'].show()
            self.drawCard(self.topCard, True, reverse)

        self.topCard = card

        if draw:
            self.e[Elements.TOP_CARD]['panel'].show()
            self.drawCard(self.topCard, False, reverse)

        curses.doupdate()

    def _resizeElement(self, element, x, y):
        window = self.e[element]['window']
        window.resize(x, y)
        window.erase()
        window.box()
        window.noutrefresh()

    def drawCard(self, card, bottom, reverse):
        color = card.color
        value = card.value
        if bottom:
            element = Elements.BELOW_CARD
            window = self.e[Elements.TOP_CARD]['window']
            window.erase()
            window.noutrefresh()
        else:
            element = Elements.TOP_CARD
        self._resizeElement(element, 12, 14)
        self._colorElement(element, color)
        if value == 'R':
            if reverse:
                value = 'R9'
            else:
                value = 'R0'
        for i, num in enumerate(UI.BIG_NUMBERS[value]):
            self._putText(element, 1, 2 + i, num, color)
        curses.doupdate()

    def expandTopCard(self, amount, reverse=False):
        window = self.e[Elements.TOP_CARD]['window']
        if amount == 11:
            self.drawCard(self.topCard, False, reverse)
        else:
            window.erase()
            window.resize(2+amount, 4+amount)
            self._colorElement(Elements.TOP_CARD, self.topCard.color)
            window.box()
            window.refresh()
            time.sleep(.06)

    def cancelStage(self):
        """Set text of stage 0 to 'cancel' for use in kicking players"""
        self._putText(Elements.PLAYER_STAGE_0, 1, 1, UI.blank(32))
        self._putText(Elements.PLAYER_STAGE_0, 1, 2, UI.blank(32))
        self._putText(Elements.PLAYER_STAGE_0, 1, 1, "Cancel")
        curses.doupdate()

    def clearAllStages(self):
        for i in range(4):
            stage = UI.STAGES[i]
            self._colorElement(stage, Colors.GRAY)
            self._putText(stage, 1, 1, UI.blank(32))
            self._putText(stage, 1, 2, UI.blank(32))
            self._putText(stage, 1, 1, "No Player", Colors.GRAY)
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

    def clearAllTiles(self):
        for i in range(4):
            tile = UI.TILES[i]
            self._colorElement(tile, Colors.GRAY)
            self._putText(tile, 1, 1, '            ')
            self._putText(tile, 1, 2, '            ')
            self._putText(tile, 1, 1, 'No Player', Colors.GRAY)
        curses.doupdate()

    def clearTile(self, num):
        tile = UI.TILES[num]
        self._colorElement(tile, Colors.GRAY)
        self._putText(tile, 1, 1, '            ')
        self._putText(tile, 1, 2, '            ')
        self._putText(tile, 1, 1, 'No Player', Colors.GRAY)
        curses.doupdate()

    def closeGroup(self, group):
        for element in UI.GROUPS[group]:
            self.e[element]['panel'].hide()
        UI._updatePanels()

    def console(self, message):
        """Print a yellow message to game's console"""
        self._console(True, message, False)

    def getIPJoinButton(self):
        data = {
            Elements.BUTTON_JOIN: {'start': 0, 'length': 32, 'label': 'Host IP:', 'active': True,
                                   'color': Colors.RED},
        }
        self.updateButtons(data)
        return self._getLineText(Elements.BUTTON_JOIN, 10, 1, 16)

    def getNameFromMainStage(self):
        self.clearStage(-1)
        self._putText(Elements.MAIN_STAGE, 1, 1, UI.blank(32))
        return self._getLineText(Elements.MAIN_STAGE, 1, 1, 12)

    def hideAllCards(self):
        for card in UI.CARDS:
            self.e[card]['panel'].hide()
        UI._updatePanels()

    def hidePile(self):
        self.e[Elements.TOP_CARD]['panel'].hide()
        self.e[Elements.BELOW_CARD]['panel'].hide()
        UI._updatePanels()

    def joinButtonConnecting(self):
        data = {
            Elements.BUTTON_JOIN: {'start': 10, 'length': 32, 'label': 'Connecting', 'active': True,
                                   'color': Colors.RED},
        }
        self.updateButtons(data)

    def modeConsole(self, message):
        self._console(False, message, False)

    def modeWarning(self, message):
        self._console(False, message, True)

    def openGroup(self, group):
        for element in UI.GROUPS[group]:
            self.e[element]['panel'].show()
        UI._updatePanels()

    def pressSettings(self):
        self._highlightButton(Elements.BUTTON_SETTINGS, Colors.GREEN)

    def resetButtonPointer(self, directory, num):
        self._restoreButton(UI.BUTTON_GROUPS[directory][num])

    def searchStage(self, num):
        """Set stage to for searching. Does not update"""
        stageName = UI.STAGES[num]
        self._colorElement(stageName, Colors.GRAY)
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
        self._putText(Elements.DECK_COUNT, 0, 1, '         ', Colors.WHITE)
        self._putText(Elements.DECK_COUNT, 0, 1, "{} Cards".format(num), Colors.WHITE)
        deckCeiling = int(math.ceil(num / 12))
        deckVisual = []
        for i in range(deckCeiling):
            deckVisual.append('=')
        self._drawDeckVisual(deckVisual)
        curses.doupdate()

    def showHand(self, offset):
        """Show the hand at the offset provided"""

    def restoreJoinButton(self):
        data = {
            Elements.BUTTON_JOIN: {'start': 8, 'length': 32, 'label': 'Join Multiplayer', 'active': True,
                                   'color': Colors.YELLOW},
        }
        self.updateButtons(data)

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

    def setHand(self, hand, name, hidden, offset):
        """Sets the current hand in UI memory to the hand provided and draws it."""
        self.hand = hand
        self.handName = name
        self.drawHand(hidden, offset)

    def drawHand(self, hidden, offset):
        for i in range(14):
            card = UI.CARDS[i]
            window = self.e[card]['window']
            panel = self.e[card]['panel']
            panel.hide()
            index = i+(14*offset)
            if index < len(self.hand) and len(self.hand) > 0:
                panel.show()
                if not hidden:
                    color = self.hand[index].color
                    value = self.hand[index].value
                else:
                    color = Colors.WHITE
                    value = '?'
                if color == Colors.WILD:
                    color = Colors.WHITE
                self._colorElement(card, color)
                if value not in ('+4', 'W'):
                    self._putText(card, 1, 1, '  ', color)
                    self._putText(card, 1, 2, '  ', color)
                    if value == '+2':
                        self._putText(card, 1, 1, value, color)
                        self._putText(card, 1, 2, value, color)
                    else:
                        self._putText(card, 2, 1, value, color)
                        self._putText(card, 1, 2, value, color)
                    window.box()
                else:
                    self.rainbowCardBox(window, value)
                #curses.panel.update_panels()
                #window.noutrefresh()

        UI._updatePanels()
        handName = self.handName + "'s Hand"

        self._putText(Elements.WINDOW_HAND,1,1,UI.blank(68))
        self._putText(Elements.WINDOW_HAND, 1, 1, handName)
        self._putText(Elements.WINDOW_HAND, 55, 1, "[{}]".format("-"*int(math.ceil(len(self.hand)/14))))

        if len(self.hand) > 0:
            self._putText(Elements.WINDOW_HAND, 56+offset, 1, "|")
        curses.doupdate()

    def rainbowCardBox(self, cardWindow, value):
        #TODO Fix
        cardWindow.addch(0,0,self.ACS_ULCORNER, curses.color_pair(3))
        for i in range(2):
            cardWindow.addch(0, 1+i, self.ACS_HLINE, curses.color_pair(3))
        cardWindow.addch(0, 3, self.ACS_URCORNER, curses.color_pair(3))
        cardWindow.addch(1, 0, self.ACS_VLINE, curses.color_pair(5))
        cardWindow.addch(1, 3, self.ACS_VLINE, curses.color_pair(5))
        cardWindow.addch(2, 0, self.ACS_VLINE, curses.color_pair(4))
        cardWindow.addch(2, 3, self.ACS_VLINE, curses.color_pair(4))
        cardWindow.addch(3, 0, self.ACS_LLCORNER, curses.color_pair(2))
        for i in range(2):
            cardWindow.addch(3, 1 + i, self.ACS_HLINE, curses.color_pair(2))
        try:
            cardWindow.addch(3, 3, self.ACS_LRCORNER, curses.color_pair(2))
        except:
            pass
        cardWindow.addstr(1, 1, '  ', curses.color_pair(5))
        cardWindow.addstr(2, 1, '  ', curses.color_pair(4))
        if value == 'W':
            cardWindow.addstr(1, 2, value, curses.color_pair(5))
            cardWindow.addstr(2, 1, value, curses.color_pair(4))
        else:
            cardWindow.addstr(1, 1, value, curses.color_pair(5))
            cardWindow.addstr(2, 1, value, curses.color_pair(4))

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

    def setTileWithPlayer(self, num, player):
        tile = UI.TILES[num]
        self._colorElement(tile, None)
        self._putText(tile, 1, 1, '            ')
        self._putText(tile, 1, 1, player.name)
        self.updateCardCount(num, player.handSize())
        curses.doupdate()

    def twirlConnect(self, i):
        self._putChar(Elements.BUTTON_JOIN, 22, 1, ' ', Colors.RED)
        if i is not None:
            ch = UI.TWIRL[i]
            self._putChar(Elements.BUTTON_JOIN, 22, 1, ch, Colors.RED)

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

    def updateCardCount(self, num, amount):
        tile = UI.TILES[num]
        cardString = str(amount) + ' Cards'
        self._putText(tile, 5, 2, '        ')
        if len(cardString) == 7:
            self._putText(tile, 6, 2, cardString)
        else:
            self._putText(tile, 5, 2, cardString)
        #if color:
        #    self.windows[tileName]['window'].bkgd(ord(' ') | self.BACK_COLORS[self.COLORS[num]])
        #    self.windows[tileName]['window'].attrset(self.TEXT_COLORS[self.COLORS[num]])
        #    self.windows[tileName]['window'].box()
        #    self.windows[tileName]['window'].refresh()

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