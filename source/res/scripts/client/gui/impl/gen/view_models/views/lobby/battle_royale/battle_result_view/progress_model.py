# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/progress_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ProgressModel, self).__init__(properties=properties, commands=commands)

    def getProgressStage(self):
        return self._getString(0)

    def setProgressStage(self, value):
        self._setString(0, value)

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getNextLevel(self):
        return self._getNumber(2)

    def setNextLevel(self, value):
        self._setNumber(2, value)

    def getEarnedPoints(self):
        return self._getNumber(3)

    def setEarnedPoints(self, value):
        self._setNumber(3, value)

    def getPointsIcon(self):
        return self._getResource(4)

    def setPointsIcon(self, value):
        self._setResource(4, value)

    def getProgressValue(self):
        return self._getNumber(5)

    def setProgressValue(self, value):
        self._setNumber(5, value)

    def getProgressDelta(self):
        return self._getNumber(6)

    def setProgressDelta(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ProgressModel, self)._initialize()
        self._addStringProperty('progressStage', '')
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('nextLevel', 0)
        self._addNumberProperty('earnedPoints', 0)
        self._addResourceProperty('pointsIcon', R.invalid())
        self._addNumberProperty('progressValue', 0)
        self._addNumberProperty('progressDelta', 0)
