# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/containers.py
import weakref
from Event import Event
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_UNEXPECTED, LOG_CURRENT_EXCEPTION
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
        raise NotImplementedError('AbstractViewContainer.add must be implemented')

    def remove(self, pyView):
        """
        Removes view from container.
        :param pyView: view to be removed from this container.
        """
        raise NotImplementedError('AbstractViewContainer.remove must be implemented')

    def clear(self):
        """
        Removes all views from container.
        """
        raise NotImplementedError('AbstractViewContainer.clear must be implemented')

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
        raise NotImplementedError('AbstractViewContainer.getView must be implemented')

    def getViewCount(self, **kwargs):
        """
        Gets number of views in container.
        :param kwargs: optional arguments.
        :return:
        """
        raise NotImplementedError('AbstractViewContainer.getViewCount must be implemented')

    def canCancelPreviousLoading(self):
        """
        Is container allow to cancel loading of view that are being loaded at a period of time.
        :return: True, if container allows to cancel loading of views being loaded in memory.
        """
        raise NotImplementedError('AbstractViewContainer.canCancelPreviousLoading must be implemented')


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
            self.__view.destroy()
            self.__view = None
        return

    def canCancelPreviousLoading(self):
        return True

    def __handleModuleDispose(self, pyView):
        subContainerType = pyView.getSubContainerType()
        if subContainerType is not None:
            self._manager.removeContainer(subContainerType)
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
    The container manager manages overlapping of views and their life time based on their type
    and scope. Performs loading of views through the specified loader.
    
    1. Overlapping of views
    UI consists of several layers. Each layer has its own Z index. It allows to control overlapping
    of views (views of the top level layer overlap views of underlying layers). The set of default
    layers depends on entry (application) type (lobby and battle have their own configuration).
    Each view can belong to one layer and it is defined by view's type. With each layer associated
    one view container that is managed by the container manager. There are two types of layers
    (view containers):
    - DefaultContainer - only one top level view can be placed in the container (layer) and if a
      new view is placed to it the previous one is destroyed;
    - PopUpContainer - several views can exist at the same time in one layer.
    Also any top level view can include a subview that is placed into a subcontainer. If a top
    level vew can include a subview, the subcontainer (DefaultContainer) is created after the top
    level view is loaded and initialized. When subview is loaded, it is placed into the top
    level view's subcontainer. The subcontainer is destroyed when the top level view is destroyed.
    
    2. Views life time
    The 'view scope' concept is introduced to simplify views lifetime management. View lifetime is
    defined by its scope and is controlled by the container manager through the scope controller.
    View scope defines when the view should be destroyed: if the parent view (parent scope) is
    destroyed, the subview is destroyed too. For details please see ScopeController description.
    """

    def __init__(self, loader, *containers):
        super(ContainerManager, self).__init__()
        self.onViewAddedToContainer = Event()
        self.__containers = {}
        proxy = weakref.proxy(self)
        for container in containers:
            assert isinstance(container, AbstractViewContainer)
            self.__containers[container.getViewType()] = container(proxy)

        self.__loader = loader
        self.__loader.onViewLoaded += self.__onViewLoaded
        self.__scopeController = GlobalScopeController()
        self.__scopeController.create()

    def load(self, alias, name=None, *args, **kwargs):
        """
        Loads a view with the given alias and puts it to the appropriate container (layer).
        
        :param alias: View's alias to be loaded.
        :param name: Name to be associated with the loaded view.
        """
        if name is None:
            name = alias
        isViewExists = self.as_getViewS(name)
        if self.__scopeController.isViewLoading(alias=alias):
            LOG_DEBUG('View with alias {} is already loading.'.format(alias))
        else:
            pyEntity = None
            if isViewExists:
                pyEntity = self.__scopeController.getViewByAlias(alias)
                if pyEntity is None:
                    isViewExists = False
                    LOG_UNEXPECTED('Unexpected case: Could not find a view with alias {} in the scope ctrl. View will be reloaded.'.format(alias))
                else:
                    LOG_DEBUG('View with alias {} ({}) is already loaded.'.format(alias, str(pyEntity)))
            if pyEntity is None:
                LOG_DEBUG('Load view with alias "{}" (name - "{}")'.format(alias, name))
                pyEntity = self.__loader.loadView(alias, name, *args, **kwargs)
            curType = pyEntity.settings.type
            if self.canCancelPreviousLoading(curType):
                canceledViews = self.__scopeController.getLoadingViewsByType(curType)
                scopeType = self.__scopeController.extractScopeFromView(pyEntity).getScopeType()
                if scopeType != ScopeTemplates.GLOBAL_SCOPE.getScopeType():
                    canceledViews.update(self.__scopeController.getLoadingViewsByScope(scopeType))
                if canceledViews:
                    self.__cancelLoadingForPyEntities(canceledViews)
            if isViewExists:
                pyEntity.validate()
            else:
                self.__scopeController.addLoadingView(pyEntity, False)
        return

    def canCancelPreviousLoading(self, containerType):
        """
        Returns True if it is required to cancel loading of top level views (and their subviews)
        for the given container (layer) type.
        
        :param containerType: Container type that corresponds to view type.
        """
        container = self.getContainer(containerType)
        if container is not None:
            return container.canCancelPreviousLoading()
        else:
            return False
            return

    def addContainer(self, viewType, name, container=None):
        """
        Adds container to managed containers. The method can be used to create subcontainer of
        a top level view (if it can include subview)
        
        :param viewType: View type. @see ViewTypes.
        :param name: Container name.
        :param container: Instance of object extending AbstractViewContainer.
        :return:
        """
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
        """
        Removes container from managed containers.
        :param viewType: type of view. @see ViewTypes.
        """
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
        """
        Returns container by the given type or None if there is no such container.
        
        :param viewType: viewType: View type. @see ViewTypes.
        """
        return self.__containers[viewType] if viewType in self.__containers else None

    def isModalViewsIsExists(self):
        """
        Returns True if a modal view exists, otherwise returns False.
        """
        for viewType in _POPUPS_CONTAINERS:
            container = self.getContainer(viewType)
            if container is not None and container.getViewCount(isModal=True):
                return True

        return False

    def getView(self, viewType, criteria=None):
        """
        Gets view by the given type and criteria if it is defined.
        
        :param viewType: type of view. @see ViewTypes.
        :param criteria: criteria to find view in container.
        :return: instance of view.
        """
        container = self.getContainer(viewType)
        if container is not None:
            view = container.getView(criteria=criteria)
        else:
            raise Exception('Container for %s view is None!' % viewType)
        return view

    def isViewAvailable(self, viewType, criteria=None):
        """
        If you want to get some view from some container, it`s may be
        unsafely operation. For example, I want to get a Hangar from a Lobby
        view. it`s a bad situation and method "getView" detects this state.
        Then, if you just want to detect an existing View, use isViewAvailable method.
        
        :param viewType: type of view. @see ViewTypes.
        :param criteria: criteria to find view in container.
        """
        container = self.getContainer(viewType)
        if container is not None:
            return container.getView(criteria=criteria) is not None
        else:
            return False
            return

    def showContainers(self, *viewTypes):
        """
        Shows containers for given view types.
        
        :param viewTypes: View types
        """
        self.as_showContainersS(viewTypes)

    def hideContainers(self, *viewTypes):
        """
        Hides containers for given view types.
        
        :param viewTypes: View types
        """
        self.as_hideContainersS(viewTypes)

    def isContainerShown(self, viewType):
        """
        Returns True if a container with the given view type is shown, otherwise returns False.
        
        :param viewType: View types
        """
        return self.as_isContainerShownS(viewType)

    def closePopUps(self):
        """
        Closes all popUps: widows and dialogs.
        """
        self.as_closePopUpsS()

    def clear(self):
        """
        Clears defined containers
        """
        for viewType in _POPUPS_CONTAINERS:
            container = self.getContainer(viewType)
            if container is not None:
                container.clear()

        return

    def _dispose(self):
        if self.__loader is not None:
            self.__loader.onViewLoaded -= self.__onViewLoaded
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
        super(ContainerManager, self)._dispose()
        return

    def __cancelLoadingForPyEntities(self, pyEntities):
        LOG_DEBUG('Loading is canceled for the following views: ', pyEntities)
        for curEntity in pyEntities:
            self.__loader.cancelLoadingByName(curEntity.uniqueName)
            self.__scopeController.removeLoadingView(curEntity)
            if curEntity.isCreated():
                curEntity.destroy()

    def __onViewLoaded(self, pyView):
        viewType = pyView.settings.type
        if viewType is None:
            LOG_ERROR('Type of view is not defined', pyView.settings)
        if viewType in self.__containers:
            if ViewTypes.DEFAULT == viewType:
                self.closePopUps()
            if self.__scopeController.isViewLoading(pyView=pyView):
                container = self.__containers[viewType]
                if container.add(pyView):
                    self.__scopeController.addView(pyView, False)
                    self.as_showS(pyView.uniqueName, 0, 0)
                    pyView.create()
                    if not pyView.isDisposed():
                        subContainerType = pyView.getSubContainerType()
                        if subContainerType is not None:
                            LOG_DEBUG('Sub container {} is created for view {}.'.format(subContainerType, str(pyView)))
                            self.addContainer(subContainerType, pyView.uniqueName)
                        LOG_DEBUG('View {} is added to container {}.'.format(str(pyView), str(container)))
                        self.onViewAddedToContainer(container, pyView)
                    else:
                        LOG_DEBUG('View {} has been destroyed during populating.'.format(str(pyView)))
            else:
                LOG_DEBUG('{} view loading is cancelled because its scope has been destroyed.'.format(str(pyView)))
                self.as_hideS(pyView.uniqueName)
                pyView.destroy()
        else:
            LOG_ERROR('Type {} of view {} is not supported or sub container has not been properly created'.format(viewType, pyView))
        return
