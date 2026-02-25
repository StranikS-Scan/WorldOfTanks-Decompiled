# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/rovers_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import AbilityModel

class RoverEnum(IntEnum):
    OLD = 1
    NEW = 2


class RoversModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RoversModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicle(self):
        return RoverEnum(self._getNumber(1))

    def setVehicle(self, value):
        self._setNumber(1, value.value)

    def getAbilities(self):
        return self._getArray(2)

    def setAbilities(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def getIsVehicleInBattle(self):
        return self._getBool(3)

    def setIsVehicleInBattle(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(RoversModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('vehicle')
        self._addArrayProperty('abilities', Array())
        self._addBoolProperty('isVehicleInBattle', False)
