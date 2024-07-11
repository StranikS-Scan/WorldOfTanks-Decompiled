# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/quests_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class QuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(QuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getMissions(self):
        return self._getArray(0)

    def setMissions(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMissionsType():
        return DailyQuestModel

    def getExpirationTime(self):
        return self._getNumber(1)

    def setExpirationTime(self, value):
        self._setNumber(1, value)

    def getIsLastSeasonDay(self):
        return self._getBool(2)

    def setIsLastSeasonDay(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(QuestsViewModel, self)._initialize()
        self._addArrayProperty('missions', Array())
        self._addNumberProperty('expirationTime', 0)
        self._addBoolProperty('isLastSeasonDay', False)
