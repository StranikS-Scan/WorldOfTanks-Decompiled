# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.portal_reward_item_model import PortalRewardItemModel

class PortalRewardType(Enum):
    PROGRESSION = 'progression'
    LAST_LEVEL_VICTORY = 'lastLevelVictory'
    ALL_VEHICLES_UPGRADED = 'allVehiclesUpgraded'


class PortalRewardsViewModel(ViewModel):
    __slots__ = ('onApprove',)

    def __init__(self, properties=4, commands=1):
        super(PortalRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getRewardType(self):
        return PortalRewardType(self._getString(0))

    def setRewardType(self, value):
        self._setString(0, value.value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getIsSpecial(self):
        return self._getBool(2)

    def setIsSpecial(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return PortalRewardItemModel

    def _initialize(self):
        super(PortalRewardsViewModel, self)._initialize()
        self._addStringProperty('rewardType')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isSpecial', False)
        self._addArrayProperty('rewards', Array())
        self.onApprove = self._addCommand('onApprove')
