# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/deconstruct_confirm_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.current_balance_model import CurrentBalanceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.main_content.deconstruct_confirm_item_model import DeconstructConfirmItemModel

class DialogType(Enum):
    DECONSTRUCT = 'deconstruct'
    UPGRADE = 'upgrade'


class DeconstructConfirmModel(DialogTemplateViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=14, commands=3):
        super(DeconstructConfirmModel, self).__init__(properties=properties, commands=commands)

    def getIsLastVehicleEquipment(self):
        return self._getBool(6)

    def setIsLastVehicleEquipment(self, value):
        self._setBool(6, value)

    def getDeconstructingEquipCoinsAmount(self):
        return self._getNumber(7)

    def setDeconstructingEquipCoinsAmount(self, value):
        self._setNumber(7, value)

    def getEquipUpgradeCost(self):
        return self._getNumber(8)

    def setEquipUpgradeCost(self, value):
        self._setNumber(8, value)

    def getDeviceName(self):
        return self._getString(9)

    def setDeviceName(self, value):
        self._setString(9, value)

    def getDialogType(self):
        return DialogType(self._getString(10))

    def setDialogType(self, value):
        self._setString(10, value.value)

    def getBalance(self):
        return self._getArray(11)

    def setBalance(self, value):
        self._setArray(11, value)

    @staticmethod
    def getBalanceType():
        return CurrentBalanceModel

    def getVehicleEquipment(self):
        return self._getArray(12)

    def setVehicleEquipment(self, value):
        self._setArray(12, value)

    @staticmethod
    def getVehicleEquipmentType():
        return DeconstructConfirmItemModel

    def getInventoryEquipment(self):
        return self._getArray(13)

    def setInventoryEquipment(self, value):
        self._setArray(13, value)

    @staticmethod
    def getInventoryEquipmentType():
        return DeconstructConfirmItemModel

    def _initialize(self):
        super(DeconstructConfirmModel, self)._initialize()
        self._addBoolProperty('isLastVehicleEquipment', False)
        self._addNumberProperty('deconstructingEquipCoinsAmount', 0)
        self._addNumberProperty('equipUpgradeCost', 0)
        self._addStringProperty('deviceName', '')
        self._addStringProperty('dialogType')
        self._addArrayProperty('balance', Array())
        self._addArrayProperty('vehicleEquipment', Array())
        self._addArrayProperty('inventoryEquipment', Array())
        self.onClose = self._addCommand('onClose')
