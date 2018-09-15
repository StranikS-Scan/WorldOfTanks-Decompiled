# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangar.py
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import events
from bootcamp.BootCampEvents import g_bootcampEvents
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BCHangar(Hangar):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, ctx=None):
        super(BCHangar, self).__init__(ctx)
        self._observer = None
        return

    def showNewElements(self, newElements):
        list = newElements['keys']
        if self._observer is not None:
            self._observer.as_showAnimatedS(list)
        self.ammoPanel.showNewElements(list)
        return

    def updateVisibleComponents(self, visibleSettings):
        if visibleSettings is None:
            visibleSettings = self.bootcampCtrl.getLobbySettings()
        if self._observer is not None:
            self._observer.as_setBootcampDataS(visibleSettings)
        self.ammoPanel.updateVisibleComponents(visibleSettings)
        self.headerComponent.updateVisibleComponents(visibleSettings)
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}) and not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO}) and not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def showHelpLayout(self):
        pass

    def _onPopulateEnd(self):
        g_bootcampEvents.onRequestChangeResearchButtonState += self.researchPanel.setNavigationEnabled

    def _populate(self):
        super(BCHangar, self)._populate()
        self._observer = self.app.bootcampManager.getObserver('BCHangarObserver')
        if self._observer is not None:
            self._observer.as_setBootcampDataS(self.bootcampCtrl.getLobbySettings())
        return

    def _dispose(self):
        g_bootcampEvents.onRequestChangeResearchButtonState -= self.researchPanel.setNavigationEnabled
        g_bootcampEvents.onHangarDispose()
        self._observer = None
        super(BCHangar, self)._dispose()
        return
