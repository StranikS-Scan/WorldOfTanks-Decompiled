# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_popover_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_decoration_slot_model import NyDecorationSlotModel

class NyPopoverDecorationSlotModel(NyDecorationSlotModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(NyPopoverDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(5)

    def setIsNew(self, value):
        self._setBool(5, value)

    def getSetting(self):
        return self._getString(6)

    def setSetting(self, value):
        self._setString(6, value)

    def getCount(self):
        return self._getNumber(7)

    def setCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NyPopoverDecorationSlotModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addStringProperty('setting', '')
        self._addNumberProperty('count', 0)
