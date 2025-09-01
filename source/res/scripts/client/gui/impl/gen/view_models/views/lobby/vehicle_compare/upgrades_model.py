# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/upgrades_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class UpgradesState(Enum):
    ZERO_UPGRADES = 'zeroUpgrades'
    PARTIAL_UPGRADES = 'partialUpgrades'
    FULL_UPGRADES = 'fullUpgrades'


class UpgradesModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(UpgradesModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return UpgradesState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(UpgradesModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isSelected', False)
