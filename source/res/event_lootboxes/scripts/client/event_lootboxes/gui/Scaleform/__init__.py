# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/Scaleform/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.system_factory import registerLobbyTooltipsBuilders

def registerLootboxesTooltipsBuilders():
    registerLobbyTooltipsBuilders([('event_lootboxes.gui.Scaleform.daapi.view.tooltips.lobby_builders', TOOLTIPS_CONSTANTS.EVLB_LOBBY_SET)])
