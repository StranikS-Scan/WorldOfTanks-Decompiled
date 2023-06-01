# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/view/splash_screen.py
import logging
from collections import namedtuple
import typing
import BigWorld
import ScaleformFileLoader
import Settings
import account_shared
import game_loading_bindings
import gui
from SoundGroups import MASTER_VOLUME_DEFAULT
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent
from gui.Scaleform.daapi.view.external_components import ExternalFlashSettings
from gui.Scaleform.daapi.view.meta.SplashScreenMeta import SplashScreenMeta
from gui.Scaleform.genConsts.SPLASHSCREENCONSTANTS import SPLASHSCREENCONSTANTS
from gui.doc_loaders.GuiDirReader import GuiDirReader
from helpers import uniprof
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
_logger = logging.getLogger(__name__)
_VideoSettings = namedtuple('_VideoSettings', ['canBeSkipped'])
VIDEO_FADE_OUT_TIME = 250
DEFAULT_VIDEO_BUFFERING_TIME = 2.0
ALWAYS_SHOW_SPLASH_SCREEN = 'development/alwaysShowIntroVideo'

def getCompulsoryVideoSettings(path):
    for settings in gui.GUI_SETTINGS.compulsoryIntroVideos:
        if settings['path'] == path:
            return _VideoSettings(settings.get('canBeSkipped', False))

    return None


def versionChanged(userPrefs):
    if userPrefs.readBool(ALWAYS_SHOW_SPLASH_SCREEN):
        return True
    mainVersion = account_shared.getClientMainVersion()
    lastVideoVersion = userPrefs.readString(Settings.INTRO_VIDEO_VERSION, '')
    return lastVideoVersion != mainVersion


def mustShowSplashScreen(userPrefs):
    if not gui.GUI_SETTINGS.guiEnabled:
        return False
    if userPrefs.readInt(Settings.KEY_SHOW_STARTUP_MOVIE, 1) == 1:
        if gui.GUI_SETTINGS.compulsoryIntroVideos:
            return True
        return versionChanged(userPrefs)
    return userPrefs.readBool(ALWAYS_SHOW_SPLASH_SCREEN, False)


class SplashScreen(ExternalFlashComponent, SplashScreenMeta):
    __slots__ = ('_movieFiles', '_writeSetting', '_bufferTime', '_soundValue', '_canSkip', '_width', '_height', '_currentMovie')

    def __init__(self, preferences):
        super(SplashScreen, self).__init__(ExternalFlashSettings('splashScreen', 'splashScreenApp.swf', 'root.main', SPLASHSCREENCONSTANTS.ON_SPLASH_SCREEN_LOADED_CALLBACK))
        self.createExternalComponent()
        self._userPrefs = preferences
        self._movieFiles = GuiDirReader.getAvailableIntroVideoFiles()
        self._writeSetting = False
        self._bufferTime = self._userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, DEFAULT_VIDEO_BUFFERING_TIME)
        self._soundValue = self._getVideoVolume() if BigWorld.isWindowVisible() else 0
        self._canSkip = True
        self._currentMovie = None
        self._width = 0
        self._height = 0
        return

    @uniprof.regionDecorator(label='offline.splash_screen', scope='enter')
    def onLoad(self):
        self.active(True)

    @uniprof.regionDecorator(label='offline.splash_screen', scope='exit')
    def onDelete(self):
        self.close()

    def onComplete(self):
        _logger.debug('Startup Video completed!')
        self._nextMovie()

    def onError(self):
        _logger.debug('Startup Video error!')
        self._nextMovie()

    def fadeOutComplete(self):
        game_loading_bindings.closeSplashScreen()

    def setStageSize(self, width, height):
        if self._isDAAPIInited():
            return self.as_setSizeS(width, height)
        self._width = width
        self._height = height

    def turnDAAPIon(self, setScript, movieClip):
        super(SplashScreen, self).turnDAAPIon(setScript, movieClip)
        self.as_setSizeS(self._width, self._height)

    def tryToSkip(self):
        if self._canSkip:
            self._nextMovie()

    def applicationVisibilityChanged(self):
        self._soundValue = self._getVideoVolume()
        self._sendDataToFlash()

    def _populate(self):
        super(SplashScreen, self)._populate()
        if self._movieFiles:
            files = [ '/'.join((SCALEFORM_SWF_PATH_V3, v)) for v in self._movieFiles ]
            ScaleformFileLoader.enableStreaming(files)
            self._nextMovie()
        else:
            self._allVideosComplete()

    def _destroy(self):
        ScaleformFileLoader.disableStreaming()
        self._userPrefs = None
        super(SplashScreen, self)._destroy()
        return

    def _nextMovie(self):
        if not self._movieFiles:
            self._allVideosComplete()
            return
        self._currentMovie = self._movieFiles.pop(0)
        settings = getCompulsoryVideoSettings(self._currentMovie)
        if settings:
            self._sendDataToFlash()
            self._canSkip = settings.canBeSkipped
        else:
            self._canSkip = True
            if versionChanged(self._userPrefs):
                self._sendDataToFlash()
                self._writeSetting = True
            else:
                _logger.debug('Startup Video skipped: %s', self._currentMovie)
                self._nextMovie()

    def _sendDataToFlash(self):
        if not self._currentMovie:
            return
        _logger.debug('Startup Video: path = %s, sound volume = %d%%', self._currentMovie, self._soundValue * 100)
        self.as_playVideoS({'source': self._currentMovie,
         'bufferTime': self._bufferTime,
         'volume': self._soundValue})

    def _allVideosComplete(self):
        if self._writeSetting:
            self._userPrefs.writeString(Settings.INTRO_VIDEO_VERSION, account_shared.getClientMainVersion())
        self.as_fadeOutS(VIDEO_FADE_OUT_TIME)

    def _getVideoVolume(self):
        ds = self._userPrefs[Settings.KEY_SOUND_PREFERENCES]
        return MASTER_VOLUME_DEFAULT / 2 if not ds else ds.readFloat('masterVolume', MASTER_VOLUME_DEFAULT) / 2


def createSplashScreen(preferences):
    return SplashScreen(preferences) if mustShowSplashScreen(preferences) else None
