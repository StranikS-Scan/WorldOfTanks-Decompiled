# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_tank_slot_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_instruction_model import NationChangeInstructionModel

class NationChangeTankSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NationChangeTankSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def instructionSlot(self):
        return self._getViewModel(0)

    def getTankImage(self):
        return self._getResource(1)

    def setTankImage(self, value):
        self._setResource(1, value)

    def getVehicleIntCD(self):
        return self._getNumber(2)

    def setVehicleIntCD(self, value):
        self._setNumber(2, value)

    def getTankNation(self):
        return self._getString(3)

    def setTankNation(self, value):
        self._setString(3, value)

    def getNoEquipment(self):
        return self._getBool(4)

    def setNoEquipment(self, value):
        self._setBool(4, value)

    def getNoCrew(self):
        return self._getBool(5)

    def setNoCrew(self, value):
        self._setBool(5, value)

    def getCrewList(self):
        return self._getArray(6)

    def setCrewList(self, value):
        self._setArray(6, value)

    def getEquipmentList(self):
        return self._getArray(7)

    def setEquipmentList(self, value):
        self._setArray(7, value)

    def getShellList(self):
        return self._getArray(8)

    def setShellList(self, value):
        self._setArray(8, value)

    def getSupplyList(self):
        return self._getArray(9)

    def setSupplyList(self, value):
        self._setArray(9, value)

    def _initialize(self):
        super(NationChangeTankSlotModel, self)._initialize()
        self._addViewModelProperty('instructionSlot', NationChangeInstructionModel())
        self._addResourceProperty('tankImage', R.invalid())
        self._addNumberProperty('vehicleIntCD', 0)
        self._addStringProperty('tankNation', '')
        self._addBoolProperty('noEquipment', True)
        self._addBoolProperty('noCrew', True)
        self._addArrayProperty('crewList', Array())
        self._addArrayProperty('equipmentList', Array())
        self._addArrayProperty('shellList', Array())
        self._addArrayProperty('supplyList', Array())
