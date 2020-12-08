# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_popover_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_break_decoration_slot_model import NewYearBreakDecorationSlotModel

class NewYearPopoverDecorationSlotModel(NewYearBreakDecorationSlotModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NewYearPopoverDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getSetting(self):
        return self._getString(9)

    def setSetting(self, value):
        self._setString(9, value)

    def getSelectedForBreak(self):
        return self._getBool(10)

    def setSelectedForBreak(self, value):
        self._setBool(10, value)

    def getCount(self):
        return self._getNumber(11)

    def setCount(self, value):
        self._setNumber(11, value)

    def getIsButton(self):
        return self._getBool(12)

    def setIsButton(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearPopoverDecorationSlotModel, self)._initialize()
        self._addStringProperty('setting', '')
        self._addBoolProperty('selectedForBreak', False)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isButton', False)
