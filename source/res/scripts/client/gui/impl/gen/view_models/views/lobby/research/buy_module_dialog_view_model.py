# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/research/buy_module_dialog_view_model.py
from enum import Enum
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class MountDisabledReason(Enum):
    INVALID = 'invalid'
    NONE = 'none'
    HEAVY = 'too heavy'
    HEAVYCHASSIS = 'too heavy chassis'
    NEEDGUN = 'need gun'
    NOTFORVEHICLETYPE = 'not for this vehicle type'
    NOTFORCURRENTVEHICLE = 'not for current vehicle'
    NEEDTURRET = 'need turret'


class ModuleType(Enum):
    FUELTANK = 'vehicleFuelTank'
    CHASSIS = 'vehicleChassis'
    ENGINE = 'vehicleEngine'
    RADIO = 'vehicleRadio'
    TURRET = 'vehicleTurret'
    GUN = 'vehicleGun'


class BuyModuleDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=3):
        super(BuyModuleDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getModuleType(self):
        return ModuleType(self._getString(10))

    def setModuleType(self, value):
        self._setString(10, value.value)

    def getModulePrice(self):
        return self._getNumber(11)

    def setModulePrice(self, value):
        self._setNumber(11, value)

    def getPreviousModuleName(self):
        return self._getString(12)

    def setPreviousModuleName(self, value):
        self._setString(12, value)

    def getPreviousModulePrice(self):
        return self._getNumber(13)

    def setPreviousModulePrice(self, value):
        self._setNumber(13, value)

    def getAutoSellEnabled(self):
        return self._getBool(14)

    def setAutoSellEnabled(self, value):
        self._setBool(14, value)

    def getMountDisabledReason(self):
        return MountDisabledReason(self._getString(15))

    def setMountDisabledReason(self, value):
        self._setString(15, value.value)

    def _initialize(self):
        super(BuyModuleDialogViewModel, self)._initialize()
        self._addStringProperty('moduleType')
        self._addNumberProperty('modulePrice', 0)
        self._addStringProperty('previousModuleName', '')
        self._addNumberProperty('previousModulePrice', 0)
        self._addBoolProperty('autoSellEnabled', False)
        self._addStringProperty('mountDisabledReason')
