# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerLobbyTooltipsBuilders, registerScaleformLobbyPackages

def registerBirthdayScaleform():
    registerScaleformLobbyPackages(('mt_birthday.gui.Scaleform.daapi.view.lobby',))


def registerGiftSystemTooltipsBuilders():
    registerLobbyTooltipsBuilders([('mt_birthday.gui.Scaleform.daapi.view.tooltips.lobby_builders', TOOLTIPS_CONSTANTS.BIRTHDAY_SET)])
