# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/birthday_lootbox_tooltip_extended_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.birthday_lootbox_slot_model import BirthdayLootboxSlotModel

class BirthdayLootboxTooltipExtendedModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BirthdayLootboxTooltipExtendedModel, self).__init__(properties=properties, commands=commands)

    def getLootboxName(self):
        return self._getString(0)

    def setLootboxName(self, value):
        self._setString(0, value)

    def getSlots(self):
        return self._getArray(1)

    def setSlots(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSlotsType():
        return BirthdayLootboxSlotModel

    def _initialize(self):
        super(BirthdayLootboxTooltipExtendedModel, self)._initialize()
        self._addStringProperty('lootboxName', '')
        self._addArrayProperty('slots', Array())
