# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/game_control/__init__.py
from gui.shared.system_factory import registerGameControllers
from resource_well.gui.game_control.resource_well_controller import ResourceWellController
from skeletons.gui.resource_well import IResourceWellController

def registerResourceWellController():
    registerGameControllers([(IResourceWellController, ResourceWellController, True)])
