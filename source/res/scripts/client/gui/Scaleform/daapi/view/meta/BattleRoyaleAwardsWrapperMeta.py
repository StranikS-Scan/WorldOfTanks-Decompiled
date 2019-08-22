# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleAwardsWrapperMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleAwardsWrapperMeta(BaseDAAPIComponent):

    def onRequestData(self, iconSizeID, rewardsCount):
        self._printOverrideError('onRequestData')

    def as_setRewardsS(self, rewards):
        return self.flashObject.as_setRewards(rewards) if self._isDAAPIInited() else None
