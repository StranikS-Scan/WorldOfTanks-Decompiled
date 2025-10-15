# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/main_reward_bonus_model.py
from gui.impl.gen.view_models.views.lobby.seniority_awards.reward_vehicle_bonus_model import RewardVehicleBonusModel

class MainRewardBonusModel(RewardVehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
        super(MainRewardBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsCompensation(self):
        return self._getBool(23)

    def setIsCompensation(self, value):
        self._setBool(23, value)

    def getCompensatedBonus(self):
        return self._getString(24)

    def setCompensatedBonus(self, value):
        self._setString(24, value)

    def _initialize(self):
        super(MainRewardBonusModel, self)._initialize()
        self._addBoolProperty('isCompensation', False)
        self._addStringProperty('compensatedBonus', '')
