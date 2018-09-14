# Embedded file name: scripts/client/gui/Scaleform/framework/ScopeControllers.py
__author__ = 'd_trofimov'
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.Scaleform.framework import ScopeTemplates

class ScopeController(DisposableEntity):

    def __init__(self, scope):
        super(ScopeController, self).__init__()
        self.__currentType = scope.getScopeType()
        self.__subControllers = []
        self.__mainView = None
        self.__views = []
        self.__loadingViews = []
        return

    def _dispose(self):
        self.__mainView = None
        self.__removeAllSubControllers()
        self.__subControllers = None
        self.__destroyViews()
        self.__views = None
        super(ScopeController, self)._dispose()
        return

    def addSubController(self, scopeController):
        scopeController.onModuleDispose += self.__handleSubControllerDispose
        self.__subControllers.append(scopeController)

    def __handleSubControllerDispose(self, subController):
        self.__removeSubController(subController)

    def __removeSubController(self, subController):
        subController.onModuleDispose -= self.__handleSubControllerDispose
        self.__subControllers.remove(subController)

    def __handleViewDispose(self, pyView):
        pyView.onModuleDispose -= self.__handleViewDispose
        self.__views.remove(pyView)
        if len(self.__views) == 0 and len(self.__loadingViews) == 0:
            self.destroy()

    def __removeAllSubControllers(self):
        while len(self.__subControllers) > 0:
            scopeController = self.__subControllers[0]
            self.__removeSubController(scopeController)
            scopeController.destroy()

    def getCurrentType(self):
        return self.__currentType

    def removeSubScopeController(self, scopeType):
        for removingScopeController in self.__subControllers:
            if removingScopeController.getCurrentType() == scopeType:
                self.__removeSubController(removingScopeController)
                removingScopeController.destroy()
            else:
                removingScopeController.removeSubScopeController(scopeType)

    def isViewLoading(self, pyView):
        outcome = pyView in self.__loadingViews
        if not outcome:
            for scopeController in self.__subControllers:
                outcome = outcome or scopeController.isViewLoading(pyView)
                if outcome:
                    break

        return outcome

    def addView(self, pyView, addAsGlobal):
        if addAsGlobal:
            if pyView in self.__loadingViews:
                self.__loadingViews.remove(pyView)
            pyView.onModuleDispose += self.__handleViewDispose
            self.__views.append(pyView)
        else:
            scope = self.__extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addView(pyView, True)

    def addLoadingView(self, pyView, addAsGlobal):
        if pyView is None:
            raise Exception('pyView can not be None!')
        if addAsGlobal:
            self.__loadingViews.append(pyView)
        else:
            scope = self.__extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addLoadingView(pyView, True)
        return

    def switchMainView(self, pyView):
        if self.__mainView != pyView:
            if self.__mainView is not None:
                self.__removeAllSubControllers()
                self.__destroyViews()
            self.__mainView = pyView
        return

    def getScopeControllerForScopeType(self, scopeType):
        if self.__currentType != scopeType:
            if self.__subControllers:
                for scopeController in self.__subControllers:
                    searchedScopeController = scopeController.getScopeControllerForScopeType(scopeType)
                    if searchedScopeController is not None:
                        return searchedScopeController

            return
        else:
            return self
            return

    def _getScopeControllerForScope(self, scope):
        scopeType = scope.getScopeType()
        existingScopeController = self.getScopeControllerForScopeType(scopeType)
        if existingScopeController is None:
            outcome = self.__searchOwnerAndCreateControllerChain(scope)
            if outcome is None:
                raise Exception('Could not to construct scopeController for %s' % scope)
            return outcome
        else:
            return existingScopeController
            return

    def __searchOwnerAndCreateControllerChain(self, scope):
        ownScopes = ScopeTemplates.GLOBAL_SCOPE.searchOwnersFor(scope)
        if len(ownScopes) == 0:
            raise Exception('Could not to construct scopeController for %s - own scopes can not be found' % scope)
        newController = None
        for ownScope in ownScopes:
            ownController = self.getScopeControllerForScopeType(ownScope.getScopeType())
            if ownController is None:
                ownController = self.__searchOwnerAndCreateControllerChain(ownScope)
            if ownController is not None:
                if newController is None:
                    newController = ScopeController(scope)
                ownController.addSubController(newController)
            else:
                raise Exception('could not create a controllers chain!')

        return newController

    def __extractScopeFromView(self, pyView):
        scope = pyView.settings.scope
        if scope.getScopeType() == ScopeTemplates.DYNAMIC_SCOPE.getScopeType():
            return pyView.getCurrentScope()
        else:
            return scope

    def __destroyViews(self):
        while self.__loadingViews is not None and len(self.__loadingViews) > 0:
            pyView = self.__loadingViews.pop()
            pyView.onModuleDispose -= self.__handleViewDispose

        while self.__views is not None and len(self.__views) > 0:
            pyView = self.__views.pop()
            pyView.onModuleDispose -= self.__handleViewDispose
            pyView.destroy()

        return


class GlobalScopeController(ScopeController):

    def __init__(self):
        super(GlobalScopeController, self).__init__(ScopeTemplates.GLOBAL_SCOPE)

    def _populate(self):
        super(GlobalScopeController, self)._populate()
        g_eventBus.addListener(ComponentEvent.COMPONENT_REGISTERED, self.__componentRegisteringHandler, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(ComponentEvent.COMPONENT_UNREGISTERED, self.__componentUnRegisteringHandler, EVENT_BUS_SCOPE.GLOBAL)

    def _dispose(self):
        super(GlobalScopeController, self)._dispose()
        g_eventBus.removeListener(ComponentEvent.COMPONENT_REGISTERED, self.__componentRegisteringHandler, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(ComponentEvent.COMPONENT_UNREGISTERED, self.__componentUnRegisteringHandler, EVENT_BUS_SCOPE.GLOBAL)

    def addView(self, pyView, addAsGlobal):
        if not addAsGlobal:
            if pyView.settings.type in ScopeTemplates.VIEW_TYPES_TO_SCOPES.keys():
                mainScope = ScopeTemplates.VIEW_TYPES_TO_SCOPES[pyView.settings.type]
                mainController = self._getScopeControllerForScope(mainScope)
                mainController.switchMainView(pyView)
            customScope = self.getScopeControllerForScopeType(pyView.alias)
            if customScope is not None:
                customScope.switchMainView(pyView)
            pyView.onModuleDispose += self.__onDisposeViewWithCustomScope
        super(GlobalScopeController, self).addView(pyView, addAsGlobal)
        return

    def __onDisposeViewWithCustomScope(self, pyView):
        pyView.onModuleDispose -= self.__onDisposeViewWithCustomScope
        self.__removeCustomScope(pyView, pyView.alias)

    def __removeCustomScope(self, view, alias):
        customScopeController = self.getScopeControllerForScopeType(alias)
        if customScopeController is not None:
            customScopeController.switchMainView(view)
            customScopeController.switchMainView(None)
        return

    def __componentRegisteringHandler(self, event):
        customScopeController = self.getScopeControllerForScopeType(event.alias)
        if customScopeController is not None:
            customScopeController.switchMainView(event.componentPy)
        return

    def __componentUnRegisteringHandler(self, event):
        self.__removeCustomScope(event.componentPy, event.alias)
