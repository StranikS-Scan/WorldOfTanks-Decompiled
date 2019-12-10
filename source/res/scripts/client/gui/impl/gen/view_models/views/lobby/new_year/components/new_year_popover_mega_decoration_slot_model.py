# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_popover_mega_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_popover_decoration_slot_model import NewYearPopoverDecorationSlotModel

class NewYearPopoverMegaDecorationSlotModel(NewYearPopoverDecorationSlotModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(NewYearPopoverMegaDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getSelected(self):
        return self._getBool(13)

    def setSelected(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(NewYearPopoverMegaDecorationSlotModel, self)._initialize()
        self._addBoolProperty('selected', False)
