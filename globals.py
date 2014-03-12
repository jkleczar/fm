import os, traceback

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
   DEFKEYSTROKES = None
   KEYS = { 'PREV_PAGE' : 'KEY_PPAGE',
            'NEXT_PAGE' : 'KEY_NPAGE',
            'HELP' : 'h',
            'UP_DIR' : 'KEY_BACKSPACE',
            'DELETE' : 'KEY_DC',
            'RETRIEVE' : "r",
            'MKDIR' : "n",
            'MOVE' : "m",
            'COPY' : "c",
            'CHMOD' : "x",
            'TOUCH' : "f",
            'FIND' : "/",
            'SORT_SWITCH' : "\t",
            'PERMS_TOGGLE' : "p",
            'OWNER_TOGGLE' : "o",
            'GROUP_TOGGLE' : "g",
            'SIZE_TOGGLE' : "s",
            'DATE_TOGGLE' : "d",
            'TIME_TOGGLE' : "t",
            'SHOW_ALL_COLS' : "+",
            'HIDE_ALL_COLS' : "-",
            'DOT_TOGGLE' : ".",
            'REFRESH' : 'KEY_F5',
            'QUIT' : "q" }
   HEADINGS = {'name' : 'NAME', 'permissions': 'PERMISSIONS', 'uid': 'OWNER', 
               'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}