# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/black_market/black_market_entry_point_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.black_market.banner.black_market_view_model import BlackMarketViewModel, StatusEnum, PhaseEnum
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from account_helpers.AccountSettings import BlackMarket, AccountSettings
from gui.server_events.events_dispatcher import showMissionsMarathon
from skeletons.gui.game_control import ICollectiveGoalEntryPointController, IMarathonEventsController, IBlackMarketController
from helpers import dependency, time_utils
_logger = logging.getLogger(__name__)

class BlackMarketEntryPointView(ViewImpl):
    __blackMarket = dependency.descriptor(IBlackMarketController)
    __collectiveGoalEntryPointController = dependency.descriptor(ICollectiveGoalEntryPointController)
    __marathonController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ('__isSingle',)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.black_market.banner.BlackMarketBannerView())
        settings.flags = flags
        settings.model = BlackMarketViewModel()
        super(BlackMarketEntryPointView, self).__init__(settings)
        self.__isSingle = True

    @property
    def viewModel(self):
        return super(BlackMarketEntryPointView, self).getViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BlackMarketEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.toBlackMarketEvent, self.__onClick), (self.__blackMarket.onStateChanged, self.__updateViewModel), (self.__blackMarket.onBlackMarketUpdated, self.__updateViewModel))

    def __onClick(self):
        AccountSettings.setBlackMarket(BlackMarket.BLACK_MARKET_ENTRY_CLICKED, True)
        marathonPrefix = self.__collectiveGoalEntryPointController.getMarathonPrefix()
        if self.__marathonController.getMarathon(marathonPrefix) is not None:
            showMissionsMarathon(marathonPrefix)
        else:
            _logger.error("Marathon %s isn't found. Check collective goal config", marathonPrefix)
        return

    def __getStatus(self):
        if self.__blackMarket.isEnabled() and not self.__blackMarket.isStarted():
            return StatusEnum.ANNOUNCE
        return StatusEnum.ACTIVE if self.__blackMarket.isEnabled() and not self.__blackMarket.isPaused() else StatusEnum.DISABLED

    def __getPhase(self):
        return PhaseEnum.LOOTBOX if self.__blackMarket.isSpecial() else PhaseEnum.SPECIAL

    def __getTimer(self):
        return self.__blackMarket.getStartTime() - time_utils.getServerUTCTime() if not self.__blackMarket.isStarted() else self.__blackMarket.getFinishTime() - time_utils.getServerUTCTime()

    def __isNewPhase(self):
        lastSeenPhase = AccountSettings.getBlackMarket(BlackMarket.BLACK_MARKET_LAST_PHASE_SEEN)
        currentPhase = self.__blackMarket.getLastOfferStartDate()
        if lastSeenPhase != currentPhase:
            AccountSettings.setBlackMarket(BlackMarket.BLACK_MARKET_ENTRY_CLICKED, False)
            AccountSettings.setBlackMarket(BlackMarket.BLACK_MARKET_LAST_PHASE_SEEN, currentPhase)

    def __updateViewModel(self):
        self.__isNewPhase()
        with self.viewModel.transaction() as tx:
            tx.setIsAloneBanner(self.__isSingle)
            tx.setStatus(self.__getStatus())
            tx.setEventPhase(self.__getPhase())
            tx.setTimer(self.__getTimer())
            tx.setIsNew(not AccountSettings.getBlackMarket(BlackMarket.BLACK_MARKET_ENTRY_CLICKED))
