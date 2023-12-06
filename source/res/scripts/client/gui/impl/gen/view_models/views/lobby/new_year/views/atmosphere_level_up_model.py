# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/atmosphere_level_up_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class AtmosphereLevelUpModel(ViewModel):
    __slots__ = ('onClose', 'onGotoStore')

    def __init__(self, properties=5, commands=2):
        super(AtmosphereLevelUpModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    @property
    def hugeRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getHugeRewardsType():
        return RewardItemModel

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getCollection(self):
        return self._getString(3)

    def setCollection(self, value):
        self._setString(3, value)

    def getIsViewReady(self):
        return self._getBool(4)

    def setIsViewReady(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(AtmosphereLevelUpModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('hugeRewards', UserListModel())
        self._addNumberProperty('level', 0)
        self._addStringProperty('collection', '')
        self._addBoolProperty('isViewReady', False)
        self.onClose = self._addCommand('onClose')
        self.onGotoStore = self._addCommand('onGotoStore')
