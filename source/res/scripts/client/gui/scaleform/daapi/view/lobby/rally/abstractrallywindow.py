# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/AbstractRallyWindow.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.rally import NavigationStack
from gui.Scaleform.daapi.view.meta.AbstractRallyWindowMeta import AbstractRallyWindowMeta

class AbstractRallyWindow(AbstractRallyWindowMeta):

    def __init__(self):
        super(AbstractRallyWindow, self).__init__()
        self._viewToUnload = None
        self._viewToLoad = None
        return

    def _requestViewLoad(self, flashAlias, itemID, closeForced = False):
        flashAliases = self.getFlashAliases()
        pythonAliases = self.getPythonAliases()
        if flashAlias in flashAliases:
            pyAlias = pythonAliases[flashAliases.index(flashAlias)]
            self._viewToLoad = (flashAlias, pyAlias, itemID)
            self._processStacks(closeForced=closeForced)
        else:
            LOG_ERROR('Passed flash alias is not registered:', flashAlias)

    def _processStacks(self, closeForced = False):
        if self._viewToUnload is not None:
            flashAlias, pyAlias, itemID = self._viewToUnload
            pyView = self.components.get(pyAlias)
            if pyView is not None:
                if not closeForced:
                    pyView.canBeClosed(lambda canBeClosed: self._closeCallback(canBeClosed))
                else:
                    self._closeCallback(True)
        elif self._viewToLoad is not None:
            self._applyViewLoad()
        return

    def _applyViewLoad(self):
        flashAlias, pyAlias, itemID = self._viewToLoad
        self._currentView = flashAlias
        self.as_loadViewS(flashAlias, pyAlias)

    def _closeCallback(self, canBeClosed):
        self._viewToUnload = None
        if canBeClosed:
            NavigationStack.nav2Prev(self.getNavigationKey())
            self._processStacks()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(AbstractRallyWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if self._viewToLoad is not None:
            NavigationStack.nav2Next(self.getNavigationKey(), *self._viewToLoad)
            flashAlias, pyAlias, itemID = self._viewToLoad
            if pyAlias == alias:
                viewPy.setData(itemID)
                self._viewToLoad = None
        return

    def getNavigationKey(self):
        return 'BaseRallyMainWindow'

    def getFlashAliases(self):
        return []

    def getPythonAliases(self):
        return []

    def minimizing(self):
        for component in self.components.itervalues():
            component.isMinimising = True

    def _dispose(self):
        self._viewToUnload = None
        self._viewToLoad = None
        super(AbstractRallyWindow, self)._dispose()
        return
