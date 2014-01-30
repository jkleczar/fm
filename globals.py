import os, traceback

# global variables
class gb:
   scrn = None  # will point to Curses window object
   cmdoutdict = [] # output of listdir as a dictionary 
   winrow = None  
   startrow = None  # index of first row in cmdoutlines to be displayed
   HEIGHT = None
   highlightLineNum = None
   UP = -1
   DOWN = 1
   namewidth = None
   COMMENT_CHAR = '#'
   OPTION_CHAR =  '='
   SPLIT_CHAR =  '|'
   CONF_PATH = os.environ['FMRC']
   DEFLIST_PATH = None
   DEFAULT_TYPES = None
   CUSTOM_DEFAULTS = None
   default_text = 'gedit '
   dotfiles = False