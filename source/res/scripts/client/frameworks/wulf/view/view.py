# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view.py
import logging
import typing
import Event
from soft_exception import SoftException
from sound_gui_manager import ViewSoundExtension
from .view_event import ViewEvent
from .view_model import ViewModel
from ..py_object_binder import PyObjectEntity, getProxy, getObject
from ..py_object_wrappers import PyObjectView, PyObjectViewSettings
from ..gui_constants import ViewFlags, ViewStatus, ViewEventType, ChildFlags, ShowingStatus
TViewModel = typing.TypeVar('TViewModel', bound=ViewModel)
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from .. import Window
    from sound_gui_manager import CommonSoundSpaceSettings
    from gui.sounds.ViewSoundManager import _ViewSoundsManager

class ViewSettings(typing.Generic[TViewModel]):
    __slots__ = ('__proxy', 'args', 'kwargs')

    def __init__(self, layoutID, flags=ViewFlags.VIEW, model=None, args=(), kwargs=None):
        super(ViewSettings, self).__init__()
        self.__proxy = PyObjectViewSettings(layoutID)
        self.__proxy.flags = flags
        self.args = args
        self.kwargs = kwargs or {}
        if model is not None:
            self.__proxy.model = getProxy(model)
        return

    @property
    def proxy(self):
        return self.__proxy

    @property
    def layoutID(self):
        return self.__proxy.layoutID

    @layoutID.setter
    def layoutID(self, layoutID):
        self.__proxy.layoutID = layoutID

    @property
    def flags(self):
        return self.__proxy.flags

    @flags.setter
    def flags(self, flags):
        self.__proxy.flags = flags

    @property
    def model(self):
        return getObject(self.__proxy.model)

    @model.setter
    def model(self, model):
        if model is not None and not isinstance(model, ViewModel):
            raise SoftException('model should be ViewModel class or extends it')
        self.__proxy.model = getProxy(model)
        return

    def clear(self):
        self.__proxy = None
        return


class View(PyObjectEntity, typing.Generic[TViewModel]):
    __slots__ = ('__viewStatus', '__showingStatus', '__viewModel', '__args', '__kwargs', 'onStatusChanged', '__isReady', 'onShowingStatusChanged', 'onFocusChanged', '__soundExtension', '__isShown', '__isFocused', '__weakref__', '__initialParentWindow')
    _COMMON_SOUND_SPACE = None

    def __init__(self, settings, wsFlags=ViewFlags.VIEW, viewModelClazz=ViewModel, *args, **kwargs):
        if not isinstance(settings, ViewSettings):
            _logger.warning('%r: Creation of view using statement View(layoutID, wsFlags, viewModelClazz, *args, **kwargs) is deprecated and will be removed in next iteration. Please, use View(ViewSettings(...))', self.__class__.__name__)
            settings = ViewSettings[TViewModel](settings)
            settings.flags = wsFlags
            settings.model = viewModelClazz()
            settings.args = args
            settings.kwargs = kwargs
        self._swapStates(ViewStatus.UNDEFINED, ViewStatus.CREATED)
        self.__viewModel = settings.model
        self.__soundExtension = ViewSoundExtension(self._COMMON_SOUND_SPACE)
        self.__soundExtension.initSoundManager()
        super(View, self).__init__(PyObjectView(settings.proxy))
        self.onStatusChanged = Event.Event()
        self.__viewStatus = ViewStatus.UNDEFINED if self.proxy is None else self.proxy.viewStatus
        self.__showingStatus = ShowingStatus.HIDDEN
        self.__isShown = False
        self.__isReady = False
        self.onShowingStatusChanged = Event.Event()
        self.__isFocused = False
        self.onFocusChanged = Event.Event()
        self.__args = settings.args
        self.__kwargs = settings.kwargs
        self.__initialParentWindow = None
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
    def layer(self):
        if self.getWindow() is not None:
            _logger.warning('Use window.layer() instead of view.layer(). Window %r. View %r', self.getWindow(), self)
        return ViewFlags.getViewType(self.proxy.viewFlags) if self.proxy is not None else 0

    @property
    def viewFlags(self):
        return self.proxy.viewFlags if self.proxy is not None else 0

    @property
    def viewStatus(self):
        return self.__viewStatus

    @property
    def showingStatus(self):
        return self.__showingStatus

    @property
    def isFocused(self):
        return self.__isFocused

    @property
    def soundManager(self):
        return self.__soundExtension.soundManager

    def checkViewFlags(self, flags):
        return self.proxy.checkViewFlags(flags) if self.proxy is not None else False

    def getViewModel(self):
        return self.__viewModel

    def setInitialParentWindow(self, window):
        self.__initialParentWindow = window

    def getInitialParentWindow(self):
        return self.__initialParentWindow

    def getParentWindow(self):
        return self.proxy.getParentWindow() if self.proxy is not None else None

    def getWindow(self):
        return self.proxy.getWindow() if self.proxy is not None else None

    def getParentView(self):
        return self.proxy.getParent() if self.proxy is not None else None

    def addChild(self, childId, view, loadImmediately=True):
        if self.proxy is not None:
            self.proxy.addChild(childId, getProxy(view), loadImmediately)
        return

    def getChild(self, childId):
        return self.proxy.getChild(childId) if self.proxy is not None else None

    def removeChild(self, childId, destroy=True):
        return self.proxy.removeChild(childId, destroy) if self.proxy is not None else None

    def getChildView(self, resourceID):
        return self.proxy.getSubView(resourceID) if self.proxy is not None else None

    def setChildView(self, resourceID, view=None, chFlags=ChildFlags.AUTO_DESTROY):
        if self.proxy is not None:
            if not self.proxy.setSubView(resourceID, getProxy(view), chFlags):
                _logger.error('%r: child %r can not be added. May be child is already added to other view or window', self, view)
        else:
            _logger.error('%r: Parent view does not have proxy, child can not be added', self)
        return

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

    def destroyWindow(self):
        window = self.getParentWindow()
        if window is not None:
            window.destroy()
        else:
            self.destroy()
        return

    def show(self):
        _logger.error('show() is not defined for View. Try window.show()')

    def hide(self):
        _logger.error('hide() is not defined for View. Try window.hide()')

    def createToolTip(self, event):
        return None

    def createPopOver(self, event):
        return None

    def createContextMenu(self, event):
        return None

    def _onLoading(self, *args, **kwargs):
        pass

    def _onLoaded(self, *args, **kwargs):
        pass

    def _initialize(self, *args, **kwargs):
        pass

    def _finalize(self):
        pass

    def _onReady(self):
        pass

    def _onShown(self):
        pass

    def _onHidden(self):
        pass

    def _onFocus(self, focused):
        pass

    def _swapStates(self, oldStatus, newStatus):
        if newStatus == ViewStatus.LOADING:
            self._onLoading(*self.__args, **self.__kwargs)
        elif newStatus == ViewStatus.LOADED:
            self.__soundExtension.startSoundSpace()
            self._onLoaded(*self.__args, **self.__kwargs)

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
        self._initialize(*self.__args, **self.__kwargs)

    def _cFini(self):
        self._finalize()
        self.__soundExtension.destroySoundManager()

    def _cViewStatusChanged(self, oldStatus, newStatus):
        self.__viewStatus = newStatus
        self._swapStates(oldStatus, newStatus)
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
