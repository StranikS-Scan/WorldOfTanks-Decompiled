# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerLobbyTooltipsBuilders

def registerWinbackTooltipsBuilders():
    registerLobbyTooltipsBuilders([('winback.gui.Scaleform.daapi.view.tooltips.winback_builders', TOOLTIPS_CONSTANTS.WINBACK_SET)])
