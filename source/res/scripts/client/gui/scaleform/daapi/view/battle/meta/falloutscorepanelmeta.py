# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/meta/FalloutScorePanelMeta.py
from gui.Scaleform.daapi.view.battle.meta.BattleComponentMeta import BattleComponentMeta

class FalloutScorePanelMeta(BattleComponentMeta):

    def as_setDataS(self, maxValue, allyValue, enemyValue, playerScore):
        self._flashObject.as_setData(maxValue, allyValue, enemyValue, playerScore)
