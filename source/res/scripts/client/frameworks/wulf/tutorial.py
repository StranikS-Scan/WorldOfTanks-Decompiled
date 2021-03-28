# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/tutorial.py
import logging
import typing
from .py_object_binder import PyObjectEntity
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
_logger = logging.getLogger(__name__)

class Tutorial(PyObjectEntity):
    __slots__ = ()

    @classmethod
    def create(cls, proxy, model):
        manager = Tutorial()
        manager.bind(proxy)
        proxy.setModel(model.proxy)
        return manager

    def getModel(self):
        return self.proxy.getModel()

    def destroy(self):
        if self.proxy is not None:
            self.proxy.clear()
        self.unbind()
        return
