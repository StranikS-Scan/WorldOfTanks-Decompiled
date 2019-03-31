# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/StartGameVideo.py
# Compiled at: 2011-10-05 18:29:21
import sys
import constants
import BigWorld
import SoundGroups
from debug_utils import LOG_DEBUG
from gui.Scaleform import SCALEFORM_STARTUP_VIDEO_MASK, SCALEFORM_STARTUP_VIDEO_PATH
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.Waiting import Waiting
import ResMgr

class StartGameVideo(UIInterface):

    def __init__(self):
        UIInterface.__init__(self)
        ds = ResMgr.openSection(SCALEFORM_STARTUP_VIDEO_PATH)
        self.movieFiles = []
        for filename in ds.keys():
            basename, extension = filename.split('.')
            if extension == 'usm' and basename[0:1] != '_':
                self.movieFiles.append(SCALEFORM_STARTUP_VIDEO_MASK % filename)

        ResMgr.purge(SCALEFORM_STARTUP_VIDEO_PATH, True)
        self.soundValue = SoundGroups.g_instance.getMasterVolume() * 100

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.addExternalCallbacks({'StartGameVideo.StopVideo': self.onStopVideo,
         'StartGameVideo.NetSteamError': self.onNetSteamError})
        if self.movieFiles:
            BigWorld.wg_setMovieSoundMuted(False)
            self.showMovie(self.movieFiles.pop(0))
        else:
            BigWorld.callback(0, lambda : self.uiHolder.processLogin())
        Waiting.hide('loadPage')

    def showMovie(self, movie):
        if constants.IS_DEVELOPMENT:
            LOG_DEBUG('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.soundValue))
        self.call('StartGameVideo.PopulateUI', [movie, self.soundValue])

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('StartGameVideo.StopVideo', 'StartGameVideo.NetSteamError')
        BigWorld.wg_setMovieSoundMuted(True)
        UIInterface.dispossessUI(self)

    def onStopVideo(self, *args):
        if self.movieFiles:
            self.showMovie(self.movieFiles.pop(0))
            return
        if constants.IS_DEVELOPMENT:
            LOG_DEBUG('Startup Video: STOP')
            try:
                tmp_fil = open('GUIUnitTest.ut', 'r')
                if tmp_fil.readline().strip() != '':
                    tmp_fil.close()
                    sys.path.append('../../gui_unit_test/scripts')
                    import GUIUnitTest
                else:
                    tmp_fil.close()
            except IOError:
                pass

        BigWorld.wg_setMovieSoundMuted(True)
        BigWorld.callback(0, lambda : self.uiHolder.processLogin())

    def onNetSteamError(self, *args):
        if constants.IS_DEVELOPMENT:
            parser = CommandArgsParser(self.onNetSteamError.__name__, 1, [str])
            code = parser.parse(*args)
            LOG_DEBUG('Startup Video: ERROR - NetStream code = %s' % code)
        BigWorld.wg_setMovieSoundMuted(True)
        BigWorld.callback(0, lambda : self.uiHolder.processLogin())
