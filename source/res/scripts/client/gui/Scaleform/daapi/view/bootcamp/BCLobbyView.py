# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyView.py
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.Scaleform.daapi.view.meta.BCLobbyViewMeta import BCLobbyViewMeta
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootCampEvents import g_bootcampEvents
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

class BCLobbyView(BCLobbyViewMeta):

    def __init__(self, ctx=None):
        BCLobbyViewMeta.__init__(self, ctx)
        self.onAnimationsCompleteCallback = None
        self.__lastAnimatedElements = None
        self.__animationInProgress = False
        g_bootcampEvents.onHangarDispose += self.onAnimationsComplete
        return

    def showNewElements(self, newElements):
        self.onAnimationsCompleteCallback = newElements['callback']
        self.__lastAnimatedElements = newElements['keys']
        if self.__lastAnimatedElements is not None:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.updateLobbyLobbySettings(self.__lastAnimatedElements)
            self.__lastAnimatedElements = None
        self.__animationInProgress = True
        headerComponent = self.getComponent(VIEW_ALIAS.LOBBY_HEADER)
        headerComponent.as_showAnimatedS(newElements)
        self.as_showAnimatedS(newElements)
        return

    def onAnimationsComplete(self):
        if not self.__animationInProgress:
            return
        else:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.resumeLesson()
            g_bootcampGarage.runViewAlias('hangar')
            if self.onAnimationsCompleteCallback is not None:
                self.onAnimationsCompleteCallback()
                self.onAnimationsCompleteCallback = None
            self.__animationInProgress = False
            return

    def updateVisibleComponents(self, visibleSettings):
        if visibleSettings is None:
            visibleSettings = g_bootcamp.getLobbySettings()
        self.as_setBootcampDataS(visibleSettings)
        headerComponent = self.getComponent(VIEW_ALIAS.LOBBY_HEADER)
        headerComponent.updateVisibleComponents()
        return

    def _populate(self):
        self.as_setBootcampDataS(g_bootcamp.getLobbySettings())
        LobbyView._populate(self)
        from bootcamp.BootcampLobbyAppearConfig import g_bootcampAppearConfig
        self.as_setAppearConfigS(g_bootcampAppearConfig.getItems())
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage:
            self.app.loaderManager.onViewLoaded += g_bootcampGarage.onViewLoaded

    def _dispose(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage:
            self.app.loaderManager.onViewLoaded -= g_bootcampGarage.onViewLoaded
        self.onAnimationsComplete()
        g_bootcampEvents.onHangarDispose -= self.onAnimationsComplete
        LobbyView._dispose(self)

    def _onVehicleBecomeElite(self, vehTypeCompDescr):
        pass
