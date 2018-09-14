# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/containers.py
import weakref
from Event import Event
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.ScopeControllers import GlobalScopeController
from gui.Scaleform.daapi.view.meta.WindowViewMeta import WindowViewMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.abstract.ContainerManagerMeta import ContainerManagerMeta
from shared_utils import findFirst
_POPUPS_CONTAINERS = (ViewTypes.TOP_WINDOW, ViewTypes.BROWSER, ViewTypes.WINDOW)
_CONTAINERS_DESTROY_ORDER = (ViewTypes.DEFAULT,
 ViewTypes.LOBBY_SUB,
 ViewTypes.WINDOW,
 ViewTypes.BROWSER,
 ViewTypes.TOP_WINDOW,
 ViewTypes.WAITING,
 ViewTypes.CURSOR,
 ViewTypes.SERVICE_LAYOUT)

class AbstractViewContainer(object):
    """
    Super-type of containers.
    """
    __slots__ = ('_type', '_manager')

    def __init__(self, viewType, manager=None):
        self._type = viewType
        self._manager = manager

    def __call__(self, manager):
        self._manager = manager
        return self

    def getViewType(self):
        return self._type

    def add(self, pyView):
        """
        Adds view to container.
        :param pyView: view to be added to this container.
        :return: True if view added to container, otherwise - False.
        """
        raise NotImplementedError('IViewContainer.add must be implemented')

    def remove(self, pyView):
        """
        Removes view from container.
        :param pyView: view to be removed from this container.
        """
        raise NotImplementedError('IViewContainer.remove must be implemented')

    def clear(self):
        """
        Removes all views from container.
        """
        raise NotImplementedError('IViewContainer.clear must be implemented')

    def destroy(self):
        """
        Destroys container.
        """
        self.clear()
        self._manager = None
        return

    def getView(self, criteria=None):
        """
        Gets view from container.
        :param criteria: criteria to find view in container.
        :return: object of view if view found in container, otherwise - None.
        """
        raise NotImplementedError('IViewContainer.getView must be implemented')

    def getViewCount(self, **kwargs):
        """
        Gets number of views in container.
        :param kwargs: optional arguments.
        :return:
        """
        raise NotImplementedError('IViewContainer.getViewCount must be implemented')

    def canCancelPreviousLoading(self):
        """
        Is container allow cancelling a previous loading.
        :return: True, if container allows cancelling a previous loading.
        """
        raise NotImplementedError('IViewContainer.canCancelPreviousLoading must be implemented')


class DefaultContainer(AbstractViewContainer):
    """
    Class of default container. Container has one object of view.
    If new view adds to container, then invokes destroy method for previous view.
    """
    __slots__ = ('__view',)

    def __init__(self, viewType, manager=None):
        assert viewType not in _POPUPS_CONTAINERS, 'Type of view can not be {}'.format(viewType)
        super(DefaultContainer, self).__init__(viewType, manager=manager)
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
            self._manager.as_hideS(self.__view.uniqueName)
            self.__view = None
        return

    def clear(self):
        if self.__view is not None:
            subContainerType = self.__view.getSubContainerType()
            if subContainerType is not None:
                self._manager.removeContainer(subContainerType)
            self.__view.onModuleDispose -= self.__handleModuleDispose
            self._manager.as_hideS(self.__view.uniqueName)
            self._manager.removeLoadingView(self.__view.alias, self.__view.uniqueName)
            self.__view.destroy()
            self.__view = None
        return

    def canCancelPreviousLoading(self):
        return True

    def __handleModuleDispose(self, pyView):
        subContainerType = pyView.getSubContainerType()
        if subContainerType is not None:
            self._manager.removeContainer(subContainerType)
        self._manager.removeLoadingView(pyView.alias, pyView.uniqueName)
        self.remove(pyView)
        return

    def getView(self, criteria=None):
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
        return 1 if self.__view is not None else 0


class POP_UP_CRITERIA(object):
    VIEW_ALIAS = 1
    UNIQUE_NAME = 2


class ExternalCriteria(object):

    def __init__(self, criteria=None):
        super(ExternalCriteria, self).__init__()
        self._criteria = criteria

    def find(self, name, obj):
        raise NotImplemented('ExternalCriteria.find must be implemented')


class PopUpContainer(AbstractViewContainer):
    """
    Class of pupUp container for windows, dialogs, ...
    NOTE: view invokes destroy method internally, container listens
        onModuleDispose.
    """
    __slots__ = ('__popUps',)

    def __init__(self, viewType, manager=None):
        super(PopUpContainer, self).__init__(viewType, manager=manager)
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
            self._manager.as_hideS(popUp.uniqueName)
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
                self._manager.removeContainer(subContainerType)
            popUp.onModuleDispose -= self.__handleModuleDispose
            self._manager.as_hideS(popUp.uniqueName)
            popUp.destroy()

        return

    def getView(self, criteria=None):
        popUp = None
        if criteria is not None:
            if isinstance(criteria, dict):
                popUp = self.__findByDictCriteria(criteria)
            elif isinstance(criteria, ExternalCriteria):
                popUp = self.__findByExCriteria(criteria)
            else:
                LOG_ERROR('Criteria is invalid', criteria)
        return popUp

    def getViewCount(self, isModal=None):
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
            popUps = filter(lambda item: item.settings.alias == viewAlias, self.__popUps.values())
            if popUps:
                popUp = popUps[0]
        return popUp

    def __findByExCriteria(self, criteria):

        def find(item):
            return criteria.find(*item)

        return findFirst(find, self.__popUps.iteritems(), ('', None))[1]

    def __handleModuleDispose(self, pyView):
        subContainerType = pyView.getSubContainerType()
        if subContainerType is not None:
            self._manager.removeContainer(subContainerType)
        self.remove(pyView)
        return


class ContainerManager(ContainerManagerMeta):
    """
    Class of container manager.
    """

    def __init__(self, loader, *containers):
        super(ContainerManager, self).__init__()
        self.onViewAddedToContainer = Event()
        proxy = weakref.proxy(self)
        self.__containers = {}
        for container in containers:
            assert isinstance(container, AbstractViewContainer)
            self.__containers[container.getViewType()] = container(proxy)

        self._loadingViews = dict()
        self.__loader = loader
        self.__loader.onViewLoaded += self.__loader_onViewLoaded
        self.__scopeController = GlobalScopeController()
        self.__scopeController.create()

    def load(self, alias, name=None, *args, **kwargs):
        """
        Loads view to container.
        :param alias:
        :param name:
        :param args:
        :param kwargs:
        :return:
        """
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

                if result:
                    self.__cancelLoadingForPyEntities(result)
            self._loadingViews[alias, name] = pyEntity
        return

    def canCancelPreviousLoading(self, containerType):
        container = self.getContainer(containerType)
        if container is not None:
            return container.canCancelPreviousLoading()
        else:
            return False
            return

    def addContainer(self, viewType, name, container=None):
        result = True
        if viewType not in self.__containers:
            if container is None:
                self.__containers[viewType] = DefaultContainer(viewType, weakref.proxy(self))
                self.as_registerContainerS(viewType, name)
            elif isinstance(container, AbstractViewContainer):
                self.__containers[viewType] = container
                self.as_registerContainerS(viewType, name)
            else:
                LOG_ERROR('Container must be implemented IViewContainer', container)
                result = False
        else:
            LOG_ERROR('Container already registered', viewType)
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
        return self.__containers[viewType] if viewType in self.__containers else None

    def isModalViewsIsExists(self):
        for viewType in _POPUPS_CONTAINERS:
            container = self.getContainer(viewType)
            if container is not None and container.getViewCount(isModal=True):
                return True

        return False

    def getView(self, viewType, criteria=None):
        container = self.getContainer(viewType)
        if container is not None:
            view = container.getView(criteria=criteria)
        else:
            raise Exception('Container for %s view is None!' % viewType)
        return view

    def isViewAvailable(self, viewType, criteria=None):
        container = self.getContainer(viewType)
        if container is not None:
            return container.getView(criteria=criteria) is not None
        else:
            return False
            return

    def showContainers(self, *viewTypes):
        self.as_showContainersS(viewTypes)

    def hideContainers(self, *viewTypes):
        self.as_hideContainersS(viewTypes)

    def isContainerShown(self, viewType):
        return self.as_isContainerShownS(viewType)

    def closePopUps(self):
        self.as_closePopUpsS()

    def clear(self):
        for viewType in _POPUPS_CONTAINERS:
            container = self.getContainer(viewType)
            if container is not None:
                container.clear()

        return

    def removeLoadingView(self, alias, uniqueName):
        self._loadingViews.pop((alias, uniqueName), None)
        return

    def _dispose(self):
        if self.__loader is not None:
            self.__loader.onViewLoaded -= self.__loader_onViewLoaded
            self.__loader = None
        for viewType in _CONTAINERS_DESTROY_ORDER:
            if viewType in self.__containers:
                container = self.__containers.pop(viewType)
                LOG_DEBUG('CONTAINER: {}/{}'.format(container, viewType))
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

    def __cancelLoadingForPyEntities(self, pyEntities):
        for curEntity in pyEntities:
            self._loadingViews.pop((curEntity.settings.alias, curEntity.uniqueName))
            self.__loader.cancelLoadingByName(curEntity.uniqueName)
            curEntity.destroy()

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
