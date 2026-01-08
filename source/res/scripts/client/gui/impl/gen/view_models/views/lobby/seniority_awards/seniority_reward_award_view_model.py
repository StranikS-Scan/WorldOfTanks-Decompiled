# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_reward_award_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class SeniorityRewardAwardViewModel(ViewModel):
    __slots__ = ('onOpenBtnClick',)

    def __init__(self, properties=5, commands=1):
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
        return BonusModel

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return VehicleModel

    def getSpecialCurrencyCount(self):
        return self._getNumber(3)

    def setSpecialCurrencyCount(self, value):
        self._setNumber(3, value)

    def getIsShopOnOpenLocked(self):
        return self._getBool(4)

    def setIsShopOnOpenLocked(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(SeniorityRewardAwardViewModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('vehicles', Array())
        self._addNumberProperty('specialCurrencyCount', -1)
        self._addBoolProperty('isShopOnOpenLocked', False)
        self.onOpenBtnClick = self._addCommand('onOpenBtnClick')
