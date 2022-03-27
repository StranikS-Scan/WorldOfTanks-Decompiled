# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/rts_quest_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class GameMode(Enum):
    TANKER = 'tanker'
    STRATEGIST = 'strategist'


class RtsQuestModel(DailyQuestModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(RtsQuestModel, self).__init__(properties=properties, commands=commands)

    @property
    def condition(self):
        return self._getViewModel(14)

    def getGameMode(self):
        return GameMode(self._getString(15))

    def setGameMode(self, value):
        self._setString(15, value.value)

    def getStartDate(self):
        return self._getNumber(16)

    def setStartDate(self, value):
        self._setNumber(16, value)

    def getFinishDate(self):
        return self._getNumber(17)

    def setFinishDate(self, value):
        self._setNumber(17, value)

    def _initialize(self):
        super(RtsQuestModel, self)._initialize()
        self._addViewModelProperty('condition', PreformattedConditionModel())
        self._addStringProperty('gameMode')
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('finishDate', 0)
