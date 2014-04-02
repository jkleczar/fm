import os, traceback

class gb:
   scrn = None
   UP = -1
   DOWN = 1
   cmdoutdict = []
   winrow =  None  
   startrow = None
   highlightlinenum = None
   prevhighlight = []
   namewidth = None
   dotfiles = False
   sortmode = True
   HEIGHT = None
   COMMENT_CHAR = '#'
   OPTION_CHAR =  '='
   CONF_PATH = None
   DEFLIST_PATH = None
   DEFAULT_TYPES = None
   CUSTOM_PROGRAMS = None
   DEFAULT_TEXT = None
   CUSTOM_KEY_STROKES = None
   TRASH_PATH = '/tmp/' + str(os.getpid())
   CKEYS = None
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
   options = [ { "PG UP" : "-- jump to prev page" } , 
               { "PG DOWN" : "-- jump to next page" },
               { "ENTER" : "-- change directory/open file" },
               { "BACKSPACE" : "-- go up a directory" },
               { "DELETE" : "-- delete file/directory" },
               { "TAB" : "-- toggle sort mode"},
               { "q" : "-- quit"},
               { "n" : "-- make directory" },
               { "f" : "-- create file (touch)" },
               { "m" : "-- rename file/directory" },
               { "c" : "-- copy file/directory" },
               { "x" : "-- change permissions (chmod)" },
               { "/" : "-- find item" },
               { "h" : "-- this help window" },
               { "r" : "-- retrieve deleted files"},
               { "p" : "-- toggle PERMISSIONS column" },
               { "o" : "-- toggle OWNER column" },
               { "g" : "-- toggle GROUP column" },
               { "s" : "-- toggle SIZE column" },
               { "d" : "-- toggle DATE column" },
               { "t" : "-- toggle TIME column" },
               { "+" : "-- turn on all columns" },
               { "-" : "-- turn off all columns" },
               { "." : "-- toggle view of dot files/directories"}
            ]
   HEADINGS = {'name' : 'NAME', 'permissions': 'PERMISSIONS', 'uid': 'OWNER', 
               'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}