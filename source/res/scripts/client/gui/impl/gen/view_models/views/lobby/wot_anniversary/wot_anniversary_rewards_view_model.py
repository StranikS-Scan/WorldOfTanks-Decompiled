# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/wot_anniversary_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.reward_item_model import RewardItemModel

class WotAnniversaryRewardsViewModel(ViewModel):
    __slots__ = ('onClosed',)

    def __init__(self, properties=2, commands=1):
        super(WotAnniversaryRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getMainRewards(self):
        return self._getArray(0)

    def setMainRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(WotAnniversaryRewardsViewModel, self)._initialize()
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClosed = self._addCommand('onClosed')
