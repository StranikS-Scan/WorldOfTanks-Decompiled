# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/defence/page.py
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from historical_battles.gui.Scaleform.daapi.view.battle.page import HistoricalBattlePage
_DEFENCE_CONFIG = {BATTLE_CTRL_ID.BATTLE_FIELD_CTRL: (BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_SPG_PANEL,)}
_DEFENCE_VIEWS_CONFIG = ()

class HistoricalBattlesDefencePage(HistoricalBattlePage):

    def __init__(self, components=None):
        override = self._getOverridedComponentsConfig(_DEFENCE_CONFIG, _DEFENCE_VIEWS_CONFIG)
        super(HistoricalBattlesDefencePage, self).__init__(components=override if not components else components)
