# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/spent_points_tooltip_model.py
from frameworks.wulf import ViewModel

class SpentPointsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SpentPointsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getInstructorPoints(self):
        return self._getNumber(1)

    def setInstructorPoints(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(SpentPointsTooltipModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addNumberProperty('instructorPoints', 0)
