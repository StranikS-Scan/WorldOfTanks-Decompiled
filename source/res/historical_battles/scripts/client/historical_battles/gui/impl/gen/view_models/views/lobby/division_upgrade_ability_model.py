# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/division_upgrade_ability_model.py
from frameworks.wulf import ViewModel

class DivisionUpgradeAbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DivisionUpgradeAbilityModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getLabel(self):
        return self._getString(1)

    def setLabel(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getCooldown(self):
        return self._getNumber(3)

    def setCooldown(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(DivisionUpgradeAbilityModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('label', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('cooldown', 0)
