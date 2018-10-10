# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/resource_manager.py
from .py_object_binder import PyObjectEntity

class ResourceManager(PyObjectEntity):

    @classmethod
    def create(cls, proxy):
        manager = ResourceManager()
        manager.bind(proxy)
        return manager

    def destroy(self):
        self.unbind()

    def getTranslatedText(self, resourceID):
        return self.proxy.getTranslatedText(resourceID)
