# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/tank_setup_panel_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.consumable_model import ConsumableModel

class TankSetupPanelViewModel(ViewModel):
    __slots__ = ('onClick',)
    TOOLTIP_SHELL = 'hangarShell'
    TOOLTIP_ABILITY = 'ability'
    TOOLTIP_RESPAWN = 'respawn'

    def __init__(self, properties=4, commands=1):
        super(TankSetupPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getVehicleType(self):
        return self._getString(1)

    def setVehicleType(self, value):
        self._setString(1, value)

    def getIsVehicleInBattle(self):
        return self._getBool(2)

    def setIsVehicleInBattle(self, value):
        self._setBool(2, value)

    def getConsumable(self):
        return self._getArray(3)

    def setConsumable(self, value):
        self._setArray(3, value)

    @staticmethod
    def getConsumableType():
        return ConsumableModel

    def _initialize(self):
        super(TankSetupPanelViewModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('isVehicleInBattle', False)
        self._addArrayProperty('consumable', Array())
        self.onClick = self._addCommand('onClick')
