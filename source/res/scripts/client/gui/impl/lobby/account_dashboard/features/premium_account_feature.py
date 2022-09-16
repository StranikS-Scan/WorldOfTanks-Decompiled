# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/premium_account_feature.py
import typing
from constants import PREMIUM_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showShop
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_dashboard.premium_account_model import PremiumAccountModel

class PremiumAccountFeature(FeatureItem):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)

    def initialize(self, *args, **kwargs):
        super(PremiumAccountFeature, self).initialize(*args, **kwargs)
        self.__startListening()

    def finalize(self):
        self.__stopListening()
        super(PremiumAccountFeature, self).finalize()

    def _fillModel(self, model):
        self.__setPremBonusValues(model=model)
        self.__updatePremState(model=model)

    def __startListening(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChange
        self.__gameSession.onPremiumNotify += self.__onPremiumStatusChanged
        g_clientUpdateManager.addCallbacks({'stats.dummySessionStats': self.__onStatsChanged,
         'premium': self.__onPremiumStatusChanged})
        self._viewModel.premiumAccount.onClick += self.__onClick

    def __stopListening(self):
        self._viewModel.premiumAccount.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChange
        self.__gameSession.onPremiumNotify -= self.__onPremiumStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onSettingsChange(self, diff):
        if not {'tankPremiumBonus', 'premSquad_config'} & set(diff.keys()):
            return
        self.__setPremBonusValues()

    def __onStatsChanged(self, *_):
        self.__updatePremState()

    def __onPremiumStatusChanged(self, *_):
        self.__updatePremState()

    @replaceNoneKwargsModel
    def __setPremBonusValues(self, model=None):
        submodel = model.premiumAccount
        settings = self.__lobbyContext.getServerSettings()
        submodel.setXpBonus(self.__toPercents(settings.getPremiumXPBonus()))
        submodel.setCreditBonus(self.__toPercents(settings.getPremiumCreditsBonus()))
        submodel.setPlatoonBonus(self.__toPercents(settings.squadPremiumBonus.ownCredits))

    @replaceNoneKwargsModel
    def __updatePremState(self, model=None):
        submodel = model.premiumAccount
        stats = self.__getStatsRequester().dummySessionStats
        base = stats.get('base', {})
        premium = stats.get('premium', {})
        submodel.setWotPremiumSecondsLeft(self.__getTimeLeft(PREMIUM_TYPE.PLUS))
        submodel.setPremiumAccountCredits(premium.get('credits', 0))
        submodel.setPremiumAccountXp(premium.get('xp', 0))
        submodel.setWgPremiumSecondsLeft(self.__getTimeLeft(PREMIUM_TYPE.BASIC))
        submodel.setStandardAccountCredits(base.get('credits', 0))
        submodel.setStandardAccountXp(base.get('xp', 0))

    def __getTimeLeft(self, premType):
        expiryTime = self.__getStatsRequester().premiumInfo.get(premType, {}).get('expiryTime', 0)
        serverTime = time_utils.getCurrentLocalServerTimestamp()
        return -1 if expiryTime == 0 or expiryTime <= serverTime else expiryTime - serverTime

    def __getStatsRequester(self):
        return self.__itemsCache.items.stats

    @staticmethod
    def __toPercents(value):
        return int(round(value * 100))

    @staticmethod
    def __onClick():
        showShop(getBuyPremiumUrl())
