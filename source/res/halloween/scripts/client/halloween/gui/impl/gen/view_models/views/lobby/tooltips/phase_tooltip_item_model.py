# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/phase_tooltip_item_model.py
from halloween.gui.impl.gen.view_models.views.lobby.common.phase_item_model import PhaseItemModel

class PhaseTooltipItemModel(PhaseItemModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(PhaseTooltipItemModel, self).__init__(properties=properties, commands=commands)

    def getDate(self):
        return self._getNumber(4)

    def setDate(self, value):
        self._setNumber(4, value)

    def getStartDate(self):
        return self._getNumber(5)

    def setStartDate(self, value):
        self._setNumber(5, value)

    def getEndDate(self):
        return self._getNumber(6)

    def setEndDate(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(PhaseTooltipItemModel, self)._initialize()
        self._addNumberProperty('date', 0)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
