# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroVideoPage.py
import SoundGroups
from bc_intro_page import BCIntroPage, INTRO_HIGHLIGHT_TYPE
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from bootcamp.BootCampEvents import g_bootcampEvents

class BCIntroVideoPage(BCIntroPage, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, settings):
        super(BCIntroVideoPage, self).__init__(settings)
        self._movieFile = settings.get('video', '')
        self._soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self._videoPlayerVisible = True
        self._goToBattleEvent = g_bootcampEvents.onBootcampGoNext

    def onIntroVideoLoaded(self):
        self.as_loadedS()
        if self._shouldHighlight(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, True)
        if self._isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, False)

    def stopVideo(self):
        self._onFinish()

    def onArenaStarted(self):
        self.destroy()

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)

    def _populate(self):
        g_bootcampEvents.onArenaStarted += self.onArenaStarted
        g_bootcampEvents.onIntroVideoLoaded += self.onIntroVideoLoaded
        self.sessionProvider.addArenaCtrl(self)
        super(BCIntroVideoPage, self)._populate()

    def _dispose(self):
        g_bootcampEvents.onIntroVideoLoaded -= self.onIntroVideoLoaded
        g_bootcampEvents.onArenaStarted -= self.onArenaStarted
        self.sessionProvider.removeArenaCtrl(self)
        super(BCIntroVideoPage, self)._dispose()

    def _onFinish(self):
        g_bootcampEvents.onIntroVideoStop()
