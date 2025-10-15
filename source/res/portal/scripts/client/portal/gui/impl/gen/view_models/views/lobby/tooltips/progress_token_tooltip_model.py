# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/progress_token_tooltip_model.py
from frameworks.wulf import ViewModel

class ProgressTokenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ProgressTokenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsTokenTooltip(self):
        return self._getBool(0)

    def setIsTokenTooltip(self, value):
        self._setBool(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getInProgress(self):
        return self._getBool(2)

    def setInProgress(self, value):
        self._setBool(2, value)

    def getCurrentPoints(self):
        return self._getNumber(3)

    def setCurrentPoints(self, value):
        self._setNumber(3, value)

    def getNextLevelPoints(self):
        return self._getNumber(4)

    def setNextLevelPoints(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(ProgressTokenTooltipModel, self)._initialize()
        self._addBoolProperty('isTokenTooltip', False)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('inProgress', False)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('nextLevelPoints', 0)
