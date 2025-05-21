# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/difficulty_tooltip_view_model.py
from frameworks.wulf import Array
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.difficulty_wave_rewards_model import DifficultyWaveRewardsModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.difficulty_item_model import DifficultyItemModel

class DifficultyTooltipViewModel(DifficultyItemModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(DifficultyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsHangar(self):
        return self._getBool(6)

    def setIsHangar(self, value):
        self._setBool(6, value)

    def getMaxCompletedMissions(self):
        return self._getNumber(7)

    def setMaxCompletedMissions(self, value):
        self._setNumber(7, value)

    def getRewardsByWave(self):
        return self._getArray(8)

    def setRewardsByWave(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsByWaveType():
        return DifficultyWaveRewardsModel

    def _initialize(self):
        super(DifficultyTooltipViewModel, self)._initialize()
        self._addBoolProperty('isHangar', False)
        self._addNumberProperty('maxCompletedMissions', 0)
        self._addArrayProperty('rewardsByWave', Array())
