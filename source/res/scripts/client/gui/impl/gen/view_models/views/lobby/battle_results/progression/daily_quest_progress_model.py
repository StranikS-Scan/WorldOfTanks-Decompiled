# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/daily_quest_progress_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class DailyQuestTypes(Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    BONUS = 'bonus'
    PREMIUM = 'premium'
    EPIC = 'epic'


class DailyQuestProgressModel(DailyQuestModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(DailyQuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return DailyQuestTypes(self._getString(12))

    def setLevel(self, value):
        self._setString(12, value.value)

    def getNavigationEnabled(self):
        return self._getBool(13)

    def setNavigationEnabled(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(DailyQuestProgressModel, self)._initialize()
        self._addStringProperty('level')
        self._addBoolProperty('navigationEnabled', False)
