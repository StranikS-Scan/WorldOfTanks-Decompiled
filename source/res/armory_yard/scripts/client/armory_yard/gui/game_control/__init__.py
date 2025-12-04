# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/__init__.py
from armory_yard.gui.game_control.armory_yard_controller import ArmoryYardController
from armory_yard.gui.game_control.armory_yard_reroll_controller import ArmoryYardRerollController
from armory_yard.gui.game_control.armory_yard_shop_controller import ArmoryYardShopController
from skeletons.gui.game_control import IArmoryYardController, IArmoryYardShopController
from gui.shared.system_factory import registerGameControllers
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController

def registerAYGameControllers():
    registerGameControllers([(IArmoryYardController, ArmoryYardController, False)])


def registerAYShopControllers():
    registerGameControllers([(IArmoryYardShopController, ArmoryYardShopController, False)])


def registerAYRerollControllers():
    registerGameControllers([(IArmoryYardRerollController, ArmoryYardRerollController, False)])
