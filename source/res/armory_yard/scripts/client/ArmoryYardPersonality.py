# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/ArmoryYardPersonality.py
from armory_yard.gui.Scaleform import registerArmoryYardScaleform, registerArmoryYardTooltipsBuilders
from armory_yard.gui.game_control import registerAYGameControllers, registerAYAwardControllers
from armory_yard.gui.shared.gui_items.items_actions import registerActions
from debug_utils import LOG_DEBUG

def preInit():
    registerArmoryYardScaleform()
    registerArmoryYardTooltipsBuilders()
    registerAYGameControllers()
    registerAYAwardControllers()
    registerActions()


def init():
    LOG_DEBUG('init', __name__)


def start():
    pass


def fini():
    pass
