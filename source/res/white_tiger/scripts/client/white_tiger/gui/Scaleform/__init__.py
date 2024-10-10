# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/__init__.py
from gui.shared.system_factory import registerLobbyTooltipsBuilders
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as _TOOLTIPS

def registerWhiteTigerBattlePackages():
    pass


def registerWhiteTigerTooltipsBuilders():
    registerLobbyTooltipsBuilders([('white_tiger.gui.Scaleform.daapi.view.tooltips.wt_lobby_builders', _TOOLTIPS.EVENT_BATTLES_SET)])
