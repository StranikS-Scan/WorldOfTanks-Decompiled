# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/battle_result_progress_tooltip_model.py
from frameworks.wulf import ViewModel

class BattleResultProgressTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattleResultProgressTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(BattleResultProgressTooltipModel, self)._initialize()
        self._addStringProperty('frontName', '')
