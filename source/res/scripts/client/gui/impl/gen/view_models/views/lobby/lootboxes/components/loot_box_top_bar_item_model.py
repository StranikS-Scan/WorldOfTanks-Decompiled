# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_top_bar_item_model.py
from frameworks.wulf import ViewModel

class LootBoxTopBarItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LootBoxTopBarItemModel, self).__init__(properties=properties, commands=commands)

    def getBoxType(self):
        return self._getString(0)

    def setBoxType(self, value):
        self._setString(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def getBoxCounter(self):
        return self._getNumber(2)

    def setBoxCounter(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(LootBoxTopBarItemModel, self)._initialize()
        self._addStringProperty('boxType', '')
        self._addBoolProperty('hasNew', False)
        self._addNumberProperty('boxCounter', 0)
