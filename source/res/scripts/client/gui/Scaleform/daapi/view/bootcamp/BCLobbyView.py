# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyView.py
from gui.Scaleform.daapi.view.bootcamp.BCAmmunitionPanelObserver import BCAmmunitionPanelObserver
from gui.Scaleform.daapi.view.bootcamp.BCCrewObserver import BCCrewObserver
from gui.Scaleform.daapi.view.bootcamp.BCHangarObserver import BCHangarObserver
from gui.Scaleform.daapi.view.bootcamp.BCPersonalCaseOberserver import BCPersonalCaseObserver
from gui.Scaleform.daapi.view.bootcamp.BCLobbyObserver import BCLobbyObserver
from gui.Scaleform.daapi.view.bootcamp.BCLobbyHeaderObserver import BCLobbyHeaderObserver
from gui.Scaleform.daapi.view.bootcamp.BCTechnicalMaintenanceObserver import BCTechnicalMaintenanceObserver
from gui.Scaleform.daapi.view.lobby.LobbyView import LobbyView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from bootcamp.BootCampEvents import g_bootcampEvents
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from bootcamp.BootcampLobbyAppearConfig import g_bootcampAppearConfig

class BCLobbyView(LobbyView):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, ctx=None):
        LobbyView.__init__(self, ctx)
        self.onAnimationsCompleteCallback = None
        self.__lastAnimatedElements = None
        self.__animationInProgress = False
        self.__observer = None
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
        headerComponent.showNewElements(newElements['keys'])
        if self.__observer is not None:
            self.__observer.as_showAnimatedS(newElements['keys'])
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
            visibleSettings = self.bootcampCtrl.getLobbySettings()
        if self.__observer:
            self.__observer.as_setBootcampDataS(visibleSettings)
        headerComponent = self.getComponent(VIEW_ALIAS.LOBBY_HEADER)
        headerComponent.updateVisibleComponents(visibleSettings)
        return

    def _populate(self):
        registerObserver = self.app.bootcampManager.registerObserverClass
        registerObserver('BCPersonalCaseObserver', BCPersonalCaseObserver)
        registerObserver('BCTechnicalMaintenanceObserver', BCTechnicalMaintenanceObserver)
        registerObserver('BCAmmunitionPanelObserver', BCAmmunitionPanelObserver)
        registerObserver('BCCrewObserver', BCCrewObserver)
        registerObserver('BCHangarObserver', BCHangarObserver)
        registerObserver('BCLobbyHeaderObserver', BCLobbyHeaderObserver)
        registerObserver('BCLobbyObserver', BCLobbyObserver)
        LobbyView._populate(self)
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage:
            self.app.loaderManager.onViewLoaded += g_bootcampGarage.onViewLoaded
        self.__observer = self.app.bootcampManager.getObserver('BCLobbyObserver')
        if self.__observer is not None:
            self.__observer.onAnimationsCompleteEvent += self.onAnimationsComplete
            self.__observer.as_setBootcampDataS(self.bootcampCtrl.getLobbySettings())
            self.__observer.as_setAppearConfigS(g_bootcampAppearConfig.getItems())
        return

    def _dispose(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage:
            self.app.loaderManager.onViewLoaded -= g_bootcampGarage.onViewLoaded
        self.onAnimationsComplete()
        g_bootcampEvents.onHangarDispose -= self.onAnimationsComplete
        if self.__observer is not None:
            self.__observer.onAnimationsCompleteEvent -= self.onAnimationsComplete
            self.__observer = None
        unregisterObserver = self.app.bootcampManager.unregisterObserverClass
        unregisterObserver('BCPersonalCaseObserver')
        unregisterObserver('BCTechnicalMaintenanceObserver')
        unregisterObserver('BCAmmunitionPanelObserver')
        unregisterObserver('BCCrewObserver')
        unregisterObserver('BCHangarObserver')
        unregisterObserver('BCLobbyHeaderObserver')
        unregisterObserver('BCLobbyObserver')
        LobbyView._dispose(self)
        return

    def _onVehicleBecomeElite(self, vehTypeCompDescr):
        pass
