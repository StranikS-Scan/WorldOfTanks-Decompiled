# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/prem_dashboard_view.py
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_view_model import PremDashboardViewModel
from gui.impl.lobby.premacc.dashboard.dashboard_premium_card import DashboardPremiumCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_double_experience_card import PremDashboardDoubleExperienceCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_header import PremDashboardHeader
from gui.impl.lobby.premacc.dashboard.prem_dashboard_maps_blacklist_card import PremDashboardMapsBlacklistCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_piggy_bank_card import PremDashboardPiggyBankCard
from gui.impl.lobby.premacc.dashboard.prem_dashboard_quests_card import PremDashboardQuestsCard
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags
from gui.shared.event_dispatcher import showHangar

class PremDashboardView(ViewImpl, SoundViewMixin):
    __slots__ = ()

    def __init__(self, layoutID):
        super(PremDashboardView, self).__init__(layoutID, ViewFlags.LOBBY_SUB_VIEW, PremDashboardViewModel)
        Waiting.show('loadPage')

    @property
    def viewModel(self):
        return super(PremDashboardView, self).getViewModel()

    def _initialize(self):
        super(PremDashboardView, self)._initialize()
        self._addSoundEvent()
        self.viewModel.onCloseAction += self.__onCloseAction
        self.viewModel.onInitialized += self.__onInitialized
        with self.viewModel.transaction() as model:
            model.setHeader(PremDashboardHeader())
            model.setPremiumCard(DashboardPremiumCard())
            model.setDoubleXPCard(PremDashboardDoubleExperienceCard())
            model.setPiggyBankCard(PremDashboardPiggyBankCard())
            model.setPremiumQuestsCard(PremDashboardQuestsCard())
            model.setMapsBlackListCard(PremDashboardMapsBlacklistCard())

    def _finalize(self):
        self.viewModel.onCloseAction -= self.__onCloseAction
        self.viewModel.onInitialized -= self.__onInitialized
        self._removeSoundEvent()

    def __onCloseAction(self):
        showHangar()

    def __onInitialized(self):
        Waiting.hide('loadPage')
