# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/reward_kit_auto_open_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_reward_row_model import LootBoxRewardRowModel

class RewardKitAutoOpenViewModel(ViewModel):
    __slots__ = ('onAccept',)

    def __init__(self, properties=4, commands=1):
        super(RewardKitAutoOpenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardRows(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardRowsType():
        return LootBoxRewardRowModel

    def getBoxesQuantity(self):
        return self._getNumber(1)

    def setBoxesQuantity(self, value):
        self._setNumber(1, value)

    def getCoinsQuantity(self):
        return self._getNumber(2)

    def setCoinsQuantity(self, value):
        self._setNumber(2, value)

    def getSacksQuantity(self):
        return self._getNumber(3)

    def setSacksQuantity(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RewardKitAutoOpenViewModel, self)._initialize()
        self._addViewModelProperty('rewardRows', UserListModel())
        self._addNumberProperty('boxesQuantity', 0)
        self._addNumberProperty('coinsQuantity', 0)
        self._addNumberProperty('sacksQuantity', 0)
        self.onAccept = self._addCommand('onAccept')
