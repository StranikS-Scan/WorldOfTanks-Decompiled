# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/progression_widget_model.py
from frameworks.wulf import ViewModel

class ProgressionWidgetModel(ViewModel):
    __slots__ = ('onOpenProgression',)

    def __init__(self, properties=3, commands=1):
        super(ProgressionWidgetModel, self).__init__(properties=properties, commands=commands)

    def getProgressionLevel(self):
        return self._getNumber(0)

    def setProgressionLevel(self, value):
        self._setNumber(0, value)

    def getCurrentPoints(self):
        return self._getNumber(1)

    def setCurrentPoints(self, value):
        self._setNumber(1, value)

    def getIsProgressionFinished(self):
        return self._getBool(2)

    def setIsProgressionFinished(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ProgressionWidgetModel, self)._initialize()
        self._addNumberProperty('progressionLevel', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addBoolProperty('isProgressionFinished', False)
        self.onOpenProgression = self._addCommand('onOpenProgression')
