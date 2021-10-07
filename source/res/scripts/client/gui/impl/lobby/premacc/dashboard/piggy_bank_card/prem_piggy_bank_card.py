# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/piggy_bank_card/prem_piggy_bank_card.py
import logging
from constants import PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewStatus
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.piggy_bank.prem_piggy_bank_card_model import PremPiggyBankCardModel
from gui.impl.lobby.premacc.piggybank_base import PiggyBankBaseView
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showPiggyBankView
_logger = logging.getLogger(__name__)

class PremPiggyBankCard(PiggyBankBaseView):

    def __init__(self, layoutID=R.views.lobby.premacc.dashboard.piggy_bank_cards.prem_piggy_bank.PremPiggyBankCard()):
        settings = ViewSettings(layoutID)
        settings.model = PremPiggyBankCardModel()
        self._serverSettings = self._lobbyContext.getServerSettings()
        super(PremPiggyBankCard, self).__init__(settings)

    def onGoToPiggyView(self, args=None):
        if self._config.get('enabled', False):
            showPiggyBankView()

    def _initialize(self, *args, **kwargs):
        super(PremPiggyBankCard, self)._initialize(*args, **kwargs)
        self._updateIsAvailable()
        self._updateIsGoldReserveEnabled()

    @replaceNoneKwargsModel
    def _updateIsAvailable(self, model=None):
        isAvailable = self._config.get('enabled', False)
        model.setIsAvailable(isAvailable)

    @replaceNoneKwargsModel
    def _updateIsGoldReserveEnabled(self, model=None):
        model.setIsGoldReserveAvailable(self._serverSettings.isRenewableSubGoldReserveEnabled())

    def _getIsTimerEnabled(self):
        isAvailable = self._config.get('enabled', False)
        result = super(PremPiggyBankCard, self)._getIsTimerEnabled()
        return result and isAvailable

    def _onServerSettingsChange(self, diff):
        if self.viewStatus == ViewStatus.DESTROYED:
            return
        super(PremPiggyBankCard, self)._onServerSettingsChange(diff)
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self._updateIsGoldReserveEnabled()
        if PremiumConfigs.PIGGYBANK in diff:
            if 'enabled' in diff.get(PremiumConfigs.PIGGYBANK):
                self._updateIsAvailable()
                self._updateTimerStatus()

    def _addListeners(self):
        super(PremPiggyBankCard, self)._addListeners()
        self.viewModel.onGoToPiggyView += self.onGoToPiggyView

    def _removeListeners(self):
        super(PremPiggyBankCard, self)._removeListeners()
        self.viewModel.onGoToPiggyView -= self.onGoToPiggyView
