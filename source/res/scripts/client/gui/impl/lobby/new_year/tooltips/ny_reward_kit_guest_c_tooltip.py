# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_reward_kit_guest_c_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class NyRewardKitGuestCTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyRewardKitGuestCTooltip())
        settings.model = ViewModel()
        super(NyRewardKitGuestCTooltip, self).__init__(settings)
