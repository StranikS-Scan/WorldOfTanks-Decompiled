# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/confirm_actions_with_equipment_dialog_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.current_balance_model import CurrentBalanceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.details_device_model import DetailsDeviceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.details_price_block_model import DetailsPriceBlockModel

class DialogType(Enum):
    SELLFROMSTORAGE = 'sellFromStorage'
    DECONSTRUCTFROMSTORAGE = 'deconstructFromStorage'
    DECONSTRUCTFROMSLOTS = 'deconstructFromSlots'


class ConfirmActionsWithEquipmentDialogModel(DialogTemplateViewModel):
    __slots__ = ('onSell', 'onDeconstruct', 'onClose')

    def __init__(self, properties=11, commands=5):
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

    def getIsLastEquipt(self):
        return self._getBool(8)

    def setIsLastEquipt(self, value):
        self._setBool(8, value)

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
        self._addBoolProperty('isLastEquipt', False)
        self._addStringProperty('dialogType')
        self._addArrayProperty('balance', Array())
        self.onSell = self._addCommand('onSell')
        self.onDeconstruct = self._addCommand('onDeconstruct')
        self.onClose = self._addCommand('onClose')
