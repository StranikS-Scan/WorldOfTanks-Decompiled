# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_craft_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_decoration_slot_common_model import NewYearDecorationSlotCommonModel

class NewYearCraftDecorationSlotModel(NewYearDecorationSlotCommonModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(NewYearCraftDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getHideSlot(self):
        return self._getBool(6)

    def setHideSlot(self, value):
        self._setBool(6, value)

    def getType(self):
        return self._getString(7)

    def setType(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(NewYearCraftDecorationSlotModel, self)._initialize()
        self._addBoolProperty('hideSlot', False)
        self._addStringProperty('type', '')
