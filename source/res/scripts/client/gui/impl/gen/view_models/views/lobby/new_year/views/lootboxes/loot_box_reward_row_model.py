# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/loot_box_reward_row_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class LootBoxRewardRowModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(LootBoxRewardRowModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getRewardsCount(self):
        return self._getNumber(2)

    def setRewardsCount(self, value):
        self._setNumber(2, value)

    def getBonusType(self):
        return self._getString(3)

    def setBonusType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(LootBoxRewardRowModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addResourceProperty('label', R.invalid())
        self._addNumberProperty('rewardsCount', 0)
        self._addStringProperty('bonusType', '')
