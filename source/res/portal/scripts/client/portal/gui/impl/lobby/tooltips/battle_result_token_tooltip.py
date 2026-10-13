# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/battle_result_token_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.battle_result_token_tooltip_model import BattleResultTokenTooltipModel
from portal_common.portal_constants import PortalBattleLevel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class BattleResultTokenTooltip(ViewImpl):
    __slots__ = ('_isWinner', '_battleDifficulty')

    def __init__(self, isWinner, battleDifficulty):
        settings = ViewSettings(R.views.portal.lobby.tooltips.BattleResultTokenTooltip())
        settings.model = BattleResultTokenTooltipModel()
        self._isWinner = isWinner
        self._battleDifficulty = battleDifficulty
        super(BattleResultTokenTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleResultTokenTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultTokenTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            self.__fillModel(vm)

    def __fillModel(self, model):
        model.setIsWinner(self._isWinner)
        model.setBattleDifficulty(self._battleDifficulty)
        model.setMaxBattleDifficulty(PortalBattleLevel.HARD)
