# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view.py
import logging
import typing
import Event
from .view_event import ViewEvent
from .view_model import ViewModel
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectView
from ..gui_constants import ViewFlags, ViewStatus, ViewEventType
_logger = logging.getLogger(__name__)

class View(PyObjectEntity):
    __slots__ = ('__viewStatus', '__viewModel', '__args', '__kwargs', 'onStatusChanged')

    def __init__(self, layoutID, wsFlags, viewModelClazz, *args, **kwargs):
        self._swapStates(ViewStatus.UNDEFINED, ViewStatus.CREATED)
        self.__viewModel = viewModelClazz()
        super(View, self).__init__(PyObjectView(layoutID, self.__viewModel.proxy, wsFlags))
        self.onStatusChanged = Event.Event()
        self.__viewStatus = ViewStatus.UNDEFINED if self.proxy is None else self.proxy.viewStatus
        self.__args = args
        self.__kwargs = kwargs
        return

    def __repr__(self):
        return '{}(uniqueID={}, layoutID={})'.format(self.__class__.__name__, self.uniqueID, self.layoutID)

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
    def viewFlags(self):
        return self.proxy.viewFlags if self.proxy is not None else 0

    @property
    def viewStatus(self):
        return self.__viewStatus

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

    def createToolTip(self, event):
        return None

    def createPopOver(self, event):
        return None

    def createContextMenu(self, event):
        return None

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
        self.__viewStatus = newStatus
        self._swapStates(oldStatus, newStatus)
        self.onStatusChanged(newStatus)

    def _cOnViewEventReceived(self, cppObject):
        event = ViewEvent(cppObject)
        if not event.eventType:
            _logger.error('%r: type of event is not defined in view event', self)
            return False
        elif not event.contentID:
            _logger.error('%r: contentID is not defined in view event', self)
            return False
        elif not event.isOn:
            _logger.error('%r: view should be destroyed in the core side by %r', self, event)
            return False
        else:
            window = None
            if event.eventType == ViewEventType.TOOLTIP:
                window = self.createToolTip(event)
            elif event.eventType == ViewEventType.POP_OVER:
                window = self.createPopOver(event)
            elif event.eventType == ViewEventType.CONTEXT_MENU:
                window = self.createContextMenu(event)
            if window is not None:
                _logger.debug('%r: %r is loaded by %r', self, window, event)
                return True
            _logger.warning('%r: window is not loaded by event %r', self, event)
            return False
