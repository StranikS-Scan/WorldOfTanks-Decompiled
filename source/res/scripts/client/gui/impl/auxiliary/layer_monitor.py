# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/layer_monitor.py
import weakref
import logging
from frameworks.wulf import ViewStatus
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class LayerMonitor(object):
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self.__window = None
        return

    def init(self, cls):
        self.__gui.windowsManager.onWindowStatusChanged += self.__windowStatusChanged
        self.__window = weakref.proxy(cls)

    def fini(self):
        self.__gui.windowsManager.onWindowStatusChanged -= self.__windowStatusChanged
        self.__window = None
        return

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == ViewStatus.LOADED:
            window = self.__gui.windowsManager.getWindow(uniqueID)
            if window.layer == self.__window.layer and window.uniqueID != self.__window.uniqueID:
                self.__window.destroy()
                _logger.info('Window %r has been destroyed by opening window %r', self.__window, window)
