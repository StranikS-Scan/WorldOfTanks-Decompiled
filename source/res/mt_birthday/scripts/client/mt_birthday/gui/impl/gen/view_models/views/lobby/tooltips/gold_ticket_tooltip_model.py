# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/gold_ticket_tooltip_model.py
from frameworks.wulf import ViewModel

class GoldTicketTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(GoldTicketTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyCount(self):
        return self._getNumber(0)

    def setCurrencyCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(GoldTicketTooltipModel, self)._initialize()
        self._addNumberProperty('currencyCount', 0)
