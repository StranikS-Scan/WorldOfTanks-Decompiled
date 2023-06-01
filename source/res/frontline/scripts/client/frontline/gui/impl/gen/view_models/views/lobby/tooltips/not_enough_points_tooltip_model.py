# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/not_enough_points_tooltip_model.py
from frameworks.wulf import ViewModel

class NotEnoughPointsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NotEnoughPointsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NotEnoughPointsTooltipModel, self)._initialize()
        self._addNumberProperty('points', 0)
