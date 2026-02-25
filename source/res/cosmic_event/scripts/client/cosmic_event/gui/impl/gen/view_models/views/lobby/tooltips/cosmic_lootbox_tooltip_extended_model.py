# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/tooltips/cosmic_lootbox_tooltip_extended_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.cosmic_lootbox_slot_model import CosmicLootboxSlotModel

class CosmicLootboxTooltipExtendedModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CosmicLootboxTooltipExtendedModel, self).__init__(properties=properties, commands=commands)

    def getLootboxName(self):
        return self._getString(0)

    def setLootboxName(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getSlots(self):
        return self._getArray(2)

    def setSlots(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSlotsType():
        return CosmicLootboxSlotModel

    def _initialize(self):
        super(CosmicLootboxTooltipExtendedModel, self)._initialize()
        self._addStringProperty('lootboxName', '')
        self._addStringProperty('description', '')
        self._addArrayProperty('slots', Array())
