# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/division_upgrade_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.division_upgrade_ability_model import DivisionUpgradeAbilityModel

class DivisionUpgradeRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onConfirm')

    def __init__(self, properties=6, commands=2):
        super(DivisionUpgradeRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getSubDivisionIndex(self):
        return self._getNumber(1)

    def setSubDivisionIndex(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getHasNewVehicles(self):
        return self._getBool(4)

    def setHasNewVehicles(self, value):
        self._setBool(4, value)

    def getAbilities(self):
        return self._getArray(5)

    def setAbilities(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAbilitiesType():
        return DivisionUpgradeAbilityModel

    def _initialize(self):
        super(DivisionUpgradeRewardsViewModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addNumberProperty('subDivisionIndex', 0)
        self._addNumberProperty('level', 0)
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('hasNewVehicles', False)
        self._addArrayProperty('abilities', Array())
        self.onClose = self._addCommand('onClose')
        self.onConfirm = self._addCommand('onConfirm')
