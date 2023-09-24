# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/respawn_info_tooltip_view.py
from frameworks.wulf import ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.respawn_info_tooltip_view_model import RespawnInfoTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class RespawnInfoTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.RespawnInfoTooltipView())
        settings.model = RespawnInfoTooltipViewModel()
        super(RespawnInfoTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RespawnInfoTooltipView, self).getViewModel()
