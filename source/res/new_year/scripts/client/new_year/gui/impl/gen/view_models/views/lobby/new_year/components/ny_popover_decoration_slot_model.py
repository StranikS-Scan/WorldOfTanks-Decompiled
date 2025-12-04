# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/components/ny_popover_decoration_slot_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_break_decoration_slot_model import NyBreakDecorationSlotModel

class NyPopoverDecorationSlotModel(NyBreakDecorationSlotModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NyPopoverDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getSetting(self):
        return self._getString(11)

    def setSetting(self, value):
        self._setString(11, value)

    def getCount(self):
        return self._getNumber(12)

    def setCount(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(NyPopoverDecorationSlotModel, self)._initialize()
        self._addStringProperty('setting', '')
        self._addNumberProperty('count', 0)
