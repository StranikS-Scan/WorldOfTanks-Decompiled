# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/windows_system/window.py
import typing
import Event
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectWindow
from ..view.view import View
from ..view.view_model import ViewModel
from ..gui_constants import WindowStatus, WindowFlags

class Window(PyObjectEntity):
    __slots__ = ('onStatusChanged', '__windowStatus', '__hasDecorator', '__weakref__')

    def __init__(self, wndFlags, *args, **kwargs):
        decorator = kwargs.pop('decorator', None)
        content = kwargs.pop('content', None)
        parent = kwargs.pop('parent', None)
        self.__hasDecorator = False
        if decorator is not None:
            decorator.getViewModel().setContent(content)
            contentProxy = decorator.proxy
            self.__hasDecorator = True
        elif content is not None:
            contentProxy = content.proxy
        else:
            contentProxy = None
        parentWndProxy = None if parent is None else parent.proxy
        super(Window, self).__init__(PyObjectWindow(wndFlags, contentProxy, parentWndProxy, args))
        self.onStatusChanged = Event.Event()
        self.__windowStatus = WindowStatus.UNDEFINED if self.proxy is None else self.proxy.windowStatus
        return

    def __repr__(self):
        return '{}(uniqueID={}, decorator={}, content={})'.format(self.__class__.__name__, self.uniqueID, self.decorator, self.content)

    @property
    def decorator(self):
        return self._getProxyContent() if self.__hasDecorator else None

    @property
    def content(self):
        if self.__hasDecorator:
            model = self._getDecoratorViewModel()
            if model is not None:
                return model.getContent()
        else:
            return self._getProxyContent()
        return

    @property
    def parent(self):
        return self.proxy.parent if self.proxy is not None else None

    @property
    def uniqueID(self):
        return self.proxy.uniqueID if self.proxy is not None else 0

    @property
    def descriptor(self):
        return self.proxy.wndDescriptor if self.proxy is not None else 0

    @property
    def windowFlags(self):
        return self.proxy.windowFlags if self.proxy is not None else WindowFlags.UNDEFINED

    @property
    def windowStatus(self):
        return self.__windowStatus

    @property
    def position(self):
        proxy = self.proxy
        return self.proxy.windowPosition if proxy is not None else (0.0, 0.0)

    @property
    def size(self):
        proxy = self.proxy
        return self.proxy.windowSize if proxy is not None else (0.0, 0.0)

    def checkWindowFlags(self, flags):
        return self.proxy.checkWindowFlags(flags)

    def isModal(self):
        return self.proxy.isModal()

    def setDecorator(self, decorator):
        self.__hasDecorator = True
        contentProxy = None if decorator is None else decorator.proxy
        self.proxy.setContent(contentProxy)
        return

    def load(self):
        self.proxy.load()

    def reload(self):
        self.proxy.reload()

    def destroy(self):
        if self.proxy is not None:
            self.proxy.destroy()
        self.onStatusChanged.clear()
        return

    def setLayer(self, layerID):
        self.proxy.setLayer(layerID)

    def resetLayer(self):
        self.proxy.resetLayer()

    def bringToFront(self):
        self.proxy.bringToFront()

    def sendToBack(self):
        self.proxy.sendToBack()

    def show(self):
        self.proxy.show()

    def hide(self):
        self.proxy.hide()

    def isHidden(self):
        return self.proxy.isHidden()

    def _initialize(self):
        pass

    def _getDecoratorViewModel(self):
        decorator = self.decorator
        return decorator.getViewModel() if decorator is not None else None

    def _getProxyContent(self):
        proxy = self.proxy
        return proxy.content if proxy is not None else None

    def _finalize(self):
        pass

    def _cInit(self):
        self._initialize()

    def _cFini(self):
        self._finalize()
        self._cWindowStatusChanged(self.windowStatus, WindowStatus.DESTROYED)
        self.unbind()

    def _cWindowStatusChanged(self, _, newStatus):
        self.__windowStatus = newStatus
        self.onStatusChanged(newStatus)
