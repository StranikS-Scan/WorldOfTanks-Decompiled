# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/abilities_tooltip_model.py
from frameworks.wulf import ViewModel

class AbilitiesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AbilitiesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getDuration(self):
        return self._getNumber(1)

    def setDuration(self, value):
        self._setNumber(1, value)

    def getReload(self):
        return self._getNumber(2)

    def setReload(self, value):
        self._setNumber(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getLearned(self):
        return self._getBool(4)

    def setLearned(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(AbilitiesTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('duration', 0)
        self._addNumberProperty('reload', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('learned', False)
