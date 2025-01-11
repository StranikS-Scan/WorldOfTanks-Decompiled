# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/tank_card_model.py
from enum import Enum
from frameworks.wulf import Array
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.enums import VehicleRole
from frameworks.wulf import ViewModel
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.ability_model import AbilityModel

class VehicleStates(Enum):
    DEFAULT = 'default'
    INBATTLE = 'inBattle'
    INPLATOON = 'inPlatoon'


class TankCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TankCardModel, self).__init__(properties=properties, commands=commands)

    def getResourceKey(self):
        return self._getString(0)

    def setResourceKey(self, value):
        self._setString(0, value)

    def getBonusPoints(self):
        return self._getNumber(1)

    def setBonusPoints(self, value):
        self._setNumber(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def getVehicleState(self):
        return VehicleStates(self._getString(3))

    def setVehicleState(self, value):
        self._setString(3, value.value)

    def getRole(self):
        return VehicleRole(self._getString(4))

    def setRole(self, value):
        self._setString(4, value.value)

    def getAbilities(self):
        return self._getArray(5)

    def setAbilities(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def _initialize(self):
        super(TankCardModel, self)._initialize()
        self._addStringProperty('resourceKey', '')
        self._addNumberProperty('bonusPoints', 0)
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('vehicleState', VehicleStates.DEFAULT.value)
        self._addStringProperty('role', VehicleRole.CARRIER.value)
        self._addArrayProperty('abilities', Array())
