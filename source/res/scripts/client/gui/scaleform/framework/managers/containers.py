# Embedded file name: scripts/client/gui/Scaleform/framework/managers/containers.py
import weakref, types
from Event import Event
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.ScopeControllers import GlobalScopeController
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.abstract.ContainerManagerMeta import ContainerManagerMeta

class IViewContainer(object):

    def add(self, pyView):
        raise NotImplementedError, 'IViewContainer.add must be implemented'

    def remove(self, pyView):
        raise NotImplementedError, 'IViewContainer.remove must be implemented'

    def clear(self):
        raise NotImplementedError, 'IViewContainer.clear must be implemented'

    def destroy(self):
        raise NotImplementedError, 'IViewContainer.destroy must be implemented'

    def getView(self, criteria = None):
        raise NotImplementedError, 'IViewContainer.getView must be implemented'

    def getViewCount(self, **kwargs):
        raise NotImplementedError, 'IViewContainer.getViewCount must be implemented'

    def canCancelPreviousLoading(self):
        raise NotImplementedError, 'IViewContainer.canCancelPreviousLoading must be implemented'


class _DefaultContainer(IViewContainer):

    def __init__(self, manager):
        super(_DefaultContainer, self).__init__()
        self.__manager = manager
        self.__view = None
        return

    def add(self, pyView):
        if self.__view is not None:
            self.__view.destroy()
        pyView.onModuleDispose += self.__handleModuleDispose
        self.__view = pyView
        return True

    def remove(self, pyView):
        if self.__view == pyView:
            self.__view.onModuleDispose -= self.__handleModuleDispose
            self.__manager.as_hideS(self.__view.uniqueName)
            self.__view = None
        return

    def clear(self):
        if self.__view is not None:
            subContainerType = self.__view.getSubContainerType()
            if subContainerType is not None:
                self.__manager.removeContainer(subContainerType)
            self.__view.onModuleDispose -= self.__handleModuleDispose
            self.__manager.as_hideS(self.__view.uniqueName)
            viewKey = (self.__view.alias, self.__view.uniqueName)
            if viewKey in self.__manager._loadingViews:
                self.__manager._loadingViews.pop(viewKey)
            self.__view.destroy()
            self.__view = None
        return

    def destroy(self):
        self.clear()
        self.__manager = None
        return

    def canCancelPreviousLoading(self):
        return True

    def __handleModuleDispose(self, pyView):
        subContainerType = pyView.getSubContainerType()
        if subContainerType is not None:
            self.__manager.removeContainer(subContainerType)
        viewKey = (pyView.alias, pyView.uniqueName)
        if viewKey in self.__manager._loadingViews:
            self.__manager._loadingViews.pop(viewKey)
        self.remove(pyView)
        return

    def getView(self, criteria = None):
        result = None
        if criteria is None or self.__view is None:
            result = self.__view
        elif POP_UP_CRITERIA.UNIQUE_NAME in criteria:
            uniqueName = criteria[POP_UP_CRITERIA.UNIQUE_NAME]
            if self.__view.uniqueName == uniqueName:
                result = self.__view
        elif POP_UP_CRITERIA.VIEW_ALIAS in criteria:
            viewAlias = criteria[POP_UP_CRITERIA.VIEW_ALIAS]
            if self.__view.settings.alias == viewAlias:
                result = self.__view
        return result

    def getViewCount(self):
        if self.__view is not None:
            return 1
        else:
            return 0


class POP_UP_CRITERIA(object):
    VIEW_ALIAS = 1
    UNIQUE_NAME = 2


class ExternalCriteria(object):

    def __init__(self, criteria = None):
        super(ExternalCriteria, self).__init__()
        self._criteria = criteria

    def find(self, name, obj):
        raise NotImplemented, 'ExternalCriteria.find must be implemented'


class _PopUpContainer(IViewContainer):

    def __init__(self, manager):
        super(_PopUpContainer, self).__init__()
        self.__manager = manager
        self.__popUps = {}

    def add(self, pyView):
        uniqueName = pyView.uniqueName
        if uniqueName in self.__popUps:
            return False
        self.__popUps[uniqueName] = pyView
        pyView.onModuleDispose += self.__handleModuleDispose
        return True

    def remove(self, pyView):
        uniqueName = pyView.uniqueName
        if uniqueName in self.__popUps:
            popUp = self.__popUps.pop(uniqueName)
            popUp.onModuleDispose -= self.__handleModuleDispose
            self.__manager.as_hideS(popUp.uniqueName)
            LOG_DEBUG('PopUp has been successfully removed', pyView, uniqueName)
        else:
            LOG_WARNING('PopUp not found', pyView, uniqueName)

    def canCancelPreviousLoading(self):
        return False

    def clear(self):
        while len(self.__popUps):
            _, popUp = self.__popUps.popitem()
            subContainerType = popUp.getSubContainerType()
            if subContainerType is not None:
                self.__manager.removeContainer(subContainerType)
            popUp.onModuleDispose -= self.__handleModuleDispose
            self.__manager.as_hideS(popUp.uniqueName)
            popUp.destroy()

        return

    def destroy(self):
        self.clear()
        self.__manager = None
        return

    def getView(self, criteria = None):
        popUp = None
        if criteria is not None:
            if type(criteria) is types.DictionaryType:
                popUp = self.__findByDictCriteria(criteria)
            elif isinstance(criteria, ExternalCriteria):
                popUp = self.__findByExCriteria(criteria)
            else:
                LOG_ERROR('Criteria is invalid', criteria)
        return popUp

    def getViewCount(self, isModal = None):
        if isModal is None:
            result = len(self.__popUps)
        else:
            result = 0
            for popUp in self.__popUps.itervalues():
                try:
                    if isinstance(popUp, WindowViewMeta):
                        if popUp.as_isModalS() == isModal:
                            result += 1
                except AttributeError:
                    LOG_CURRENT_EXCEPTION()

        return result

    def __findByDictCriteria(self, criteria):
        popUp = None
        if POP_UP_CRITERIA.UNIQUE_NAME in criteria:
            uniqueName = criteria[POP_UP_CRITERIA.UNIQUE_NAME]
            if uniqueName in self.__popUps:
                popUp = self.__popUps[uniqueName]
        elif POP_UP_CRITERIA.VIEW_ALIAS in criteria:
            viewAlias = criteria[POP_UP_CRITERIA.VIEW_ALIAS]
            popUps = filter(lambda popUp: popUp.settings.alias == viewAlias, self.__popUps.values())
            if len(popUps):
                popUp = popUps[0]
        return popUp

    def __findByExCriteria(self, criteria):
        popUp = None
        popUps = filter(lambda item: criteria.find(*item), self.__popUps.iteritems())
        if len(popUps):
            popUp = popUps[0][1]
        return popUp

    def __handleModuleDispose(self, pyView):
        subContainerType = pyView.getSubContainerType()
        if subContainerType is not None:
            self.__manager.removeContainer(subContainerType)
        self.remove(pyView)
        return


class ContainerManager(ContainerManagerMeta):
    onViewAddedToContainer = Event()
    __DESTROY_ORDER = (ViewTypes.DEFAULT,
     ViewTypes.LOBBY_SUB,
     ViewTypes.WINDOW,
     ViewTypes.BROWSER,
     ViewTypes.TOP_WINDOW,
     ViewTypes.WAITING,
     ViewTypes.CURSOR,
     ViewTypes.SERVICE_LAYOUT)
    __CONTAINERS_TO_CLEAR = (ViewTypes.WINDOW, ViewTypes.BROWSER, ViewTypes.TOP_WINDOW)

    def __init__(self, loader):
        super(ContainerManager, self).__init__()
        proxy = weakref.proxy(self)
        self.__containers = {ViewTypes.DEFAULT: _DefaultContainer(proxy),
         ViewTypes.CURSOR: _DefaultContainer(proxy),
         ViewTypes.WAITING: _DefaultContainer(proxy),
         ViewTypes.WINDOW: _PopUpContainer(proxy),
         ViewTypes.BROWSER: _PopUpContainer(proxy),
         ViewTypes.TOP_WINDOW: _PopUpContainer(proxy),
         ViewTypes.SERVICE_LAYOUT: _DefaultContainer(proxy)}
        self._loadingViews = dict()
        self.__loader = loader
        self.__loader.onViewLoaded += self.__loader_onViewLoaded
        self.__scopeController = GlobalScopeController()
        self.__scopeController.create()

    def load(self, alias, name = None, *args, **kwargs):
        if name is None:
            name = alias
        isViewExists = self.as_getViewS(name)
        if not isViewExists and (alias, name) not in self._loadingViews:
            pyEntity = self.__loader.loadView(alias, name, *args, **kwargs)
            self.__scopeController.addLoadingView(pyEntity, False)
            curType = pyEntity.settings.type
            if self.canCancelPreviousLoading(curType):
                result = []
                for kev, val in self._loadingViews.iteritems():
                    if val.settings.type == pyEntity.settings.type:
                        result.append(val)

                if len(result) > 0:
                    self.__cancelLoadingForPyEntities(result)
            self._loadingViews[alias, name] = pyEntity
        return

    def __cancelLoadingForPyEntities(self, pyEntities):
        for curEntity in pyEntities:
            self._loadingViews.pop((curEntity.settings.alias, curEntity.uniqueName))
            self.__loader.cancelLoadingByName(curEntity.uniqueName)
            curEntity.destroy()

    def canCancelPreviousLoading(self, containerType):
        container = self.getContainer(containerType)
        if container is not None:
            return container.canCancelPreviousLoading()
        else:
            return False
            return

    def addContainer(self, containerType, name, container = None):
        result = True
        if containerType not in self.__containers:
            if container is None:
                self.__containers[containerType] = _DefaultContainer(weakref.proxy(self))
                self.as_registerContainerS(containerType, name)
            elif isinstance(container, IViewContainer):
                self.__containers[containerType] = container
                self.as_registerContainerS(containerType, name)
            else:
                LOG_ERROR('Container must be implemented IViewContainer', container)
                result = False
        else:
            LOG_ERROR('Container already registered', containerType)
            result = False
        return result

    def removeContainer(self, viewType):
        self.__scopeController.removeSubScopeController(ScopeTemplates.VIEW_TYPES_TO_SCOPES[viewType].getScopeType())
        result = True
        if viewType in self.__containers:
            container = self.__containers[viewType]
            container.destroy()
            self.as_unregisterContainerS(viewType)
            del self.__containers[viewType]
        else:
            result = False
        return result

    def getContainer(self, viewType):
        if viewType in self.__containers:
            return self.__containers[viewType]
        else:
            return None

    def isModalViewsIsExists(self):
        if self.getContainer(ViewTypes.TOP_WINDOW).getViewCount(isModal=True) > 0:
            return True
        elif self.getContainer(ViewTypes.BROWSER).getViewCount(isModal=True) > 0:
            return True
        else:
            return self.getContainer(ViewTypes.WINDOW).getViewCount(isModal=True) > 0

    def getView(self, viewType, criteria = None):
        view = None
        container = self.getContainer(viewType)
        if container is not None:
            view = container.getView(criteria=criteria)
        else:
            raise Exception('Container for %s view is None!' % viewType)
        return view

    def isViewAvailable(self, viewType, criteria = None):
        container = self.getContainer(viewType)
        if container is not None:
            return container.getView(criteria=criteria) is not None
        else:
            return False
            return

    def closePopUps(self):
        self.as_closePopUpsS()

    def clear(self):
        for c in self.__CONTAINERS_TO_CLEAR:
            self.getContainer(c).clear()

    def _dispose(self):
        if self.__loader is not None:
            self.__loader.onViewLoaded -= self.__loader_onViewLoaded
            self.__loader = None
        for viewType in self.__DESTROY_ORDER:
            if viewType in self.__containers:
                container = self.__containers.pop(viewType)
                LOG_DEBUG('CONTAINER: ' + str(container) + '/' + viewType)
                container.destroy()

        if len(self.__containers):
            LOG_ERROR('No all containers are destructed.')
        self.__containers.clear()
        self.onViewAddedToContainer.clear()
        self.__scopeController.destroy()
        self.__scopeController = None
        self._loadingViews.clear()
        self._loadingViews = None
        super(ContainerManager, self)._dispose()
        return

    def __loader_onViewLoaded(self, pyView):
        viewType = pyView.settings.type
        if viewType is None:
            LOG_ERROR('Type of view is not defined', pyView.settings)
        viewKey = (pyView.alias, pyView.uniqueName)
        if viewKey in self._loadingViews:
            self._loadingViews.pop(viewKey)
        if viewType in self.__containers:
            if ViewTypes.DEFAULT == viewType:
                self.closePopUps()
            if self.__scopeController.isViewLoading(pyView):
                container = self.__containers[viewType]
                if container.add(pyView):
                    self.__scopeController.addView(pyView, False)
                    self.as_showS(pyView.uniqueName, 0, 0)
                    pyView.create()
                    subContainerType = pyView.getSubContainerType()
                    if subContainerType is not None:
                        self.addContainer(subContainerType, pyView.uniqueName)
                    LOG_DEBUG('View added to container', pyView)
                    self.onViewAddedToContainer(container, pyView)
            else:
                LOG_DEBUG('"%s" view cancelled to load, because its scope has been destroyed.' % str(pyView))
                self.as_hideS(pyView.uniqueName)
                pyView.destroy()
        else:
            LOG_ERROR('Type "%s" of view "%s" is not supported' % (viewType, pyView))
        return
