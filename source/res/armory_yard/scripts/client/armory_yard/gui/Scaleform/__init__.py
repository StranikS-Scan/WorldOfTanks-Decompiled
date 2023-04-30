# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerScaleformLobbyPackages, registerLobbyTooltipsBuilders

def registerArmoryYardScaleform():
    registerScaleformLobbyPackages(('armory_yard.gui.Scaleform.daapi.view.lobby',))


def registerArmoryYardTooltipsBuilders():
    registerLobbyTooltipsBuilders([('armory_yard.gui.Scaleform.daapi.view.tooltips.lobby_builders', TOOLTIPS_CONSTANTS.ARMORY_YARD_LOBBY_SET)])
