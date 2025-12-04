# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_stage_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_top_reward_model import NyTopRewardModel

class StageState(Enum):
    ACTIVE = 'active'
    FINISHED = 'finished'
    NOTSTARTED = 'notStarted'


class NyStageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyStageModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getState(self):
        return StageState(self._getString(3))

    def setState(self, value):
        self._setString(3, value.value)

    def getPosition(self):
        return self._getNumber(4)

    def setPosition(self, value):
        self._setNumber(4, value)

    def getIsRecalc(self):
        return self._getBool(5)

    def setIsRecalc(self, value):
        self._setBool(5, value)

    def getTops(self):
        return self._getArray(6)

    def setTops(self, value):
        self._setArray(6, value)

    @staticmethod
    def getTopsType():
        return NyTopRewardModel

    def _initialize(self):
        super(NyStageModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addStringProperty('state')
        self._addNumberProperty('position', 0)
        self._addBoolProperty('isRecalc', False)
        self._addArrayProperty('tops', Array())
