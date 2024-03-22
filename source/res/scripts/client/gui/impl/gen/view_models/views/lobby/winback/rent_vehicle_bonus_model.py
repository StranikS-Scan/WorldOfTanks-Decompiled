# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/rent_vehicle_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.winback.vehicle_bonus_model import VehicleBonusModel

class RentType(Enum):
    TIME = 'time'
    WINS = 'wins'
    BATTLES = 'battles'


class RentVehicleBonusModel(VehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(RentVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getRentType(self):
        return RentType(self._getString(18))

    def setRentType(self, value):
        self._setString(18, value.value)

    def getRentDuration(self):
        return self._getNumber(19)

    def setRentDuration(self, value):
        self._setNumber(19, value)

    def _initialize(self):
        super(RentVehicleBonusModel, self)._initialize()
        self._addStringProperty('rentType')
        self._addNumberProperty('rentDuration', 0)
