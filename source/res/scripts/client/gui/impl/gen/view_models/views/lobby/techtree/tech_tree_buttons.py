# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/tech_tree_buttons.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ButtonType(Enum):
    EARLYACCESS = 'earlyAccess'
    PARAGONS = 'paragons'


class State(Enum):
    ENABLED = 'enabled'
    DISABLED = 'disabled'


class TechTreeButtons(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TechTreeButtons, self).__init__(properties=properties, commands=commands)

    def getBranchID(self):
        return self._getNumber(0)

    def setBranchID(self, value):
        self._setNumber(0, value)

    def getButtonRow(self):
        return self._getNumber(1)

    def setButtonRow(self, value):
        self._setNumber(1, value)

    def getButtonType(self):
        return ButtonType(self._getString(2))

    def setButtonType(self, value):
        self._setString(2, value.value)

    def getButtonState(self):
        return State(self._getString(3))

    def setButtonState(self, value):
        self._setString(3, value.value)

    def getVehiclesCDs(self):
        return self._getArray(4)

    def setVehiclesCDs(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehiclesCDsType():
        return int

    def _initialize(self):
        super(TechTreeButtons, self)._initialize()
        self._addNumberProperty('branchID', 0)
        self._addNumberProperty('buttonRow', 0)
        self._addStringProperty('buttonType')
        self._addStringProperty('buttonState')
        self._addArrayProperty('vehiclesCDs', Array())
