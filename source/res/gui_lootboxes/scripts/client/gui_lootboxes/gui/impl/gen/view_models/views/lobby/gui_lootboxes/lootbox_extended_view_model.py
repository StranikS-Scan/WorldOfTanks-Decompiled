# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootbox_extended_view_model.py
from frameworks.wulf import Array
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel

class LootboxExtendedViewModel(LootboxViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(LootboxExtendedViewModel, self).__init__(properties=properties, commands=commands)

    def getSlots(self):
        return self._getArray(10)

    def setSlots(self, value):
        self._setArray(10, value)

    @staticmethod
    def getSlotsType():
        return SlotViewModel

    def _initialize(self):
        super(LootboxExtendedViewModel, self)._initialize()
        self._addArrayProperty('slots', Array())
