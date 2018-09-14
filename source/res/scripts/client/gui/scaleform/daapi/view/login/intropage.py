# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/IntroPage.py
import SoundGroups
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.IntroPageMeta import IntroPageMeta
from gui.doc_loaders.GuiDirReader import GuiDirReader
from gui.shared import events
from helpers import isIntroVideoSettingChanged, writeIntroVideoSetting

class IntroPage(IntroPageMeta):

    def __init__(self, _=None):
        super(IntroPage, self).__init__()
        self.__movieFiles = GuiDirReader.getAvailableIntroVideoFiles()
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self.__writeSetting = False

    def stopVideo(self):
        if self.__movieFiles is not None and len(self.__movieFiles):
            self.__showNextMovie()
            return
        else:
            LOG_DEBUG('Startup Video: STOP')
            self.__sendResult(True)
            return

    def handleError(self, data):
        self.__sendResult(False, 'Startup Video: ERROR - NetStream code = {0:>s}'.format(data))

    def _populate(self):
        super(IntroPage, self)._populate()
        if self.__movieFiles is not None and len(self.__movieFiles):
            self.__showNextMovie()
        else:
            self.__sendResult(False, 'There is no movie files for broadcast!')
        return

    def _dispose(self):
        super(IntroPage, self)._dispose()

    def __showNextMovie(self):
        moviePath = self.__movieFiles.pop(0)
        if moviePath in GUI_SETTINGS.compulsoryIntroVideos:
            self.__showMovie(moviePath, False)
        elif isIntroVideoSettingChanged():
            self.__showMovie(moviePath, True)
            self.__writeSetting = True
        else:
            LOG_DEBUG('Startup Video skipped: {}'.format(moviePath))
            if self.__movieFiles is not None and len(self.__movieFiles):
                self.__showNextMovie()
            else:
                self.__sendResult(True)
        return

    def __showMovie(self, movie, canSkip):
        LOG_DEBUG('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.__soundValue * 100))
        self.as_playVideoS({'source': movie,
         'volume': self.__soundValue,
         'canSkip': canSkip})

    def __sendResult(self, isSuccess, msg=''):
        """
        Call callback and send result of work
        @param isSuccess: is result of current component working has no errors
        @param msg: described reason of error
        """
        if not isSuccess:
            LOG_ERROR(msg)
        if self.__writeSetting:
            writeIntroVideoSetting()
        self.fireEvent(events.GlobalSpaceEvent(events.GlobalSpaceEvent.GO_NEXT))
