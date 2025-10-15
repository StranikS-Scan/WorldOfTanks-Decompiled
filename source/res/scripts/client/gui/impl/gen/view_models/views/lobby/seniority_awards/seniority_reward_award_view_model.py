# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_reward_award_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.main_reward_bonus_model import MainRewardBonusModel

class SeniorityRewardAwardViewModel(ViewModel):
    __slots__ = ('onOpenShop', 'onSelectVehicle')

    def __init__(self, properties=6, commands=2):
        super(SeniorityRewardAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return MainRewardBonusModel

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return VehicleModel

    def getMainRewards(self):
        return self._getArray(3)

    def setMainRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMainRewardsType():
        return MainRewardBonusModel

    def getSpecialCurrencyCount(self):
        return self._getNumber(4)

    def setSpecialCurrencyCount(self, value):
        self._setNumber(4, value)

    def getIsShopOnOpenLocked(self):
        return self._getBool(5)

    def setIsShopOnOpenLocked(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(SeniorityRewardAwardViewModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('mainRewards', Array())
        self._addNumberProperty('specialCurrencyCount', -1)
        self._addBoolProperty('isShopOnOpenLocked', False)
        self.onOpenShop = self._addCommand('onOpenShop')
        self.onSelectVehicle = self._addCommand('onSelectVehicle')
