import os, traceback

# global variables
class gb:
   scrn = None
   UP = -1
   DOWN = 1
   cmdoutdict = []
   winrow = None  
   startrow = None
   highlightLineNum = None
   prevhighlight = []
   namewidth = None
   dotfiles = False
   SORTING_MODE = True
   HEIGHT = None
   COMMENT_CHAR = '#'
   OPTION_CHAR =  '='
   CONF_PATH = None
   DEFLIST_PATH = None
   DEFAULT_TYPES = None
   CUSTOM_DEFAULTS = None
   default_text_prog = None
   CUSTOMKEYSTROKES = None
   BINPATH = '/tmp/' + str(os.getpid())
   KEYS = { 'PREV_PAGE' : 'curses.KEY_PPAGE',
            'NEXT_PAGE' : 'curses.KEY_NPAGE',
            'HELP' : 'ord("h")',
            'UP_DIR' : 'curses.KEY_BACKSPACE',
            'DELETE' : 'curses.KEY_DC',
            'RETRIEVE' : 'ord("r")',
            'MKDIR' : 'ord("n")',
            'MOVE' : 'ord("m")',
            'COPY' : 'ord("c")',
            'CHMOD' : 'ord("x")',
            'TOUCH' : 'ord("f")',
            'FIND' : 'ord("/")',
            'SORT_SWITCH' : 'ord("\t")',
            'PERMS_TOGGLE' : 'ord("p")',
            'OWNER_TOGGLE' : 'ord("o")',
            'GROUP_TOGGLE' : 'ord("g")',
            'SIZE_TOGGLE' : 'ord("s")',
            'DATE_TOGGLE' : 'ord("d")',
            'TIME_TOGGLE' : 'ord("t")',
            'SHOW_ALL_COLS' : 'ord("+")',
            'HIDE_ALL_COLS' : 'ord("-")',
            'DOT_TOGGLE' : 'ord(".")',
            'REFRESH' : 'curses.KEY_F5',
            'QUIT' : 'ord("q")' }