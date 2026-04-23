# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/skeletons/__init__.py
from gui.shared.system_factory import registerGameControllers
from open_bundle.gui.game_control.open_bundle_controller import OpenBundleController
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController

def registerOpenBundleController():
    registerGameControllers([(IOpenBundleController, OpenBundleController, False)])
