# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/__init__.py
from armory_yard.gui.game_control.armory_yard_controller import ArmoryYardController
from armory_yard.gui.game_control.awards_controller import ArmoryYardStyleQuestsHandler
from skeletons.gui.game_control import IArmoryYardController
from gui.shared.system_factory import registerGameControllers, registerAwardControllerHandler

def registerAYGameControllers():
    registerGameControllers([(IArmoryYardController, ArmoryYardController, False)])


def registerAYAwardControllers():
    registerAwardControllerHandler(ArmoryYardStyleQuestsHandler)
