# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_reward_kits_unavailable_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class NyRewardKitsUnavailableTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyRewardKitsUnavailableTooltip())
        settings.model = ViewModel()
        super(NyRewardKitsUnavailableTooltip, self).__init__(settings)
