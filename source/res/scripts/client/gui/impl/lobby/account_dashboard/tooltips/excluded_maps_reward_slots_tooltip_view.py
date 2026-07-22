# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/tooltips/excluded_maps_reward_slots_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_dashboard.tooltips.excluded_maps_reward_slots_tooltip_view_model import ExcludedMapsRewardSlotsTooltipViewModel
from gui.impl.pub import ViewImpl

class ExcludedMapsRewardSlotsTooltipView(ViewImpl):
    __slots__ = ('__state', '__coolDown', '__expiration')

    def __init__(self, state, coolDown, expiration):
        settings = ViewSettings(R.views.lobby.account_dashboard.tooltips.ExcludedMapsRewardSlotsTooltipView())
        settings.flags = ViewFlags.VIEW
        settings.model = ExcludedMapsRewardSlotsTooltipViewModel()
        super(ExcludedMapsRewardSlotsTooltipView, self).__init__(settings)
        self.__state = state
        self.__coolDown = coolDown
        self.__expiration = expiration

    @property
    def viewModel(self):
        return super(ExcludedMapsRewardSlotsTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ExcludedMapsRewardSlotsTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            vmTx.setState(self.__state)
            vmTx.setCooldownTime(self.__coolDown)
            vmTx.setExpirationTime(self.__expiration)
