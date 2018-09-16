# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view.py
import typing
import Event
import GUI
from .view_model import ViewModel
from ..py_object_binder import PyObjectEntity
from ..gui_constants import ViewFlags, ViewStatus

class View(PyObjectEntity):
    __slots__ = ('_proxy', '__viewModel', '__args', '__kwargs', 'onStatusChanged')

    def __init__(self, layoutID, wsFlags, viewModelClazz, *args, **kwargs):
        self._swapStates(ViewStatus.UNDEFINED, ViewStatus.CREATED)
        self.__viewModel = viewModelClazz()
        super(View, self).__init__(GUI.PyObjectView(layoutID, self.__viewModel.proxy, wsFlags))
        self.onStatusChanged = Event.Event()
        self.__args = args
        self.__kwargs = kwargs

    @property
    def layoutID(self):
        return self.proxy.layoutID if self.proxy is not None else 0

    @property
    def uniqueID(self):
        return self.proxy.uniqueID if self.proxy is not None else 0

    @property
    def viewType(self):
        return ViewFlags.getViewType(self.proxy.viewFlags) if self.proxy is not None else ''

    @property
    def viewStatus(self):
        return self.proxy.viewStatus if self.proxy is not None else ViewStatus.UNDEFINED

    def checkViewFlags(self, flags):
        return self.proxy.checkViewFlags(flags) if self.proxy is not None else False

    def getViewModel(self):
        return self.__viewModel

    def getParentWindow(self):
        return self.proxy.getParentWindow() if self.proxy is not None else None

    def getParentView(self):
        return self.proxy.getParent() if self.proxy is not None else None

    def load(self):
        self.proxy.load()

    def destroy(self):
        if self.proxy is not None:
            self.proxy.destroy()
        self.onStatusChanged.clear()
        if self.__viewModel is not None:
            self.__viewModel.unbind()
            self.__viewModel = None
        return

    def show(self):
        self.proxy.show()

    def hide(self):
        self.proxy.hide()

    def _initialize(self, *args, **kwargs):
        pass

    def _finalize(self):
        pass

    def _swapStates(self, oldStatus, newStatus):
        pass

    def _cInit(self):
        self._initialize(*self.__args, **self.__kwargs)

    def _cFini(self):
        self._finalize()
        self._cViewStatusChanged(self.viewStatus, ViewStatus.DESTROYED)
        self.unbind()

    def _cViewStatusChanged(self, oldStatus, newStatus):
        self._swapStates(oldStatus, newStatus)
        self.onStatusChanged(newStatus)
