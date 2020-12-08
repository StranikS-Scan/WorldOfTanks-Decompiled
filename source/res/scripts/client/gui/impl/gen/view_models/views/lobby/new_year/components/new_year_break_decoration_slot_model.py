# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_break_decoration_slot_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_decoration_slot_common_model import NewYearDecorationSlotCommonModel

class NewYearBreakDecorationSlotModel(NewYearDecorationSlotCommonModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(NewYearBreakDecorationSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(6)

    def setIsNew(self, value):
        self._setBool(6, value)

    def getBreakDuration(self):
        return self._getReal(7)

    def setBreakDuration(self, value):
        self._setReal(7, value)

    def getInProgressAnimation(self):
        return self._getBool(8)

    def setInProgressAnimation(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(NewYearBreakDecorationSlotModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addRealProperty('breakDuration', 0.0)
        self._addBoolProperty('inProgressAnimation', False)
