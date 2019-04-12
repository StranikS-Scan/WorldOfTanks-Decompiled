# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesRewardsRanksMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RankedBattlesRewardsRanksMeta(BaseDAAPIComponent):

    def onDivisionIdxChanged(self, index):
        self._printOverrideError('onDivisionIdxChanged')

    def onRequestData(self, iconSizeID, rewardsCount):
        self._printOverrideError('onRequestData')

    def as_setDivisionsDataS(self, divisions, immediately):
        return self.flashObject.as_setDivisionsData(divisions, immediately) if self._isDAAPIInited() else None

    def as_setRewardsS(self, rewards):
        return self.flashObject.as_setRewards(rewards) if self._isDAAPIInited() else None
