# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/confirm_actions_with_equipment_dialog_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.details_device_model import DetailsDeviceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.details_price_block_model import DetailsPriceBlockModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sub_views.current_balance_model import CurrentBalanceModel

class DialogType(Enum):
    DECONSTRUCTFROMSTORAGE = 'deconstructFromStorage'
    DECONSTRUCTFROMSLOTS = 'deconstructFromSlots'


class ConfirmActionsWithEquipmentDialogModel(DialogTemplateViewModel):
    __slots__ = ('onDeconstruct', 'onClose')

    def __init__(self, properties=11, commands=4):
        super(ConfirmActionsWithEquipmentDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def detailsDevice(self):
        return self._getViewModel(6)

    @staticmethod
    def getDetailsDeviceType():
        return DetailsDeviceModel

    @property
    def detailsPriceBlock(self):
        return self._getViewModel(7)

    @staticmethod
    def getDetailsPriceBlockType():
        return DetailsPriceBlockModel

    def getAlertText(self):
        return self._getString(8)

    def setAlertText(self, value):
        self._setString(8, value)

    def getDialogType(self):
        return DialogType(self._getString(9))

    def setDialogType(self, value):
        self._setString(9, value.value)

    def getBalance(self):
        return self._getArray(10)

    def setBalance(self, value):
        self._setArray(10, value)

    @staticmethod
    def getBalanceType():
        return CurrentBalanceModel

    def _initialize(self):
        super(ConfirmActionsWithEquipmentDialogModel, self)._initialize()
        self._addViewModelProperty('detailsDevice', DetailsDeviceModel())
        self._addViewModelProperty('detailsPriceBlock', DetailsPriceBlockModel())
        self._addStringProperty('alertText', '')
        self._addStringProperty('dialogType')
        self._addArrayProperty('balance', Array())
        self.onDeconstruct = self._addCommand('onDeconstruct')
        self.onClose = self._addCommand('onClose')
