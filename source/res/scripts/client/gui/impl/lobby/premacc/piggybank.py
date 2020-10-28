# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/piggybank.py
import logging
import time
from math import ceil
from constants import PremiumConfigs
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.impl.gen import R
from gui.impl.lobby.premacc.piggybank_base import PiggyBankBaseView, PiggyBankConstants
from gui.impl.lobby.premacc.premacc_helpers import toPercents
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.gen.view_models.views.lobby.premacc.piggybank_model import PiggybankModel
from frameworks.wulf import ViewFlags, ViewSettings
from gui.shared.event_dispatcher import showTankPremiumAboutPage, showShop
from gui.shared.utils.scheduled_notifications import _Notifier
from helpers import time_utils
_logger = logging.getLogger(__name__)

def _getBackBtnLabel():
    return R.strings.premacc.piggyBank.backBtnAddLabel()


class TimerNotifier(_Notifier):

    def _getNextNotificationDelta(self, delta):
        if delta <= time_utils.ONE_DAY:
            period = time_utils.ONE_MINUTE
        else:
            period = time_utils.ONE_HOUR
        td = delta % period or period
        _logger.debug('_getNextNotificationDelta: %s ', time.strftime('%H:%M:%S', time.gmtime(td)))
        return td


class PiggyBankView(PiggyBankBaseView):
    _PERIOD = 7 * time_utils.ONE_DAY
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.premacc.piggybank.Piggybank()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = PiggybankModel()
        super(PiggyBankView, self).__init__(settings)

    def onPremAccProlong(self, _=None):
        showShop(getBuyPremiumUrl())

    def onBackBtnClicked(self, _=None):
        self.destroyWindow()

    def onGoToContentPage(self):
        showTankPremiumAboutPage()

    def _createNotifier(self):
        return TimerNotifier(self._getDeltaTime, self._updateTimer)

    def _initialize(self, *args, **kwargs):
        super(PiggyBankView, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setBackBtnLabel(_getBackBtnLabel())
            self._updatePercentDiscount(model=model)
            self._updateIsPremUsed(model=model)
            self._updatePeriodInDays(model=model)
            self._updatePiggyIsFull(model=model)

    @replaceNoneKwargsModel
    def _updateIsPremUsed(self, credits_=None, model=None):
        credits_ = credits_ or self._data.get('credits', 0)
        isPremium = self._isTankPremiumActive()
        isPremUsed = isPremium or credits_ > 0
        model.setIsPremUsed(isPremUsed)

    @replaceNoneKwargsModel
    def _updatePeriodInDays(self, model=None):
        period = self._config.get('cycleLength', self._PERIOD)
        periodInDays = ceil(period / time_utils.ONE_DAY)
        model.setPeriodInDays(periodInDays)

    @replaceNoneKwargsModel
    def _updatePercentDiscount(self, model=None):
        percent = toPercents(self._config.get('multiplier', 0))
        model.setPercentDiscount(percent)

    @replaceNoneKwargsModel
    def _updatePiggyIsFull(self, credits_=None, model=None):
        creditsValue = credits_ or self._data.get('credits', 0)
        maxAmount = self._config.get('threshold', PiggyBankConstants.MAX_AMOUNT)
        model.setPiggyIsFull(creditsValue >= maxAmount)

    def _updateCredits(self, credits_=None):
        super(PiggyBankView, self)._updateCredits(credits_)
        self._updatePiggyIsFull(credits_)
        self._updateIsPremUsed(credits_)

    def _updatePrem(self, *args):
        super(PiggyBankView, self)._updatePrem()
        self._updateIsPremUsed()

    def _onServerSettingsChange(self, diff):
        super(PiggyBankView, self)._onServerSettingsChange(diff)
        if PremiumConfigs.PIGGYBANK not in diff:
            return
        diffConfig = diff.get(PremiumConfigs.PIGGYBANK)
        if 'threshold' in diffConfig:
            self._updatePiggyIsFull()
        if 'cycleLength' in diffConfig:
            self._updatePeriodInDays()
        if 'multiplier' in diffConfig:
            self._updatePercentDiscount()

    def _addListeners(self):
        super(PiggyBankView, self)._addListeners()
        self.viewModel.onPremAccProlong += self.onPremAccProlong
        self.viewModel.onBackBtnClicked += self.onBackBtnClicked
        self.viewModel.onGoToContentPage += self.onGoToContentPage

    def _removeListeners(self):
        super(PiggyBankView, self)._removeListeners()
        self.viewModel.onPremAccProlong -= self.onPremAccProlong
        self.viewModel.onBackBtnClicked -= self.onBackBtnClicked
        self.viewModel.onGoToContentPage -= self.onGoToContentPage
