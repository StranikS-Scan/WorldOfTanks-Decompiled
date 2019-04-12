# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCOutroVideoPage.py
import SoundGroups
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.Scaleform.daapi.view.meta.BCOutroVideoPageMeta import BCOutroVideoPageMeta
from gui.Scaleform.daapi.view.bootcamp.BCLobbySpaceEnv import BCLobbySpaceEnv
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampTransition import BootcampTransition
from gui.app_loader import settings as app_settings
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class BCOutroVideoPage(BCOutroVideoPageMeta):
    __sound_env__ = BCLobbySpaceEnv
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(BCOutroVideoPage, self).__init__()
        self.__movieFiles = [settings['video']]
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self.__writeSetting = False

    def stopVideo(self):
        if self.__movieFiles:
            self.__showNextMovie()
            return
        LOG_DEBUG_DEV_BOOTCAMP('Startup Video: STOP')
        self.__onFinish()

    def handleError(self, data):
        self.__onFinish()

    def videoFinished(self):
        self.__onFinish()

    def _populate(self):
        super(BCOutroVideoPage, self)._populate()
        self.appLoader.detachCursor(app_settings.APP_NAME_SPACE.SF_LOBBY)
        if self.__movieFiles:
            self.__showNextMovie()
        else:
            self.__onFinish()

    def _dispose(self):
        super(BCOutroVideoPage, self)._dispose()
        self.appLoader.attachCursor(app_settings.APP_NAME_SPACE.SF_LOBBY, _CTRL_FLAG.GUI_ENABLED)

    def __showNextMovie(self):
        moviePath = self.__movieFiles.pop(0)
        self.__showMovie(moviePath)

    def __showMovie(self, movie):
        BootcampTransition.stop()
        LOG_DEBUG_DEV_BOOTCAMP('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.__soundValue * 100))
        self.as_playVideoS({'source': movie,
         'volume': self.__soundValue})

    def __onFinish(self):
        g_bootcampEvents.onOutroVideoStop()
        self.destroy()
