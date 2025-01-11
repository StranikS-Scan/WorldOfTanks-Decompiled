# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_drop_down_menu_item_model.py
from gui.impl.gen.view_models.ui_kit.drop_down_menu_item_model import DropDownMenuItemModel

class LootBoxDropDownMenuItemModel(DropDownMenuItemModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(LootBoxDropDownMenuItemModel, self).__init__(properties=properties, commands=commands)

    def getLabelStr(self):
        return self._getString(4)

    def setLabelStr(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(LootBoxDropDownMenuItemModel, self)._initialize()
        self._addStringProperty('labelStr', '')
