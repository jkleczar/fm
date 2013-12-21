from __future__ import print_function  

import curses, os, sys, traceback, stat, time, datetime, logging, errno, shutil
from globals import *
from stat import *
from pwd import getpwuid
from grp import getgrgid

# get all items in current directory
# store the files and their stat info
def preparelist():
   prep = os.listdir('.')

   gb.cmdoutdict = []
   row = 0

   cmdoutdirs = []
   cmdoutfiles = []

   # first store all stat info in a dictionary
   for ln in prep:
      # get and store file info
      line = getstatinfo(ln)
      # remove EOLN if it is still there
      if ln[-1] == '\n': ln = ln[:-1]

      s = os.lstat(ln)

      if stat.S_ISREG(s.st_mode):
         cmdoutfiles.append(line)
      else:
         cmdoutdirs.append(line)

   # headings first
   line = {'name': 'NAME', 'permissions': 'drwxrwxrwx', 'uid': 'OWNER', 'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}
   gb.cmdoutdict.append(line)

   # append the rest of lines
   gb.cmdoutdict += cmdoutdirs + cmdoutfiles

# get stat info of a file/dir
# return dictionary of file stat info
def getstatinfo(ln):
   statinfo = os.stat(ln)
   protbits = formatpermissions(ln)
   uid = getpwuid(statinfo.st_uid).pw_name
   gid = getgrgid(statinfo.st_gid).gr_name
   size = str(statinfo.st_size)
   mtime = datetime.datetime.strptime(time.ctime(statinfo.st_mtime), "%a %b %d %H:%M:%S %Y")
   modDate = mtime.strftime("%b %d")
   modTime = mtime.strftime("%H:%M")

   line = {'name': ln, 'permissions': protbits, 'uid': uid, 'gid': gid, 'size': size, 'modDate': modDate, 'modTime': modTime}

   return line

# format file/dir permissions from stat module to rwx format.
# return formatted permissions
def formatpermissions(itemname):
   statinfo = os.stat(itemname)
   mode = statinfo.st_mode

   isdir = 'd' if S_ISDIR(mode) else '-'
   irusr = 'r' if stat.S_IRUSR & mode else '-'
   iwusr = 'w' if stat.S_IWUSR & mode else '-'
   ixusr = 'x' if stat.S_IXUSR & mode else '-'
   irgrp = 'r' if stat.S_IRGRP & mode else '-'
   iwgrp = 'w' if stat.S_IWGRP & mode else '-'
   ixgrp = 'x' if stat.S_IXGRP & mode else '-'
   iroth = 'r' if stat.S_IROTH & mode else '-'
   iwoth = 'w' if stat.S_IWOTH & mode else '-'
   ixoth = 'x' if stat.S_IXOTH & mode else '-'

   return isdir + irusr + iwusr + ixusr + irgrp + iwgrp + ixgrp + iroth + iwoth + ixoth

# set all display options to default values
def initialisedisplayoptions():
   gb.protbits = True
   gb.owner = True
   gb.group = True
   gb.size = True
   gb.lastModDate = True
   gb.lastModTime = True

# print a single row
def printrow(dictline, format):
   gb.wincol = 0;
   printcol(gb.wincol, dictline, 'name', format, True)
   printcol(gb.permscol, dictline, 'permissions', format, gb.protbits)
   printcol(gb.uidcol, dictline, 'uid', format, gb.owner)
   printcol(gb.gidcol, dictline, 'gid', format, gb.group)
   printcol(gb.sizecol, dictline, 'size', format, gb.size)
   printcol(gb.modDatecol, dictline, 'modDate', format, gb.lastModDate)
   printcol(gb.modTimecol, dictline, 'modTime', format, gb.lastModTime)

# print line based on row, col no
# and formatting (color, bold etc.)
def printcol(wincol, dictline, colname, lineformat, displayoption):
   if displayoption:
      gb.scrn.addstr(gb.winrow, wincol, dictline[colname], lineformat)

# get length of widest column
def colwidth(colname, isOn):
   length = 0

   if isOn:
      for ln in gb.cmdoutdict:
         if len(ln[colname]) > length:
            length = len(ln[colname])
      length += 2
   return length

def displaydir()  :
   # clear screen
   gb.scrn.erase()
   gb.scrn.addstr(curses.LINES - 1, 90, str(gb.highlightLineNum))
   gb.scrn.addstr(curses.LINES - 1, 95, str(gb.index))
   # now paint the rows
   top = gb.startrow + 1
   bottom = gb.startrow+curses.LINES

   gb.winrow = 0

   printrow(gb.cmdoutdict[0], (gb.purple | curses.A_BOLD))
   gb.winrow += 1

   if len(gb.cmdoutdict) > 1:
      if ( gb.highlightLineNum >= len(gb.cmdoutdict) ):
         gb.highlightLineNum = len(gb.cmdoutdict) - 1
         gb.index = gb.highlightLineNum

      for line in gb.cmdoutdict[top:bottom]:
         # highlight current line
         color = gb.green if isdir(line['name']) else gb.white
         format = curses.A_NORMAL if gb.winrow != gb.highlightLineNum else curses.A_BOLD

         printrow(line, color | format)
         gb.winrow += 1

   gb.scrn.refresh()

def updown(inc):
   nextLineNum = gb.highlightLineNum + inc
   # paging
   if inc == gb.UP and gb.highlightLineNum == 1 and gb.startrow != 0:
      gb.startrow += gb.UP
      return
   elif inc == gb.DOWN and nextLineNum == curses.LINES and (gb.startrow+curses.LINES) != len(gb.cmdoutdict):
      gb.startrow += gb.DOWN
      return

   # scroll highlight line
   if inc == gb.UP and (gb.startrow != 0 or gb.highlightLineNum != 1):
      gb.highlightLineNum = nextLineNum
   elif inc == gb.DOWN and (gb.startrow+gb.highlightLineNum+1) != len(gb.cmdoutdict) and gb.highlightLineNum != curses.LINES:
      gb.highlightLineNum = nextLineNum

# check if the item on current line is a directory
# return true or false
def isdir(name):
   return S_ISDIR(os.stat(name).st_mode)

def cd(name):
   try:
      gb.scrn.refresh()
      #index = gb.highlightLineNum if gb.highlightLineNum != 0 else 1
      os.chdir(name)
      rerun()
   except OSError as e:
      curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
      gb.scrn.addstr(curses.LINES - 1, 0, "Error: " + format(e.strerror), curses.color_pair(1) | curses.A_BOLD)

def mkdir(dirname):
   try:
      gb.scrn.refresh()
      os.mkdir(dirname)
      rerun()
   except OSError as e:
      curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
      gb.scrn.addstr(curses.LINES - 1, 0, "Error: " + format(e.strerror), curses.color_pair(1) | curses.A_BOLD)

def removeItem(name):
   try:
      if(isdir(name)):
         os.rmdir(name)
      else:
         os.remove(name)
      rerun()
   except OSError as e:
      if e.errno == errno.ENOTEMPTY:
         gb.scrn.addstr(curses.LINES - 1, 0,
                        "Error: Directory not empty. Are you sure you want to remove it with all its contents? y/n",
                        curses.color_pair(1) | curses.A_BOLD)

         if gb.scrn.getch() == ord("y"):
            shutil.rmtree(name)
         
         rerun()
      else:
         curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
         gb.scrn.addstr(curses.LINES - 1, 0, "Error: " + format(e.strerror), curses.color_pair(1) | curses.A_BOLD)

# initlialise colours that will be used in the program
def initialisecolours():
   background = curses.COLOR_BLACK
   # color pairs for display
   # green for dirs
   curses.init_pair(2, curses.COLOR_GREEN, background)
   # white for files
   curses.init_pair(3, curses.COLOR_WHITE, background)
   # purple for headings
   curses.init_pair(4, curses.COLOR_MAGENTA, background)
   # blue for background
   curses.init_pair(5, curses.COLOR_WHITE, background)
   # set colour pairs for dirs (green) and regular files (white)
   gb.green = curses.color_pair(2)
   gb.white = curses.color_pair(3)
   gb.purple = curses.color_pair(4)

def setcolswidths():
   gb.permscol = colwidth('name', True)
   gb.uidcol = colwidth('name', True) + colwidth('permissions', gb.protbits)
   gb.gidcol = colwidth('name', True) + colwidth('permissions', gb.protbits) + colwidth('uid', gb.owner)
   gb.sizecol = colwidth('name', True) + colwidth('permissions', gb.protbits) + colwidth('uid', gb.owner) + colwidth('gid', gb.group)
   gb.modDatecol = colwidth('name', True) + colwidth('permissions', gb.protbits) + colwidth('uid', gb.owner) + colwidth('gid', gb.group) + colwidth('size', gb.size)
   gb.modTimecol = colwidth('name', True) + colwidth('permissions', gb.protbits) + colwidth('uid', gb.owner) + colwidth('gid', gb.group) + colwidth('size', gb.size) + colwidth('modDate', gb.lastModDate)

# run/re-run the displaying of dir contents
def rerun():
   gb.ls = preparelist()
   setcolswidths()
   displaydir()

def main():
   # window setup
   gb.scrn = curses.initscr()
   curses.noecho()
   curses.cbreak()
   curses.start_color();
   gb.scrn.keypad(1)
   curses.curs_set(0)

   gb.scrn.bkgd(' ', curses.color_pair(5))
   initialisecolours()
   initialisedisplayoptions()
   
   gb.highlightLineNum = 1
   gb.index = 1;
   gb.startrow = 0

   preparelist()
   setcolswidths()

   # user command loop
   while True:
      displaydir()
      # get user command
      c = gb.scrn.getch()

      if c == ord("q"): break
      # move up/down
      elif c == curses.KEY_UP: updown(gb.UP)
      elif c == curses.KEY_DOWN: updown(gb.DOWN)
      # display options
      elif c == ord("p"):
         gb.protbits = not gb.protbits
         rerun()
      elif c == ord("o"):
         gb.owner = not gb.owner
         rerun()
      elif c == ord("g"):
         gb.group = not gb.group
         rerun()
      elif c == ord("s"):
         gb.size = not gb.size
         rerun()
      elif c == ord("d"):
         gb.lastModDate = not gb.lastModDate
         rerun()
      elif c == ord("t"):
         gb.lastModTime = not gb.lastModTime
         rerun()
      # show all options
      elif c == ord("+"):
         initialisedisplayoptions()
         rerun()
      elif c == ord("\n"):
         cd(gb.cmdoutdict[gb.highlightLineNum]['name'])
      elif c == curses.KEY_BACKSPACE:
         cd('..')
      elif c == ord("m"):
         curses.echo()
         dirname = gb.scrn.getstr(curses.LINES - 1, 0)
         mkdir(dirname)
         curses.noecho()
      elif c == ord("r"):
         removeItem(gb.cmdoutdict[gb.highlightLineNum]['name'])

   restorescreen()

def restorescreen():
   curses.nocbreak()
   curses.echo()
   curses.endwin()

if __name__ =='__main__':
   try:
      main()
   except:
      restorescreen()
      # print error message re exception
      traceback.print_exc()