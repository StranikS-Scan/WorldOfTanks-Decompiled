# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_style_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class NewYearStyleRewardViewModel(ViewModel):
    __slots__ = ('onStylePreview',)

    def __init__(self, properties=5, commands=1):
        super(NewYearStyleRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getIsStyle(self):
        return self._getBool(2)

    def setIsStyle(self, value):
        self._setBool(2, value)

    def getIsVehicleCustomizationEnabled(self):
        return self._getBool(3)

    def setIsVehicleCustomizationEnabled(self, value):
        self._setBool(3, value)

    def getVehicleState(self):
        return self._getString(4)

    def setVehicleState(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(NewYearStyleRewardViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('styleName', '')
        self._addBoolProperty('isStyle', False)
        self._addBoolProperty('isVehicleCustomizationEnabled', True)
        self._addStringProperty('vehicleState', '')
        self.onStylePreview = self._addCommand('onStylePreview')
