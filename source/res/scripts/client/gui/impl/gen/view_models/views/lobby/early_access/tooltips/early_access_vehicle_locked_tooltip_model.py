# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/tooltips/early_access_vehicle_locked_tooltip_model.py
from frameworks.wulf import ViewModel

class EarlyAccessVehicleLockedTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EarlyAccessVehicleLockedTooltipModel, self).__init__(properties=properties, commands=commands)

    def getWillAvailableTimestamp(self):
        return self._getNumber(0)

    def setWillAvailableTimestamp(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(EarlyAccessVehicleLockedTooltipModel, self)._initialize()
        self._addNumberProperty('willAvailableTimestamp', 0)
