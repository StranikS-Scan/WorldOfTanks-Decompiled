# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/customization_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class CustomizationBonusModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(CustomizationBonusModel, self).__init__(properties=properties, commands=commands)

    def getCustomizationID(self):
        return self._getNumber(9)

    def setCustomizationID(self, value):
        self._setNumber(9, value)

    def getStyleCD(self):
        return self._getNumber(10)

    def setStyleCD(self, value):
        self._setNumber(10, value)

    def getItem(self):
        return self._getString(11)

    def setItem(self, value):
        self._setString(11, value)

    def getIcon(self):
        return self._getString(12)

    def setIcon(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(CustomizationBonusModel, self)._initialize()
        self._addNumberProperty('customizationID', 0)
        self._addNumberProperty('styleCD', 0)
        self._addStringProperty('item', '')
        self._addStringProperty('icon', '')
