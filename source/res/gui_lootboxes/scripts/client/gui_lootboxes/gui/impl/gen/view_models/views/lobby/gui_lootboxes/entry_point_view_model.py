# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/entry_point_view_model.py
from frameworks.wulf import ViewModel

class EntryPointViewModel(ViewModel):
    __slots__ = ('onOpenStorage',)

    def __init__(self, properties=4, commands=1):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getBoxesCount(self):
        return self._getNumber(0)

    def setBoxesCount(self, value):
        self._setNumber(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def getIsLootBoxesEnabled(self):
        return self._getBool(2)

    def setIsLootBoxesEnabled(self, value):
        self._setBool(2, value)

    def getHasInfinite(self):
        return self._getBool(3)

    def setHasInfinite(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addNumberProperty('boxesCount', 0)
        self._addBoolProperty('hasNew', False)
        self._addBoolProperty('isLootBoxesEnabled', True)
        self._addBoolProperty('hasInfinite', False)
        self.onOpenStorage = self._addCommand('onOpenStorage')
