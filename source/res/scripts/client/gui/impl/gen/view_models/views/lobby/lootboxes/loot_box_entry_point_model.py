# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_entry_point_model.py
from frameworks.wulf import ViewModel

class LootBoxEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=2, commands=1):
        super(LootBoxEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getBoxesCount(self):
        return self._getNumber(0)

    def setBoxesCount(self, value):
        self._setNumber(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(LootBoxEntryPointModel, self)._initialize()
        self._addNumberProperty('boxesCount', 0)
        self._addBoolProperty('hasNew', False)
        self.onWidgetClick = self._addCommand('onWidgetClick')
