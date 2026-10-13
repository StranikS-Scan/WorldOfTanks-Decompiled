# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/progression/mission_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class MissionModel(DailyQuestModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(MissionModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(12)

    def setBonuses(self, value):
        self._setArray(12, value)

    @staticmethod
    def getBonusesType():
        return TokenBonusModel

    def _initialize(self):
        super(MissionModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
