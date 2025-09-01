# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/quest_model.py
from frameworks.wulf import ViewModel

class QuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(QuestModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getQuestCondition(self):
        return self._getString(1)

    def setQuestCondition(self, value):
        self._setString(1, value)

    def getSummary(self):
        return self._getString(2)

    def setSummary(self, value):
        self._setString(2, value)

    def getQuestType(self):
        return self._getString(3)

    def setQuestType(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(QuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('questCondition', '')
        self._addStringProperty('summary', '')
        self._addStringProperty('questType', '')
