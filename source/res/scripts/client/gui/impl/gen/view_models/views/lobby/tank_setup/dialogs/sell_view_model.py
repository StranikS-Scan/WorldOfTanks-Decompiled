# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/sell_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.equipment_price_model import EquipmentPriceModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sub_views.current_balance_model import CurrentBalanceModel

class ModuleType(Enum):
    IMPROVED = 'improved'
    TROPHY = 'trophy'
    STANDARD = 'standard'


class SellViewModel(DialogTemplateViewModel):
    __slots__ = ('onSell', 'onClose')

    def __init__(self, properties=10, commands=4):
        super(SellViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def equipmentPrice(self):
        return self._getViewModel(6)

    @staticmethod
    def getEquipmentPriceType():
        return EquipmentPriceModel

    @property
    def equipment(self):
        return self._getViewModel(7)

    @staticmethod
    def getEquipmentType():
        return ItemBonusModel

    def getModuleType(self):
        return ModuleType(self._getString(8))

    def setModuleType(self, value):
        self._setString(8, value.value)

    def getBalance(self):
        return self._getArray(9)

    def setBalance(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBalanceType():
        return CurrentBalanceModel

    def _initialize(self):
        super(SellViewModel, self)._initialize()
        self._addViewModelProperty('equipmentPrice', EquipmentPriceModel())
        self._addViewModelProperty('equipment', ItemBonusModel())
        self._addStringProperty('moduleType')
        self._addArrayProperty('balance', Array())
        self.onSell = self._addCommand('onSell')
        self.onClose = self._addCommand('onClose')
