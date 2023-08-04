# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/bonus_probabilities_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel

class BonusProbabilitiesViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BonusProbabilitiesViewModel, self).__init__(properties=properties, commands=commands)

    def getLootboxName(self):
        return self._getString(0)

    def setLootboxName(self, value):
        self._setString(0, value)

    def getLootboxTier(self):
        return self._getNumber(1)

    def setLootboxTier(self, value):
        self._setNumber(1, value)

    def getSlots(self):
        return self._getArray(2)

    def setSlots(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSlotsType():
        return SlotViewModel

    def _initialize(self):
        super(BonusProbabilitiesViewModel, self)._initialize()
        self._addStringProperty('lootboxName', '')
        self._addNumberProperty('lootboxTier', 0)
        self._addArrayProperty('slots', Array())
