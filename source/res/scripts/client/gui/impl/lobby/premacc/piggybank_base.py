# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/piggybank_base.py
import logging
from constants import PREMIUM_TYPE, PremiumConfigs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.lobby.premacc.premacc_helpers import PiggyBankConstants, getDeltaTimeHelper
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class PiggyBankBaseView(ViewImpl, SoundViewMixin):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('_config', '_data', '_notifier', '_isTimerEnabled')

    def __init__(self, settings):
        super(PiggyBankBaseView, self).__init__(settings)
        self._config = None
        self._data = None
        self._notifier = None
        self._isTimerEnabled = False
        return

    @property
    def viewModel(self):
        return super(PiggyBankBaseView, self).getViewModel()

    def getNotifier(self):
        return self._notifier

    def _createNotifier(self):
        return PeriodicNotifier(self._getDeltaTime, self._updateTimer, (time_utils.ONE_MINUTE,))

    def _getIsTimerEnabled(self):
        isPremium = self._isTankPremiumActive()
        credits_ = self._data.get('credits', 0)
        correctTime = self._getDeltaTime() > 0
        return isPremium or credits_ > 0 and correctTime

    def _initialize(self, *args, **kwargs):
        super(PiggyBankBaseView, self)._initialize(*args, **kwargs)
        self._addSoundEvent()
        self._addListeners()
        self._config = self._lobbyContext.getServerSettings().getPiggyBankConfig()
        self._data = self._itemsCache.items.stats.piggyBank
        self._notifier = self._createNotifier()
        with self.getViewModel().transaction() as model:
            self._updateIsTankPremiumActive(model=model)
            self._updateMaxAmount(model=model)
            self._updateCurrentAmount(model=model)
        self._updateTimerStatus()

    def _finalize(self):
        self._removeListeners()
        self._config = None
        self._data = None
        self._notifier.stopNotification()
        self._notifier.clear()
        self._notifier = None
        self._removeSoundEvent()
        super(PiggyBankBaseView, self)._finalize()
        return

    def _getDeltaTime(self):
        return 0 if not self._config or not self._data else getDeltaTimeHelper(self._config, self._data)

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

    @replaceNoneKwargsModel
    def _updateMaxAmount(self, model=None):
        maxAmount = self._config.get('creditsThreshold', PiggyBankConstants.MAX_AMOUNT)
        maxAmountStr = self.gui.systemLocale.getNumberFormat(maxAmount)
        model.setMaxAmount(maxAmount)
        model.setMaxAmountStr(maxAmountStr)

    @replaceNoneKwargsModel
    def _updateCurrentAmount(self, credits_=None, model=None):
        creditsValue = credits_ or self._data.get('credits', 0)
        creditsValueStr = self.gui.systemLocale.getNumberFormat(creditsValue)
        model.setCurrentAmount(creditsValue)
        model.setCurrentAmountStr(creditsValueStr)

    @replaceNoneKwargsModel
    def _updateTimer(self, model=None):
        isTimerEnabled = self._getIsTimerEnabled()
        if not isTimerEnabled:
            return
        _logger.info('_updateTimer')
        finishDeltatime = self._getDeltaTime()
        model.setTimeleft(finishDeltatime)

    @replaceNoneKwargsModel
    def _updateIsTankPremiumActive(self, model=None):
        isPremium = self._isTankPremiumActive()
        model.setIsTankPremiumActive(isPremium)

    def _updateCredits(self, credits_=None):
        self._updateCurrentAmount(credits_)
        self._updateTimerStatus()

    def _updatePrem(self, *args):
        self._updateIsTankPremiumActive()
        self._updateTimerStatus()

    def _updateLastSmashTimestamp(self, _):
        self._updateTimerStatus()

    def _onPiggyBankChanged(self, piggyBank):
        self._data.update(piggyBank)

    def _onServerSettingsChange(self, diff):
        if PremiumConfigs.PIGGYBANK not in diff:
            return
        self._config = self._lobbyContext.getServerSettings().getPiggyBankConfig()
        diffConfig = diff.get(PremiumConfigs.PIGGYBANK)
        if 'creditsThreshold' in diffConfig:
            self._updateMaxAmount()
        elif 'cycleLength' in diffConfig or 'cycleStartTime' in diffConfig:
            self._updateTimerStatus()

    def _addListeners(self):
        g_clientUpdateManager.addCallbacks({PiggyBankConstants.PIGGY_BANK: self._onPiggyBankChanged,
         PiggyBankConstants.PIGGY_BANK_CREDITS: self._updateCredits,
         PiggyBankConstants.PIGGY_BANK_SMASH_TIMESTAMP_CREDITS: self._updateLastSmashTimestamp})
        self._gameSession.onPremiumNotify += self._updatePrem
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._gameSession.onPremiumNotify -= self._updatePrem
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange

    def _isTankPremiumActive(self):
        return self._itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
