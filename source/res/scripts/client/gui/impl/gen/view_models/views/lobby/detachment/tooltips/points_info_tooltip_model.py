# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/points_info_tooltip_model.py
from frameworks.wulf import ViewModel

class PointsInfoTooltipModel(ViewModel):
    __slots__ = ()
    MOBILIZATION = 'mobilization'
    DEFAULT = 'default'

    def __init__(self, properties=6, commands=0):
        super(PointsInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getIsClickable(self):
        return self._getBool(1)

    def setIsClickable(self, value):
        self._setBool(1, value)

    def getPoints(self):
        return self._getNumber(2)

    def setPoints(self, value):
        self._setNumber(2, value)

    def getPointsPerLevel(self):
        return self._getNumber(3)

    def setPointsPerLevel(self, value):
        self._setNumber(3, value)

    def getMaximumPoints(self):
        return self._getNumber(4)

    def setMaximumPoints(self, value):
        self._setNumber(4, value)

    def getBonusPoints(self):
        return self._getNumber(5)

    def setBonusPoints(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PointsInfoTooltipModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addBoolProperty('isClickable', False)
        self._addNumberProperty('points', 0)
        self._addNumberProperty('pointsPerLevel', 0)
        self._addNumberProperty('maximumPoints', 0)
        self._addNumberProperty('bonusPoints', 0)
