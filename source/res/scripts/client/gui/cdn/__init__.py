# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/cdn/__init__.py
from controller import PurchaseCache
from skeletons.gui.cdn import IPurchaseCache
__all__ = ('getPurchaseCache',)

def getPurchaseCache(manager):
    controller = PurchaseCache()
    controller.init()
    manager.addInstance(IPurchaseCache, controller, finalizer='fini')
