import curses, os, sys, re, shutil, stat, time, datetime, \
       errno, math, mimetypes
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

      if ln[0] == '.':
         if gb.dotfiles:
            cmdoutdirs.append(line) if isdir(ln) else cmdoutfiles.append(line)
      else:
         cmdoutdirs.append(line) if isdir(ln) else cmdoutfiles.append(line)

   # headings first
   line = {'name': 'NAME', 'permissions': 'PERMISSIONS', 'uid': 'OWNER', 
           'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}
   gb.cmdoutdict.append(line)

   cmdoutdirs = sorted(cmdoutdirs, key=lambda k: k['name']) 
   cmdoutfiles = sorted(cmdoutfiles, key=lambda k: k['name']) 

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

   line = {'name': ln, 'permissions': protbits, 'uid': uid, 'gid': gid, 
           'size': size, 'modDate': modDate, 'modTime': modTime}

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
   printcol(gb.wincol, dictline, 'name', format, True, False)
   printcol(gb.permscol, dictline, 'permissions', format, gb.protbits, False)
   printcol(gb.uidcol, dictline, 'uid', format, gb.owner, False)
   printcol(gb.gidcol, dictline, 'gid', format, gb.group, False)
   printcol(gb.sizecol, dictline, 'size', format, gb.size, True)
   printcol(gb.modDatecol, dictline, 'modDate', format, gb.lastModDate, False)
   printcol(gb.modTimecol, dictline, 'modTime', format, gb.lastModTime, False)

# print line based on row, col no
# and formatting (color, bold etc.)
def printcol(wincol, dictline, colname, lineformat, displayoption, justified):
   if displayoption and wincol < gb.scrn.getmaxyx()[1] - 1:
      line = dictline[colname][0:gb.scrn.getmaxyx()[1]-wincol]
      if justified:
         gb.scrn.addstr(gb.winrow, wincol-2, line.rjust(colwidth(colname, True)), lineformat)
      else:
         gb.scrn.addstr(gb.winrow, wincol, line, lineformat)

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
   bottom = gb.startrow + gb.HEIGHT-1

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
   else:
      gb.highlightLineNum = 0
   gb.scrn.refresh()

# move highlight up/down one line within files visible on screen
def updownonscreen(inc):
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

# scroll highlight up/down from the edge of screen 
def updownpaging(inc):
   nextLineNum = gb.highlightLineNum + inc
   if inc == gb.UP and gb.highlightLineNum == 1 and gb.startrow != 0:
      gb.startrow += gb.UP
      return
   elif inc == gb.DOWN and nextLineNum == gb.HEIGHT-1 and (gb.startrow + gb.HEIGHT-1) != len(gb.cmdoutdict):
      gb.startrow += gb.DOWN
      return

# move highlight up/down
def updown(inc):
   gb.scrn.addstr(gb.HEIGHT - 1, 3, str(gb.highlightLineNum))
   if ( (gb.highlightLineNum == 1 and inc == gb.UP ) or 
         gb.highlightLineNum == gb.HEIGHT-2 and inc == gb.DOWN ):
      updownpaging(inc)
      displaydir()
   else:
      updownonscreen(inc)

# go to next page of dir contents
def nextpage():
   diff = len(gb.cmdoutdict) - len(gb.cmdoutdict[0:gb.startrow+gb.HEIGHT-1])

   if diff > 0: 
      gb.startrow += gb.HEIGHT - 2
      gb.highlightLineNum = 1

      displaydir()

# go to previous page of dir contents
def prevpage():
   if gb.startrow > 0:

      if gb.startrow - gb.winrow > 0:
         gb.startrow -= gb.HEIGHT - 2
      else:
         gb.startrow = 0

      gb.highlightLineNum = 1

      displaydir()

# check if the item on current line is a directory
# return true or false
def isdir(name):
   return S_ISDIR(os.stat(name).st_mode)

# change directory
def cd(name):
   try:
      if len(gb.cmdoutdict) <= 1:
         gb.highlightLineNum = 1

      gb.scrn.refresh()
      os.chdir(name)
      gb.startrow = 0
      rerun()
   except OSError as e:
      printerror(format(e.strerror))

# make directory
def mkdir():
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in directory name you wish to create: ")
   dirname = gb.scrn.getstr(gb.HEIGHT - 1, 43)
   try:
      gb.scrn.refresh()
      os.mkdir(dirname)
      if len(gb.cmdoutdict) == 1:
         gb.highlightLineNum = 1
      rerun()
   except OSError as e:
      printerror(format(e.strerror))
   curses.noecho()

# remove file or directory
def removeItem(name):
   try:
      if gb.highlightLineNum == gb.HEIGHT-2:
         gb.highlightLineNum -= 1

      if(isdir(name)):
         os.rmdir(name)
      else:
         os.remove(name)
      rerun()
   except OSError as e:
      if e.errno == errno.ENOTEMPTY:
         gb.scrn.addstr(gb.HEIGHT - 1, 0,
                        "Error: Directory not empty. Are you sure you want to remove it with all its contents? y/n",
                        curses.color_pair(1) | curses.A_BOLD)

         if gb.scrn.getch() == ord("y"):
            shutil.rmtree(name)  
         rerun() 
      else:
         printerror(e)
      

def rename(source):
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in desired destination: ")
   destination = gb.scrn.getstr(gb.HEIGHT - 1, 29)
   try:
      os.rename(source, destination)
      rerun()
   except OSError as e:
      printerror(e)
   curses.noecho()

def copy(source):
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in desired destination: ")
   destination = gb.scrn.getstr(gb.HEIGHT - 1, 29)
   try:
      if isdir(source):
         shutil.copytree(source, destination)
      else:
         #copy and sest permissions according to umask
         shutil.copyfile(source, destination)
      rerun()
   except (IOError, os.error) as e:
      printerror(e)

# open current file 
def openfile(current):
   # get mime type of file
   mimetype = mimetypes.guess_type(current)[0]

   fileExtension = os.path.splitext(current)[1]
   # ensure proper formatting of string before opening
   current = re.escape(current)
   
   # first get custom default applications
   if fileExtension in gb.CUSTOM_DEFAULTS:
      executeline = gb.CUSTOM_DEFAULTS[fileExtension].replace('<FILE>', current) + " &"
   else: 
      # now check mime types against default types
      if gb.DEFAULT_TYPES != {} and mimetype in gb.DEFAULT_TYPES:
         executeline = gb.DEFAULT_TYPES[mimetype] + " " + current + " 2>/dev/null &" 
      else:
         # if no defaults are set allow for opening textfiles with a default program
         executeline = gb.default_text_prog + " " + current + ' &' \
                       if mimetype == None or 'text' in mimetype \
                       else ''
   
   os.system(executeline)

# parse a config file of format 
# option = value
# skip commented lines 
# return dictionary of options and values
def parse_config(conffile, commentchar, optionchar):
   options = {}
   f = open(str(conffile))
   for line in f:
      # First, remove comments:
      if commentchar in line:
         # split on comment char, keep only the part before
         line = line.split(commentchar, 1)[0]
      # Second, find lines with an option=value:
      if gb.OPTION_CHAR in line:
         # split on option char:
         option, value = line.split(optionchar, 1)
         # strip spaces:
         option = option.strip()
         value = value.strip()
         # store in dictionary:
         options[option] = value
   f.close()

   return options

# get a dictionary of mime types as keys and programs to open then with as values
def getdefaulttypes():
   mimetypes = {}
   if gb.DEFLIST_PATH != '':
      mimetypes = parse_config(gb.DEFLIST_PATH, '[', gb.OPTION_CHAR)

      for mime in mimetypes:
         mimetypes[mime] = mimetypes[mime].split(';')[0] if ';' in mimetypes[mime] else mimetypes[mime]
         mimetypes[mime] = mimetypes[mime].replace('.desktop', '')
         mimetypes[mime] = mimetypes[mime].strip()

   return mimetypes

def chmod(current):
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in permissions in decimal format: ")
   perms = gb.scrn.getstr(gb.HEIGHT - 1, 39)

   try:
      os.chmod(current, int(perms, 8))  
      rerun()
   except ValueError, e:
      printerror(e)


def resize():
   curses.endwin()
   gb.HEIGHT = gb.scrn.getmaxyx()[0]
   # reset highlighted line
   if gb.highlightLineNum >= gb.HEIGHT:
      gb.highlightLineNum = gb.HEIGHT-2

def find():
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in name of file and starting path: ")
   name, path = gb.scrn.getstr(gb.HEIGHT - 1, 40).split(" ", 1)

   retpath = name + " not found in " + path 

   for root, dirs, files in os.walk(path):
      if name in files:
         retpath = os.path.join(root, name)

   displaydir()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, retpath)

def help():
   gb.scrn.clear()
   curses.endwin()

   options = [ { "PG UP" : "-- jump to prev page" } , 
               { "PG DOWN" : "-- jump to prev page" },
               { "ENTER" : "-- change directory/open file" },
               { "BACKSPACE" : "-- go up a directory" },
               { "DELETE" : "-- delete file/directory" },
               { "Q" : "-- quit"},
               { "N" : "-- make directory" },
               { "M" : "-- rename file/directory" },
               { "C" : "-- copy file/directory" },
               { "X" : "-- change permissions (chmod)" },
               { "H" : "-- this help window" },
               { "/" : "-- find file" },
               { "P" : "-- toggle PERMISSIONS column" },
               { "O" : "-- toggle OWNER column" },
               { "G" : "-- toggle GROUP column" },
               { "S" : "-- toggle SIZE column" },
               { "D" : "-- toggle DATE column" },
               { "T" : "-- toggle TIME column" },
               { "+" : "-- turn on all columns" },
               { "." : "-- toggle view of dot files/directories"}
             ]

   WIDTH = gb.scrn.getmaxyx()[1]

   if WIDTH > len('FM HELP'):
      gb.scrn.addstr(0, WIDTH/2 - 4, 'FM HELP', curses.color_pair(2) | curses.A_BOLD)
      row = 1
      for option in options:
         if row < gb.HEIGHT and WIDTH > 10:
            for key, value in option.iteritems():
               gb.scrn.addstr(row, 0, key, curses.A_BOLD)
               gb.scrn.addstr(row, 10, value[0:WIDTH-11])
            row+=1

   if gb.scrn.getch() == curses.KEY_RESIZE: 
      resize()
      help()
   else:
      rerun()

def printerror(e):
   displaydir()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Error: " + str(e) + \
      ". Press any key to continue.", curses.color_pair(1) | curses.A_BOLD)

   if gb.scrn.getch() == curses.KEY_RESIZE: resize()

   displaydir()

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

def setglobals():
   gb.highlightLineNum = 1
   gb.startrow = 0
   gb.HEIGHT = gb.scrn.getmaxyx()[0]
   gb.namewidth = 20

   configparsed = parse_config(gb.CONF_PATH, \
                               gb.COMMENT_CHAR, gb.OPTION_CHAR)

   # extract mimeapps.list and default.list paths from configuration file
   mimeappslist = configparsed.pop('MIMEAPPSLIST') \
                  if 'MIMEAPPSLIST' in configparsed \
                  else ''
   defaultslist = configparsed.pop('DEFLIST') \
                  if 'DEFLIST' in configparsed \
                  else ''
   
   gb.DEFLIST_PATH = mimeappslist if os.path.exists(mimeappslist) \
                                  else defaultslist if os.path.exists(defaultslist) \
                                  else ''
   # the rest are custom default programs
   gb.CUSTOM_DEFAULTS = configparsed

   # set default text opener in case other default programs are unset
   gb.default_text_prog = gb.CUSTOM_DEFAULTS['default'] \
                          if 'default' in gb.CUSTOM_DEFAULTS \
                          else gb.default_text_prog

   gb.DEFAULT_TYPES =  getdefaulttypes()

# run/re-run the displaying of dir contents
def rerun():
   preparelist()
   setcolpositions()
   displaydir()

def main(stdscr):
   # window setup
   gb.scrn = stdscr
   curses.curs_set(0)

   initialisecolours()
   initialisedisplayoptions()
   setglobals()

   rerun()

   # user command loop
   while True:
      current = gb.cmdoutdict[gb.startrow+gb.highlightLineNum]['name']
      #gb.scrn.addstr(gb.HEIGHT - 1, 1, str(current))

      # get user command
      c = gb.scrn.getch()

      #quit
      if c == ord("q"): break
      # check for screen resize
      elif c == curses.KEY_RESIZE: 
         resize()
         rerun()
      # move up/down
      elif c == curses.KEY_UP: updown(gb.UP) 
      elif c == curses.KEY_DOWN: updown(gb.DOWN)  
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
      # if it's a dir: change dir
      # if it's a file: open file with the default program
      elif c == ord("\n"): 
         if isdir(current):
            cd(current)
         else:
            openfile(current)
      # go up a directory
      elif c == curses.KEY_BACKSPACE: cd('..')
      # make new directory
      elif c == ord("n"): mkdir()
      # delete file/directory
      elif c == curses.KEY_DC: removeItem(current)
      # rename/move
      elif c == ord("m"): rename(current)
      # copy file
      elif c == ord("c"): copy(current)
      elif c == ord("x"): chmod(current)
      elif c == ord("/"): find()
      elif c == ord("h"): help()
      elif c == ord("."): 
         gb.dotfiles = not gb.dotfiles
         gb.startrow = 0
         rerun()

if __name__ =='__main__':
   curses.wrapper(main)