# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_tank_slot_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_tank_setup_model import NationChangeTankSetupModel

class NationChangeTankSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NationChangeTankSlotModel, self).__init__(properties=properties, commands=commands)

    def getTankImage(self):
        return self._getResource(0)

    def setTankImage(self, value):
        self._setResource(0, value)

    def getVehicleIntCD(self):
        return self._getNumber(1)

    def setVehicleIntCD(self, value):
        self._setNumber(1, value)

    def getTankNation(self):
        return self._getString(2)

    def setTankNation(self, value):
        self._setString(2, value)

    def getNoEquipment(self):
        return self._getBool(3)

    def setNoEquipment(self, value):
        self._setBool(3, value)

    def getNoCrew(self):
        return self._getBool(4)

    def setNoCrew(self, value):
        self._setBool(4, value)

    def getCrewList(self):
        return self._getArray(5)

    def setCrewList(self, value):
        self._setArray(5, value)

    def getSetups(self):
        return self._getArray(6)

    def setSetups(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(NationChangeTankSlotModel, self)._initialize()
        self._addResourceProperty('tankImage', R.invalid())
        self._addNumberProperty('vehicleIntCD', 0)
        self._addStringProperty('tankNation', '')
        self._addBoolProperty('noEquipment', True)
        self._addBoolProperty('noCrew', True)
        self._addArrayProperty('crewList', Array())
        self._addArrayProperty('setups', Array())
