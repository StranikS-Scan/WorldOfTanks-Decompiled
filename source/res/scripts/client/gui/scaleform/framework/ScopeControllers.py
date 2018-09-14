# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/ScopeControllers.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent
from shared_utils import findFirst
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.Scaleform.framework import ScopeTemplates

class ScopeControllerError(StandardError):
    """
    General class for all ScopeController-specific exceptions.
    """
    pass


class ScopeController(DisposableEntity):
    """
    The class provides functionality to manage views lifetime based on 'view scope' concept.
    The controller holds references to views that are already loaded or are being loaded. It has a
    hierarchical structure, where views are grouped by their scope. The controller can includes
    sub controllers (it depends on scope hierarchy, for details see ScopeTemplates.py and
    VIEW_TYPES_TO_SCOPES enum) with subviews.
    Several views can belong to the same scope, but only one scope controller for a particular
    scope can exist at runtime. The controller listens view's onModuleDispose event to maintain
    its own state (list of loading/loaded views) in actual state. If all views that are belong
    to the same scope are destroyed, the scope controller is destroyed too automatically.
    """

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
        self.__subControllers = []
        self.__destroyViews()
        self.__views = []
        super(ScopeController, self)._dispose()
        return

    def getCurrentType(self):
        """
        Returns controller's scope type (see SCOPE_TYPE enum).
        """
        return self.__currentType

    def getViewByKey(self, key):
        """
        Finds a view with the given alias in the list of loaded views. If there is no view in
        the inner list, tries to find it in sub controllers.
        
        :param key: View key represented by tuple (alias, view name)
        :return: Reference to view object or None if there is no view with the given alias.
        """
        view = findFirst(lambda v: v.key == key, self.__views, None)
        if view is None:
            for c in self.__subControllers:
                view = c.getViewByKey(key)
                if view is not None:
                    break

        return view

    def getLoadingViewByKey(self, key):
        """
        Finds a view with the given alias in the list of views being loaded now. If there is no
        such view tries to find it in sub-controllers.
        
        :param key: View key represented by tuple (alias, view name)
        :return: Reference to view object or None if there is no view with the given alias.
        """
        view = findFirst(lambda v: v.key == key, self.__loadingViews, None)
        if view is None:
            for c in self.__subControllers:
                view = c.getLoadingViewByKey(key)
                if view is not None:
                    break

        return view

    def getLoadingViewsByType(self, viewType):
        """
        Returns a set of views with the given view type that are being loaded in memory now.
        
        :param viewType: type of view. @see ViewTypes.
        :return:  Set of View objects.
        """
        views = {v for v in self.__loadingViews if v.settings.type == viewType}
        for scopeController in self.__subControllers:
            views.update(scopeController.getLoadingViewsByType(viewType))

        return views

    def getLoadingViewsByScope(self, scopeType=None):
        """
        Returns a set of views that belong to the given scope (child views) and are being loaded
        in memory now.
        
        :param scopeType: Scope type.
        :return: Set of View objects.
        """
        views = set()
        ctrl = self.getScopeControllerForScopeType(scopeType)
        if ctrl is not None:
            views.update(ctrl.__getLoadingViews())
        return views

    def addSubController(self, scopeController):
        """
        Adds sub controller to the inner hierarchy based on its scope.
        
        :param scopeController: Reference to a scope controller
        """
        if scopeController not in self.__subControllers:
            scopeController.onModuleDispose += self.__handleSubControllerDispose
            self.__subControllers.append(scopeController)

    def removeSubScopeController(self, scopeType):
        """
        Finds sub controller with the given scope in the inner hierarchy and removes it.
        
        :param scopeType: Scope type (see SCOPE_TYPE enum).
        """
        subControllers = self.__subControllers[:]
        for removingScopeController in subControllers:
            if removingScopeController.getCurrentType() == scopeType:
                self.__removeSubController(removingScopeController)
                removingScopeController.destroy()
            removingScopeController.removeSubScopeController(scopeType)

    def isViewLoading(self, pyView=None, key=None):
        """
        Checks if the given view is being loaded now (check is preformed by all hierarchy,
        including sub-controllers).
        
        :param pyView: Reference to a view objects.
        :param key: View key represented by tuple (alias, view name) to be used for an alternative
                    search.
        :return: True if the given view is in loading list, otherwise False.
        """
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
            raise ValueError('pyView or pyView alias can not be None!')
            return

    def addView(self, pyView, addAsGlobal):
        """
        Adds the loaded view to the proper controller (or sub controller) based on view's
        scope and removes it from the loading list.
        
        :param pyView: Reference to a view objects.
        :param addAsGlobal: Flags indicating whether the given view should be added to the inner
        views list, ignoring view's scope.
        """
        if addAsGlobal:
            if pyView in self.__loadingViews:
                self.__loadingViews.remove(pyView)
            pyView.onModuleDispose += self.__handleViewDispose
            self.__views.append(pyView)
        else:
            scope = self.extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addView(pyView, True)

    def addLoadingView(self, pyView, addAsGlobal):
        """
        Adds view (being loaded now) into the proper controller (or sub controller)
        based on view's scope.
        
        :param pyView: Reference to a view objects.
        :param addAsGlobal: Flags indicating whether the given view should be added to the inner
        loading list, ignoring view's scope.
        :return:
        """
        if pyView is None:
            raise ValueError('pyView can not be None!')
        if addAsGlobal:
            self.__loadingViews.append(pyView)
        else:
            scope = self.extractScopeFromView(pyView)
            controller = self._getScopeControllerForScope(scope)
            controller.addLoadingView(pyView, True)
        return

    def removeLoadingView(self, pyView):
        """
        Removes view from the loading list.
        
        :param pyView: Reference to a view objects.
        :return: bool, True if the view has been removed, otherwise False..
        """
        if pyView is not None:
            if pyView in self.__loadingViews:
                self.__loadingViews.remove(pyView)
                if not self.__views and not self.__loadingViews:
                    self.destroy()
                return True
            for scopeController in self.__subControllers:
                if scopeController.removeLoadingView(pyView):
                    return True

        return False

    def switchMainView(self, pyView):
        """
        Switchs the main view to the given one. Previous main view (and its sub views located in
        the sub controllers) is destroyed. Sub controllers are destroyed too.
        
        :param pyView: Reference to a view objects.
        """
        if self.__mainView != pyView:
            if self.__mainView is not None:
                self.__removeAllSubControllers()
                self.__destroyViews()
            self.__mainView = pyView
        return

    def getScopeControllerForScopeType(self, scopeType):
        """
        Finds a sub controller (or itself) with the given scope type.
        
        :param scopeType: Scope type (see SCOPE_TYPE enum).
        :return: Reference to scope controller or None.
        """
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
    def extractScopeFromView(self, pyView):
        scope = pyView.settings.scope
        if scope.getScopeType() == ScopeTemplates.DYNAMIC_SCOPE.getScopeType():
            return pyView.getCurrentScope()
        else:
            return scope

    def _getScopeControllerForScope(self, scope):
        """
        Returns scope, that currentScopeType == pyView.scopeType
        
        :param scope: scope, a SimpleScope derived instance
        """
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
        """
        Returns all view (including subview in sub-controllers) that are being loaded now.
        :return: set of views
        """
        views = set()
        views.update(self.__loadingViews)
        for c in self.__subControllers:
            views.update(c.__getLoadingViews())

        return views

    def __handleSubControllerDispose(self, subController):
        self.__removeSubController(subController)

    def __removeSubController(self, subController):
        subController.onModuleDispose -= self.__handleSubControllerDispose
        self.__subControllers.remove(subController)

    def __handleViewDispose(self, pyView):
        pyView.onModuleDispose -= self.__handleViewDispose
        self.__views.remove(pyView)
        if not self.__views and not self.__loadingViews:
            self.destroy()

    def __removeAllSubControllers(self):
        while len(self.__subControllers) > 0:
            scopeController = self.__subControllers[0]
            self.__removeSubController(scopeController)
            scopeController.destroy()

    def __searchOwnerAndCreateControllerChain(self, scope):
        ownScopes = ScopeTemplates.GLOBAL_SCOPE.searchOwnersFor(scope)
        if len(ownScopes) == 0:
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
