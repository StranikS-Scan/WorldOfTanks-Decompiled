# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangar.py
from gui.Scaleform.daapi.view.meta.BCHangarMeta import BCHangarMeta
from bootcamp.Bootcamp import g_bootcamp
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import events
from bootcamp.BootCampEvents import g_bootcampEvents

class BCHangar(BCHangarMeta):

    def __init__(self, ctx=None):
        super(BCHangar, self).__init__(ctx)

    def showNewElements(self, newElements):
        self.as_showAnimatedS(newElements)

    def updateVisibleComponents(self, visibleSettings):
        if visibleSettings is None:
            visibleSettings = g_bootcamp.getLobbySettings()
        self.as_setBootcampDataS(visibleSettings)
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}) and not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_OUTRO_VIDEO}) and not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def showHelpLayout(self):
        pass

    def _onPopulateStarted(self):
        self.as_setBootcampDataS(g_bootcamp.getLobbySettings())

    def _onPopulateEnd(self):
        g_bootcampEvents.onRequestChangeResearchButtonState += self.researchPanel.setNavigationEnabled

    def _dispose(self):
        g_bootcampEvents.onRequestChangeResearchButtonState -= self.researchPanel.setNavigationEnabled
        g_bootcampEvents.onHangarDispose()
        super(BCHangar, self)._dispose()
