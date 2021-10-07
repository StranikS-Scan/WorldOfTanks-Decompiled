# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/piggy_bank_card/wot_plus_piggy_bank_card.py
import BigWorld
from constants import PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG, PREMIUM_TYPE
from frameworks.wulf import ViewSettings, ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.piggy_bank.piggy_bank_states import BankState
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.piggy_bank.wot_plus_piggy_bank_card_model import WotPlusPiggyBankCardModel
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showPiggyBankView
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class WotPlusPiggyBankCard(ViewImpl):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.premacc.dashboard.piggy_bank_cards.wot_plus_piggy_bank.WotPlusPiggyBankCard())
        settings.model = WotPlusPiggyBankCardModel()
        self._notifier = None
        self._premState = None
        self._wotPlusState = None
        self._wotPlusInfo = BigWorld.player().renewableSubscription
        super(WotPlusPiggyBankCard, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WotPlusPiggyBankCard, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WotPlusPiggyBankCard, self)._onLoading()
        self._addListeners()
        self._notifier = PeriodicNotifier(self._getDeltaTime, self._updateTimer, (time_utils.ONE_MINUTE,))
        self._isTimerEnabled = False
        self._premState = BankState.AVAILABLE
        self._wotPlusState = BankState.AVAILABLE
        with self.viewModel.transaction() as model:
            self._setMaxAmounts(model=model)
            self._setCurrentCredits(model=model)
            self._setCurrentGold(model=model)
            self._updatePremState(model=model)
            self._updateWotPlusState(model=model)
            self._updateTimer(model=model)

    def _finalize(self):
        self._notifier.stopNotification()
        self._notifier.clear()
        self._notifier = None
        self._removeListeners()
        super(WotPlusPiggyBankCard, self)._finalize()
        return

    @replaceNoneKwargsModel
    def _setMaxAmounts(self, model=None):
        serverSettings = self._lobbyContext.getServerSettings()
        maxAmount = serverSettings.getPiggyBankConfig().get('creditsThreshold', PiggyBankConstants.MAX_AMOUNT)
        maxAmountStr = self.gui.systemLocale.getNumberFormat(maxAmount)
        model.setCreditMaxAmount(maxAmountStr)
        maxAmount = serverSettings.getRenewableSubMaxGoldReserveCapacity()
        maxAmountStr = self.gui.systemLocale.getNumberFormat(maxAmount)
        model.setGoldMaxAmount(maxAmountStr)

    @replaceNoneKwargsModel
    def _setCurrentCredits(self, value=None, model=None):
        creditsValue = value or self._itemsCache.items.stats.piggyBank.get('credits', 0)
        creditsValueStr = self.gui.systemLocale.getNumberFormat(creditsValue)
        model.setCreditCurrentAmount(creditsValueStr)

    def _updateCredits(self, value=None):
        self._setCurrentCredits(value)

    @replaceNoneKwargsModel
    def _setCurrentGold(self, gold=None, model=None):
        goldValue = gold or self._itemsCache.items.stats.piggyBank.get('gold', 0)
        goldValueStr = self.gui.systemLocale.getNumberFormat(goldValue)
        model.setGoldCurrentAmount(goldValueStr)

    def _updateGold(self, gold=None):
        self._setCurrentGold(gold)

    @replaceNoneKwargsModel
    def _updatePremState(self, model=None):
        serverSettings = self._lobbyContext.getServerSettings()
        isEnabled = serverSettings.getPiggyBankConfig().get('enabled', False)
        hasPremium = self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        state = BankState.AVAILABLE
        if not isEnabled:
            state = BankState.DISABLE
        elif hasPremium:
            state = BankState.ACTIVE
        if self._premState != state:
            self._premState = state
            self._updateTimerStatus()
        model.setPremState(state.value)

    def _updatePrem(self, *args):
        self._updatePremState()

    @replaceNoneKwargsModel
    def _updateWotPlusState(self, model=None):
        serverSettings = self._lobbyContext.getServerSettings()
        isGoldEnabled = serverSettings.isRenewableSubGoldReserveEnabled()
        hasWotPlus = self._wotPlusInfo.isEnabled()
        state = BankState.AVAILABLE
        if not isGoldEnabled:
            state = BankState.DISABLE
        elif hasWotPlus:
            state = BankState.ACTIVE
        if self._wotPlusState != state:
            self._wotPlusState = state
            self._updateTimerStatus()
        model.setWotPlusState(state.value)

    @replaceNoneKwargsModel
    def _updateTimer(self, model=None):
        isTimerEnabled = self._getIsTimerEnabled()
        if not isTimerEnabled:
            return
        finishDeltatime = self._getDeltaTime()
        model.setTimeToOpen(finishDeltatime)

    def _getDeltaTime(self):
        serverSettings = self._lobbyContext.getServerSettings()
        config = serverSettings.getPiggyBankConfig()
        data = self._itemsCache.items.stats.piggyBank
        return getDeltaTimeHelper(config, data)

    def _getIsTimerEnabled(self):
        hasGold = self._itemsCache.items.stats.piggyBank.get('gold', 0)
        hasCredits = self._itemsCache.items.stats.piggyBank.get('credits', 0)
        return self._wotPlusState == BankState.ACTIVE or self._premState == BankState.ACTIVE or hasCredits or hasGold

    def _updateTimerStatus(self):
        isTimerEnabled = self._getIsTimerEnabled()
        if self._isTimerEnabled != isTimerEnabled:
            self._isTimerEnabled = isTimerEnabled
            if isTimerEnabled:
                self._notifier.startNotification()
                self._updateTimer()
            else:
                self._notifier.stopNotification()
        elif isTimerEnabled:
            self._notifier.startNotification()
            self._updateTimer()

    def _updateLastSmashTimestamp(self, *args):
        self._updateTimerStatus()

    def _onServerSettingsChange(self, diff):
        if self.viewStatus == ViewStatus.DESTROYED:
            return
        if PremiumConfigs.PIGGYBANK not in diff and RENEWABLE_SUBSCRIPTION_CONFIG not in diff:
            return
        diffConfigPiggy = diff.get(PremiumConfigs.PIGGYBANK)
        diffConfigGold = diff.get(RENEWABLE_SUBSCRIPTION_CONFIG)
        if 'creditsThreshold' in diffConfigPiggy or 'maxGoldReserveCapacity' in diffConfigGold:
            self._setMaxAmounts()
        if 'enabled' in diffConfigPiggy:
            self._updatePremState()
        if 'enableGoldReserve' in diffConfigGold:
            self._updateWotPlusState()
        if 'cycleLength' in diffConfigPiggy or 'cycleStartTime' in diffConfigPiggy:
            self._updateTimerStatus()

    def _onWotPlusDataChanged(self, diff):
        if 'isEnabled' in diff:
            self._updateWotPlusState()

    def __onCardClick(self):
        showPiggyBankView()

    def _addListeners(self):
        self.viewModel.onCardClick += self.__onCardClick
        g_clientUpdateManager.addCallbacks({PiggyBankConstants.PIGGY_BANK_CREDITS: self._updateCredits,
         PiggyBankConstants.PIGGY_BANK_GOLD: self._updateGold,
         PiggyBankConstants.PIGGY_BANK_SMASH_TIMESTAMP_CREDITS: self._updateLastSmashTimestamp,
         PiggyBankConstants.PIGGY_BANK_SMASH_TIMESTAMP_GOLD: self._updateLastSmashTimestamp})
        self._gameSession.onPremiumNotify += self._updatePrem
        self._wotPlusInfo.onRenewableSubscriptionDataChanged += self._onWotPlusDataChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def _removeListeners(self):
        self.viewModel.onCardClick -= self.__onCardClick
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._gameSession.onPremiumNotify -= self._updatePrem
        self._wotPlusInfo.onRenewableSubscriptionDataChanged -= self._onWotPlusDataChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
