# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/research/buy_module_dialog_view_model.py
from enum import Enum
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class MountDisabledReason(Enum):
    INVALID = 'invalid'
    NONE = 'none'
    NEEDGUN = 'need gun'
    NOTFORVEHICLETYPE = 'not for this vehicle type'
    NOTFORCURRENTVEHICLE = 'not for current vehicle'
    NEEDTURRET = 'need turret'


class ModuleType(Enum):
    FUELTANK = 'vehicleFuelTank'
    CHASSIS = 'vehicleChassis'
    WHEELEDCHASSIS = 'vehicleWheeledChassis'
    ENGINE = 'vehicleEngine'
    RADIO = 'vehicleRadio'
    TURRET = 'vehicleTurret'
    GUN = 'vehicleGun'


class BuyModuleDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=3):
        super(BuyModuleDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getModuleType(self):
        return ModuleType(self._getString(11))

    def setModuleType(self, value):
        self._setString(11, value.value)

    def getModulePrice(self):
        return self._getNumber(12)

    def setModulePrice(self, value):
        self._setNumber(12, value)

    def getPreviousModuleName(self):
        return self._getString(13)

    def setPreviousModuleName(self, value):
        self._setString(13, value)

    def getPreviousModulePrice(self):
        return self._getNumber(14)

    def setPreviousModulePrice(self, value):
        self._setNumber(14, value)

    def getAutoSellEnabled(self):
        return self._getBool(15)

    def setAutoSellEnabled(self, value):
        self._setBool(15, value)

    def getMountDisabledReason(self):
        return MountDisabledReason(self._getString(16))

    def setMountDisabledReason(self, value):
        self._setString(16, value.value)

    def _initialize(self):
        super(BuyModuleDialogViewModel, self)._initialize()
        self._addStringProperty('moduleType')
        self._addNumberProperty('modulePrice', 0)
        self._addStringProperty('previousModuleName', '')
        self._addNumberProperty('previousModulePrice', 0)
        self._addBoolProperty('autoSellEnabled', False)
        self._addStringProperty('mountDisabledReason')
