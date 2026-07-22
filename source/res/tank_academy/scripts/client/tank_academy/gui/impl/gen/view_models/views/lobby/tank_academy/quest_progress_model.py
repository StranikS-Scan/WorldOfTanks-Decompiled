# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/quest_progress_model.py
from frameworks.wulf import ViewModel

class QuestProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(QuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getCountCompleted(self):
        return self._getNumber(0)

    def setCountCompleted(self, value):
        self._setNumber(0, value)

    def getLastSeenProgress(self):
        return self._getNumber(1)

    def setLastSeenProgress(self, value):
        self._setNumber(1, value)

    def getTotalQuests(self):
        return self._getNumber(2)

    def setTotalQuests(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(QuestProgressModel, self)._initialize()
        self._addNumberProperty('countCompleted', 0)
        self._addNumberProperty('lastSeenProgress', 0)
        self._addNumberProperty('totalQuests', 0)
