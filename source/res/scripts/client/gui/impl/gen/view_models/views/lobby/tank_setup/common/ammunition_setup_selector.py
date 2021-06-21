# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ammunition_setup_selector.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SetupStates(IntEnum):
    NORMAL = 0
    WARNING = 1


class AmmunitionSetupSelector(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(AmmunitionSetupSelector, self).__init__(properties=properties, commands=commands)

    def getIsSwitchEnabled(self):
        return self._getBool(0)

    def setIsSwitchEnabled(self, value):
        self._setBool(0, value)

    def getStates(self):
        return self._getArray(1)

    def setStates(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(AmmunitionSetupSelector, self)._initialize()
        self._addBoolProperty('isSwitchEnabled', False)
        self._addArrayProperty('states', Array())
