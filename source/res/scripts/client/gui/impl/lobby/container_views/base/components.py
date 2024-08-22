# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/container_views/base/components.py
import typing
from weakref import ref
from Event import Event
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.container_views.base.events import ContainerLifecycleEvents
from gui.impl.pub import ViewImpl
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import List, Optional, Type
    from frameworks.wulf import View, ViewEvent, Window
    from frameworks.wulf.gui_constants import ShowingStatus

class ContainerBase(object):

    def __init__(self, *args, **kwargs):
        self.__components = None
        self.__context = self._getContext(**kwargs)
        self.__lifecycleEvents = ContainerLifecycleEvents()
        self.__interactionController = self.__createIterationController()
        self.__addComponents()
        super(ContainerBase, self).__init__(*args, **kwargs)
        return

    @property
    def context(self):
        return self.__context

    @property
    def components(self):
        return self.__components

    @property
    def interactionCtrl(self):
        return self.__interactionController

    @property
    def lifecycleEvents(self):
        return self.__lifecycleEvents

    def refresh(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)
            for component in self.components.values():
                cvm = component._getViewModel(vm)
                cvm.setComponentKey(component.key)
                component._fillViewModel(cvm)

    def createToolTip(self, event):
        window = self.__callComponentMethod('createToolTip', event)
        return window or super(ContainerBase, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        view = self.__callComponentMethod('createToolTipContent', event, contentID)
        return view or super(ContainerBase, self).createToolTipContent(event, contentID)

    def createPopOver(self, event):
        window = self.__callComponentMethod('createPopOver', event)
        return window or super(ContainerBase, self).createPopOver(event)

    def createPopOverContent(self, event):
        view = self.__callComponentMethod('createPopOverContent', event)
        return view or super(ContainerBase, self).createPopOverContent(event)

    def createContextMenu(self, event):
        window = self.__callComponentMethod('createContextMenu', event)
        return window or super(ContainerBase, self).createContextMenu(event)

    def createContextMenuContent(self, event):
        view = self.__callComponentMethod('createContextMenuContent', event)
        return view or super(ContainerBase, self).createContextMenuContent(event)

    def _getContext(self, *args, **kwargs):
        raise NotImplementedError

    def _getComponents(self):
        return []

    def _getInteractionControllerCls(self):
        raise NotImplementedError

    def _fillViewModel(self, vm):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        super(ContainerBase, self)._onLoading(*args, **kwargs)
        self.lifecycleEvents.onLoading(*args, **kwargs)
        self.refresh()

    def _onLoaded(self, *args, **kwargs):
        super(ContainerBase, self)._onLoaded(*args, **kwargs)
        self.lifecycleEvents.onLoaded(*args, **kwargs)

    def _initialize(self, *args, **kwargs):
        super(ContainerBase, self)._initialize(*args, **kwargs)
        self.lifecycleEvents.initialize(*args, **kwargs)

    def _finalize(self):
        self.lifecycleEvents.finalize()
        super(ContainerBase, self)._finalize()
        self.__removeComponents()
        del self.__interactionController
        del self.__context
        del self.__lifecycleEvents

    def _onReady(self):
        super(ContainerBase, self)._onReady()
        self.lifecycleEvents.onReady()

    def _onShown(self):
        super(ContainerBase, self)._onShown()
        self.lifecycleEvents.onShown()

    def _onHidden(self):
        super(ContainerBase, self)._onHidden()
        self.lifecycleEvents.onHidden()

    def _onFocus(self, focused):
        super(ContainerBase, self)._onFocus(focused)
        self.lifecycleEvents.onFocus(focused)

    def _swapStates(self, oldStatus, newStatus):
        super(ContainerBase, self)._swapStates(oldStatus, newStatus)
        try:
            self.lifecycleEvents.swapStates(oldStatus, newStatus)
        except AttributeError:
            pass

    def _swapShowingStates(self, oldStatus, newStatus):
        super(ContainerBase, self)._swapShowingStates(oldStatus, newStatus)
        self.lifecycleEvents.swapShowingStates(oldStatus, newStatus)

    def _subscribe(self):
        super(ContainerBase, self)._subscribe()
        self.interactionCtrl.subscribe()

    def _unsubscribe(self):
        self.interactionCtrl.unsubscribe()
        super(ContainerBase, self)._unsubscribe()

    def __addComponents(self):
        self.__components = {}
        for component in self._getComponents():
            self.__components[component.key] = component

    def __removeComponents(self):
        for component in list(self.__components.keys()):
            del self.__components[component]

    def __callComponentMethod(self, method, event, *args, **kwargs):
        componentKey = event.getArgument('componentKey')
        if componentKey is None:
            return
        else:
            component = self.__components.get(componentKey, None)
            if component is None:
                msg = 'Calling "%s" failed. No component with key "%s" in component list' % (method, componentKey)
                raise SoftException(msg)
            if hasattr(component, method):
                result = getattr(component, method)(event, *args, **kwargs)
                if result is not None:
                    return result
            return

    def __createIterationController(self):
        controllerCls = self._getInteractionControllerCls()
        return controllerCls(self)


class ComponentBase(object):

    def __init__(self, key, parent):
        msg = 'Parent view must be subclassed from ContainerBase and ViewImpl. ContainerBase MUST be first.'
        super(ComponentBase, self).__init__()
        self.__key = key
        self.__parent = ref(parent)
        self.__events = ref(parent.interactionCtrl.eventsProvider)
        self.__subscribeToLifecycleEvents()

    @property
    def context(self):
        return self.parent.context

    @property
    def events(self):
        return self.__events()

    @property
    def key(self):
        return self.__key

    @property
    def parent(self):
        return self.__parent()

    @property
    def viewModel(self):
        return self._getViewModel(self.parent.viewModel)

    def createContextMenu(self, event):
        return None

    def createContextMenuContent(self, event):
        return None

    def createPopOver(self, event):
        return None

    def createPopOverContent(self, event):
        return None

    def createToolTip(self, event):
        return None

    def createToolTipContent(self, event, contentID):
        return None

    def setData(self, data):
        pass

    def _getEvents(self):
        return tuple()

    def _getViewModel(self, vm):
        raise NotImplementedError

    def _fillViewModel(self, vm):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        self._subscribe()

    def _onLoaded(self, *args, **kwargs):
        pass

    def _initialize(self, *args, **kwargs):
        pass

    def _finalize(self):
        self._unsubscribe()
        self.__unsubscribeFromLifecycleEvents()

    def _onReady(self):
        pass

    def _onShown(self):
        pass

    def _onHidden(self):
        pass

    def _onFocus(self, focused):
        pass

    def _swapStates(self, oldStatus, newStatus):
        pass

    def _swapShowingStates(self, oldStatus, newStatus):
        pass

    def _subscribe(self):
        for event, handler in self._getEvents():
            event += handler

    def _unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

    def __subscribeToLifecycleEvents(self):
        for name in dir(self.parent.lifecycleEvents):
            event = getattr(self.parent.lifecycleEvents, name)
            if not isinstance(event, Event):
                continue
            event += getattr(self, '_' + name)

    def __unsubscribeFromLifecycleEvents(self):
        for name in dir(self.parent.lifecycleEvents):
            event = getattr(self.parent.lifecycleEvents, name)
            if not isinstance(event, Event):
                continue
            event -= getattr(self, '_' + name)
