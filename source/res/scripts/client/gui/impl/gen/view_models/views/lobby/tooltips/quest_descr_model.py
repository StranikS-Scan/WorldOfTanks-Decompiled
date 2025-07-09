# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/quest_descr_model.py
from frameworks.wulf import ViewModel

class QuestDescrModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(QuestDescrModel, self).__init__(properties=properties, commands=commands)

    def getQuestName(self):
        return self._getString(0)

    def setQuestName(self, value):
        self._setString(0, value)

    def getConditions(self):
        return self._getString(1)

    def setConditions(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(QuestDescrModel, self)._initialize()
        self._addStringProperty('questName', '')
        self._addStringProperty('conditions', '')
