# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/restore_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.equipment_price_model import EquipmentPriceModel

class EquipmentType(Enum):
    IMPROVED = 'improved'
    TROPHY = 'trophy'
    MODERNIZED = 'modernized'


class RestoreViewModel(DialogTemplateViewModel):
    __slots__ = ('onRestore', 'onClose', 'onAmountChange')

    def __init__(self, properties=11, commands=5):
        super(RestoreViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def equipmentBonus(self):
        return self._getViewModel(6)

    @staticmethod
    def getEquipmentBonusType():
        return ItemBonusModel

    def getEquipmentType(self):
        return EquipmentType(self._getString(7))

    def setEquipmentType(self, value):
        self._setString(7, value.value)

    def getMinEquipCount(self):
        return self._getNumber(8)

    def setMinEquipCount(self, value):
        self._setNumber(8, value)

    def getMaxEquipCount(self):
        return self._getNumber(9)

    def setMaxEquipCount(self, value):
        self._setNumber(9, value)

    def getEquipmentPriceList(self):
        return self._getArray(10)

    def setEquipmentPriceList(self, value):
        self._setArray(10, value)

    @staticmethod
    def getEquipmentPriceListType():
        return EquipmentPriceModel

    def _initialize(self):
        super(RestoreViewModel, self)._initialize()
        self._addViewModelProperty('equipmentBonus', ItemBonusModel())
        self._addStringProperty('equipmentType')
        self._addNumberProperty('minEquipCount', 0)
        self._addNumberProperty('maxEquipCount', 0)
        self._addArrayProperty('equipmentPriceList', Array())
        self.onRestore = self._addCommand('onRestore')
        self.onClose = self._addCommand('onClose')
        self.onAmountChange = self._addCommand('onAmountChange')
