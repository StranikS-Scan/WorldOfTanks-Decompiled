# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/progression_widget_model.py
from frameworks.wulf import ViewModel

class ProgressionWidgetModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(ProgressionWidgetModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getProgressionCurrent(self):
        return self._getNumber(2)

    def setProgressionCurrent(self, value):
        self._setNumber(2, value)

    def getProgressionTotal(self):
        return self._getNumber(3)

    def setProgressionTotal(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ProgressionWidgetModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addNumberProperty('level', 0)
        self._addNumberProperty('progressionCurrent', 0)
        self._addNumberProperty('progressionTotal', 0)
        self.onClick = self._addCommand('onClick')
