# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/battle/races_hud/races_minimap_component_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class RacesMinimapComponentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(RacesMinimapComponentModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    def getOwnVehiclePosX(self):
        return self._getReal(1)

    def setOwnVehiclePosX(self, value):
        self._setReal(1, value)

    def getOwnVehiclePosY(self):
        return self._getReal(2)

    def setOwnVehiclePosY(self, value):
        self._setReal(2, value)

    def getOwnVehicleAngle(self):
        return self._getReal(3)

    def setOwnVehicleAngle(self, value):
        self._setReal(3, value)

    def getArenaBottomLeftX(self):
        return self._getReal(4)

    def setArenaBottomLeftX(self, value):
        self._setReal(4, value)

    def getArenaBottomLeftY(self):
        return self._getReal(5)

    def setArenaBottomLeftY(self, value):
        self._setReal(5, value)

    def getArenaTopRightX(self):
        return self._getReal(6)

    def setArenaTopRightX(self, value):
        self._setReal(6, value)

    def getArenaTopRightY(self):
        return self._getReal(7)

    def setArenaTopRightY(self, value):
        self._setReal(7, value)

    def getMinimapName(self):
        return self._getString(8)

    def setMinimapName(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(RacesMinimapComponentModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())
        self._addRealProperty('ownVehiclePosX', 0.0)
        self._addRealProperty('ownVehiclePosY', 0.0)
        self._addRealProperty('ownVehicleAngle', 0.0)
        self._addRealProperty('arenaBottomLeftX', 0.0)
        self._addRealProperty('arenaBottomLeftY', 0.0)
        self._addRealProperty('arenaTopRightX', 0.0)
        self._addRealProperty('arenaTopRightY', 0.0)
        self._addStringProperty('minimapName', '')
