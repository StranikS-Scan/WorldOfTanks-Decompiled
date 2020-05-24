# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/AbstractRallyWindow.py
from adisp import process
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.AbstractRallyWindowMeta import AbstractRallyWindowMeta
from gui.prb_control.entities.base.ctx import LeavePrbAction, PrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared.events import RallyWindowEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE

class AbstractRallyWindow(AbstractRallyWindowMeta, IPrbListener):

    def __init__(self):
        super(AbstractRallyWindow, self).__init__()
        self._viewToLoad = None
        self.addListener(RallyWindowEvent.ON_CLOSE, self.__onClose, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def getFlashAliases(self):
        return []

    def getPythonAliases(self):
        return []

    def minimizing(self):
        for component in self.components.itervalues():
            component.isMinimising = True

    def onWindowClose(self):
        self.fireEvent(RallyWindowEvent(RallyWindowEvent.ON_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)

    def _getPythonAlias(self, flashAlias):
        flashAliases = self.getFlashAliases()
        pythonAliases = self.getPythonAliases()
        pyAlias = None
        if flashAlias in flashAliases:
            pyAlias = pythonAliases[flashAliases.index(flashAlias)]
        return pyAlias

    def _requestViewLoad(self, flashAlias, itemID):
        pyAlias = self._getPythonAlias(flashAlias)
        if pyAlias is not None:
            self._viewToLoad = (flashAlias, pyAlias, itemID)
            self._currentView = flashAlias
            self.as_loadViewS(flashAlias, pyAlias)
        else:
            LOG_ERROR('Passed flash alias is not registered:', flashAlias)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(AbstractRallyWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if self._viewToLoad is not None:
            _, pyAlias, itemID = self._viewToLoad
            if pyAlias == alias:
                viewPy.setData(itemID)
                self._viewToLoad = None
        return

    def _dispose(self):
        self.removeListener(RallyWindowEvent.ON_CLOSE, self.__onClose, scope=EVENT_BUS_SCOPE.LOBBY)
        self._viewToUnload = None
        self._viewToLoad = None
        super(AbstractRallyWindow, self)._dispose()
        return

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))

    @process
    def _doSelect(self, prebattleActionName, accountsToInvite=None):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattleActionName, accountsToInvite=accountsToInvite))

    def __onClose(self, event):
        self._doLeave()
