# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/daily_quests_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class DailyQuestsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DailyQuestsModel, self).__init__(properties=properties, commands=commands)

    def getEventCoinCount(self):
        return self._getNumber(0)

    def setEventCoinCount(self, value):
        self._setNumber(0, value)

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return QuestModel

    def _initialize(self):
        super(DailyQuestsModel, self)._initialize()
        self._addNumberProperty('eventCoinCount', 0)
        self._addArrayProperty('quests', Array())
