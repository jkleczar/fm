import curses, os, sys, traceback

# global variables
class gb:
   scrn = None  # will point to Curses window object
   cmdoutdict = [] # output of listdir as a dictionary 
   winrow = None  # current row position in screen
   startrow = None  # index of first row in cmdoutlines to be displayed
   index = None
   highlightLineNum = None
   UP = -1
   DOWN = 1