# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_end_warning_panel.py
from gui.Scaleform.daapi.view.battle.classic.battle_end_warning_panel import BattleEndWarningPanel
from helpers.time_utils import ONE_MINUTE

class EventBattleEndWarningPanel(BattleEndWarningPanel):

    def _totalTimeFormat(self, _):
        minutes, seconds = divmod(int(self._appearTime), ONE_MINUTE)
        return (str(minutes), str(seconds))
