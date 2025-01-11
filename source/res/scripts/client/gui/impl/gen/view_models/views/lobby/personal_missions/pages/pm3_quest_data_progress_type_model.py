# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quest_data_progress_type_model.py
from frameworks.wulf import ViewModel

class Pm3QuestDataProgressTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(Pm3QuestDataProgressTypeModel, self).__init__(properties=properties, commands=commands)

    def getFrom(self):
        return self._getNumber(0)

    def setFrom(self, value):
        self._setNumber(0, value)

    def getTo(self):
        return self._getNumber(1)

    def setTo(self, value):
        self._setNumber(1, value)

    def getDelta(self):
        return self._getNumber(2)

    def setDelta(self, value):
        self._setNumber(2, value)

    def getNewFrom(self):
        return self._getNumber(3)

    def setNewFrom(self, value):
        self._setNumber(3, value)

    def getAnimationIndex(self):
        return self._getNumber(4)

    def setAnimationIndex(self, value):
        self._setNumber(4, value)

    def getProgressIcon(self):
        return self._getString(5)

    def setProgressIcon(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(Pm3QuestDataProgressTypeModel, self)._initialize()
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
        self._addNumberProperty('delta', 0)
        self._addNumberProperty('newFrom', 0)
        self._addNumberProperty('animationIndex', 0)
        self._addStringProperty('progressIcon', '')
