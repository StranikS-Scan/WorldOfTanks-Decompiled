# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/__init__.py
from skeletons.gui.web import IWebController
__all__ = ('getWebServicesConfig',)

def getWebServicesConfig(manager):
    from gui.wgcg.web_controller import WebController
    ctrl = WebController()
    ctrl.init()
    manager.addInstance(IWebController, ctrl, finalizer='fini')
