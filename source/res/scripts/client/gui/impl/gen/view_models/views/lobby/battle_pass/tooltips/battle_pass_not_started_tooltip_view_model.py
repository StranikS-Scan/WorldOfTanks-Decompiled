# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_not_started_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassNotStartedTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassNotStartedTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getDate(self):
        return self._getString(0)

    def setDate(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(BattlePassNotStartedTooltipViewModel, self)._initialize()
        self._addStringProperty('date', '')
