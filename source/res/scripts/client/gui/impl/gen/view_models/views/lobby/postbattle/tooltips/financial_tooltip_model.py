# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/tooltips/financial_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.postbattle.details_group_model import DetailsGroupModel

class FinancialTooltipModel(DetailsGroupModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(FinancialTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyType(self):
        return self._getString(3)

    def setCurrencyType(self, value):
        self._setString(3, value)

    def getAccountType(self):
        return self._getNumber(4)

    def setAccountType(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(FinancialTooltipModel, self)._initialize()
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('accountType', 0)
