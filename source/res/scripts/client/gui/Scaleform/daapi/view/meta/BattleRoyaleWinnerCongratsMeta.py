# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleWinnerCongratsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleWinnerCongratsMeta(BaseDAAPIComponent):

    def playWinSound(self):
        self._printOverrideError('playWinSound')

    def as_setStpCoinsS(self, initial, factor=1, bonus=1):
        return self.flashObject.as_setStpCoins(initial, factor, bonus) if self._isDAAPIInited() else None
