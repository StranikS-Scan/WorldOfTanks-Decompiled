# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/atmosphere_level_up_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class AtmosphereLevelUpModel(ViewModel):
    __slots__ = ('onClose', 'onGoToTanks')

    def __init__(self, properties=4, commands=2):
        super(AtmosphereLevelUpModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @property
    def hugeRewards(self):
        return self._getViewModel(1)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getIsViewReady(self):
        return self._getBool(3)

    def setIsViewReady(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AtmosphereLevelUpModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('hugeRewards', UserListModel())
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isViewReady', False)
        self.onClose = self._addCommand('onClose')
        self.onGoToTanks = self._addCommand('onGoToTanks')
