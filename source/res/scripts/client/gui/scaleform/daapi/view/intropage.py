# Embedded file name: scripts/client/gui/Scaleform/daapi/view/IntroPage.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.IntroPageMeta import IntroPageMeta
import SoundGroups
from gui.Scaleform.managers.Cursor import Cursor
from gui.doc_loaders.GuiDirReader import GuiDirReader

class IntroPage(View, IntroPageMeta, AppRef):

    def __init__(self, ctx):
        super(IntroPage, self).__init__()
        self.__resultCallback = ctx.get('resultCallback')
        self.__movieFiles = GuiDirReader.getAvailableIntroVideoFiles()
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2

    def _populate(self):
        super(IntroPage, self)._populate()
        if self.__movieFiles is not None and len(self.__movieFiles):
            BigWorld.wg_setMovieSoundMuted(False)
            self.__showNextMovie()
        else:
            self.__sendResult(False, 'There is no movie files for broadcast!')
        return

    def __showNextMovie(self):
        self.__showMovie(self.__movieFiles.pop(0))

    def __showMovie(self, movie):
        LOG_DEBUG('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.__soundValue * 100))
        self.as_playVideoS({'source': movie,
         'volume': self.__soundValue})

    def __sendResult(self, isSuccess, msg = ''):
        """
        Call callback and send result of work
        @param isSuccess: is result of current component working has no errors
        @param msg: described reason of error
        """
        if self.__resultCallback is not None:
            self.__resultCallback(isSuccess, msg)
        return

    def _dispose(self):
        self.__resultCallback = None
        BigWorld.wg_setMovieSoundMuted(True)
        super(IntroPage, self)._dispose()
        return

    def stopVideo(self):
        if self.__movieFiles is not None and len(self.__movieFiles):
            self.__showNextMovie()
            return
        else:
            LOG_DEBUG('Startup Video: STOP')
            BigWorld.wg_setMovieSoundMuted(True)
            self.__sendResult(True)
            return

    def handleError(self, data):
        errorStr = 'Startup Video: ERROR - NetStream code = {0:>s}'.format(data)
        LOG_ERROR(errorStr)
        BigWorld.wg_setMovieSoundMuted(True)
        self.__sendResult(False, errorStr)
