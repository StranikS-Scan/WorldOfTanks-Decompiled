# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/fallout_battle_loading.py
from gui.Scaleform.daapi.view.battle.shared.battle_loading import BattleLoading
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class FalloutMultiTeamBattleLoading(BattleLoading):

    def getIsFalloutMode(self):
        return True

    def _setTipsInfo(self):
        arenaDP = self._battleCtx.getArenaDP()
        self.as_setEventInfoPanelDataS({'bgUrl': '',
         'items': []})
        self.as_setVisualTipInfoS(self.__makeVisualTipVO(arenaDP))
