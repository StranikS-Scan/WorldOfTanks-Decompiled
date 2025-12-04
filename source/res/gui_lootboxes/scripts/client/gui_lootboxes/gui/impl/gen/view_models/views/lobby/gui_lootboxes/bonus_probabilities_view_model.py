# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/bonus_probabilities_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.slot_view_model import SlotViewModel

class BonusProbabilitiesViewModel(ViewModel):
    __slots__ = ('onClose', 'onPreview')

    def __init__(self, properties=8, commands=2):
        super(BonusProbabilitiesViewModel, self).__init__(properties=properties, commands=commands)

    def getLootboxName(self):
        return self._getString(0)

    def setLootboxName(self, value):
        self._setString(0, value)

    def getLootboxID(self):
        return self._getNumber(1)

    def setLootboxID(self, value):
        self._setNumber(1, value)

    def getLootboxTier(self):
        return self._getNumber(2)

    def setLootboxTier(self, value):
        self._setNumber(2, value)

    def getSlots(self):
        return self._getArray(3)

    def setSlots(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSlotsType():
        return SlotViewModel

    def getGuaranteedFrequencies(self):
        return self._getArray(4)

    def setGuaranteedFrequencies(self, value):
        self._setArray(4, value)

    @staticmethod
    def getGuaranteedFrequenciesType():
        return int

    def getHasLootLists(self):
        return self._getBool(5)

    def setHasLootLists(self, value):
        self._setBool(5, value)

    def getRotationStage(self):
        return self._getNumber(6)

    def setRotationStage(self, value):
        self._setNumber(6, value)

    def getLootLists(self):
        return self._getArray(7)

    def setLootLists(self, value):
        self._setArray(7, value)

    @staticmethod
    def getLootListsType():
        return SlotViewModel

    def _initialize(self):
        super(BonusProbabilitiesViewModel, self)._initialize()
        self._addStringProperty('lootboxName', '')
        self._addNumberProperty('lootboxID', 0)
        self._addNumberProperty('lootboxTier', 0)
        self._addArrayProperty('slots', Array())
        self._addArrayProperty('guaranteedFrequencies', Array())
        self._addBoolProperty('hasLootLists', False)
        self._addNumberProperty('rotationStage', 0)
        self._addArrayProperty('lootLists', Array())
        self.onClose = self._addCommand('onClose')
        self.onPreview = self._addCommand('onPreview')
