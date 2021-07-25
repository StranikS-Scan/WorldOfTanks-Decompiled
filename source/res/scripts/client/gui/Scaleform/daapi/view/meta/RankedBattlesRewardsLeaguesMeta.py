# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RankedBattlesRewardsLeaguesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RankedBattlesRewardsLeaguesMeta(BaseDAAPIComponent):

    def onStyleClick(self, styleID):
        self._printOverrideError('onStyleClick')

    def as_setRewardsS(self, rewards):
        return self.flashObject.as_setRewards(rewards) if self._isDAAPIInited() else None
