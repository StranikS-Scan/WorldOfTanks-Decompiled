# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/prem_dashboard_view.py
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_view_model import PremDashboardViewModel
from gui.impl.lobby.premacc.dashboard.dashboard_premium_card import DashboardPremiumCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_double_experience_card import PremDashboardDoubleExperienceCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_header import PremDashboardHeader
from gui.impl.lobby.premacc.dashboard.prem_dashboard_maps_blacklist_card import PremDashboardMapsBlacklistCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_piggy_bank_card import PremDashboardPiggyBankCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_quests_card import PremDashboardQuestsCard
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags, ViewSettings
from gui.shared.event_dispatcher import showHangar

class PremDashboardView(ViewImpl, SoundViewMixin):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PremDashboardViewModel()
        super(PremDashboardView, self).__init__(settings)
        Waiting.show('loadPage')

    @property
    def viewModel(self):
        return super(PremDashboardView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PremDashboardView, self)._onLoading()
        self._addSoundEvent()
        self.viewModel.onCloseAction += self.__onCloseAction
        self.viewModel.onInitialized += self.__onInitialized
        self.setChildView(R.dynamic_ids.prem_dashboard.header(), PremDashboardHeader())
        self.setChildView(R.dynamic_ids.prem_dashboard.premium_card(), DashboardPremiumCard())
        self.setChildView(R.dynamic_ids.prem_dashboard.double_xp_card(), PremDashboardDoubleExperienceCard())
        self.setChildView(R.dynamic_ids.prem_dashboard.piggy_bank_card(), PremDashboardPiggyBankCard())
        self.setChildView(R.dynamic_ids.prem_dashboard.premium_quests_card(), PremDashboardQuestsCard())
        self.setChildView(R.dynamic_ids.prem_dashboard.maps_black_list_card(), PremDashboardMapsBlacklistCard())

    def _finalize(self):
        self.viewModel.onCloseAction -= self.__onCloseAction
        self.viewModel.onInitialized -= self.__onInitialized
        self._removeSoundEvent()

    def __onCloseAction(self):
        showHangar()

    def __onInitialized(self):
        Waiting.hide('loadPage')
