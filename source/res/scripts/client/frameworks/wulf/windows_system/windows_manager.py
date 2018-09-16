# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/windows_system/windows_manager.py
import logging
from ..py_object_binder import PyObjectEntity
_logger = logging.getLogger(__name__)

class WindowsManager(PyObjectEntity):

    @classmethod
    def create(cls, proxy):
        vm = WindowsManager()
        vm.bind(proxy)
        return vm

    def destroy(self):
        self.unbind()

    def getView(self, uniqueID):
        return self.proxy.getPyView(uniqueID)

    def getViewByLayoutID(self, layoutID):
        return self.proxy.getPyViewByLayoutID(layoutID)

    def getWindow(self, uniqueID):
        return self.proxy.getPyWindow(uniqueID)

    def loadView(self, layoutID, viewClass, *args, **kwargs):
        pyView = self.getView(layoutID)
        if pyView is None:
            pyView = viewClass(layoutID, *args, **kwargs)
            pyView.load()
        else:
            _logger.warning('View is already loading/loaded: %r.', layoutID)
        return pyView
