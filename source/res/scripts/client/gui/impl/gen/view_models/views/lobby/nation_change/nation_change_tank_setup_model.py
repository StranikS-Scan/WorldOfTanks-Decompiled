# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_tank_setup_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.nation_change.nation_change_instruction_model import NationChangeInstructionModel

class NationChangeTankSetupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NationChangeTankSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def instructionSlot(self):
        return self._getViewModel(0)

    @staticmethod
    def getInstructionSlotType():
        return NationChangeInstructionModel

    def getEquipmentList(self):
        return self._getArray(1)

    def setEquipmentList(self, value):
        self._setArray(1, value)

    def getShellList(self):
        return self._getArray(2)

    def setShellList(self, value):
        self._setArray(2, value)

    def getSupplyList(self):
        return self._getArray(3)

    def setSupplyList(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(NationChangeTankSetupModel, self)._initialize()
        self._addViewModelProperty('instructionSlot', NationChangeInstructionModel())
        self._addArrayProperty('equipmentList', Array())
        self._addArrayProperty('shellList', Array())
        self._addArrayProperty('supplyList', Array())
