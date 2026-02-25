# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily_experience/daily_experience_view.py
import typing
from PlayerEvents import g_playerEvents
from constants import PREMIUM_TYPE, PremiumConfigs
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl, getWotPlusShopUrl
from gui.game_control.wot_plus.utils import getAdditionalXPPromoData
from gui.impl.gen.view_models.views.lobby.account_dashboard.daily_experience_view_model import DailyExperienceViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showWotPlusInfoPage, showShop, showTankPremiumAboutPage
from helpers import dependency
from renewable_subscription_common.schema import renewableSubscriptionsConfigSchema
from renewable_subscription_common.settings_constants import RS_TIER
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
if typing.TYPE_CHECKING:
    from gui.game_control.wot_plus_controller import WotPlusController

class DailyExperienceView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = DailyExperienceViewModel()
        super(DailyExperienceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyExperienceView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(DailyExperienceView, self)._initialize(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        wotPlusSettings = self.__wotPlusController.getSettingsStorage()
        serverSettings = self.__lobbyContext.getServerSettings()
        premiumBonusConfig = serverSettings.getAdditionalBonusConfig()
        hasPremium = any((self.__itemsCache.items.stats.isActivePremium(premiumType) for premiumType in PREMIUM_TYPE.AFFECTING_TYPES_SET))
        hasWotPlus = self.__wotPlusController.hasSubscription()
        isPremiumBonusEnabled = premiumBonusConfig.get('enabled', False)
        isWotPlusBonusEnabled = wotPlusSettings.isAdditionalXPBonusEnabled()
        premiumAdditionalCount = premiumBonusConfig.get('applyCount') if isPremiumBonusEnabled and hasPremium else 0
        wotPlusAdditionalCount = wotPlusSettings.getAdditionalXPBonusCount()
        usesLeft = 0
        if hasPremium and isPremiumBonusEnabled:
            usesLeft += self.__itemsCache.items.stats.applyAdditionalXPCount
        if hasWotPlus and isWotPlusBonusEnabled:
            usesLeft += self.__itemsCache.items.stats.applyAdditionalWoTPlusXPCount
        with self.viewModel.transaction() as model:
            model.setMultiplier(int(premiumBonusConfig.get('bonusFactor')))
            model.setLeftBonusCount(usesLeft)
            model.setTotalBonusCount(premiumAdditionalCount + wotPlusAdditionalCount)
            model.setWotPremiumMaxApplications(premiumBonusConfig.get('applyCount'))
            model.setWotPlusMaxApplications(getAdditionalXPPromoData())
            model.setIsWotPlusBonusEnabled(isWotPlusBonusEnabled)
            model.setIsWotPlus(hasWotPlus)
            model.setIsWotPremium(hasPremium)

    def _onPremiumNotify(self, *args):
        self.__updateViewModel()

    def _onStatsUpdated(self, *args):
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.onBackButtonClick, self.__onClose),
         (self.viewModel.onWotPremiumUpgradeButtonClick, self.__onWotPremiumUpgradeBtnClick),
         (self.viewModel.onWotPlusSubscribeButtonClick, self.__onWotPlusSubscribeBtnClick),
         (self.viewModel.onWotPremiumDetailsButtonClick, self.__onWotPremiumDetailsBtnClick),
         (self.viewModel.onWotPlusDetailsButtonClick, self.__onWotPlusDetailsBtnClick),
         (self.__gameSession.onPremiumNotify, self._onPremiumNotify),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.__wotPlusController.onDataChanged, self.__onWotPlusChange),
         (g_playerEvents.onConfigModelUpdated, self._onConfigModelUpdated))

    def _getCallbacks(self):
        return (('stats.applyAdditionalXPCount', self._onStatsUpdated), ('stats.applyAdditionalWoTPlusXPCount', self._onStatsUpdated))

    def __onServerSettingsChange(self, diff):
        if PremiumConfigs.DAILY_BONUS in diff:
            self.__updateViewModel()

    def _onConfigModelUpdated(self, gpKey):
        if renewableSubscriptionsConfigSchema.gpKey == gpKey:
            self.__updateViewModel()

    def __onWotPlusChange(self, data):
        if RS_TIER in data:
            self.__updateViewModel()

    def __onClose(self):
        self.destroyWindow()

    def __onWotPlusSubscribeBtnClick(self):
        showShop(getWotPlusShopUrl())

    def __onWotPremiumDetailsBtnClick(self):
        showTankPremiumAboutPage()

    def __onWotPremiumUpgradeBtnClick(self):
        showShop(getBuyPremiumUrl())

    def __onWotPlusDetailsBtnClick(self):
        showWotPlusInfoPage(WotPlusInfoPageSource.REWARD_SCREEN, useCustomSoundSpace=True)
