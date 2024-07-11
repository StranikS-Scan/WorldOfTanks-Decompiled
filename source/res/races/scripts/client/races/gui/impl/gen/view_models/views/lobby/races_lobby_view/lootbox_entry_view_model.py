# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/lootbox_entry_view_model.py
from frameworks.wulf import ViewModel

class LootboxEntryViewModel(ViewModel):
    __slots__ = ('onOpenStorage',)

    def __init__(self, properties=5, commands=1):
        super(LootboxEntryViewModel, self).__init__(properties=properties, commands=commands)

    def getIsVisible(self):
        return self._getBool(0)

    def setIsVisible(self, value):
        self._setBool(0, value)

    def getBoxesCount(self):
        return self._getNumber(1)

    def setBoxesCount(self, value):
        self._setNumber(1, value)

    def getHasNew(self):
        return self._getBool(2)

    def setHasNew(self, value):
        self._setBool(2, value)

    def getIsLootBoxesEnabled(self):
        return self._getBool(3)

    def setIsLootBoxesEnabled(self, value):
        self._setBool(3, value)

    def getHasInfinite(self):
        return self._getBool(4)

    def setHasInfinite(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(LootboxEntryViewModel, self)._initialize()
        self._addBoolProperty('isVisible', False)
        self._addNumberProperty('boxesCount', 0)
        self._addBoolProperty('hasNew', False)
        self._addBoolProperty('isLootBoxesEnabled', True)
        self._addBoolProperty('hasInfinite', False)
        self.onOpenStorage = self._addCommand('onOpenStorage')
