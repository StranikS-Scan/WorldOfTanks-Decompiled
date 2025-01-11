# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_selector_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class LootBoxSelectorItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(LootBoxSelectorItemModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(0)

    def setIndex(self, value):
        self._setNumber(0, value)

    def getBoxName(self):
        return self._getResource(1)

    def setBoxName(self, value):
        self._setResource(1, value)

    def getBoxType(self):
        return self._getString(2)

    def setBoxType(self, value):
        self._setString(2, value)

    def getBoxCounter(self):
        return self._getNumber(3)

    def setBoxCounter(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(LootBoxSelectorItemModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addResourceProperty('boxName', R.invalid())
        self._addStringProperty('boxType', '')
        self._addNumberProperty('boxCounter', 0)
