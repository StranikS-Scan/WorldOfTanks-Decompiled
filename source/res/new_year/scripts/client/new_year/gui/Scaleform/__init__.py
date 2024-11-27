# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerScaleformLobbyPackages, registerLobbyTooltipsBuilders

def registerNewYearScaleform():
    registerScaleformLobbyPackages(('new_year.gui.Scaleform.daapi.view.lobby',))
    registerLobbyTooltipsBuilders([('new_year.gui.Scaleform.daapi.view.tooltips.lobby_builders', TOOLTIPS_CONSTANTS.NEW_YEAR_LOBBY_SET)])
