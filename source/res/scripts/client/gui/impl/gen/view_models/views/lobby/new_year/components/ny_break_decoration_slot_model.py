# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_break_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_decoration_slot_model import NyDecorationSlotModel

class NyBreakDecorationSlotModel(NyDecorationSlotModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(NyBreakDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(7)

    def setIsNew(self, value):
        self._setBool(7, value)

    def getIsPure(self):
        return self._getBool(8)

    def setIsPure(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(NyBreakDecorationSlotModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addBoolProperty('isPure', False)
