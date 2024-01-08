# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/windows_system/window.py
import logging
import typing
import Event
from soft_exception import SoftException
from ..py_object_binder import PyObjectEntity, getProxy, getObject
from ..py_object_wrappers import PyObjectWindowSettings
from ..py_object_wrappers import PyObjectWindow
from ..view.view import View
from ..view.view_model import ViewModel
from ..gui_constants import WindowStatus, WindowFlags, ViewStatus, ShowingStatus
_logger = logging.getLogger(__name__)

class WindowSettings(object):
    __slots__ = ('__proxy',)

    def __init__(self):
        super(WindowSettings, self).__init__()
        self.__proxy = PyObjectWindowSettings()

    def clear(self):
        self.__proxy = None
        return

    @property
    def proxy(self):
        return self.__proxy

    @property
    def flags(self):
        return self.__proxy.flags

    @flags.setter
    def flags(self, flags):
        self.__proxy.flags = flags

    @property
    def layer(self):
        return self.__proxy.layer

    @layer.setter
    def layer(self, layer):
        self.__proxy.layer = layer

    @property
    def name(self):
        return self.__proxy.name

    @name.setter
    def name(self, name):
        self.__proxy.name = name

    @property
    def areaID(self):
        return self.__proxy.areaID

    @areaID.setter
    def areaID(self, areaID):
        self.__proxy.areaID = areaID

    @property
    def decorator(self):
        return getObject(self.__proxy.decorator)

    @decorator.setter
    def decorator(self, decorator):
        if decorator is not None and not isinstance(decorator, View):
            raise SoftException('Decorator should be View class or extends it')
        self.__proxy.decorator = getProxy(decorator)
        return

    @property
    def content(self):
        return getObject(self.__proxy.content)

    @content.setter
    def content(self, content):
        if content is not None and not isinstance(content, View):
            raise SoftException('Content should be View class or extends it')
        self.__proxy.content = getProxy(content)
        return

    @property
    def parent(self):
        return getObject(self.__proxy.parent)

    @parent.setter
    def parent(self, parent):
        if parent is not None and not isinstance(parent, Window):
            raise SoftException('Content should be Window class or extends it')
        self.__proxy.parent = getProxy(parent)
        return


class Window(PyObjectEntity):
    __slots__ = ('onStatusChanged', '__windowStatus', 'onShowingStatusChanged', 'onFocusChanged', '__showingStatus', '__isShown', '__isFocused', '__isReady', '__weakref__')

    def __init__(self, settings):
        settings.name = self.getName()
        super(Window, self).__init__(PyObjectWindow(settings.proxy))
        self.onStatusChanged = Event.Event()
        self.__windowStatus = WindowStatus.UNDEFINED if self.proxy is None else self.proxy.windowStatus
        self.onShowingStatusChanged = Event.Event()
        self.__showingStatus = ShowingStatus.HIDDEN
        self.__isShown = False
        self.__isReady = False
        self.__isFocused = False
        self.onFocusChanged = Event.Event()
        _logger.debug('Creating %r with %r', self, settings)
        return

    def __repr__(self):
        return '{}(uniqueID={}, layer={}, decorator={}, content={})'.format(self.__class__.__name__, self.uniqueID, self.layer, self.decorator, self.content)

    def getName(self):
        module = self.__class__.__module__
        return self.__class__.__name__ if module is None else '.'.join((module, self.__class__.__name__))

    @property
    def decorator(self):
        proxy = self.proxy
        return proxy.decorator if proxy is not None else None

    @property
    def content(self):
        proxy = self.proxy
        return proxy.content if proxy is not None else None

    @property
    def parent(self):
        return self.proxy.parent if self.proxy is not None else None

    @property
    def layer(self):
        return self.proxy.layer if self.proxy is not None else -1

    @property
    def uniqueID(self):
        return self.proxy.uniqueID if self.proxy is not None else 0

    @property
    def windowFlags(self):
        return self.proxy.windowFlags if self.proxy is not None else WindowFlags.UNDEFINED

    @property
    def windowStatus(self):
        return self.__windowStatus

    @property
    def showingStatus(self):
        return self.__showingStatus

    @property
    def isFocused(self):
        return self.__isFocused

    @property
    def position(self):
        proxy = self.proxy
        return self.proxy.windowPosition if proxy is not None else (0.0, 0.0)

    @property
    def globalPosition(self):
        proxy = self.proxy
        return self.proxy.calculateGlobalPosition if proxy is not None else (0.0, 0.0)

    @property
    def size(self):
        proxy = self.proxy
        return self.proxy.windowSize if proxy is not None else (0.0, 0.0)

    @property
    def typeFlag(self):
        return self.windowFlags & WindowFlags.WINDOW_TYPE_MASK

    @property
    def stateFlag(self):
        return self.windowFlags & WindowFlags.WINDOW_STATE_MASK

    @property
    def modalityFlag(self):
        return self.windowFlags & WindowFlags.WINDOW_MODALITY_MASK

    def checkWindowFlags(self, flags):
        return self.proxy.checkWindowFlags(flags)

    def isModal(self):
        return self.proxy.isModal()

    def setDecorator(self, decorator):
        self.__detachFromDecorator()
        self.proxy.setDecorator(getProxy(decorator))
        self.__attachToDecorator()

    def setContent(self, content):
        self.__detachFromContent()
        self.proxy.setContent(getProxy(content))
        self.__attachToContent()

    def setParent(self, parent):
        self.proxy.setParent(getProxy(parent))

    def load(self):
        _logger.info('Loading window: %r', self)
        self.proxy.load()

    def reload(self):
        self.proxy.reload()

    def destroy(self):
        _logger.debug('Destroying window: %r', self)
        if self.proxy is not None:
            self.proxy.destroy()
        self.onStatusChanged.clear()
        return

    def setLayer(self, layerID):
        self.proxy.setLayer(layerID)

    def resetLayer(self):
        self.proxy.resetLayer()

    def tryFocus(self):
        self.proxy.tryFocus()

    def show(self, focus=True):
        self.proxy.show(focus)

    def hide(self, destroy=False):
        self.proxy.hide(destroy)

    def isHidden(self):
        return self.proxy.isHidden()

    def _getDecoratorViewModel(self):
        decorator = self.decorator
        return decorator.getViewModel() if decorator is not None else None

    def _initialize(self):
        self.__attachToDecorator()
        self.__attachToContent()

    def _finalize(self):
        self.__detachFromDecorator()
        self.__detachFromContent()

    def _onReady(self):
        self.show()

    def _onShown(self):
        _logger.debug('_onShown %r', self)

    def _onHidden(self):
        _logger.debug('_onHidden %r', self)

    def _onFocus(self, focused):
        _logger.debug('_onFocus %r %r', focused, self)

    def _onDecoratorReady(self):
        pass

    def _onDecoratorReleased(self):
        pass

    def _onContentReady(self):
        pass

    def _onContentReleased(self):
        pass

    def _swapShowingStates(self, oldStatus, newStatus):
        if newStatus == ShowingStatus.SHOWN:
            if not self.__isShown:
                self.__isShown = True
                self._onShown()
        elif newStatus == ShowingStatus.HIDDEN:
            if self.__isShown:
                self.__isShown = False
                self._onHidden()
        elif newStatus == ShowingStatus.SHOWING:
            pass
        elif newStatus == ShowingStatus.HIDING:
            pass

    def _cInit(self):
        self._initialize()

    def _cFini(self):
        self._finalize()

    def _cWindowStatusChanged(self, _, newStatus):
        self.__windowStatus = newStatus
        _logger.debug('Status changed to %r for %r', newStatus, self)
        self.onStatusChanged(newStatus)

    def _cShowingStatusChanged(self, oldStatus, newStatus):
        oldStatus = ShowingStatus(oldStatus)
        newStatus = ShowingStatus(newStatus)
        self.__showingStatus = newStatus
        self._swapShowingStates(oldStatus, newStatus)
        self.onShowingStatusChanged(newStatus)

    def _cReady(self):
        self.__isReady = True
        self._onReady()

    def _cFocusChanged(self, focused):
        self.__isFocused = focused
        self._onFocus(focused)
        self.onFocusChanged(focused)

    def __attachToDecorator(self):
        decorator = self.decorator
        if decorator is not None:
            if decorator.viewStatus == ViewStatus.LOADED:
                self._onDecoratorReady()
            decorator.onStatusChanged += self.__onDecoratorStatusChanged
        return

    def __detachFromDecorator(self):
        decorator = self.decorator
        if decorator is not None:
            self._onDecoratorReleased()
            decorator.onStatusChanged -= self.__onDecoratorStatusChanged
        return

    def __attachToContent(self):
        content = self.content
        if content is not None:
            if content.viewStatus == ViewStatus.LOADED:
                self._onContentReady()
            content.onStatusChanged += self.__onContentStatusChanged
        return

    def __detachFromContent(self):
        content = self.content
        if content is not None:
            self._onContentReleased()
            content.onStatusChanged -= self.__onContentStatusChanged
        return

    def __onDecoratorStatusChanged(self, newStatus):
        if newStatus == ViewStatus.LOADED:
            self._onDecoratorReady()
        elif newStatus == ViewStatus.DESTROYED:
            self._onDecoratorReleased()

    def __onContentStatusChanged(self, newStatus):
        if newStatus == ViewStatus.LOADED:
            self._onContentReady()
        elif newStatus == ViewStatus.DESTROYED:
            self._onContentReleased()
