# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/view_component.py
from __future__ import absolute_import
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
    from typing import Any, Callable, Dict, Optional, Type, Tuple, Union, Set
    from _weakref import ReferenceType
_logger = logging.getLogger(__name__)

class ViewComponent(ViewImpl[TViewModel]):

    def __init__(self, layoutID=R.aliases.common.none(), model=ViewModel, enabled=True, sharedLayoutId=0, *args, **kwargs):
        settings = ViewSettings(layoutID, model=model(), args=args, kwargs=kwargs)
        settings.sharedLayoutID = sharedLayoutId
        super(ViewComponent, self).__init__(settings, *args, **kwargs)
        self.__enabled = enabled
        self._childrenByUid = {}
        self._childrenUidByPosition = {}
        self._childPositionByUid = {}
        self.__childrenInited = False
        self.__em = EventManager()
        self.onEnabledChanged = Event(self.__em)
        self._root = weakref.ref(self)
        self.__dependents = set()
        self.__dependencies = set()

    @property
    def dependents(self):
        return self.__dependents

    @property
    def dependencies(self):
        return self.__dependencies

    def prepare(self):
        pass

    def isEnabled(self):
        return self.__enabled

    def getChildByPosId(self, posId):
        uid = self._childrenUidByPosition.get(posId)
        return None if uid is None else self._childrenByUid.get(uid)

    def setEnabled(self, value):
        if self.__enabled == value:
            return
        self.__enabled = value
        self.onEnabledChanged(self.uniqueID)

    def _onLoading(self, *args, **kwargs):
        super(ViewComponent, self)._onLoading(*args, **kwargs)
        self._initChildren()
        self.__childrenInited = True
        self._prepareChildren()

    def _getChildComponents(self):
        return {}

    def _initChildren(self):
        cfg = self._getChildComponents()
        if isinstance(cfg, tuple):
            cfg = dict.fromkeys(cfg)
        for posId, viewFactory in iteritems(cfg):
            self._constructChild(posId, viewFactory)

    def _constructChild(self, posId, viewFactory=None):
        try:
            child = self.__constructChildFromFactory(posId) if viewFactory is None else viewFactory()
        except Exception:
            _logger.exception('%r (pos %d) construction failed for %r', viewFactory, posId, self)
            raise

        if child is None:
            _logger.error('Child construction failed. posId=%d, parent=%r', posId, self)
            return
        else:
            try:
                self._registerChild(posId, child)
            except Exception:
                _logger.error('%r (pos %d) registration failed for %r', child or viewFactory, posId, self)
                if child:
                    child.destroy()
                raise

            return

    def _registerChild(self, posId, child):
        uid = child.uniqueID
        if uid in child.dependents:
            _logger.error('Self dependency %d for %d (%r)', uid, posId, child)
            return
        elif posId in self._childrenUidByPosition:
            _logger.error('Registration failed. posId %d for %r is already set for %r', posId, child, self)
            return
        else:
            childComponentsCfg = child._getChildComponents()
            if isinstance(childComponentsCfg, tuple):
                for dependencyPosId in childComponentsCfg:
                    if dependencyPosId in self._childrenUidByPosition:
                        self.getChildByPosId(dependencyPosId).dependents.add(uid)
                    else:
                        self._constructChild(dependencyPosId, None)
                    child.dependencies.add(self._childrenUidByPosition[dependencyPosId])

            child.dependents.add(self.uniqueID)
            self._childrenByUid[uid] = child
            self._childrenUidByPosition[posId] = uid
            self._childPositionByUid[uid] = posId
            if self.__childrenInited:
                self._prepareChild(uid, child)
            return

    def _prepareChildren(self):
        for uid, child in iteritems(self._childrenByUid):
            self._prepareChild(uid, child)

    def _getRoot(self):
        return self._root() if self._root is not None else None

    def _setChild(self, posId, child):
        root = self._getRoot()
        if root is None:
            return
        else:
            root.setChildView(posId, child, ChildFlags.EMPTY)
            return

    def _getChild(self, posId):
        root = self._getRoot()
        return None if root is None else root.getChildView(posId)

    def _prepareChild(self, uid, child):
        child._root = weakref.ref(self._root())
        child.prepare()
        child.onEnabledChanged += self.__onChildEnabledChanged
        if child.isEnabled():
            posId = self._childPositionByUid[uid]
            self._setChild(posId, child)

    def _finalize(self):
        self.__em.clear()
        self._removeChildren()
        self._root = None
        super(ViewComponent, self)._finalize()
        return

    def _unregisterChild(self, uid, destroy):
        child = self._childrenByUid.get(uid, None)
        if child is None:
            _logger.error('Child with uid %d is not found for %r', uid, self)
            return
        elif self.uniqueID not in child.dependents:
            _logger.error('Cannot unregister %d. Wrong userId %d, %r', uid, self.uniqueID, self)
            return
        else:
            if uid in self.__dependencies:
                self.__dependencies.remove(uid)
            child.dependents.remove(self.uniqueID)
            if child.dependents:
                return
            child._root = None
            child.onEnabledChanged -= self.__onChildEnabledChanged
            posId = self._childPositionByUid[uid]
            del self._childrenByUid[uid]
            del self._childrenUidByPosition[posId]
            del self._childPositionByUid[uid]
            if self._getChild(posId) is not None:
                self._setChild(posId, None)
            if destroy and child.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                child.destroy()
            return

    def _removeChildren(self):
        for uid in list(self._childrenByUid):
            self._unregisterChild(uid, True)

    def __constructChildFromFactory(self, resId, *args, **kwargs):
        settings = self.gui.entitiesFactory.getSettings(resId)
        if settings is None:
            _logger.error('View Settings by resId=%s is not found.', resId)
            return
        elif not issubclass(settings.clazz, ViewComponent):
            _logger.error('View Settings by resId=%s has wrong clazz=%r.', resId, settings.clazz)
            return
        else:
            return settings.clazz(*args, **kwargs)

    def __onChildEnabledChanged(self, uid):
        child = self._childrenByUid[uid]
        posId = self._childPositionByUid[uid]
        if child.isEnabled():
            if self._getChild(posId) is not None:
                _logger.error('Child %d is already enabled for %r', posId, self)
                return
            self._setChild(posId, child)
        else:
            if self._getChild(posId) is None:
                _logger.error('Child %d is already disabled for %r', posId, self)
                return
            self._setChild(posId, None)
        return
