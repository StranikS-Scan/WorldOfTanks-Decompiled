# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/view_monitor.py
from typing import TYPE_CHECKING
import logging
import weakref
from frameworks.wulf import ViewStatus
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if TYPE_CHECKING:
    from typing import Optional, Set, Iterable
_logger = logging.getLogger(__name__)

class ViewMonitor(object):
    __slots__ = ('_view', '_ignoreViewLayoutIds')
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self._view = None
        self._ignoreViewLayoutIds = set()
        return

    def init(self, view, ignoreViewLayoutIds=None):
        self.__gui.windowsManager.onViewStatusChanged += self.__viewStatusChanged
        self._view = weakref.proxy(view)
        self._ignoreViewLayoutIds = set(ignoreViewLayoutIds or [])

    def fini(self):
        self.__gui.windowsManager.onViewStatusChanged -= self.__viewStatusChanged
        self._view = None
        return

    def __viewStatusChanged(self, viewUniqueID, viewNewStatus):
        if viewNewStatus == ViewStatus.LOADED:
            newView = self.__gui.windowsManager.getView(viewUniqueID)
            if not newView:
                return
            if newView.layoutID in self._ignoreViewLayoutIds:
                _logger.info('View %r remains alive, new view is being opened over it %r', self._view, newView)
                return
            try:
                newView.layer
            except AssertionError:
                return

            if newView.layer == self._view.layer and newView.uniqueID != self._view.uniqueID:
                self._view.destroy()
                _logger.info('View %r has been destroyed by opening new view %r', self._view, newView)
