# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/reward_bonus_item_view_model.py
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class RewardBonusItemViewModel(BonusItemViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(RewardBonusItemViewModel, self).__init__(properties=properties, commands=commands)

    def getIsSecretReward(self):
        return self._getBool(9)

    def setIsSecretReward(self, value):
        self._setBool(9, value)

    def getSecretRewardTooltipMessage(self):
        return self._getString(10)

    def setSecretRewardTooltipMessage(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(RewardBonusItemViewModel, self)._initialize()
        self._addBoolProperty('isSecretReward', False)
        self._addStringProperty('secretRewardTooltipMessage', '')
