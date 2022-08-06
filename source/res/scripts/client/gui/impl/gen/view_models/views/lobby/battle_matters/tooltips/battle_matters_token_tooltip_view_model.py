# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/tooltips/battle_matters_token_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattleMattersTokenTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattleMattersTokenTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(BattleMattersTokenTooltipViewModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
