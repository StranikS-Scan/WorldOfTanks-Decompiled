# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_taler_tooltip.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_taler_tooltip_view_model import BattlePassTalerTooltipViewModel
from gui.impl.pub import ViewImpl

class BattlePassTalerTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.mono.battle_pass.tooltips.bptaler())
        settings.model = BattlePassTalerTooltipViewModel()
        super(BattlePassTalerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassTalerTooltip, self).getViewModel()
