# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_entry_point_model.py
from frameworks.wulf import ViewModel

class LootBoxEntryPointModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def __init__(self, properties=0, commands=1):
        super(LootBoxEntryPointModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LootBoxEntryPointModel, self)._initialize()
        self.onWidgetClick = self._addCommand('onWidgetClick')
