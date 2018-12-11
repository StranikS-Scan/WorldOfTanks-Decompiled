# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_box_top_bar_item_model.py
from frameworks.wulf import ViewModel

class LootBoxTopBarItemModel(ViewModel):
    __slots__ = ()

    def getBoxType(self):
        return self._getString(0)

    def setBoxType(self, value):
        self._setString(0, value)

    def getBoxCounter(self):
        return self._getNumber(1)

    def setBoxCounter(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(LootBoxTopBarItemModel, self)._initialize()
        self._addStringProperty('boxType', '')
        self._addNumberProperty('boxCounter', 0)
