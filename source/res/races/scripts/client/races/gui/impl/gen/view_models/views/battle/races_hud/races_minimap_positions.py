# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/battle/races_hud/races_minimap_positions.py
from frameworks.wulf import ViewModel

class RacesMinimapPositions(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RacesMinimapPositions, self).__init__(properties=properties, commands=commands)

    def getPosX(self):
        return self._getReal(0)

    def setPosX(self, value):
        self._setReal(0, value)

    def getPosY(self):
        return self._getReal(1)

    def setPosY(self, value):
        self._setReal(1, value)

    def getAngle(self):
        return self._getReal(2)

    def setAngle(self, value):
        self._setReal(2, value)

    def getVehicleID(self):
        return self._getNumber(3)

    def setVehicleID(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RacesMinimapPositions, self)._initialize()
        self._addRealProperty('posX', 0.0)
        self._addRealProperty('posY', 0.0)
        self._addRealProperty('angle', 0.0)
        self._addNumberProperty('vehicleID', 0)
