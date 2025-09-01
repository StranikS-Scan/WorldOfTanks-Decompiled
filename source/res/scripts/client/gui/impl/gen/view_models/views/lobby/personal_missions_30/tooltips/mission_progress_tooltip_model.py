# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/tooltips/mission_progress_tooltip_model.py
from frameworks.wulf import Array, ViewModel

class MissionProgressTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MissionProgressTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTotalMissionsAmount(self):
        return self._getNumber(0)

    def setTotalMissionsAmount(self, value):
        self._setNumber(0, value)

    def getCompletedMissionsAmount(self):
        return self._getNumber(1)

    def setCompletedMissionsAmount(self, value):
        self._setNumber(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return unicode

    def _initialize(self):
        super(MissionProgressTooltipModel, self)._initialize()
        self._addNumberProperty('totalMissionsAmount', 0)
        self._addNumberProperty('completedMissionsAmount', 0)
        self._addArrayProperty('vehicles', Array())
