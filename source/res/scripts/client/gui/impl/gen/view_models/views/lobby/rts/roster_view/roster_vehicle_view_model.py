# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/roster_view/roster_vehicle_view_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.vehicle_base_model import VehicleBaseModel

class MannerEnum(IntEnum):
    SCOUT = 1
    DEFENSIVE = 2
    HOLD = 3


class RosterVehicleViewModel(VehicleBaseModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(RosterVehicleViewModel, self).__init__(properties=properties, commands=commands)

    def getIsUnsuitable(self):
        return self._getBool(8)

    def setIsUnsuitable(self, value):
        self._setBool(8, value)

    def getManner(self):
        return MannerEnum(self._getNumber(9))

    def setManner(self, value):
        self._setNumber(9, value.value)

    def _initialize(self):
        super(RosterVehicleViewModel, self)._initialize()
        self._addBoolProperty('isUnsuitable', False)
        self._addNumberProperty('manner')
