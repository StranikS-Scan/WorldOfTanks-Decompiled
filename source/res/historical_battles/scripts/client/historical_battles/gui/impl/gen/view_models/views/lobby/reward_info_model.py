# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/reward_info_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.ability_model import AbilityModel

class RewardInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def ability(self):
        return self._getViewModel(0)

    @staticmethod
    def getAbilityType():
        return AbilityModel

    def getIsAchieved(self):
        return self._getBool(1)

    def setIsAchieved(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(RewardInfoModel, self)._initialize()
        self._addViewModelProperty('ability', AbilityModel())
        self._addBoolProperty('isAchieved', False)
