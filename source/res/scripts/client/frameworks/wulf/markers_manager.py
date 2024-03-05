# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/markers_manager.py
import logging
import typing
from .py_object_binder import PyObjectEntity
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    import Math
_logger = logging.getLogger(__name__)

class MarkersManager(PyObjectEntity):
    __slots__ = ()

    @classmethod
    def create(cls, proxy):
        manager = MarkersManager()
        manager.bind(proxy)
        return manager

    def addMarkerStatic(self, viewModel, worldPos):
        self.proxy.addMarkerStatic(viewModel, worldPos)

    def addMarkerDynamic(self, viewModel, dataProvider):
        self.proxy.addMarkerDynamic(viewModel, dataProvider)

    def removeMarker(self, viewModel):
        self.proxy.removeMarker(viewModel)

    def clear(self):
        self.proxy.clear()

    def destroy(self):
        if self.proxy is not None:
            self.proxy.clear()
        self.unbind()
        return
