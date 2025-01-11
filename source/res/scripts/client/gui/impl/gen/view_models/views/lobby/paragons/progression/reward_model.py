# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/progression/reward_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RewardModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getIsReceived(self):
        return self._getBool(7)

    def setIsReceived(self, value):
        self._setBool(7, value)

    def getIsClaimed(self):
        return self._getBool(8)

    def setIsClaimed(self, value):
        self._setBool(8, value)

    def getIsSelectableVehicle(self):
        return self._getBool(9)

    def setIsSelectableVehicle(self, value):
        self._setBool(9, value)

    def getIsSelectableVehicleClaimed(self):
        return self._getBool(10)

    def setIsSelectableVehicleClaimed(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addBoolProperty('isReceived', False)
        self._addBoolProperty('isClaimed', False)
        self._addBoolProperty('isSelectableVehicle', False)
        self._addBoolProperty('isSelectableVehicleClaimed', False)
