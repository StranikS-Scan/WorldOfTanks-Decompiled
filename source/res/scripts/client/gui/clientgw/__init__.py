# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/__init__.py
from skeletons.gui.web import IWebController
__all__ = ('getWebServicesConfig',)

def getWebServicesConfig(manager):
    from gui.clientgw.web_controller import WebController
    ctrl = WebController()
    ctrl.init()
    manager.addInstance(IWebController, ctrl, finalizer='fini')
