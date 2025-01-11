# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_item_part_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_item_part_progress_model import Pm3QuestItemPartProgressModel

class Pm3QuestItemPartModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(Pm3QuestItemPartModel, self).__init__(properties=properties, commands=commands)

    def getIdName(self):
        return self._getString(0)

    def setIdName(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getHeaderDescription(self):
        return self._getString(4)

    def setHeaderDescription(self, value):
        self._setString(4, value)

    def getType(self):
        return self._getString(5)

    def setType(self, value):
        self._setString(5, value)

    def getIsCycle(self):
        return self._getBool(6)

    def setIsCycle(self, value):
        self._setBool(6, value)

    def getIsCumulative(self):
        return self._getBool(7)

    def setIsCumulative(self, value):
        self._setBool(7, value)

    def getBiathlonGoal(self):
        return self._getNumber(8)

    def setBiathlonGoal(self, value):
        self._setNumber(8, value)

    def getProgression(self):
        return self._getArray(9)

    def setProgression(self, value):
        self._setArray(9, value)

    @staticmethod
    def getProgressionType():
        return Pm3QuestItemPartProgressModel

    def getQuestTooltipID(self):
        return self._getNumber(10)

    def setQuestTooltipID(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(Pm3QuestItemPartModel, self)._initialize()
        self._addStringProperty('idName', '')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('headerDescription', '')
        self._addStringProperty('type', '')
        self._addBoolProperty('isCycle', False)
        self._addBoolProperty('isCumulative', False)
        self._addNumberProperty('biathlonGoal', 0)
        self._addArrayProperty('progression', Array())
        self._addNumberProperty('questTooltipID', 0)
