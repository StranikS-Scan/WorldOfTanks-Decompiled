# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_main_widget_tooltip_model.py
from frameworks.wulf import ViewModel

class NyMainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NyMainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getString(0)

    def setCurrentLevel(self, value):
        self._setString(0, value)

    def getNextLevel(self):
        return self._getString(1)

    def setNextLevel(self, value):
        self._setString(1, value)

    def getCurrentPoints(self):
        return self._getNumber(2)

    def setCurrentPoints(self, value):
        self._setNumber(2, value)

    def getNextPoints(self):
        return self._getNumber(3)

    def setNextPoints(self, value):
        self._setNumber(3, value)

    def getDeltaFromPoints(self):
        return self._getNumber(4)

    def setDeltaFromPoints(self, value):
        self._setNumber(4, value)

    def getSecondsLeft(self):
        return self._getNumber(5)

    def setSecondsLeft(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NyMainWidgetTooltipModel, self)._initialize()
        self._addStringProperty('currentLevel', 'I')
        self._addStringProperty('nextLevel', 'II')
        self._addNumberProperty('currentPoints', 1)
        self._addNumberProperty('nextPoints', 1)
        self._addNumberProperty('deltaFromPoints', 0)
        self._addNumberProperty('secondsLeft', 0)
