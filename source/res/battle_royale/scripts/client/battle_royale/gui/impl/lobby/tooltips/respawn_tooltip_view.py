# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/respawn_tooltip_view.py
from frameworks.wulf import ViewSettings
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.respawn_tooltip_view_model import RespawnTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class RespawnTooltipView(ViewImpl):
    __slots__ = ('_respawnPeriods',)

    def __init__(self, respawnPeriods):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.RespawnTooltipView())
        settings.model = RespawnTooltipViewModel()
        self._respawnPeriods = respawnPeriods
        super(RespawnTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RespawnTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        if self._respawnPeriods is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setPlatoonTimeToRessurect(self._respawnPeriods.platoonTimeToRessurect)
                tx.setPlatoonRespawnPeriod(self._respawnPeriods.platoonRespawnPeriod)
                tx.setSoloRespawnPeriod(self._respawnPeriods.soloRespawnPeriod)
            return
