# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/task_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.reward_model import RewardModel

class TaskStateEnum(IntEnum):
    UNCOMPLETED = 0
    COMPLETED = 1
    LOCKED = 2


class TaskModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(TaskModel, self).__init__(properties=properties, commands=commands)

    def getTaskId(self):
        return self._getNumber(0)

    def setTaskId(self, value):
        self._setNumber(0, value)

    def getTaskState(self):
        return TaskStateEnum(self._getNumber(1))

    def setTaskState(self, value):
        self._setNumber(1, value.value)

    def getIsCompletedFirstTime(self):
        return self._getBool(2)

    def setIsCompletedFirstTime(self, value):
        self._setBool(2, value)

    def getSecondsBeforeUnlock(self):
        return self._getNumber(3)

    def setSecondsBeforeUnlock(self, value):
        self._setNumber(3, value)

    def getIsUnlockedFirstTime(self):
        return self._getBool(4)

    def setIsUnlockedFirstTime(self, value):
        self._setBool(4, value)

    def getAnimationCounter(self):
        return self._getNumber(5)

    def setAnimationCounter(self, value):
        self._setNumber(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(TaskModel, self)._initialize()
        self._addNumberProperty('taskId', 0)
        self._addNumberProperty('taskState')
        self._addBoolProperty('isCompletedFirstTime', False)
        self._addNumberProperty('secondsBeforeUnlock', 0)
        self._addBoolProperty('isUnlockedFirstTime', False)
        self._addNumberProperty('animationCounter', 0)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('description', '')
