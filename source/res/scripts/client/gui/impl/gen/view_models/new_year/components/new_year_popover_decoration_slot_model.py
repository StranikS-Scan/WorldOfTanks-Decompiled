# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_popover_decoration_slot_model.py
from gui.impl.gen.view_models.new_year.components.new_year_decoration_slot_common_model import NewYearDecorationSlotCommonModel

class NewYearPopoverDecorationSlotModel(NewYearDecorationSlotCommonModel):
    __slots__ = ()

    def getIsNew(self):
        return self._getBool(6)

    def setIsNew(self, value):
        self._setBool(6, value)

    def getSetting(self):
        return self._getString(7)

    def setSetting(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(NewYearPopoverDecorationSlotModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addStringProperty('setting', '')
