# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/reward_path_difficulty_mission_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class RewardPathDifficultyMissionViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RewardPathDifficultyMissionViewModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getMissionID(self):
        return self._getString(1)

    def setMissionID(self, value):
        self._setString(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def getIsCompleted(self):
        return self._getBool(3)

    def setIsCompleted(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(RewardPathDifficultyMissionViewModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('missionID', '')
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isCompleted', False)
