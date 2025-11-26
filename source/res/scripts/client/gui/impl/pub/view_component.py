# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/view_component.py
import logging
import weakref
from future.utils import iteritems
from typing import TYPE_CHECKING
from Event import Event, EventManager
from frameworks.wulf import ViewModel, ViewSettings, ViewStatus
from frameworks.wulf.gui_constants import ChildFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.view_impl import TViewModel
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional, Type
    from _weakref import ReferenceType
_logger = logging.getLogger(__name__)

class ViewComponent(ViewImpl[TViewModel]):

    def __init__(self, layoutID=R.aliases.common.none(), model=ViewModel, enabled=True, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = model()
        settings.args = args
        settings.kwargs = kwargs
        super(ViewComponent, self).__init__(settings, settings.flags, *args, **kwargs)
        self.__enabled = enabled
        self._childrenByUid = {}
        self._childrenUidByPosition = {}
        self._childPositionByUid = {}
        self.__childrenInited = False
        self.__em = EventManager()
        self.onEnabledChanged = Event(self.__em)
        self._root = weakref.ref(self)

    def prepare(self):
        pass

    def isEnabled(self):
        return self.__enabled

    def setEnabled(self, value):
        if self.__enabled == value:
            return
        self.__enabled = value
        self.onEnabledChanged(self.uniqueID)

    def _getChildComponents(self):
        return {}

    def _initChildren(self):
        for posId, viewFactory in iteritems(self._getChildComponents()):
            try:
                self._registerChild(posId, viewFactory())
            except Exception:
                _logger.exception('%r initialization failed for %r', viewFactory, self)

    def _registerChild(self, posId, child):
        if posId in self._childrenUidByPosition:
            _logger.error('Registration failed. posId %d for %r is already set for %r', posId, child, self)
            return
        uid = child.uniqueID
        self._childrenByUid[uid] = child
        self._childrenUidByPosition[posId] = uid
        self._childPositionByUid[uid] = posId
        if self.__childrenInited:
            self._prepareChild(uid, child)

    def _onLoading(self, *args, **kwargs):
        super(ViewComponent, self)._onLoading(*args, **kwargs)
        self._initChildren()
        self.__childrenInited = True
        self._prepareChildren()

    def _prepareChildren(self):
        for uid, child in iteritems(self._childrenByUid):
            self._prepareChild(uid, child)

    def _setChild(self, posId, child):
        self._root().setChildView(posId, child, ChildFlags.EMPTY)

    def _getChild(self, posId):
        return self._root().getChildView(posId)

    def _prepareChild(self, uid, child):
        child._root = weakref.ref(self._root())
        child.prepare()
        child.onEnabledChanged += self.__onChildEnabledChanged
        if child.isEnabled():
            posId = self._childPositionByUid[uid]
            self._setChild(posId, child)

    def _finalize(self):
        self.__em.clear()
        self.__removeChildren()
        self._root = None
        super(ViewComponent, self)._finalize()
        return

    def _unregisterChild(self, uid, destroy):
        child = self._childrenByUid.get(uid, None)
        if child is None:
            _logger.error('Child with uid %r is not found for %r', uid, self)
            return
        else:
            child._root = None
            child.onEnabledChanged -= self.__onChildEnabledChanged
            posId = self._childPositionByUid[uid]
            del self._childrenByUid[uid]
            del self._childrenUidByPosition[posId]
            del self._childPositionByUid[uid]
            if self.getChildView(posId) is not None:
                self._setChild(posId, None)
            if destroy and child.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                child.destroy()
            return

    def __removeChildren(self):
        for uid in list(self._childrenByUid):
            self._unregisterChild(uid, True)

    def __onChildEnabledChanged(self, uid):
        child = self._childrenByUid[uid]
        posId = self._childPositionByUid[uid]
        if child.isEnabled():
            if self.getChildView(posId) is not None:
                _logger.error('Child %d is already enabled for %r', posId, self)
                return
            self._setChild(posId, child)
        else:
            if self.getChildView(posId) is None:
                _logger.error('Child %d is already disabled for %r', posId, self)
                return
            self._setChild(posId, None)
        return
