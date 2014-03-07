import os, traceback

# global variables
class gb:
   scrn = None
   cmdoutdict = []
   winrow = None  
   startrow = None
   HEIGHT = None
   highlightLineNum = None
   prevhighlight = []
   UP = -1
   DOWN = 1
   namewidth = None
   COMMENT_CHAR = '#'
   OPTION_CHAR =  '='
   CONF_PATH = None
   DEFLIST_PATH = None
   DEFAULT_TYPES = None
   CUSTOM_DEFAULTS = None
   dotfiles = False
   BINPATH = '/tmp/' + str(os.getpid())
   SORTING_MODE = True