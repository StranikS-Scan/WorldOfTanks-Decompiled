# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/windows_system/window.py
import typing
import Event
import GUI
from ..py_object_binder import PyObjectEntity
from ..view.view import View
from ..view.view_model import ViewModel
from ..gui_constants import WindowStatus

class Window(PyObjectEntity):
    __slots__ = ('onStatusChanged',)

    def __init__(self, wndFlags, decorator, content=None, parent=None):
        if decorator is not None:
            decorator.getViewModel().setContent(content)
            contentProxy = decorator.proxy
        elif content is not None:
            contentProxy = content.proxy
        else:
            contentProxy = None
        parentWndProxy = None if parent is None else parent.proxy
        super(Window, self).__init__(GUI.PyObjectWindow(wndFlags, contentProxy, parentWndProxy))
        self.onStatusChanged = Event.Event()
        return

    def __repr__(self):
        return '{}(uniqueID={}, content={})'.format(self.__class__.__name__, self.uniqueID, self.content)

    @property
    def content(self):
        return self.proxy.content.getViewModel().getContent() if self.proxy.content is not None else None

    @property
    def parent(self):
        return self.proxy.parent

    @property
    def uniqueID(self):
        return self.proxy.uniqueID

    @property
    def windowFlags(self):
        return self.proxy.windowFlags

    @property
    def windowStatus(self):
        return self.proxy.windowStatus

    def setContent(self, content):
        contentProxy = None if content is None else content.proxy
        self.proxy.setContent(contentProxy)
        return

    def load(self):
        self.proxy.load()

    def destroy(self):
        if self.proxy is not None:
            self.proxy.destroy()
        self.onStatusChanged.clear()
        return

    def setLayer(self, layerID):
        self.proxy.setLayer(layerID)

    def bringToFront(self):
        self.proxy.bringToFront()

    def sendToBack(self):
        self.proxy.sendToBack()

    def show(self):
        self.proxy.show()

    def hide(self):
        self.proxy.hide()

    def _initialize(self):
        pass

    def _getDecoratorViewModel(self):
        return self.proxy.content.viewModel

    def _finalize(self):
        pass

    def _cInit(self):
        self._initialize()

    def _cFini(self):
        self._finalize()
        self._cWindowStatusChanged(self.windowStatus, WindowStatus.DESTROYED)
        self.unbind()

    def _cWindowStatusChanged(self, _, newStatus):
        self.onStatusChanged(newStatus)
