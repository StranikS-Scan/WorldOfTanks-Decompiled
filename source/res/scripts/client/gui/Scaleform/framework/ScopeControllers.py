# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/ScopeControllers.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent
from shared_utils import findFirst
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.Scaleform.framework import ScopeTemplates
from soft_exception import SoftException

class ScopeControllerError(SoftException):
    pass


class ScopeController(DisposableEntity):

    def __init__(self, scope):
        super(ScopeController, self).__init__()
        self.__currentType = scope.getScopeType()
        self.__subControllers = []
        self.__mainView = None
        self.__views = []
        self.__loadingViews = []
        return

    @property
    def mainView(self):
        return self.__mainView

    def getCurrentType(self):
        return self.__currentType

    def getViewByKey(self, key):
        view = findFirst(lambda v: v.key == key, self.__views, None)
        if view is None:
            for c in self.__subControllers:
                view = c.getViewByKey(key)
                if view is not None:
                    break

        return view

    def getLoadingViewByKey(self, key):
        view = findFirst(lambda v: v.key == key, self.__loadingViews, None)
        if view is None:
            for c in self.__subControllers:
                view = c.getLoadingViewByKey(key)
                if view is not None:
                    break

        return view

    def findViews(self, comparator):
        views = [ v for v in self.__views if comparator(v) ]
        views.extend([ v for v in self.__loadingViews if comparator(v) ])
        for c in self.__subControllers:
            views.extend(c.findViews(comparator))

        return views

    def getLoadingViewsByType(self, viewType):
        views = {v for v in self.__loadingViews if v.viewType == viewType}
        for scopeController in self.__subControllers:
            views.update(scopeController.getLoadingViewsByType(viewType))

        return views

    def getLoadingViewsByScope(self, scopeType=None):
        views = set()
        ctrl = self.getScopeControllerForScopeType(scopeType)
        if ctrl is not None:
            views.update(ctrl.__getLoadingViews())
        return views

    def addSubController(self, scopeController):
        if scopeController not in self.__subControllers:
            scopeController.onDispose += self.__handleSubControllerDispose
            self.__subControllers.append(scopeController)

    def removeSubScopeController(self, scopeType):
        subControllers = self.__subControllers[:]
        for removingScopeController in subControllers:
            if removingScopeController.getCurrentType() == scopeType:
                self.__removeSubController(removingScopeController)
                removingScopeController.destroy()
            removingScopeController.removeSubScopeController(scopeType)

    def isViewLoading(self, pyView=None, key=None):
        if pyView is not None:
            outcome = pyView in self.__loadingViews
            if not outcome:
                for scopeController in self.__subControllers:
                    outcome = scopeController.isViewLoading(pyView)
                    if outcome:
                        break

            return outcome
        elif key is not None:
            return self.getLoadingViewByKey(key) is not None
        else:
            raise SoftException('pyView or pyView alias can not be None!')
            return

    def addView(self, pyView, addAsGlobal):
        if addAsGlobal:
            if pyView in self.__loadingViews:
                self.__loadingViews.remove(pyView)
            pyView.onDispose += self._handleViewDispose
            self.__views.append(pyView)
        else:
            scope = self.extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addView(pyView, True)

    def addLoadingView(self, pyView, addAsGlobal):
        if pyView is None:
            raise SoftException('pyView can not be None!')
        if addAsGlobal:
            pyView.onDispose += self._handleViewDispose
            self.__loadingViews.append(pyView)
        else:
            scope = self.extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addLoadingView(pyView, True)
        return

    def removeLoadingView(self, pyView):
        if pyView is not None:
            if pyView in self.__loadingViews:
                pyView.onDispose -= self._handleViewDispose
                self.__loadingViews.remove(pyView)
                if not self.__views and not self.__loadingViews:
                    self.destroy()
                return True
            for scopeController in self.__subControllers:
                if scopeController.removeLoadingView(pyView):
                    return True

        return False

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

    @classmethod
    def extractScopeFromView(cls, pyView):
        scope = pyView.viewScope
        return pyView.getCurrentScope() if scope.getScopeType() == ScopeTemplates.DYNAMIC_SCOPE.getScopeType() else scope

    def _dispose(self):
        self.__mainView = None
        self.__removeAllSubControllers()
        self.__clearLoadingViews()
        self.__destroyViews()
        super(ScopeController, self)._dispose()
        return

    def _handleViewDispose(self, pyView):
        pyView.onDispose -= self._handleViewDispose
        if pyView in self.__loadingViews:
            self.__loadingViews.remove(pyView)
        elif pyView in self.__views:
            self.__views.remove(pyView)
        if not self.__views and not self.__loadingViews:
            self.destroy()

    def _getScopeControllerForScope(self, scope):
        scopeType = scope.getScopeType()
        existingScopeController = self.getScopeControllerForScopeType(scopeType)
        if existingScopeController is None:
            outcome = self.__searchOwnerAndCreateControllerChain(scope)
            if outcome is None:
                raise ScopeControllerError('Could not to construct scopeController for {}'.format(scope))
            return outcome
        else:
            return existingScopeController
            return

    def __getLoadingViews(self):
        views = set()
        views.update(self.__loadingViews)
        for c in self.__subControllers:
            views.update(c.__getLoadingViews())

        return views

    def __handleSubControllerDispose(self, subController):
        self.__removeSubController(subController)

    def __removeSubController(self, subController):
        subController.onDispose -= self.__handleSubControllerDispose
        self.__subControllers.remove(subController)

    def __removeAllSubControllers(self):
        while self.__subControllers:
            scopeController = self.__subControllers[0]
            self.__removeSubController(scopeController)
            scopeController.destroy()

    def __searchOwnerAndCreateControllerChain(self, scope):
        ownScopes = ScopeTemplates.GLOBAL_SCOPE.searchOwnersFor(scope)
        if not ownScopes:
            raise ScopeControllerError('Could not to construct scopeController for {} - own scopes can not be found'.format(scope))
        newController = None
        for ownScope in ownScopes:
            ownController = self.getScopeControllerForScopeType(ownScope.getScopeType())
            if ownController is None:
                ownController = self.__searchOwnerAndCreateControllerChain(ownScope)
            if ownController is not None:
                if newController is None:
                    newController = ScopeController(scope)
                    newController.create()
                ownController.addSubController(newController)
            raise ScopeControllerError('Could not create a controllers chain!')

        return newController

    def __destroyViews(self):
        self.__destroyViewsFrom(self.__views)

    def __clearLoadingViews(self):
        self.__clearViewsFrom(self.__loadingViews)

    @classmethod
    def __destroyViewsFrom(cls, views):
        while views:
            pyView = views.pop()
            pyView.onDispose -= cls._handleViewDispose
            if not pyView.isDisposed():
                pyView.destroy()

    @classmethod
    def __clearViewsFrom(cls, views):
        while views:
            pyView = views.pop()
            pyView.onDispose -= cls._handleViewDispose

    def __repr__(self):
        return '{}[{}]=[type=[{}], mainView=[{}], views=[{}], loadingViews=[{}], child=[{}]]'.format(self.__class__.__name__, hex(id(self)), self.__currentType, self.__mainView, self.__views, self.__loadingViews, self.__subControllers)


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
            if pyView.viewType in ScopeTemplates.VIEW_TYPES_TO_SCOPES.keys():
                mainScope = ScopeTemplates.VIEW_TYPES_TO_SCOPES[pyView.viewType]
                mainController = self._getScopeControllerForScope(mainScope)
                mainController.switchMainView(pyView)
            customScope = self.getScopeControllerForScopeType(pyView.getAlias())
            if customScope is not None:
                customScope.switchMainView(pyView)
        super(GlobalScopeController, self).addView(pyView, addAsGlobal)
        return

    def _handleViewDispose(self, pyView):
        if pyView.viewType in ScopeTemplates.VIEW_TYPES_TO_SCOPES.keys():
            mainScope = ScopeTemplates.VIEW_TYPES_TO_SCOPES[pyView.viewType]
            mainController = self.getScopeControllerForScopeType(mainScope.getScopeType())
            if mainController is not None and mainController.mainView == pyView:
                mainController.switchMainView(None)
        self.__removeCustomScope(pyView, pyView.getAlias())
        super(GlobalScopeController, self)._handleViewDispose(pyView)
        return

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
