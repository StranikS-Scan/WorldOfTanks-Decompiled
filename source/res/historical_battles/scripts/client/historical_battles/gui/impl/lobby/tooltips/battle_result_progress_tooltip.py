# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/battle_result_progress_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.battle_result_progress_tooltip_model import BattleResultProgressTooltipModel

class BattleResultProgressTooltip(ViewImpl):
    __slots__ = ('__frontName',)

    def __init__(self, frontName):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.BattleResultProgressTooltip())
        settings.model = BattleResultProgressTooltipModel()
        self.__frontName = frontName
        super(BattleResultProgressTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleResultProgressTooltip, self).getViewModel()

    def _onLoading(self):
        super(BattleResultProgressTooltip, self)._initialize()
        with self.viewModel.transaction() as tx:
            tx.setFrontName(self.__frontName)
