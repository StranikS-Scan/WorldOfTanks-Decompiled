# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleWinnerCongratsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleWinnerCongratsMeta(BaseDAAPIComponent):

    def onBecomeVisible(self):
        self._printOverrideError('onBecomeVisible')

    def as_setStpCoinsS(self, initial, factor=1, placeBonus=0):
        return self.flashObject.as_setStpCoins(initial, factor, placeBonus) if self._isDAAPIInited() else None
