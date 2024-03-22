# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/bonus_xp_feature.py
import typing
from constants import PremiumConfigs, PREMIUM_TYPE, RENEWABLE_SUBSCRIPTION_CONFIG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showDailyExpPageView
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_dashboard.bonus_xp_model import BonusXpModel

class BonusXPFeature(FeatureItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def initialize(self, *args, **kwargs):
        super(BonusXPFeature, self).initialize(*args, **kwargs)
        self.__startListening()

    def finalize(self):
        self.__stopListening()
        super(BonusXPFeature, self).finalize()

    def _fillModel(self, model):
        self.__updateModel(model=model)

    def __startListening(self):
        self.__gameSession.onPremiumNotify += self.__onUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.__wotPlusController.onDataChanged += self._onWotPlusChange
        g_clientUpdateManager.addCallbacks({'stats.applyAdditionalXPCount': self.__onUpdate,
         'stats.applyAdditionalWoTPlusXPCount': self.__onUpdate})
        self._viewModel.bonusXp.onClick += self.__onClick

    def __stopListening(self):
        self._viewModel.bonusXp.onClick -= self.__onClick
        self.__gameSession.onPremiumNotify -= self.__onUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.__wotPlusController.onDataChanged -= self._onWotPlusChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onUpdate(self, *_):
        self.__updateModel()

    def _onServerSettingsChange(self, diff):
        if PremiumConfigs.DAILY_BONUS in diff or RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__updateModel()

    def _onWotPlusChange(self, data):
        if 'isEnabled' in data:
            self.__updateModel()

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        submodel = model.bonusXp
        serverSettings = self.__lobbyContext.getServerSettings()
        premiumBonusConfig = serverSettings.getAdditionalBonusConfig()
        isPremiumBonusEnabled = premiumBonusConfig.get('enabled', False)
        isWotPlusBonusEnabled = serverSettings.isAdditionalWoTPlusEnabled()
        hasPremium = any((self.__itemsCache.items.stats.isActivePremium(premiumType) for premiumType in PREMIUM_TYPE.AFFECTING_TYPES_SET))
        hasWotPlus = self.__wotPlusController.isEnabled()
        premiumAdditionalCount = premiumBonusConfig.get('applyCount') if isPremiumBonusEnabled and hasPremium else 0
        wotPlusAdditionalCount = serverSettings.getAdditionalWoTPlusXPCount() if hasWotPlus and isWotPlusBonusEnabled else 0
        submodel.setIsEnabled(isPremiumBonusEnabled or isWotPlusBonusEnabled)
        submodel.setMultiplier(int(premiumBonusConfig.get('bonusFactor')))
        usesLeft = 0
        if hasPremium and isPremiumBonusEnabled:
            usesLeft += self.__itemsCache.items.stats.applyAdditionalXPCount
        if hasWotPlus and isWotPlusBonusEnabled:
            usesLeft += self.__itemsCache.items.stats.applyAdditionalWoTPlusXPCount
        submodel.setUsesLeft(usesLeft)
        submodel.setTotalUses(premiumAdditionalCount + wotPlusAdditionalCount)
        submodel.setIsWotPlusBonusEnabled(isWotPlusBonusEnabled)
        submodel.setIsWotPlus(hasWotPlus)
        submodel.setIsWotPremium(hasPremium)
        submodel.setDailyAppliedXP(self.__itemsCache.items.stats.dailyAppliedAdditionalXP)

    def __onClick(self):
        showDailyExpPageView()
