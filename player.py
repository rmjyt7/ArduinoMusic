import serial
import commands
import os
import re
import thread
import sys
from glob import glob
from time import sleep
from cmus import CmusRemote

ser = serial.Serial('/dev/ttyACM0', 9600)

cmus = CmusRemote('127.0.0.1:1337', 'apassword')

class MainMenu:
  def __init__(self):
    self.display()

  def display(self):
    ser.write('1. Info|2. Browse;')

  def handleCommand(self, command):
    if command == 1:
      return StatusMenu
    elif command == 2:
      return FileManager

  def end(self):
    pass

class StatusMenu:
  song = 'unknown'
  endThread = False
  lastDisplay = ''

  def __init__(self):
    self.vol = commands.getstatusoutput('vol')[1]

    self.songTitle()

    self.display()

    thread.start_new_thread(self.update, ())

  def end(self):
    self.endThread = True

  def update(self):
    while True:
      if self.endThread:
        sys.exit()

      self.songTitle()
      self.getStatus()

      sleep(1)

  def handleCommand(self, command):
    if command == 1:
      print('volup')
      self.vol = commands.getstatusoutput('vol +')[1]
    elif command == 2:
      print('voldown')
      self.vol = commands.getstatusoutput('vol -')[1]
    elif command == 3:
      print('next')
      cmus.nextSong()
    elif command == 4:
      print('prev')
      cmus.prevSong()
    elif command == 5:
      print('playpause')
      if self.status == 'playing':
        cmus.pauseSong()
      else:
        cmus.playSong()
    elif command == 10:
        cmus.clearPlaylist()
    elif command == 20:
        cmus.stopSong()
    elif command == 30:
      print('seekforward')
    elif command == 40:
      print('seekbackward')
    elif command == 50:
      print('menu')
      return MainMenu

    self.songTitle()
    self.getStatus()
    self.display()

  def songTitle(self):
    out = cmus.getStatus()

    tags = [line.split(' ')[1:] for line in out.split('\n') if line[:3] == 'tag']

    found = False
    for tag in tags:
      if tag[0] == 'title':
        self.song = ' '.join(tag[1:])
        found = True

    if not found:
      self.song = 'unknown'

    self.getStatus()

    self.display()

  def getStatus(self):
    out = cmus.getStatus()

    match = re.match(r'status (.+)', out)

    self.status = match.group(1)

  def display(self):
    d = '%s|%s  V%s%%;' % (self.song, self.status, self.vol)
    if d != self.lastDisplay:
      ser.write(d)
      self.lastDisplay = d


class FileManager:
  fileindex = 0
  foldersongs = []

  def __init__(self):
    os.chdir('/mnt/nas/greg/Music/')

    self._loadfiles()

    self.display()

  def handleCommand(self, command):
    if command == 1:
      print('add')
      self.add()
    elif command == 2:
      print('scrollup')
      self.scrollup()
    elif command == 3:
      print('scrolldown')
      self.scrolldown()
    elif command == 4:
      print('selectfolder')
      self.selectfolder()
    elif command == 5:
      print('folderup')
      self.folderup()
    elif command == 10:
      print('clear')
      self.foldersongs = []
    elif command == 50:
      print('menu')
      return MainMenu

    self.display()

    return None

  def display(self):
    if len(self.files) == 0:
      ser.write('No files!|;')
    elif len(self.files) == 1 or self.fileindex + 1 == len(self.files):
      ser.write('>' + self.files[self.fileindex] + '|;')
    else:
      ser.write('>' + self.files[self.fileindex] + '|' + self.files[self.fileindex + 1] + ';')


  def _loadfiles(self):
    self.files = glob('*/')

    if len(self.files) > 0:
      self.files.sort()

  def _findmedia(self):
    self.foldersongs = []

    formats = ('*.mp3', '*.flac')

    foldersongs = []

    for files in formats:
      foldersongs.extend(glob(files))

    d = os.getcwd()

    for f in foldersongs:
      self.foldersongs.append(os.path.join(d, f))

    if len(self.foldersongs) > 0:
      self.foldersongs.sort()

  def scrollup(self):
    if self.fileindex - 1 >= 0:
      self.fileindex = self.fileindex - 1

    self.display()

  def scrolldown(self):
    if self.fileindex + 1 < len(self.files):
      self.fileindex = self.fileindex + 1

    self.display()

  def folderup(self):
    self.fileindex = 0

    os.chdir('..')

    self._loadfiles()

  def selectfolder(self):
    os.chdir(self.files[self.fileindex])

    self.fileindex = 0

    self._loadfiles()

    self.display()

  def add(self):
    prev = os.getcwd()

    if len(self.files) == 0:
        return

    os.chdir(self.files[self.fileindex])

    self._findmedia()

    os.chdir(prev)

    for song in self.foldersongs:
      print song
      cmus.addSong(song)

  def end(self):
    pass

manager = MainMenu()

ser.write('|;')

sleep(5)

manager.display()
manager.handleCommand(1)

def getCommand(gotCommand):
  while True:
    line = ser.readline()

    gotCommand(int(line))

def handleCommand(command):
  global manager

  thing = manager.handleCommand(command)

  if thing is not None:
    manager.end()
    manager = thing()
    manager.display()

getCommand(handleCommand)
