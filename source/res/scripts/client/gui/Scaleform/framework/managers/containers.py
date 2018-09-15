# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/containers.py
import weakref
from collections import OrderedDict
from Event import Event
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_ERROR, LOG_UNEXPECTED
from shared_utils import CONST_CONTAINER
from gui.Scaleform.framework.ScopeControllers import GlobalScopeController
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.abstract.ContainerManagerMeta import ContainerManagerMeta
from gui.Scaleform.framework.managers.loaders import ViewLoadMode, ViewKey
from shared_utils import findFirst
_POPUPS_CONTAINERS = (ViewTypes.TOP_WINDOW, ViewTypes.BROWSER, ViewTypes.WINDOW)
_CONTAINERS_DESTROY_ORDER = (ViewTypes.DEFAULT,
 ViewTypes.LOBBY_SUB,
 ViewTypes.LOBBY_TOP_SUB,
 ViewTypes.WINDOW,
 ViewTypes.BROWSER,
 ViewTypes.TOP_WINDOW,
 ViewTypes.WAITING,
 ViewTypes.OVERLAY,
 ViewTypes.CURSOR,
 ViewTypes.SERVICE_LAYOUT)

class POP_UP_CRITERIA(object):
    VIEW_ALIAS = 1
    UNIQUE_NAME = 2


class VIEW_SEARCH_CRITERIA(CONST_CONTAINER):
    VIEW_ALIAS = 1
    VIEW_UNIQUE_NAME = 2

    @classmethod
    def ALL(cls):
        return (cls.VIEW_UNIQUE_NAME, cls.VIEW_ALIAS)


class ExternalCriteria(object):

    def __init__(self, criteria=None):
        super(ExternalCriteria, self).__init__()
        self._criteria = criteria

    def find(self, name, obj):
        raise NotImplemented('ExternalCriteria.find must be implemented')


_VIEW_SEARCH_CRITERIA_HANDLERS = {VIEW_SEARCH_CRITERIA.VIEW_ALIAS: lambda view, value: view.alias == value,
 VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: lambda view, value: view.uniqueName == value}

class ViewContainer(object):
    """
    Represents Python wrapper on Scaleform view container. Holds references to loaded (visible) views, references
    to views that are currently being loaded and references to child view containers.
    Containers are associated with a Z index and are used to control views overlapping (currently it is not possible
    to set up Z-index of a particular view; it can be reached by placing view in a proper container).
    ViewContainer is a multi-views container that means that several view can exist at the same time (can be visible).
    Key points:
    1. View cannot live without a parent container. If the parent container is destroyed, the view is destroyed too.
       If a view is removed from its parent container it is automatically destroyed.
    2. If a view has sub-containers (for sub views) they are automatically created immediately after the view is
       created and populated (see EntityState.CREATED state description). These sub-containers are owned by the
       view's parent container and automatically destroyed when the parent view or its container is destroyed.
    3. Once a view is added to container, the container tracks it and is responsible for it. View cannot be moved from
       one container to another. Be aware that adding a view that belongs to another container may lead to critical
       errors and to corrupt data.
    4. Once a sub-container is added to container, the container tracks it and is responsible for it. Sub-container
       cannot be moved from one container to another.
    5. When a container is destroyed, all its childs (views, loading views, sub-containers, etc.) are destroyed too.
    """
    __slots__ = ('__viewType', '__child', '_views', '_loadingViews', '__containerManager', '__parentContainer')

    def __init__(self, viewType, containerManager=None):
        """
        Ctr.
        :param viewType: container type, that indicates which type of view (see ViewTypes) it can contain.
        :param containerManager: reference to IContainerManager proxy.
        """
        super(ViewContainer, self).__init__()
        self._views = {}
        self._loadingViews = {}
        self.__child = {}
        self.__viewType = viewType
        self.__containerManager = containerManager
        self.__parentContainer = None
        return

    def __repr__(self):
        return '{}[{}]=[viewType=[{}], views=[{}], loadingViews=[{}], child=[{}]]'.format(self.__class__.__name__, hex(id(self)), self.__viewType, self._views, self._loadingViews, self.__child)

    def destroy(self):
        """
        Destroys all childs (views, loading views, sub-containers, etc.) and clears inner state.
        """
        while self.__child:
            container = next(self.__child.itervalues())
            container.destroy()

        self.clear()
        if self.__parentContainer is not None:
            self.__parentContainer.removeChildContainer(self.getViewType())
            self.__parentContainer = None
        self.__containerManager = None
        return

    def clear(self):
        """
        Destroy all owned views (including sub-views from sub containers).
        """
        self._removeLoadingViews()
        self._removeViews()

    def getViewType(self):
        """
        Gets view type with that the container is associated.
        :return: string, see ViewTypes
        """
        return self.__viewType

    def getParentContainer(self):
        """
        Gets a reference to the parent container or None if there is no any.
        :return: an instance of ViewContainer or None.
        """
        return self.__parentContainer

    def addChildContainer(self, container, name=None):
        """
        Adds the given sub-container and notify FE-side to register a new container with the given name.
        :param container: sub-container represented by ViewContainer
        :param name: string, name with that the sub-container will be registered on FE-side.
        :return: bool, True if container has been added or False if already there is container with the same type.
        """
        viewType = container.getViewType()
        if viewType not in self.__child:
            self.__child[container.getViewType()] = container
            container.__containerManager = self.__containerManager
            container.__parentContainer = self
            self._registerContainer(container.getViewType(), name)
            return True
        return False

    def removeChildContainer(self, viewType):
        """
        Removes and destroys child container with the given type. Note that removes only direct child (doesn't remove
        child of child).
        :param viewType: container type to be destroyed (see ViewTypes)
        :return: bool, True if container has been removed or False if there is no container with the given type.
        """
        if viewType in self.__child:
            container = self.__child.pop(viewType)
            container.__parentContainer = None
            container.destroy()
            container.__containerManager = None
            self._unregisterContainer(viewType)
            return True
        else:
            return False

    def getChildContainer(self, viewType):
        """
        Gets child container with the given type or None if there is no any. Note that returns only direct child
        (doesn't lookup child of its direct child). To lookup a container in all hierarchy use findContainer method.
        :param viewType: container type (see ViewTypes)
        :return: an instance of ViewContainer or None
        """
        return self.__child.get(viewType, None)

    def findContainer(self, viewType):
        """
        Performs search in depth to find a container with the given type and returns a reference to it or None if
        there is no any.
        :param viewType: container type (see ViewTypes)
        :return: an instance of ViewContainer or None
        """
        if self.__viewType == viewType:
            return self
        else:
            child = self.getChildContainer(viewType)
            if child is not None:
                return child
            for c in self.__child.itervalues():
                child = c.getChildContainer(viewType)
                if child is not None:
                    return child

            return

    def findView(self, viewKey):
        """
        Performs search in depth to find a view with the given key and returns a reference to it or None if
        there is no any.
        :param viewKey: view key (see ViewKey)
        :return: an instance of View or None
        """
        if viewKey in self._views:
            return self._views[viewKey]
        else:
            for c in self.__child.itervalues():
                view = c.findView(viewKey)
                if view is not None:
                    return view

            return

    def addView(self, pyView):
        """
        Adds the given view as direct view child if the view has proper type.
        If the view has its own sub-containers they will be added immediately if the view is already created or
        as soon as the view will be created.
        :param pyView: view, see View class
        :return: True if the view has been added or False if the view has not been added (it is already in it or
                 the view is not supported by container or its sub-containers)
        """
        if not self.isViewCompatible(pyView):
            LOG_ERROR('Cannot add view {} to container {}. Incompatible view type.'.format(pyView, self))
            return False
        return self._addView(pyView)

    def removeView(self, pyView):
        """
        Removes and destroys the given view (if it belongs to container or its sub-containers) with its sub-containers
        and sub-views.
        :param pyView: view to be destroyed and removed, see View class
        :return: True if the view has been removed; otherwise False.
        """
        viewType = pyView.settings.type
        container = self.findContainer(viewType)
        if container is None:
            LOG_WARNING('There is no container {} to remove view!'.format(viewType, pyView))
            return False
        else:
            return container._removeView(pyView) if pyView.key in container._views else False

    def addLoadingView(self, pyView):
        """
        Adds the given loading view as direct child (if container type is equal to view type) or tries to find a
        proper sub-container to add to it the view.
        :param pyView: view, see View class
        :return: True if the view has been added or False if the view has not been added (it is already in it or
                 the view is not supported by container or its sub-containers)
        """
        if not self.isViewCompatible(pyView):
            LOG_ERROR('Cannot add loading view {} to container {}. Incompatible view type.'.format(pyView, self))
            return False
        return self._addLoadingView(pyView)

    def removeLoadingView(self, pyView):
        """
        Removes and destroys the given loading view (if it belongs to container or its sub-containers) with its
        sub-containers and sub-views.
        Be aware that if required to add a loading view to list of loaded views just call addView method without
        removing from container, because removeLoadingView destroys the removed view.
        :param pyView: view to be destroyed and removed, see View class
        :return: True if the view has been removed; otherwise False.
        """
        viewType = pyView.settings.type
        container = self.findContainer(viewType)
        if container is None:
            LOG_WARNING('There is no container {} to remove loading view!'.format(viewType, pyView))
            return False
        else:
            return container._removeLoadingView(pyView) if pyView.key in container._loadingViews else False

    def getAllLoadingViews(self):
        """
        Returns list of all loading views (including from sub-containers).
        :return: list of Views.
        """
        views = self._loadingViews.values()
        for c in self.__child.itervalues():
            views.extend(c.getAllLoadingViews())

        return views

    def removeAllLoadingViews(self):
        """
        Recursively removes (destroys) all loading views in (including in sub-containers).
        """
        self._removeLoadingViews()
        for c in self.__child.itervalues():
            c.removeAllLoadingViews()

    def removeLoadingSubViews(self):
        """
        Recursively removes (destroys) all loading views in sub-containers (child-containers).Note that views owned by
        himself are not removed (only sub views)!
        """
        for c in self.__child.itervalues():
            c.removeAllLoadingViews()

    def getView(self, criteria):
        if isinstance(criteria, dict):
            view = self.__findByDictCriteria(criteria)
        elif isinstance(criteria, ExternalCriteria):
            view = self.__findByExCriteria(criteria)
        else:
            LOG_ERROR('Criteria is invalid', criteria)
            view = None
        return view

    def getViewCount(self, isModal=None):
        if isModal is None:
            result = len(self._views)
        else:
            result = 0
            for view in self._views.itervalues():
                if view.isViewModal() == isModal:
                    result += 1

        return result

    def isViewCompatible(self, pyView):
        """
        Returns True if the given view is compatible with the container and can be added to it. False otherwise.
        :param pyView: view, see View class
        :return: bool
        """
        return self.__viewType == pyView.settings.type

    def _registerContainer(self, viewType, name):
        if self.__containerManager is not None:
            self.__containerManager.registerViewContainer(viewType, name)
        return

    def _unregisterContainer(self, viewType):
        if self.__containerManager is not None:
            self.__containerManager.unregisterViewContainer(viewType)
        return

    def _addViewEventListeners(self, pyView):
        pyView.onCreated += self._onViewCreated
        pyView.onDispose += self._onViewDisposed

    def _removeViewEventListeners(self, pyView):
        pyView.onCreated -= self._onViewCreated
        pyView.onDispose -= self._onViewDisposed

    def _addLoadingViewEventListeners(self, pyView):
        pyView.onDispose += self._onLoadingViewDisposed

    def _removeLoadingViewEventListeners(self, pyView):
        pyView.onDispose -= self._onLoadingViewDisposed

    def _onViewDisposed(self, pyView):
        self.removeView(pyView)

    def _onViewCreated(self, pyView):
        self.__addViewSubContainers(pyView)

    def _onLoadingViewDisposed(self, pyView):
        self.removeLoadingView(pyView)

    def _removeLoadingViews(self):
        while self._loadingViews:
            view = next(self._loadingViews.itervalues())
            self.removeLoadingView(view)

    def _removeViews(self):
        while self._views:
            view = next(self._views.itervalues())
            self.removeView(view)

    def _addView(self, pyView):
        viewKey = pyView.key
        if viewKey in self._views:
            return False
        if viewKey in self._loadingViews:
            loadingView = self._loadingViews.pop(viewKey)
            self._removeLoadingViewEventListeners(loadingView)
        self._views[viewKey] = pyView
        self._addViewEventListeners(pyView)
        if pyView.isCreated():
            self.__addViewSubContainers(pyView)
        LOG_DEBUG('View with key {} has been added to container {}'.format(viewKey, self))
        return True

    def _removeView(self, pyView):
        viewKey = pyView.key
        pyView = self._views.pop(viewKey)
        self._removeViewEventListeners(pyView)
        self.__removeViewSubContainers(pyView)
        if not pyView.isDisposed():
            pyView.destroy()
        return True

    def _addLoadingView(self, pyView):
        if pyView.key not in self._loadingViews and pyView.key not in self._views:
            self._loadingViews[pyView.key] = pyView
            self._addLoadingViewEventListeners(pyView)
            return True
        return False

    def _removeLoadingView(self, pyView):
        pyView = self._loadingViews.pop(pyView.key)
        self._removeViewEventListeners(pyView)
        if not pyView.isDisposed():
            pyView.destroy()
        return True

    def __addViewSubContainers(self, pyView):
        for subContainerSettings in pyView.getSubContainersSettings():
            clazz = subContainerSettings.clazz or DefaultContainer
            subContainer = clazz(subContainerSettings.type)
            self.addChildContainer(subContainer, pyView.uniqueName)
            LOG_DEBUG('Sub container {} is created for view {}.'.format(subContainerSettings, str(pyView)))

    def __removeViewSubContainers(self, pyView):
        for containerSettings in pyView.getSubContainersSettings():
            self.removeChildContainer(containerSettings.type)

    def __findByDictCriteria(self, criteria):
        for key in VIEW_SEARCH_CRITERIA.ALL():
            if key in criteria:
                value = criteria[key]
                handler = _VIEW_SEARCH_CRITERIA_HANDLERS[key]
                for v in self._views.itervalues():
                    if handler(v, value):
                        return v

        return None

    def __findByExCriteria(self, criteria):

        def find(item):
            return criteria.find(*item)

        return findFirst(find, self._views.iteritems(), ('', None))[1]


class SingleViewContainer(ViewContainer):
    """
    Class of default container. Container can have only one object of view at the same time.
    If new view is added to container the previous one is destroyed (it is true for loading views too).
    Note: the previous view is destroyed BEFORE the new one is created and showed for the user.
    Note: represents logic of the old DefaultContainer.
    """

    def __init__(self, viewType, manager=None):
        assert viewType not in _POPUPS_CONTAINERS, 'Type of view can not be {}'.format(viewType)
        super(SingleViewContainer, self).__init__(viewType, manager)

    def getView(self, criteria=None):
        view = None
        if criteria is None:
            if self._views:
                view = next(self._views.itervalues())
        else:
            view = super(SingleViewContainer, self).getView(criteria)
        return view

    def _addLoadingView(self, pyView):
        loadingViews = self.getAllLoadingViews()
        status = super(SingleViewContainer, self)._addLoadingView(pyView)
        if status:
            for v in loadingViews:
                self.removeLoadingView(v)

        return status

    def _addView(self, pyView):
        status = super(SingleViewContainer, self)._addView(pyView)
        if status:
            self._setMainView(pyView)
        self._removeLoadingViews()
        return status

    def _setMainView(self, pyView):
        for v in self._views.values():
            if v != pyView:
                self.removeView(v)


class DefaultContainer(SingleViewContainer):
    """
    Class of default container. Container can have only one object of view at the same time.
    If new view is added to container the previous one is destroyed (it is true for loading views too).
    Note: the previous view is destroyed only AFTER the new one has been created and showed for the user.
    """

    def _onViewCreated(self, pyView):
        super(DefaultContainer, self)._onViewCreated(pyView)
        self._setMainView(pyView)

    def _setMainView(self, pyView):
        if pyView.isCreated():
            super(DefaultContainer, self)._setMainView(pyView)


class PopUpContainer(ViewContainer):
    """
    Container for pop-up views: pop-up windows, dialogs, ...
    """
    pass


class _GlobalViewContainer(ViewContainer):
    """
    Global container (root swf of FE side). Note that currently all top-level containers (in global scope) are
    hardcoded on FE side, therefore _registerContainer and _unregisterContainer are empty. In future, if FE will
    support dynamic adding of  top-level containers just use original version of these methods.
    """
    __slots__ = ()

    def __init__(self, containerManager):
        super(_GlobalViewContainer, self).__init__(None, containerManager)
        return

    def _registerContainer(self, viewType, name):
        pass

    def _unregisterContainer(self, viewType):
        pass


class _ViewCollection(object):
    """
    Represents collection of Views objects. Tracks views lifecycle and automatically remove view from if the view
    is destroyed.
    """

    def __init__(self):
        super(_ViewCollection, self).__init__()
        self._views = {}

    def __iter__(self):
        return self._views.__iter__()

    def __contains__(self, viewKey):
        return viewKey in self._views

    def __len__(self):
        return self._views.__len__()

    def destroy(self):
        for view in self._views.itervalues():
            view.onDispose -= self._onViewDisposed
            if not view.isDisposed():
                view.destroy()

        self._views.clear()

    def clear(self):
        for view in self._views.itervalues():
            view.onDispose -= self._onViewDisposed

        self._views.clear()

    def findViews(self, comparator):
        """
        Finds all views using the given comparator.
        
        :param comparator: callable that takes one argument (View) and returns bool
        :return: list of found views
        """
        return [ v for v in self._views.itervalues() if comparator(v) ]

    def addView(self, view):
        viewKey = view.key
        if viewKey not in self._views:
            self._views[viewKey] = view
            view.onDispose += self._onViewDisposed
            return True
        return False

    def getView(self, viewKey):
        return self._views.get(viewKey, None)

    def removeView(self, viewKey):
        if viewKey in self._views:
            view = self._views.pop(viewKey)
            view.onDispose -= self._onViewDisposed
            return True
        return False

    def _onViewDisposed(self, view):
        self.removeView(view.key)


class ChainItem(object):
    __slots__ = ('loadParams', 'args', 'kwargs')

    def __init__(self, loadParams, args, kwargs):
        super(ChainItem, self).__init__()
        self.loadParams = loadParams
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '{}[{}]=[loadParams={}, args={}, kwargs={}'.format(self.__class__.__name__, hex(id(self)), self.loadParams, self.args, self.kwargs)


class _LoadingChain(object):
    """
    Represents chain of view to load them successor one after the other. The next view is loaded only after the
    previous one has been loaded and created (shown). If any view in the chain is already loaded (or destroyed), the
    view is skipped and the next view is loaded. To stop loading the chain should be destroyed.
    Note: the same view should not appear twice in the same chain!
    Be aware that all chains should be added to a chain manager. It is not recommended to use the separately from the
    chain manager. After a chain has been added to the chain manager, the chain manager is responsible for it. After
    all views have been loaded, the chain notifies the chain manager about that and it performs all required logic to
    clean up resources and to break cross references.
    """

    def __init__(self, chainItems):
        super(_LoadingChain, self).__init__()
        self.__chainManager = None
        self.__currentItem = None
        self.__currentView = None
        self.__queue = OrderedDict()
        for item in chainItems:
            assert isinstance(item, ChainItem)
            viewKey = item.loadParams.viewKey
            assert viewKey not in self.__queue
            self.__queue[viewKey] = item

        return

    def __repr__(self):
        return '{}[{}]=[currentView={}, queue={}, '.format(self.__class__.__name__, hex(id(self)), self.__currentView, self.__queue)

    def destroy(self):
        """
        Destroys the object and clean up resources.
        """
        if self.__chainManager is not None:
            self.__chainManager.removeChain(self)
            self.__chainManager = None
        self.__queue.clear()
        self.__currentItem = None
        if self.__currentView is not None:
            self.__removeViewEventListeners(self.__currentView)
            self.__currentView = None
        return

    def setChainManager(self, chainManager):
        self.__chainManager = chainManager

    def isViewInChain(self, viewKey):
        """
        Determines if a view with the given view key presents in the chain.
        :param viewKey: ViewKey instance.
        :return: bool
        """
        return viewKey in self.__queue

    def getViewByViewKey(self, viewKey):
        """
        Gets a reference to view with the passed key or None if there is no view with the given key in the chain.
        :param viewKey: ViewKey instance.
        :return: reference to View object or None.
        """
        self.__queue.get(viewKey, None)
        return

    def removeViewByViewKey(self, viewKey):
        """
        Removes view with the given key from the chain (if it presents in the chain)
        :param viewKey: ViewKey instance of view to be removed.
        """
        if self.isViewInChain(viewKey):
            del self.__queue[viewKey]

    def hasIntersectionWith(self, chain):
        """
        Determines if the chain has the same views with the given one.
        :param chain: an instance of _LoadingChain, to be used for comparing.
        :return: True if there is at least one the same view in the both chains; otherwise - False.
        """
        for viewKey in self.__queue:
            if chain.isViewInChain(viewKey):
                return True

        return False

    def run(self):
        """
        Runs chain to load all views that make up the chain.
        """
        if self.__currentItem is not None:
            LOG_WARNING('Chain of views loading is already running.', self)
            return
        else:
            self.__loadNextView()
            return

    def __loadNextView(self):
        self.__currentItem = None
        if self.__currentView is not None:
            self.__removeViewEventListeners(self.__currentView)
            self.__currentView = None
        stop = False
        while not stop:
            if not self.__queue:
                stop = True
                if self.__chainManager is not None:
                    self.__chainManager.removeChain(self)
            viewKey, item = self.__queue.popitem(last=False)
            if self.__chainManager is not None:
                view = self.__chainManager.load(item)
                self.__currentItem = item
                self.__currentView = view
                if view is not None:
                    if view.isDisposed() or view.isCreated():
                        pass
                    else:
                        stop = True
                        self.__addViewEventListeners(self.__currentView)
            LOG_WARNING('Could not load view with key {}. Chain manager is not specified.'.format(viewKey))

        return

    def __onViewDisposed(self, pyView):
        if pyView == self.__currentView:
            self.__loadNextView()
        else:
            LOG_UNEXPECTED('Got onDispose event for view {}. Unexpected case.'.format(pyView))

    def __onViewCreated(self, pyView):
        if pyView == self.__currentView:
            self.__loadNextView()
        else:
            LOG_UNEXPECTED('Got onCreated event for view {}. Unexpected case.'.format(pyView))

    def __addViewEventListeners(self, pyView):
        pyView.onCreated += self.__onViewCreated
        pyView.onDispose += self.__onViewDisposed

    def __removeViewEventListeners(self, pyView):
        pyView.onCreated -= self.__onViewCreated
        pyView.onDispose -= self.__onViewDisposed


class _ChainManager(object):
    """
    Represents manager of active chains (see _LoadingChain) and is used by the container manger to track all chains
    requested by the user.
    Note: the same view should not appear in different chains (see addChain method).
    """

    def __init__(self, containerManager):
        super(_ChainManager, self).__init__()
        self.__containerManager = containerManager
        self.__chains = []

    def destroy(self):
        while self.__chains:
            chain = self.__chains[0]
            chain.destroy()

        del self.__chains[:]
        self.__containerManager = None
        return

    def addChain(self, chain):
        for ch in self.__chains:
            if ch.hasIntersectionWith(chain):
                return False

        self.__chains.append(chain)
        chain.setChainManager(weakref.proxy(self))
        return True

    def removeChain(self, chain):
        if chain in self.__chains:
            self.__chains.remove(chain)
            chain.setChainManager(None)
            return True
        else:
            return False

    def getChainByViewKey(self, viewKey):
        for chain in self.__chains:
            if chain.isViewInChain(viewKey):
                return chain

        return None

    def load(self, chainItem):
        return self.__containerManager.load(chainItem.loadParams, *chainItem.args, **chainItem.kwargs)


class IContainerManager(object):

    def registerViewContainer(self, viewType, name):
        raise NotImplementedError

    def unregisterViewContainer(self, viewType):
        raise NotImplementedError


class ContainerManager(ContainerManagerMeta, IContainerManager):
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
    Also any top level view can include a subview that is placed into a sub-container. If a top
    level view can include a sub-view, the sub-container is created after the top level view is loaded and
    initialized. When sub-view is loaded, it is placed into the top level view's sub-container. The sub-container
    is destroyed when the top level view is destroyed.
    
    2. Views life time
    The 'view scope' concept is introduced to simplify views lifetime management. View lifetime is
    defined by its scope and is controlled by the container manager through the scope controller.
    View scope defines when the view should be destroyed: if the parent view (parent scope) is
    destroyed, the subview is destroyed too. For details please see ScopeController description.
    """

    def __init__(self, loader, *containers):
        super(ContainerManager, self).__init__()
        self.onViewAddedToContainer = Event()
        self.onViewLoading = Event()
        self.onViewLoaded = Event()
        self.__globalContainer = _GlobalViewContainer(weakref.proxy(self))
        for container in containers:
            assert isinstance(container, ViewContainer)
            self.__globalContainer.addChildContainer(container)

        self.__loader = loader
        self.__loader.onViewLoadInit += self.__onViewLoadInit
        self.__loader.onViewLoaded += self.__onViewLoaded
        self.__scopeController = GlobalScopeController()
        self.__scopeController.create()
        self.__viewCache = _ViewCollection()
        self.__chainMng = _ChainManager(weakref.proxy(self))

    def _dispose(self):
        self.__viewCache.destroy()
        self.__chainMng.destroy()
        if self.__loader is not None:
            self.__loader.onViewLoaded -= self.__onViewLoaded
            self.__loader.onViewLoadInit -= self.__onViewLoadInit
            self.__loader = None
        for viewType in _CONTAINERS_DESTROY_ORDER:
            container = self.__globalContainer.findContainer(viewType)
            if container is not None:
                LOG_DEBUG('Destroy container {} ({})'.format(viewType, container))
                container.destroy()

        self.__globalContainer.destroy()
        self.onViewAddedToContainer.clear()
        self.__scopeController.destroy()
        self.__scopeController = None
        super(ContainerManager, self)._dispose()
        return

    def destroyViews(self, alias, name=None):

        def compareByAlias(view):
            return view.key.alias == alias

        def compareByAliasAndName(view):
            viewKey = view.key
            return viewKey.alias == alias and viewKey.name == name

        if name is None:
            comparator = compareByAlias
        else:
            comparator = compareByAliasAndName
        views = self.__scopeController.findViews(comparator)
        views.extend(self.__viewCache.findViews(comparator))
        for view in views:
            if not view.isDisposed():
                LOG_DEBUG('The view {} will be destroyed...'.format(view))
                view.destroy()

        viewKey = ViewKey(alias, name)
        chain = self.__chainMng.getChainByViewKey(viewKey)
        if chain is not None:
            chain.removeViewByViewKey(viewKey)
        return

    def loadChain(self, chainItems):
        """
        Loads the given views (chain items) one after the other.
        
        :param chainItems: list of ChainItem items.
        """
        chain = _LoadingChain(chainItems)
        if self.__chainMng.addChain(chain):
            chain.run()
        else:
            LOG_WARNING('Could not add a new chain. Loading of chain [{}] is canceled.'.format(chainItems))
            chain.destroy()

    def load(self, loadParams, *args, **kwargs):
        """
        Loads a view with the given alias and puts it to the appropriate container (layer).
        
        :param loadParams: instance of ViewLoadParams
        :param args: args to be passed to view's constructor.
        :param kwargs: kwargs to be passed to view's constructor.
        :return: instance of view (loading or loaded). None if no view is loaded.
        """
        viewKey = loadParams.viewKey
        viewLoadingItem = self.__loader.getViewLoadingItem(viewKey)
        if viewLoadingItem is not None:
            LOG_DEBUG('View with key {} is already loading. item=[{}]'.format(viewKey, viewLoadingItem))
            view = viewLoadingItem.pyEntity
            if loadParams.loadMode == ViewLoadMode.DEFAULT:
                loadingViewLoadMode = viewLoadingItem.loadParams.loadMode
                if loadingViewLoadMode == ViewLoadMode.PRELOAD:
                    viewLoadingItem.loadParams = loadParams
                    self.__addLoadingView(view)
            elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                pass
            else:
                LOG_WARNING('Unsupported load mode {}. View loading will be skipped.'.format(loadParams))
                view = None
        else:
            view = self.__globalContainer.findView(viewKey)
            if view is None:
                view = self.__viewCache.getView(viewKey)
                if view is None:
                    chain = self.__chainMng.getChainByViewKey(viewKey)
                    if chain is not None:
                        LOG_WARNING('View with loadParams={} is in the loading chain {}. The request will be skipped.'.format(loadParams, chain))
                    else:
                        LOG_DEBUG('Load view with loadParams={}. Loader=[{}]'.format(loadParams, self.__loader))
                        if loadParams.loadMode == ViewLoadMode.DEFAULT:
                            view = self.__loader.loadView(loadParams, *args, **kwargs)
                            self.__addLoadingView(view)
                        elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                            view = self.__loader.loadView(loadParams, *args, **kwargs)
                        else:
                            LOG_WARNING('Unsupported load mode {}. View loading will be skipped.'.format(loadParams))
                elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                    LOG_DEBUG('View with key {} ({}) is already pre-loaded.'.format(viewKey, view))
                elif loadParams.loadMode == ViewLoadMode.DEFAULT:
                    LOG_DEBUG('Load view with loadParams={} from the cache. Cache=[{}]'.format(loadParams, self.__viewCache))
                    self.__viewCache.removeView(viewKey)
                    self.__showAndInitializeView(view)
                    view.validate(*args, **kwargs)
                else:
                    LOG_WARNING('Unsupported load mode {}. View loading will be skipped.'.format(loadParams))
                    view = None
            else:
                LOG_DEBUG('View with key {} ({}) is already loaded.'.format(viewKey, view))
                viewType = view.settings.type
                viewContainer = self.__globalContainer.findContainer(viewType)
                viewContainer.addView(view)
                view.validate(*args, **kwargs)
        return view

    def getContainer(self, viewType):
        """
        Returns container by the given type or None if there is no such container.
        
        :param viewType: viewType: View type. @see ViewTypes.
        """
        return self.__globalContainer.findContainer(viewType)

    def getViewByKey(self, viewKey):
        """
        Returns view object by view key if is view already exists
        :param viewKey: view key (@see ViewKey)
        :return: view object (@see View)
        """
        if self.__loader is not None:
            loadingItem = self.__loader.getViewLoadingItem(viewKey)
            if loadingItem is not None:
                return loadingItem.pyEntity
        sources = (self.__globalContainer.findView, self.__viewCache.getView)
        for source in sources:
            view = source(viewKey)
            if view is not None:
                return view

        return

    def isViewCreated(self, viewKey):
        """
        Return True view is loaded and visible
        :param viewKey: view key (@see ViewKey)
        """
        return self.__globalContainer.findView(viewKey) is not None

    def isViewInCache(self, viewKey):
        """
        Return True view is loaded and is in cache
        :param viewKey: view key (@see ViewKey)
        """
        return self.__viewCache.getView(viewKey) is not None

    def isModalViewsIsExists(self):
        """
        Returns True if a modal view exists, otherwise returns False.
        """
        for viewType in _POPUPS_CONTAINERS:
            container = self.__globalContainer.findContainer(viewType)
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
        container = self.__globalContainer.findContainer(viewType)
        if container is not None:
            return container.getView(criteria=criteria)
        else:
            LOG_WARNING('Could not found container {}.'.format(viewType))
            return

    def isViewAvailable(self, viewType, criteria=None):
        """
        If you want to get some view from some container, it`s may be
        unsafely operation. For example, I want to get a Hangar from a Lobby
        view. it`s a bad situation and method "getView" detects this state.
        Then, if you just want to detect an existing View, use isViewAvailable method.
        
        :param viewType: type of view. @see ViewTypes.
        :param criteria: criteria to find view in container.
        """
        container = self.__globalContainer.findContainer(viewType)
        return container.getView(criteria=criteria) is not None if container is not None else False

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

    def clear(self):
        """
        Clears pop-ups containers.
        """
        for viewType in _POPUPS_CONTAINERS:
            container = self.__globalContainer.findContainer(viewType)
            if container is not None:
                container.clear()

        return

    def closePopUps(self):
        """
        Closes all popUps: widows and dialogs.
        """
        self.as_closePopUpsS()

    def registerViewContainer(self, viewType, uniqueName):
        self.as_registerContainerS(viewType, uniqueName)
        LOG_DEBUG('A new container [type={}, name={}] has been registered.'.format(viewType, uniqueName))

    def unregisterViewContainer(self, viewType):
        self.as_unregisterContainerS(viewType)
        LOG_DEBUG('The container [type={}] has been unregistered.'.format(viewType))

    def __addLoadingView(self, pyView):
        viewType = pyView.settings.type
        viewContainer = self.__globalContainer.findContainer(viewType)
        if viewContainer is not None:
            viewContainer.addLoadingView(pyView)
        else:
            LOG_WARNING('Loading of view {} is requested but the container {} is still not exist!'.format(pyView, viewType))
        self.__scopeController.addLoadingView(pyView, False)
        return

    def __showAndInitializeView(self, pyView):
        viewType = pyView.settings.type
        if viewType is None:
            LOG_ERROR('Type of view is not defined. View {} will be destroyed.', pyView)
            pyView.destroy()
            return False
        else:
            status = False
            container = self.__globalContainer.findContainer(viewType)
            if container is not None:
                if ViewTypes.DEFAULT == viewType:
                    self.closePopUps()
                if container.addView(pyView):
                    self.__scopeController.addView(pyView, False)
                    self.as_showS(pyView.uniqueName, 0, 0)
                    pyView.create()
                    self.onViewAddedToContainer(container, pyView)
                    status = True
                else:
                    LOG_ERROR('{} view cannot be added to container {} and will be destroyed.'.format(pyView, container))
                    pyView.destroy()
            else:
                LOG_ERROR('Type {} of view {} is not supported or container has not been properly created'.format(viewType, pyView))
                pyView.destroy()
            return status

    def __addViewToCache(self, pyView):
        view = self.__viewCache.getView(pyView.key)
        if view is not None:
            LOG_UNEXPECTED('The view with key {} is already in the cache.'.format(pyView.key), pyView, view)
            if view != pyView:
                view.destroy()
                if self.__viewCache.addView(pyView):
                    LOG_DEBUG('View {} has been added to the cache {}'.format(pyView, self.__viewCache))
                else:
                    LOG_DEBUG('Cannot add view {} in the cache {}'.format(pyView, self.__viewCache))
        elif self.__viewCache.addView(pyView):
            LOG_DEBUG('View {} has been added to the cache {}'.format(pyView, self.__viewCache))
        else:
            LOG_DEBUG('Cannot add view {} in the cache {}'.format(pyView, self.__viewCache))
        return

    def __onViewLoaded(self, pyView, loadParams):
        self.onViewLoaded(pyView)
        loadMode = loadParams.loadMode
        if loadMode == ViewLoadMode.DEFAULT:
            if self.__scopeController.isViewLoading(pyView=pyView):
                self.__showAndInitializeView(pyView)
            else:
                LOG_DEBUG('{} view loading is cancelled because its scope has been destroyed.'.format(pyView))
                pyView.destroy()
        elif loadMode == ViewLoadMode.PRELOAD:
            self.__addViewToCache(pyView)
        else:
            LOG_WARNING('Unsupported load mode {}. View {} will be destroyed.'.format(loadMode, pyView))
            pyView.destroy()

    def __onViewLoadInit(self, view, *args, **kwargs):
        self.onViewLoading(view)
