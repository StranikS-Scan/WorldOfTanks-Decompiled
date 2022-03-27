# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/tooltips/rts_points_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.tooltips.rts_points_condition_model import RtsPointsConditionModel

class RtsPointsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RtsPointsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getConditions(self):
        return self._getArray(0)

    def setConditions(self, value):
        self._setArray(0, value)

    def getIsStrategist(self):
        return self._getBool(1)

    def setIsStrategist(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(RtsPointsTooltipViewModel, self)._initialize()
        self._addArrayProperty('conditions', Array())
        self._addBoolProperty('isStrategist', False)
