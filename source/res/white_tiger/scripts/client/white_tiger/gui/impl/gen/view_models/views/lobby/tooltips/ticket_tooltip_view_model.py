# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/ticket_tooltip_view_model.py
from frameworks.wulf import ViewModel

class TicketTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(TicketTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getQuantity(self):
        return self._getNumber(0)

    def setQuantity(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(TicketTooltipViewModel, self)._initialize()
        self._addNumberProperty('quantity', 0)
