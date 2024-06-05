# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_task_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class TaskStateEnum(IntEnum):
    UNCOMPLETED = 0
    COMPLETED = 1
    LOCKED = 2


class MissionTaskTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MissionTaskTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getTaskState(self):
        return TaskStateEnum(self._getNumber(1))

    def setTaskState(self, value):
        self._setNumber(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getSecondsBeforeUnlock(self):
        return self._getNumber(3)

    def setSecondsBeforeUnlock(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MissionTaskTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addNumberProperty('taskState')
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('secondsBeforeUnlock', 0)
