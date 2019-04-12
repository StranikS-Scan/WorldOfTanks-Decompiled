# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/dashboard_premium_card.py
import BigWorld
from constants import PREMIUM_TYPE
from frameworks.wulf import ViewFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.card_prem_info_model import CardPremInfoModel
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.dashboard_premium_card_model import DashboardPremiumCardModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showPremiumDialog
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class DashboardPremiumCard(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self, *args, **kwargs):
        super(DashboardPremiumCard, self).__init__(R.views.dashboardPremiumCard(), ViewFlags.COMPONENT, DashboardPremiumCardModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(DashboardPremiumCard, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(DashboardPremiumCard, self)._initialize(*args, **kwargs)
        self.__startListening()
        with self.viewModel.transaction() as model:
            self.__setPremBonusValues(model)
            self.__updatePremState(model)
            _StatsGroupBuilder(self.__getStatsRequester().dummySessionStats).setStats(model)

    def _finalize(self):
        super(DashboardPremiumCard, self)._finalize()
        self.__stopListening()

    def __startListening(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChange
        self.__gameSession.onPremiumNotify += self.__onPremiumStatusChanged
        g_clientUpdateManager.addCallbacks({'stats.dummySessionStats': self.__onStatsChanged,
         'premium': self.__onPremiumStatusChanged})
        self.viewModel.onClick += self.__onClick

    def __stopListening(self):
        self.viewModel.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChange
        self.__gameSession.onPremiumNotify -= self.__onPremiumStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onSettingsChange(self, diff):
        if not {'tankPremiumBonus', 'premSquad_config'} & set(diff.keys()):
            return
        self.__setPremBonusValues(self.viewModel)

    def __onStatsChanged(self, _):
        _StatsGroupBuilder(stats=self.__getStatsRequester().dummySessionStats).setStats(self.viewModel)

    def __onPremiumStatusChanged(self, *_):
        self.__updatePremState(self.viewModel)

    def __setPremBonusValues(self, model):
        settings = self.__lobbyContext.getServerSettings()
        model.setExperienceBonus(_toPercents(settings.getPremiumXPBonus()))
        model.setCreditsBonus(_toPercents(settings.getPremiumCreditsBonus()))
        model.setSquadBonus(_toPercents(settings.squadPremiumBonus.ownCredits))

    def __updatePremState(self, model):
        model.setIsBasePremiumActive(self.__getStatsRequester().isActivePremium(PREMIUM_TYPE.BASIC))
        model.setBasePremTimeLeft(self.__getTimeLeft(PREMIUM_TYPE.BASIC))
        model.setIsTankPremiumActive(self.__getStatsRequester().isActivePremium(PREMIUM_TYPE.PLUS))
        model.setTankPremTimeLeft(self.__getTimeLeft(PREMIUM_TYPE.PLUS))
        model.setIsNotPremium(not self.__getStatsRequester().isPremium)

    def __getTimeLeft(self, premType):
        expiryTime = self.__getStatsRequester().premiumInfo.get(premType, {}).get('expiryTime', 0)
        serverTime = time_utils.getCurrentLocalServerTimestamp()
        return -1 if expiryTime == 0 or expiryTime <= serverTime else expiryTime - serverTime

    def __getStatsRequester(self):
        return self.__itemsCache.items.stats

    @staticmethod
    def __onClick():
        showPremiumDialog()


class _StatsGroupBuilder(object):

    def __init__(self, stats):
        self.__stats = stats

    def setStats(self, model):
        self.__setStatsGroup(model.withoutPremium, self.__stats.get('base', {}))
        self.__setStatsGroup(model.withPremium, self.__stats.get('premium', {}))

    def __setStatsGroup(self, statsModel, sessionData):
        items = statsModel.getItems()
        items.clear()
        items.addViewModel(self.__buildPremStatsModel(sessionData.get('credits', 0), 'CreditsIcon_2', isCredits=True))
        items.addViewModel(self.__buildPremStatsModel(sessionData.get('xp', 0), 'XpIcon_1'))
        items.invalidate()

    @staticmethod
    def __buildPremStatsModel(value, icon, isCredits=False):
        result = CardPremInfoModel()
        result.setValue(BigWorld.wg_getIntegralFormat(value))
        result.setIcon(R.images.gui.maps.icons.library.dyn(icon)())
        result.setIsCredits(isCredits)
        return result


def _toPercents(value):
    return int(value * 100)
