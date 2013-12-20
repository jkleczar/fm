import curses, os, sys, traceback

# global variables
class gb:
   scrn = None  # will point to Curses window object
   cmdoutlines = []  # output of listdir as a string
   cmdoutdict = [] # output of listdir as a dictionary 
   winrow = None  # current row position in screen
   startrow = None  # index of first row in cmdoutlines to be displayed