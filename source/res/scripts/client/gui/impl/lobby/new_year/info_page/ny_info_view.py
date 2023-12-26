# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/info_page/ny_info_view.py
from constants import CURRENT_REALM
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.shared.event_dispatcher import showLootBoxBuyWindow, showAboutEvent
from helpers import getLanguageCode, dependency
from new_year.ny_level_helper import getNYGeneralConfig
from ny_common.settings import NYLootBoxConsts
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.ny.loggers import NyInfoViewLogger

class NyInfoView(NyHistoryPresenter):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyInfoView, self).initialize()
        source = self.__lobbyContext.getServerSettings().getLootBoxShop().get(NYLootBoxConsts.SOURCE)
        generalConfig = getNYGeneralConfig()
        with self.viewModel.transaction() as model:
            model.setEventStartDate(generalConfig.getEventStartTime())
            model.setEventEndDate(generalConfig.getEventEndTime())
            model.setIsExternalBuy(source == NYLootBoxConsts.EXTERNAL)
            model.region.setRealm(CURRENT_REALM)
            model.region.setLanguage(getLanguageCode())

    def finalize(self):
        NyInfoViewLogger().onViewClosed()
        super(NyInfoView, self).finalize()

    def _getEvents(self):
        events = super(NyInfoView, self)._getEvents()
        return events + ((self.viewModel.videoCover.onClick, self.__onPlayVideo), (self.viewModel.onShowAboutEvent, self.__onShowAboutEvent), (self.viewModel.onShowRewardKitBuyWindow, self.__onShowRewardKitBuyWindow))

    def __onShowAboutEvent(self):
        showAboutEvent()

    def __onPlayVideo(self):
        showInfoVideo()

    def __onShowRewardKitBuyWindow(self):
        showLootBoxBuyWindow()
