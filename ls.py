import curses, os, sys, traceback, stat, time, datetime, logging, errno, shutil, math
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
      if wincol < gb.scrn.getmaxyx()[1] - 1:
         gb.scrn.addstr(gb.winrow, wincol, dictline[colname][0:gb.scrn.getmaxyx()[1]-wincol], lineformat)

# get length of widest column
def colwidth(colname, isOn):
   length = 0

   if isOn:
      for ln in gb.cmdoutdict:
         if len(ln[colname]) > length:
            length = len(ln[colname])
      length += 2
   return length

# set column widths based on widest item in a column
def setcolpositions():
   #round up to nearest 10 in case the column is wider
   if colwidth('name', True) > gb.namewidth:
      gb.namewidth = int(math.ceil(colwidth('name', True) / 10.0)) * 10

   gb.permscol = gb.namewidth
   gb.uidcol = gb.permscol + colwidth('permissions', gb.protbits)
   gb.gidcol = gb.uidcol + colwidth('uid', gb.owner)
   gb.sizecol = gb.gidcol + colwidth('gid', gb.group)
   gb.modDatecol = gb.sizecol + colwidth('size', gb.size)
   gb.modTimecol = gb.modDatecol + colwidth('modDate', gb.lastModDate)

# display directory contents
def displaydir()  :
   # clear screen
   gb.scrn.clear()

   gb.winrow = 0

   # now paint the rows
   # headings first
   printrow(gb.cmdoutdict[0], (gb.purple | curses.A_BOLD))
   gb.winrow += 1

   # set top and bottom index
   # omit headings from top 
   top = gb.startrow + 1
   bottom = gb.startrow+gb.scrn.getmaxyx()[0]-1

   #gb.scrn.addstr(curses.LINES - 1, 0, "startrow: " + str(gb.startrow))
   #gb.scrn.addstr(curses.LINES - 1, 12, "now on: " + str(gb.startrow+gb.highlightLineNum))

   # now dir contents (if any)
   if len(gb.cmdoutdict) > 1:
      # adjust highlighted line index 
      if ( gb.highlightLineNum >= len(gb.cmdoutdict) ):
         gb.highlightLineNum = len(gb.cmdoutdict) - 1

      for line in gb.cmdoutdict[top:bottom]:
         # set colours and highlighting
         color = gb.green if isdir(line['name']) else gb.white
         format = curses.A_NORMAL if gb.winrow != gb.highlightLineNum else curses.A_BOLD

         printrow(line, color | format)
         gb.winrow += 1

   gb.scrn.refresh()


# move cursor up or down
def updownpaging(inc):
   nextLineNum = gb.highlightLineNum + inc
   # paging
   if inc == gb.UP and gb.highlightLineNum == 1 and gb.startrow != 0:
      gb.startrow += gb.UP
      return
   elif inc == gb.DOWN and nextLineNum == gb.scrn.getmaxyx()[0]-1 and (gb.startrow+gb.scrn.getmaxyx()[0]-1) != len(gb.cmdoutdict):
      gb.startrow += gb.DOWN
      return

   # scroll highlight line
   if inc == gb.UP and (gb.startrow != 0 or gb.highlightLineNum != 1):
      gb.highlightLineNum = nextLineNum
   elif inc == gb.DOWN and (gb.startrow+gb.highlightLineNum) != len(gb.cmdoutdict)-1 and gb.highlightLineNum != gb.scrn.getmaxyx()[0]-1:
      gb.highlightLineNum = nextLineNum


# move highlight up/down one line
def updown(inc):
   tmp = gb.highlightLineNum + inc

   # ignore attempts to go off the edge of the screen
   if 0 < tmp < len(gb.cmdoutdict)-gb.startrow: 
      # unhighlight the current line by rewriting it in default attributes
      tmprow = gb.cmdoutdict[gb.highlightLineNum + gb.startrow]   

      color = gb.green if isdir(tmprow['name']) else gb.white
      gb.winrow = gb.highlightLineNum
      printrow(tmprow, color)

      # highlight the previous/next line
      gb.winrow = tmp

      ln = gb.cmdoutdict[gb.highlightLineNum + gb.startrow + inc]
      highlightcolor = gb.green if isdir(ln['name']) else gb.white
      printrow(ln, (highlightcolor | curses.A_BOLD))
      
      gb.highlightLineNum += inc

      gb.scrn.refresh()

# go to next page of dir contents
def nextpage():
   diff = len(gb.cmdoutdict) - len(gb.cmdoutdict[0:gb.startrow+curses.LINES-1])

   if diff > 0: 
      gb.startrow += curses.LINES - 2

      if gb.highlightLineNum > len(gb.cmdoutdict[gb.startrow:-1]):
         gb.highlightLineNum = len(gb.cmdoutdict[gb.startrow:-1])

# go to previous page of dir contents
def prevpage():
   if gb.startrow > 0:

      if gb.startrow - gb.winrow > 0:
         gb.startrow -= curses.LINES - 2
      else:
         gb.startrow = 0

# check if the item on current line is a directory
# return true or false
def isdir(name):
   return S_ISDIR(os.stat(name).st_mode)

# change directory
def cd(name):
   try:
      gb.scrn.refresh()
      os.chdir(name)
      gb.startrow = 0
      rerun()
   except OSError as e:
      printerror(e)

# make directory
def mkdir():
   curses.echo()
   gb.scrn.addstr(curses.LINES - 1, 0, "Type in directory name you wish to create: ")
   dirname = gb.scrn.getstr(curses.LINES - 1, 43)
   try:
      gb.scrn.refresh()
      os.mkdir(dirname)
      rerun()
   except OSError as e:
      printerror(e)
   curses.noecho()

# remove file or directory
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
         printerror(e)
      

def rename(source, destination):
   try:
      os.rename(source, destination)
      rerun()
   except OSError as e:
      printerror(e)

def printerror(e):
   displaydir()
   gb.scrn.addstr(curses.LINES - 1, 0, "Error: " + format(e.strerror) + \
      ". Press any key to continue.", curses.color_pair(1) | curses.A_BOLD)
   restorescreen()
   gb.scrn.getch()

# initlialise colours that will be used in the program
def initialisecolours():
   background = curses.COLOR_BLACK
   # color pairs for display
   # red for errors
   curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
   # green for dirs
   curses.init_pair(2, curses.COLOR_GREEN, background)
   # white for files
   curses.init_pair(3, curses.COLOR_WHITE, background)
   # purple for headings
   curses.init_pair(4, curses.COLOR_MAGENTA, background)
   # set colour pairs for dirs (green) and regular files (white)
   gb.scrn.bkgd(' ', curses.color_pair(3))

   gb.green = curses.color_pair(2)
   gb.white = curses.color_pair(3)
   gb.purple = curses.color_pair(4)

# run/re-run the displaying of dir contents
def rerun():
   gb.ls = preparelist()
   setcolpositions()
   displaydir()

def main():
   # window setup
   gb.scrn = curses.initscr()
   curses.noecho()
   curses.cbreak()
   curses.start_color();
   gb.scrn.keypad(1)
   curses.curs_set(0)

   initialisecolours()
   initialisedisplayoptions()
   
   gb.highlightLineNum = 1
   gb.startrow = 0

   #default length of first column
   gb.namewidth = 20

   preparelist()
   setcolpositions()

   displaydir()

   # user command loop
   while True:
      current = gb.startrow+gb.highlightLineNum

      gb.scrn.addstr(gb.scrn.getmaxyx()[0] - 1, 12, str(gb.highlightLineNum))

      # get user command
      c = gb.scrn.getch()

      #quit
      if c == ord("q"): break
      # check for screen resize
      elif c == curses.KEY_RESIZE:
         curses.endwin()
         # reset highlighted line
         if gb.highlightLineNum >= gb.scrn.getmaxyx()[0]:
            gb.highlightLineNum = gb.scrn.getmaxyx()[0]-2
         displaydir()
      # move up/down
      elif c == curses.KEY_UP: 
         if ( gb.highlightLineNum == 1 ):
            updownpaging(gb.UP)
            displaydir()
         else: 
            updown(gb.UP)
      elif c == curses.KEY_DOWN: 
         if ( gb.highlightLineNum == gb.scrn.getmaxyx()[0]-2):
            updownpaging(gb.DOWN)
            displaydir()
         else:
            updown(gb.DOWN)   
      # go to previous/next 'page' of files
      elif c == curses.KEY_PPAGE: prevpage()
      elif c == curses.KEY_NPAGE: nextpage()
      # refresh
      elif c == ord("r"): displaydir()
      # display options
      # permissions
      elif c == ord("p"):
         gb.protbits = not gb.protbits
         rerun()
      # owner
      elif c == ord("o"):
         gb.owner = not gb.owner
         rerun()
      # group
      elif c == ord("g"):
         gb.group = not gb.group
         rerun()
      # size
      elif c == ord("s"):
         gb.size = not gb.size
         rerun()
      # date
      elif c == ord("d"):
         gb.lastModDate = not gb.lastModDate
         rerun()
      # time
      elif c == ord("t"):
         gb.lastModTime = not gb.lastModTime
         rerun()
      # show all options
      elif c == ord("+"):
         initialisedisplayoptions()
         rerun()
      # change directory
      elif c == ord("\n"):
      #elif c == curses.KEY_RIGHT:
         cd(gb.cmdoutdict[current]['name'])
      # go up a directory
      elif c == curses.KEY_BACKSPACE:
         cd('..')
      # make new directory
      elif c == ord("n"):
         mkdir()
      # delete file/directory
      elif c == curses.KEY_DC:
         removeItem(gb.cmdoutdict[current]['name'])
      # rename/move
      elif c == ord("m"):
         curses.echo()
         gb.scrn.addstr(curses.LINES - 1, 0, "Type in desired destination: ")
         destination = gb.scrn.getstr(curses.LINES - 1, 29)
         rename(gb.cmdoutdict[current]['name'], destination)
         curses.noecho()

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