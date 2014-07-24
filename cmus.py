import os
import commands


class CmusRemote:

    def __init__(self, server=None, password=None):
        self.server = server
        self.password = password

    def getStatus(self):
        return self._runCommandWithOutput('-Q')

    def nextSong(self):
        return self._runCommand('--next')

    def prevSong(self):
        return self._runCommand('--prev')

    def playSong(self):
        return self._runCommand('--play')

    def pauseSong(self):
        return self._runCommand('--pause')

    def stopSong(self):
        return self._runCommand('--stop')

    def clearPlaylist(self):
        return self._runCommand('--clear')

    def addSong(self, song):
        return self._runCommand('--playlist "%s"' % (song))

    def _runCommand(self, command):
        return os.system('cmus-remote --server %s --passwd %s %s' % (self.server, self.password, command))

    def _runCommandWithOutput(self, command):
        return commands.getstatusoutput('cmus-remote --server %s --passwd %s %s' % (self.server, self.password, command))[1]
