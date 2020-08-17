# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/IntroPage.py
from collections import namedtuple
import ScaleformFileLoader
import Settings
import SoundGroups
import gui
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform import SCALEFORM_SWF_PATH_V3, DEFAULT_VIDEO_BUFFERING_TIME as _DEFAULT_BUFFERING
from gui.Scaleform.daapi.view.meta.IntroPageMeta import IntroPageMeta
from gui.doc_loaders.GuiDirReader import GuiDirReader
from helpers import isIntroVideoSettingChanged, writeIntroVideoSetting, dependency, uniprof
from skeletons.gameplay import IGameplayLogic, GUIEventID
_VideoSettings = namedtuple('_VideoSettings', ['canBeSkipped'])

def _getCompalsoryVideoSettings(path):
    for settings in gui.GUI_SETTINGS.compulsoryIntroVideos:
        if settings['path'] == path:
            return _VideoSettings(settings.get('canBeSkipped', False))

    return None


class IntroPage(IntroPageMeta):
    gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self, _=None):
        super(IntroPage, self).__init__()
        self.__movieFiles = GuiDirReader.getAvailableIntroVideoFiles()
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self.__writeSetting = False
        self.__bufferTime = Settings.g_instance.userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, _DEFAULT_BUFFERING)
        self.__moviePath = None
        return

    def stopVideo(self):
        if self.__movieFiles:
            self.__showNextMovie()
            return
        LOG_DEBUG('Startup Videos has been played: STOP')
        self.__sendResult(True)

    def handleError(self, data):
        self.__sendResult(False, 'Startup Video: ERROR - NetStream code = {0:>s}'.format(data))

    def onUpdateStage(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        self.__soundValue = ds.readFloat('masterVolume', SoundGroups.MASTER_VOLUME_DEFAULT) / 2
        self.__showMovie(self.__moviePath, True)

    @uniprof.regionDecorator(label='offline.intro_video', scope='enter')
    def _populate(self):
        super(IntroPage, self)._populate()
        if self.__movieFiles:
            files = [ '/'.join((SCALEFORM_SWF_PATH_V3, v)) for v in self.__movieFiles ]
            ScaleformFileLoader.enableStreaming(files)
            self.__showNextMovie()
        else:
            self.__sendResult(False, 'There is no movie files for broadcast!')
        gui.g_guiResetters.add(self.onUpdateStage)

    @uniprof.regionDecorator(label='offline.intro_video', scope='exit')
    def _dispose(self):
        gui.g_guiResetters.discard(self.onUpdateStage)
        ScaleformFileLoader.disableStreaming()
        super(IntroPage, self)._dispose()

    def __showNextMovie(self):
        self.__moviePath = self.__movieFiles.pop(0)
        settings = _getCompalsoryVideoSettings(self.__moviePath)
        if settings:
            self.__showMovie(self.__moviePath, settings.canBeSkipped)
        elif isIntroVideoSettingChanged():
            self.__showMovie(self.__moviePath, True)
            self.__writeSetting = True
        else:
            LOG_DEBUG('Startup Video skipped: {}'.format(self.__moviePath))
            if self.__movieFiles:
                self.__showNextMovie()
            else:
                self.__sendResult(True)

    def __showMovie(self, movie, canSkip):
        LOG_DEBUG('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.__soundValue * 100))
        self.as_playVideoS({'source': movie,
         'bufferTime': self.__bufferTime,
         'volume': self.__soundValue,
         'canSkip': canSkip})

    def __sendResult(self, isSuccess, msg=''):
        if not isSuccess:
            LOG_ERROR(msg)
        if self.__writeSetting:
            writeIntroVideoSetting()
        self.gameplay.postStateEvent(GUIEventID.INTRO_VIDEO_FINISHED)
