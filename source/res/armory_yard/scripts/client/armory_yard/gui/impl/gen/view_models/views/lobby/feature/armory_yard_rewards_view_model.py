# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_vehicle_model import ArmoryYardRewardsVehicleModel

class ArmoryYardRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowVehicle')
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_REWARDS = 10

    def __init__(self, properties=6, commands=2):
        super(ArmoryYardRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getStages(self):
        return self._getNumber(1)

    def setStages(self, value):
        self._setNumber(1, value)

    def getHasAllRewards(self):
        return self._getBool(2)

    def setHasAllRewards(self, value):
        self._setBool(2, value)

    def getVehicles(self):
        return self._getArray(3)

    def setVehicles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getVehiclesType():
        return ArmoryYardRewardsVehicleModel

    def getMainRewards(self):
        return self._getArray(4)

    def setMainRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMainRewardsType():
        return ItemBonusModel

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(ArmoryYardRewardsViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('stages', 0)
        self._addBoolProperty('hasAllRewards', False)
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onShowVehicle = self._addCommand('onShowVehicle')
