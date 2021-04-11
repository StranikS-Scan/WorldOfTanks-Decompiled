# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/__init__.py
from gui.platform.wgnp.controller import WGNPRequestController
from skeletons.gui.platform.wgnp_controller import IWGNPRequestController
__all__ = ('getWGNPRequestController',)

def getWGNPRequestController(manager):
    controller = WGNPRequestController()
    controller.init()
    manager.addInstance(IWGNPRequestController, controller, finalizer='fini')
