# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_tickets_tooltip_model.py
from frameworks.wulf import ViewModel

class FestivalTicketsTooltipModel(ViewModel):
    __slots__ = ()

    def getTicketsStr(self):
        return self._getString(0)

    def setTicketsStr(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(FestivalTicketsTooltipModel, self)._initialize()
        self._addStringProperty('ticketsStr', '')
