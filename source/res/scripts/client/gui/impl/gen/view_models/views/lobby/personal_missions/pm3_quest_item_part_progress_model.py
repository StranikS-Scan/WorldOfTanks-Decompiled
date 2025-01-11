# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_item_part_progress_model.py
from frameworks.wulf import ViewModel

class Pm3QuestItemPartProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(Pm3QuestItemPartProgressModel, self).__init__(properties=properties, commands=commands)

    def getTo(self):
        return self._getNumber(0)

    def setTo(self, value):
        self._setNumber(0, value)

    def getCurrentValue(self):
        return self._getNumber(1)

    def setCurrentValue(self, value):
        self._setNumber(1, value)

    def getPreviousValue(self):
        return self._getNumber(2)

    def setPreviousValue(self, value):
        self._setNumber(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getIsFailed(self):
        return self._getBool(4)

    def setIsFailed(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(Pm3QuestItemPartProgressModel, self)._initialize()
        self._addNumberProperty('to', 0)
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('previousValue', 0)
        self._addStringProperty('icon', '')
        self._addBoolProperty('isFailed', False)
