# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/main_view_reward_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class RewardsType(Enum):
    MAIN = 'main'
    OPERATION = 'operation'
    CAMPAIGN = 'campaign'


class MainViewRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MainViewRewardModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(0)

    def setItems(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemsType():
        return IconBonusModel

    def getRewardsType(self):
        return RewardsType(self._getString(1))

    def setRewardsType(self, value):
        self._setString(1, value.value)

    def getCompletedTasks(self):
        return self._getNumber(2)

    def setCompletedTasks(self, value):
        self._setNumber(2, value)

    def getTasksNumber(self):
        return self._getNumber(3)

    def setTasksNumber(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MainViewRewardModel, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addStringProperty('rewardsType')
        self._addNumberProperty('completedTasks', 0)
        self._addNumberProperty('tasksNumber', 0)
