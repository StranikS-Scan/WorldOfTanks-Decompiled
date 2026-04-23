# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/impl/gen/view_models/views/lobby/feature/museum_vehicle_characteristics.py
from enum import Enum
from frameworks.wulf import ViewModel

class Characteristic(Enum):
    CREW = 'crew'
    MASS = 'mass'
    ARMOR = 'armor'
    CALIBER = 'caliber'
    SPEED = 'speed'
    WEAPON = 'weapon'
    COMBATCREW = 'combatCrew'
    POWER = 'power'


class MuseumVehicleCharacteristics(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MuseumVehicleCharacteristics, self).__init__(properties=properties, commands=commands)

    def getKey(self):
        return Characteristic(self._getString(0))

    def setKey(self, value):
        self._setString(0, value.value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MuseumVehicleCharacteristics, self)._initialize()
        self._addStringProperty('key')
        self._addStringProperty('value', '')
