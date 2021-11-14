# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/__init__.py
import typing
from gui.platform.wgnp.steam_account.controller import WGNPSteamAccRequestController
from gui.platform.wgnp.demo_account.controller import WGNPDemoAccRequestController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController, IWGNPDemoAccRequestController
if typing.TYPE_CHECKING:
    from helpers.dependency import DependencyManager
__all__ = ('getWGNPRequestControllers',)

def getWGNPRequestControllers(manager):
    wgnpSteamAccController = WGNPSteamAccRequestController()
    wgnpSteamAccController.init()
    manager.addInstance(IWGNPSteamAccRequestController, wgnpSteamAccController, finalizer='fini')
    wgnpDemoAccController = WGNPDemoAccRequestController()
    wgnpDemoAccController.init()
    manager.addInstance(IWGNPDemoAccRequestController, wgnpDemoAccController, finalizer='fini')
