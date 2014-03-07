import curses, os, sys, re, shutil, stat, time, datetime, \
       errno, math, mimetypes, distutils.dir_util
from globals import *
from stat import *
from pwd import getpwuid
from grp import getgrgid

# set global variables
def setglobals():
   gb.highlightLineNum = 1
   gb.startrow = 0
   gb.HEIGHT = gb.scrn.getmaxyx()[0]
   gb.namewidth = 20

   if 'FMLRC' in os.environ:
      gb.CONF_PATH = os.environ['FMLRC']
   else:
      gb.scrn.addstr(0, 0, 'Ooops! FMLRC variable not set. To set:')
      gb.scrn.addstr(2, 0, 'export FMLRC=/path/to/.fmlrc')
      gb.scrn.addstr(4, 0, 'Press any key to quit.')
      gb.scrn.getch()
      sys.exit()

   configparsed = parse_config(gb.CONF_PATH, gb.COMMENT_CHAR, gb.OPTION_CHAR)
   # extract mimeapps.list and default.list paths from configuration file
   mimeappslist = configparsed.pop('MIMEAPPSLIST') if 'MIMEAPPSLIST' in configparsed else ''
   defaultslist = configparsed.pop('DEFLIST') if 'DEFLIST' in configparsed else ''

   gb.DEFLIST_PATH = mimeappslist if os.path.exists(mimeappslist) else defaultslist \
                                     if os.path.exists(defaultslist) else ''
   # the rest are custom default programs
   gb.CUSTOM_DEFAULTS = configparsed
   # set default text opener in case other default programs are unset
   if 'default' in gb.CUSTOM_DEFAULTS:
      gb.default_text_prog = gb.CUSTOM_DEFAULTS['default']

   gb.DEFAULT_TYPES =  getdefaulttypes()

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

# set all display options to default values
def initialisedisplayoptions():
   gb.protbits = True
   gb.owner = True
   gb.group = True
   gb.size = True
   gb.lastModDate = True
   gb.lastModTime = True

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

# check if the item on current line is a directory
# return true or false
def isdir(name):
   return S_ISDIR(os.lstat(name).st_mode)

# get all items in current directory
# store the files and their stat info
def preparelist():
   prep = os.listdir('.')

   gb.cmdoutdict = []
   row = 0

   if gb.SORTING_MODE:
      sortallbyname(prep)
   else:
      sortbyfiletype(prep)

def sortallbyname(preplist):
   cmdoutfiles = []

   # first store all stat info in a dictionary
   for ln in preplist:
      # get and store file info
      line = getstatinfo(ln)

      if ln[0] == '.':
         if gb.dotfiles:
            cmdoutfiles.append(line)
      else: 
         cmdoutfiles.append(line)

   # headings first
   line = {'name': 'NAME', 'permissions': 'PERMISSIONS', 'uid': 'OWNER', 
           'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}
   gb.cmdoutdict.append(line)

   cmdoutfiles = sorted(cmdoutfiles, key=lambda k : ( k['name'].lower() if k['name'][0] != '.' else k['name'][1:].lower() )) 

   # append the rest of lines
   gb.cmdoutdict += cmdoutfiles

# sort names then dirs
def sortbyfiletype(preplist):
   cmdoutdirs = []
   cmdoutfiles = []

   # first store all stat info in a dictionary
   for ln in preplist:
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

   cmdoutdirs = sorted(cmdoutdirs, key=lambda k: k['name'].lower()) 
   cmdoutfiles = sorted(cmdoutfiles, key=lambda k: k['name'].lower()) 

   # append the rest of lines
   gb.cmdoutdict += cmdoutdirs + cmdoutfiles

# get stat info of a file/dir
# return dictionary of file stat info
def getstatinfo(ln):
   statinfo = os.lstat(ln)
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
   statinfo = os.lstat(itemname)
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

# display list of files on screen
def displayscreencontent(fileList):
   gb.scrn.clear()
   curses.endwin()
   
   gb.winrow = 0
   top = gb.startrow + 1
   bottom = gb.startrow + gb.HEIGHT - 1

   if isinstance(fileList[0], dict):
      printrow(gb.cmdoutdict[0], (gb.purple | curses.A_BOLD))
   else:
      gb.scrn.addstr(0, 0, fileList[0])

   gb.winrow += 1

   if len(fileList) > 1:
      # adjust highlighted line index 
      if ( gb.highlightLineNum >= len(fileList) ):
         gb.highlightLineNum = len(fileList) - 1

      if isinstance(fileList[0], dict):
         for line in fileList[top:bottom]:
            # set colours and highlighting
            color = gb.green if isdir(line['name']) else gb.white
            format = curses.A_NORMAL if gb.winrow != gb.highlightLineNum else curses.A_BOLD

            printrow(line, color | format)
            gb.winrow += 1
      else:
         for f in fileList[top:bottom]:
            format = curses.A_NORMAL if gb.winrow != gb.highlightLineNum else curses.A_BOLD
            gb.scrn.addstr(gb.winrow, 0, f, format)
            gb.winrow+=1
   else:
      gb.highlightLineNum = 0

   gb.scrn.refresh()

# move highlight up/down
def updown(inc, fileList):
   if ( (gb.highlightLineNum == 1 and inc == gb.UP ) or 
         gb.highlightLineNum == gb.HEIGHT-2 and inc == gb.DOWN ):
      updownpaging(inc, fileList)
      displayscreencontent(fileList)
   else:
      updownonscreen(inc, fileList)

# scroll highlight up/down from the edge of screen 
def updownpaging(inc, fileList):
   nextLineNum = gb.highlightLineNum + inc
   if inc == gb.UP and gb.highlightLineNum == 1 and gb.startrow != 0:
      gb.startrow += gb.UP
      return
   elif inc == gb.DOWN and nextLineNum == gb.HEIGHT-1 and (gb.startrow + gb.HEIGHT-1) != len(fileList):
      gb.startrow += gb.DOWN
      return

# move highlight up/down one line within files visible on screen
def updownonscreen(inc, filesList):
   tmp = gb.highlightLineNum + inc

   # ignore attempts to go off the edge of the screen
   if 0 < tmp < len(filesList)-gb.startrow: 
      tmprow = filesList[gb.highlightLineNum + gb.startrow]
      highlightedline = filesList[gb.highlightLineNum + gb.startrow + inc]

      if isinstance(tmprow, dict):
         color = gb.green if isdir(tmprow['name']) else gb.white
         gb.winrow = gb.highlightLineNum
         printrow(tmprow, color)
         gb.winrow = tmp
         highlightcolor = gb.green if isdir(highlightedline['name']) else gb.white
         printrow(highlightedline, (highlightcolor | curses.A_BOLD))
      else:
         gb.scrn.addstr(gb.highlightLineNum, 0, tmprow)
         gb.scrn.addstr(tmp, 0, highlightedline, curses.A_BOLD)
      
      gb.highlightLineNum += inc
      gb.scrn.refresh()

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

# handle the screen in case it gets resized
def resize():
   curses.endwin()
   gb.HEIGHT = gb.scrn.getmaxyx()[0]
   # reset highlighted line
   if gb.highlightLineNum >= gb.HEIGHT:
      gb.highlightLineNum = gb.HEIGHT-2

# go to previous page of dir contents
def prevpage():
   if gb.startrow > 0:
      if gb.startrow - gb.winrow > 0:
         gb.startrow -= gb.HEIGHT - 2
      else:
         gb.startrow = 0

      gb.highlightLineNum = 1
      displayscreencontent(gb.cmdoutdict)

# go to next page of dir contents
def nextpage():
   diff = len(gb.cmdoutdict) - len(gb.cmdoutdict[0:gb.startrow+gb.HEIGHT-1])

   if diff > 0: 
      gb.startrow += gb.HEIGHT - 2
      gb.highlightLineNum = 1
      displayscreencontent(gb.cmdoutdict)

# return current list of deleted files in recycle bin
def getDeletedFiles():
   fileList = []
   fileList.append("Files to retrieve")
   rootdir = gb.BINPATH

   for root, subFolders, files in os.walk(rootdir):
      for f in files:
         fileList.append(os.path.join(root, f))

   return fileList

# retrieve a file from recycle bin
def retrieveFile(fileList):
   try:
      originalPath = fileList[gb.highlightLineNum].replace(gb.BINPATH, '/')

      if not os.path.exists(os.path.dirname(originalPath)):
         os.makedirs(os.path.dirname(originalPath))

      os.rename(fileList[gb.highlightLineNum], originalPath)
      return getDeletedFiles()
   except OSError as e:
      printerror(e)

# retrieve deleted files
def retrieveDeletes():
   fileList = getDeletedFiles()

   if len(fileList) > 1:
      gb.startrow = 0
      gb.highlightLineNum = 1

      displayscreencontent(fileList)

      while True:
         c = gb.scrn.getch()

         if c == ord("q"): 
            gb.highlightLineNum = 1
            rerun()
            break
         elif c == curses.KEY_UP: updown(gb.UP, fileList)
         elif c == curses.KEY_DOWN: updown(gb.DOWN, fileList)
         elif c == ord("\n"):
            fileList = retrieveFile(fileList)
            if len(fileList) > 1:
               displayscreencontent(fileList)
            else:
               gb.highlightLineNum = 1
               gb.scrn.clear()
               curses.endwin()
               rerun()
               break
   else:
      gb.scrn.clear()
      curses.endwin()
      gb.scrn.addstr(0, 0, "No files to retrieve. Press any key to continue.")
      gb.scrn.getch()
      rerun()

def cdoropen(current):
   if gb.highlightLineNum > 0:
      if isdir(current):
         gb.prevhighlight.append({"highlight" : gb.highlightLineNum, "startrow" : gb.startrow})
         cd(current)
         preparelist()
      else:
         openfile(current)

# change directory
def cd(name):
   try:
      gb.scrn.refresh()
      os.chdir(name)
      gb.highlightLineNum = 1
      gb.startrow = 0
   except OSError as e:
      printerror(format(e.strerror))

# go up a directory
def updir():
   os.chdir('..')
   prev = gb.prevhighlight.pop() if gb.prevhighlight else {'highlight' : 1, 'startrow' : 0}
   gb.highlightLineNum = prev['highlight']
   gb.startrow = prev['startrow']

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
   except OSError as e:
      printerror(format(e.strerror))
   curses.noecho()

# remove a file or directory
# put it in a temporary bin file 
def removeItem(name):
   if gb.highlightLineNum > 0:
      binpath = gb.BINPATH + os.getcwd()
      oldcmdoutlen = len(gb.cmdoutdict) - gb.startrow - 1

      try:
         if isdir(name):
            if os.listdir(name): # dir not empty
               if not os.path.exists(binpath):
                  os.makedirs(binpath)

               distutils.dir_util.copy_tree(name, binpath + '/' + name)
               shutil.rmtree(name)
            else:
               os.rmdir(name)
         else:
            if not os.path.exists(binpath):
                  os.makedirs(binpath)
                  
            os.rename(name, binpath + '/' + name)
         
         if gb.highlightLineNum == oldcmdoutlen:
            gb.highlightLineNum -= 1
         if gb.startrow >= len(gb.cmdoutdict) - 2:
            gb.startrow -= 1
            gb.highlightLineNum = 1
      except OSError as e:
         printerror(e)

# rename file
def rename(source):
   if gb.highlightLineNum > 0:
      oldcmdoutlen = len(gb.cmdoutdict) - gb.startrow - 1
      curses.echo()
      gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in desired destination: ")
      destination = gb.scrn.getstr(gb.HEIGHT - 1, 29)
      try:
         os.rename(source, destination)
         if gb.highlightLineNum == oldcmdoutlen:
            gb.highlightLineNum -= 1
         if gb.startrow >= len(gb.cmdoutdict) - 2:
            gb.startrow -= 1
            gb.highlightLineNum = 1
      except OSError as e:
         printerror(e)
      curses.noecho()

# copy file/dir
def copy(source):
   if gb.highlightLineNum > 0:
      curses.echo()
      gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in desired destination: ")
      destination = gb.scrn.getstr(gb.HEIGHT - 1, 29)
      try:
         if isdir(source):
            shutil.copytree(source, destination.decode(encoding='UTF-8'))
         else:
            #copy and set permissions according to umask
            shutil.copyfile(source, destination.decode(encoding='UTF-8'))
      except (IOError, os.error) as e:
         printerror(e)

# change file permissions
def chmod(current):
   if gb.highlightLineNum > 0:
      curses.echo()
      gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in permissions in decimal format: ")
      perms = gb.scrn.getstr(gb.HEIGHT - 1, 39)

      try:
         os.chmod(current, int(perms, 8))  
      except ValueError as e:
         printerror(e)

      curses.noecho()

# create file
def touch(times=None):
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in a file name: ")
   fname = gb.scrn.getstr(gb.HEIGHT - 1, 21)

   with file(fname, 'a'):
      os.utime(fname, times)

# open help window
def help():
   gb.scrn.clear()
   curses.endwin()

   options = [ { "PG UP" : "-- jump to prev page" } , 
               { "PG DOWN" : "-- jump to next page" },
               { "ENTER" : "-- change directory/open file" },
               { "BACKSPACE" : "-- go up a directory" },
               { "DELETE" : "-- delete file/directory" },
               { "TAB" : "-- toggle sort mode"},
               { "q" : "-- quit"},
               { "n" : "-- make directory" },
               { "m" : "-- rename file/directory" },
               { "c" : "-- copy file/directory" },
               { "x" : "-- change permissions (chmod)" },
               { "h" : "-- this help window" },
               { "r" : "-- retrieve deleted files"},
               { "p" : "-- toggle PERMISSIONS column" },
               { "o" : "-- toggle OWNER column" },
               { "g" : "-- toggle GROUP column" },
               { "s" : "-- toggle SIZE column" },
               { "d" : "-- toggle DATE column" },
               { "t" : "-- toggle TIME column" },
               { "+" : "-- turn on all columns" },
               { "." : "-- toggle view of dot files/directories"}
             ]

   WIDTH = gb.scrn.getmaxyx()[1]

   if WIDTH > len('FM HELP'):
      gb.scrn.addstr(0, WIDTH // 2 - 4, 'FML HELP', curses.color_pair(2) | curses.A_BOLD)
      row = 1
      for option in options:
         if row < gb.HEIGHT and WIDTH > 10:
            for key in option:
               gb.scrn.addstr(row, 0, key, curses.A_BOLD)
               gb.scrn.addstr(row, 10, option[key[0:WIDTH-11]])
            row+=1

   if gb.scrn.getch() == curses.KEY_RESIZE: 
      resize()
      help()
   else:
      rerun()

# toggle dotfiles on/off
def toggledotfiles():
   gb.dotfiles = not gb.dotfiles
   gb.startrow = 0

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

# find file within current directory
def findFile():
   curses.echo()
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Type in filename you want to look for: ")
   filename = gb.scrn.getstr(gb.HEIGHT - 1, 39)

   filteredFiles = []

   line = {'name': 'NAME', 'permissions': 'PERMISSIONS', 'uid': 'OWNER', 
           'gid': 'GROUP', 'size': 'SIZE', 'modDate': 'DATE', 'modTime': 'TIME'}

   filteredFiles.append(line)

   for f in gb.cmdoutdict[1:len(gb.cmdoutdict)]:
      if not isdir(f['name']):
         if filename.decode(encoding='UTF-8') in f['name']:
            filteredFiles.append(f)

   if len(filteredFiles) > 1:
      gb.cmdoutdict = filteredFiles
      gb.highlightLineNum = 1
      gb.startrow = 0
      curses.noecho()
   else: 
      displayscreencontent(gb.cmdoutdict)
      gb.scrn.addstr(gb.HEIGHT - 1, 0, "No matches found. Press any key to continue")
      gb.scrn.getch()

# in case an operation fails print error message at the bottom of the screen
def printerror(e):
   displayscreencontent(gb.cmdoutdict)
   gb.scrn.addstr(gb.HEIGHT - 1, 0, "Error: " + str(e) + \
      ". Press any key to continue.", curses.color_pair(1) | curses.A_BOLD)

   if gb.scrn.getch() == curses.KEY_RESIZE: resize()

   displayscreencontent(gb.cmdoutdict)

def quit():
   if os.path.exists(gb.BINPATH) and len(getDeletedFiles()) > 1:
      gb.scrn.addstr(gb.HEIGHT - 1, 0, "Bin is not empty. Press 'y' to open file retriever " \
                                             + "or any other key to quit." , \
                                             curses.color_pair(1) | curses.A_BOLD)

      if gb.scrn.getch() == ord('y'):
         retrieveDeletes()
      else:
         shutil.rmtree(gb.BINPATH)
         sys.exit()
   else:
      sys.exit()

# run/re-run the displaying of dir contents
def rerun():
   preparelist()
   setcolpositions()
   displayscreencontent(gb.cmdoutdict)

def main(stdscr):
   # window setup
   gb.scrn = stdscr
   curses.curs_set(0)

   setglobals()
   initialisedisplayoptions()
   initialisecolours()

   rerun()

   # user command loop
   while True:
      #with open("../test.txt", "a") as myfile:
      #   myfile.write(str(gb.highlightLineNum))

      # set current file
      current = gb.cmdoutdict[gb.startrow + gb.highlightLineNum]['name']

      gb.scrn.addstr(gb.HEIGHT - 1, 0, str(gb.startrow))
      gb.scrn.addstr(gb.HEIGHT - 1, 5, str(len(gb.cmdoutdict) - 1))

      # get user command
      c = gb.scrn.getch()

      if c == curses.KEY_UP or c == curses.KEY_DOWN \
         or c == ord("h") or c == ord("r") or c == ord("q"):
         # move up
         if  c == curses.KEY_UP: updown(gb.UP, gb.cmdoutdict) 
         # move down
         elif c == curses.KEY_DOWN: updown(gb.DOWN, gb.cmdoutdict)
         # help file
         elif c == ord("h"): help()
         # retrieve deletes
         elif c == ord("r"): retrieveDeletes()
         # quit
         elif c == ord("q"): quit()
      elif c == curses.KEY_PPAGE or c == curses.KEY_NPAGE or c == curses.KEY_RESIZE \
           or c == ord("\n") or c == ord("/"):
         # go to previous 'page' of files
         if c == curses.KEY_PPAGE: prevpage()
         # go to next 'page' of files
         elif c == curses.KEY_NPAGE: nextpage()
         # check for screen resize
         elif c == curses.KEY_RESIZE: resize()
         elif c == ord("\n"): cdoropen(current)
         # filter directory for file string
         elif c == ord("/"): findFile()
         displayscreencontent(gb.cmdoutdict)
      else: 
         # display options
         # permissions
         if c == ord("p"): gb.protbits = not gb.protbits
         # owner
         elif c == ord("o"): gb.owner = not gb.owner
         # group
         elif c == ord("g"): gb.group = not gb.group
         # size
         elif c == ord("s"): gb.size = not gb.size
         # date
         elif c == ord("d"): gb.lastModDate = not gb.lastModDate
         # time
         elif c == ord("t"): gb.lastModTime = not gb.lastModTime
         # show all options
         elif c == ord("+"): initialisedisplayoptions()
         # make new directory
         elif c == ord("n"): mkdir()
         # delete file/directory
         elif c == curses.KEY_DC: removeItem(current)
         # rename/move
         elif c == ord("m"): rename(current)
         # copy file
         elif c == ord("c"): copy(current) 
         # chmod
         elif c == ord("x"): chmod(current)
         # create file
         elif c == ord("f"): touch()
         # toggle dot files
         elif c == ord("."): toggledotfiles()
         # switch between sorting modes
         elif c == ord("\t"): gb.SORTING_MODE = not gb.SORTING_MODE
         # go up a directory
         elif c == curses.KEY_BACKSPACE: updir() 
         # refresh
         elif c == curses.KEY_F5: gb.highlightLineNum = 1
         rerun()

if __name__ =='__main__':
   curses.wrapper(main)