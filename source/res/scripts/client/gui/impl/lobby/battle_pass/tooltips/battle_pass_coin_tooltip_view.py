# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_coin_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view_model import BattlePassCoinTooltipViewModel
from gui.impl.pub import ViewImpl

class BattlePassCoinTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView())
        settings.model = BattlePassCoinTooltipViewModel()
        super(BattlePassCoinTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassCoinTooltipView, self).getViewModel()
