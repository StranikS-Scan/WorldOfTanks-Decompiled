# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/containers.py
import logging
import weakref
from collections import OrderedDict
from Event import Event
from shared_utils import CONST_CONTAINER
from gui.Scaleform.framework.ScopeControllers import GlobalScopeController
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.abstract.ContainerManagerMeta import ContainerManagerMeta
from gui.Scaleform.framework.managers.loaders import ViewLoadMode, ViewKey
from gui.Scaleform.framework.settings import UIFrameworkImpl
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_POPUPS_CONTAINERS = (ViewTypes.TOP_WINDOW, ViewTypes.BROWSER, ViewTypes.WINDOW)
_CONTAINERS_DESTROY_ORDER = (ViewTypes.MARKER,
 ViewTypes.DEFAULT,
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
        raise NotImplementedError('ExternalCriteria.find must be implemented')


_VIEW_SEARCH_CRITERIA_HANDLERS = {VIEW_SEARCH_CRITERIA.VIEW_ALIAS: lambda view, value: view.alias == value,
 VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: lambda view, value: view.uniqueName == value}

class ViewContainer(object):
    __slots__ = ('__viewType', '__child', '_views', '_loadingViews', '__containerManager', '__parentContainer')

    def __init__(self, viewType, containerManager=None):
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
        self._removeLoadingViews()
        self._removeViews()

    def getViewType(self):
        return self.__viewType

    def getParentContainer(self):
        return self.__parentContainer

    def addChildContainer(self, container, name=None):
        viewType = container.getViewType()
        if viewType not in self.__child:
            self.__child[container.getViewType()] = container
            container.__containerManager = self.__containerManager
            container.__parentContainer = self
            self._registerContainer(container.getViewType(), name)
            return True
        return False

    def removeChildContainer(self, viewType):
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
        return self.__child.get(viewType, None)

    def findContainer(self, viewType):
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
        if viewKey in self._views:
            return self._views[viewKey]
        else:
            for c in self.__child.itervalues():
                view = c.findView(viewKey)
                if view is not None:
                    return view

            return

    def addView(self, pyView):
        if not self.isViewCompatible(pyView):
            _logger.error('Cannot add view %r to container %r. Incompatible view type.', pyView, self)
            return False
        return self._addView(pyView)

    def removeView(self, pyView):
        viewType = pyView.viewType
        container = self.findContainer(viewType)
        if container is None:
            _logger.warning('There is no container "%s" to remove view "%r"!', viewType, pyView)
            return False
        else:
            return container._removeView(pyView) if pyView.key in container._views else False

    def addLoadingView(self, pyView):
        if not self.isViewCompatible(pyView):
            _logger.error('Cannot add loading view %r to container %r. Incompatible view type.', pyView, self)
            return False
        return self._addLoadingView(pyView)

    def removeLoadingView(self, pyView):
        viewType = pyView.viewType
        container = self.findContainer(viewType)
        if container is None:
            _logger.warning('There is no container %s to remove loading view %r!', viewType, pyView)
            return False
        else:
            return container._removeLoadingView(pyView) if pyView.key in container._loadingViews else False

    def getAllLoadingViews(self):
        views = self._loadingViews.values()
        for c in self.__child.itervalues():
            views.extend(c.getAllLoadingViews())

        return views

    def removeAllLoadingViews(self):
        self._removeLoadingViews()
        for c in self.__child.itervalues():
            c.removeAllLoadingViews()

    def removeLoadingSubViews(self):
        for c in self.__child.itervalues():
            c.removeAllLoadingViews()

    def getView(self, criteria):
        if isinstance(criteria, dict):
            view = self.__findByDictCriteria(criteria)
        elif isinstance(criteria, ExternalCriteria):
            view = self.__findByExCriteria(criteria)
        else:
            _logger.error('Criteria is invalid: %r', criteria)
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
        return self.__viewType == pyView.viewType

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
        _logger.debug('View with key %s has been added to container %r', viewKey, self)
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
            _logger.debug('Sub container %r is created for view %r.', subContainerSettings, str(pyView))

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

    def __init__(self, viewType, manager=None):
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

    def _onViewCreated(self, pyView):
        super(DefaultContainer, self)._onViewCreated(pyView)
        self._setMainView(pyView)

    def _setMainView(self, pyView):
        if pyView.isCreated():
            super(DefaultContainer, self)._setMainView(pyView)


class PopUpContainer(ViewContainer):
    pass


class _GlobalViewContainer(ViewContainer):
    __slots__ = ()

    def __init__(self, containerManager):
        super(_GlobalViewContainer, self).__init__(None, containerManager)
        return

    def _registerContainer(self, viewType, name):
        pass

    def _unregisterContainer(self, viewType):
        pass


class _ViewCollection(object):

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

    def __init__(self, chainItems):
        super(_LoadingChain, self).__init__()
        self.__chainManager = None
        self.__currentItem = None
        self.__currentView = None
        self.__queue = OrderedDict()
        for item in chainItems:
            viewKey = item.loadParams.viewKey
            self.__queue[viewKey] = item

        return

    def __repr__(self):
        return '{}[{}]=[currentView={}, queue={}, '.format(self.__class__.__name__, hex(id(self)), self.__currentView, self.__queue)

    def destroy(self):
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
        return viewKey in self.__queue

    def getViewByViewKey(self, viewKey):
        self.__queue.get(viewKey, None)
        return

    def removeViewByViewKey(self, viewKey):
        if self.isViewInChain(viewKey):
            del self.__queue[viewKey]

    def hasIntersectionWith(self, chain):
        for viewKey in self.__queue:
            if chain.isViewInChain(viewKey):
                return True

        return False

    def run(self):
        if self.__currentItem is not None:
            _logger.warning('Chain of views loading is already running: %r.', self)
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
            _logger.warning('Could not load view with key %s. Chain manager is not specified.', viewKey)

        return

    def __onViewDisposed(self, pyView):
        if pyView == self.__currentView:
            self.__loadNextView()
        else:
            _logger.warning('Got onDispose event for view %r. Unexpected case.', pyView)

    def __onViewCreated(self, pyView):
        if pyView == self.__currentView:
            self.__loadNextView()
        else:
            _logger.warning('Got onCreated event for view %r. Unexpected case.', pyView)

    def __addViewEventListeners(self, pyView):
        pyView.onCreated += self.__onViewCreated
        pyView.onDispose += self.__onViewDisposed

    def __removeViewEventListeners(self, pyView):
        pyView.onCreated -= self.__onViewCreated
        pyView.onDispose -= self.__onViewDisposed


class _ChainManager(object):

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

    def __init__(self, loader, *containers):
        super(ContainerManager, self).__init__()
        self.onViewAddedToContainer = Event()
        self.onViewLoading = Event()
        self.onViewLoaded = Event()
        self.__globalContainer = _GlobalViewContainer(weakref.proxy(self))
        for container in containers:
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
                _logger.debug('Destroy container %s (%r)', viewType, container)
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
                _logger.debug('The view %r will be destroyed...', view)
                view.destroy()

        viewKey = ViewKey(alias, name)
        chain = self.__chainMng.getChainByViewKey(viewKey)
        if chain is not None:
            chain.removeViewByViewKey(viewKey)
        return

    def loadChain(self, chainItems):
        chain = _LoadingChain(chainItems)
        if self.__chainMng.addChain(chain):
            chain.run()
        else:
            _logger.warning('Could not add a new chain. Loading of chain [%r] is canceled.', chainItems)
            chain.destroy()

    def load(self, loadParams, *args, **kwargs):
        viewKey = loadParams.viewKey
        viewLoadingItem = self.__loader.getViewLoadingItem(viewKey)
        if viewLoadingItem is not None:
            _logger.debug('View with key %s is already loading. item=[%r]', viewKey, viewLoadingItem)
            view = viewLoadingItem.pyEntity
            if loadParams.loadMode == ViewLoadMode.DEFAULT:
                loadingViewLoadMode = viewLoadingItem.loadParams.loadMode
                if loadingViewLoadMode == ViewLoadMode.PRELOAD:
                    viewLoadingItem.loadParams = loadParams
                    self.__addLoadingView(view)
            elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                pass
            else:
                _logger.warning('Unsupported load mode %r. View loading will be skipped.', loadParams)
                view = None
        else:
            view = self.__globalContainer.findView(viewKey)
            if view is None:
                view = self.__viewCache.getView(viewKey)
                if view is None:
                    chain = self.__chainMng.getChainByViewKey(viewKey)
                    if chain is not None:
                        _logger.warning('View with loadParams=%r is in the loading chain %r. The request will be skipped.', loadParams, chain)
                    else:
                        _logger.debug('Load view with loadParams=%r. Loader=[%r]', loadParams, self.__loader)
                        if loadParams.loadMode == ViewLoadMode.DEFAULT:
                            view = self.__loader.loadView(loadParams, *args, **kwargs)
                            self.__addLoadingView(view)
                        elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                            view = self.__loader.loadView(loadParams, *args, **kwargs)
                        else:
                            _logger.warning('Unsupported load mode %r. View loading will be skipped.', loadParams)
                elif loadParams.loadMode == ViewLoadMode.PRELOAD:
                    _logger.debug('View with key %s (%r) is already pre-loaded.', viewKey, view)
                elif loadParams.loadMode == ViewLoadMode.DEFAULT:
                    _logger.debug('Load view with loadParams=%r from the cache. Cache=[%r]', loadParams, self.__viewCache)
                    self.__viewCache.removeView(viewKey)
                    self.__showAndInitializeView(view)
                    view.validate(*args, **kwargs)
                else:
                    _logger.warning('Unsupported load mode %r. View loading will be skipped.', loadParams)
                    view = None
            else:
                _logger.debug('View with key %s (%r) is already loaded.', viewKey, view)
                viewType = view.viewType
                viewContainer = self.__globalContainer.findContainer(viewType)
                viewContainer.addView(view)
                view.validate(*args, **kwargs)
        return view

    def getContainer(self, viewType):
        return self.__globalContainer.findContainer(viewType)

    def getViewByKey(self, viewKey):
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
        return self.__globalContainer.findView(viewKey) is not None

    def isViewInCache(self, viewKey):
        return self.__viewCache.getView(viewKey) is not None

    def isModalViewsIsExists(self):
        for viewType in _POPUPS_CONTAINERS:
            container = self.__globalContainer.findContainer(viewType)
            if container is not None and container.getViewCount(isModal=True):
                return True

        return False

    def getView(self, viewType, criteria=None):
        container = self.__globalContainer.findContainer(viewType)
        if container is not None:
            return container.getView(criteria=criteria)
        else:
            _logger.warning('Could not found container %s.', viewType)
            return

    def isViewAvailable(self, viewType, criteria=None):
        container = self.__globalContainer.findContainer(viewType)
        return container.getView(criteria=criteria) is not None if container is not None else False

    def showContainers(self, *viewTypes):
        self.as_showContainersS(viewTypes)

    def hideContainers(self, *viewTypes):
        self.as_hideContainersS(viewTypes)

    def isContainerShown(self, viewType):
        return self.as_isContainerShownS(viewType)

    def clear(self):
        for viewType in _POPUPS_CONTAINERS:
            container = self.__globalContainer.findContainer(viewType)
            if container is not None:
                container.clear()

        return

    def closePopUps(self):
        self.as_closePopUpsS()

    def registerViewContainer(self, viewType, uniqueName):
        self.as_registerContainerS(viewType, uniqueName)
        _logger.debug('A new container [type=%s, name=%s] has been registered.', viewType, uniqueName)

    def unregisterViewContainer(self, viewType):
        self.as_unregisterContainerS(viewType)
        _logger.debug('The container [type=%s] has been unregistered.', viewType)

    def __addLoadingView(self, pyView):
        viewType = pyView.viewType
        viewContainer = self.__globalContainer.findContainer(viewType)
        if viewContainer is not None:
            viewContainer.addLoadingView(pyView)
        else:
            _logger.warning('Loading of view %r is requested but the container %s is still not exist!', pyView, viewType)
        self.__scopeController.addLoadingView(pyView, False)
        return

    def __showAndInitializeView(self, pyView):
        viewType = pyView.viewType
        if viewType is None:
            _logger.error('Type of view is not defined. View %r will be destroyed.', pyView)
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
                    if pyView.uiImpl == UIFrameworkImpl.SCALEFORM:
                        self.as_showS(pyView.uniqueName, 0, 0)
                    pyView.create()
                    self.onViewAddedToContainer(container, pyView)
                    status = True
                else:
                    _logger.error('%r view cannot be added to container %r and will be destroyed.', pyView, container)
                    pyView.destroy()
            else:
                _logger.error('Type %s of view %r is not supported or container has not been properly created', viewType, pyView)
                pyView.destroy()
            return status

    def __addViewToCache(self, pyView):
        view = self.__viewCache.getView(pyView.key)
        if view is not None:
            _logger.warning('The view with key %r is already in the cache.', pyView.key)
            if view != pyView:
                view.destroy()
                if self.__viewCache.addView(pyView):
                    _logger.debug('View %r has been added to the cache %r', pyView, self.__viewCache)
                else:
                    _logger.debug('Cannot add view %r in the cache %r', pyView, self.__viewCache)
        elif self.__viewCache.addView(pyView):
            _logger.debug('View %r has been added to the cache %r', pyView, self.__viewCache)
        else:
            _logger.debug('Cannot add view %r in the cache %r', pyView, self.__viewCache)
        return

    def __onViewLoaded(self, pyView, loadParams):
        self.onViewLoaded(pyView)
        loadMode = loadParams.loadMode
        if loadMode == ViewLoadMode.DEFAULT:
            if self.__scopeController.isViewLoading(pyView=pyView):
                self.__showAndInitializeView(pyView)
            else:
                _logger.debug('%r view loading is cancelled because its scope has been destroyed.', pyView)
                pyView.destroy()
        elif loadMode == ViewLoadMode.PRELOAD:
            self.__addViewToCache(pyView)
        else:
            _logger.warning('Unsupported load mode %s. View %r will be destroyed.', loadMode, pyView)
            pyView.destroy()

    def __onViewLoadInit(self, view, *args, **kwargs):
        self.onViewLoading(view)
