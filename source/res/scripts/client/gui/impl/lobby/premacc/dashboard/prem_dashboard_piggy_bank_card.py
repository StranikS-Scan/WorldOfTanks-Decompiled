# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/dashboard/prem_dashboard_piggy_bank_card.py
import logging
from constants import PremiumConfigs
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.premacc.dashboard.prem_dashboard_piggy_bank_card_model import PremDashboardPiggyBankCardModel
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.impl.lobby.premacc.piggybank_base import PiggyBankBaseView
from gui.shared.event_dispatcher import showPiggyBankView
_logger = logging.getLogger(__name__)

class PremDashboardPiggyBankCard(PiggyBankBaseView):

    def __init__(self, *args, **kwargs):
        super(PremDashboardPiggyBankCard, self).__init__(R.views.premDashboardPiggyBankCard(), ViewFlags.VIEW, PremDashboardPiggyBankCardModel)

    def onGoToPiggyView(self, args=None):
        if self._config.get('enabled', False):
            showPiggyBankView()

    def _initialize(self, *args, **kwargs):
        super(PremDashboardPiggyBankCard, self)._initialize(*args, **kwargs)
        self._updateIsAvailable()

    @replaceNoneKwargsModel
    def _updateIsAvailable(self, model=None):
        isAvailable = self._config.get('enabled', False)
        model.setIsAvailable(isAvailable)

    def _getIsTimerEnabled(self):
        isAvailable = self._config.get('enabled', False)
        result = super(PremDashboardPiggyBankCard, self)._getIsTimerEnabled()
        return result and isAvailable

    def _onServerSettingsChange(self, diff):
        super(PremDashboardPiggyBankCard, self)._onServerSettingsChange(diff)
        if PremiumConfigs.PIGGYBANK not in diff:
            return
        diffConfig = diff.get(PremiumConfigs.PIGGYBANK)
        if 'enabled' in diffConfig:
            self._updateIsAvailable()
            self._updateTimerStatus()

    def _addListeners(self):
        super(PremDashboardPiggyBankCard, self)._addListeners()
        self.viewModel.onGoToPiggyView += self.onGoToPiggyView

    def _removeListeners(self):
        super(PremDashboardPiggyBankCard, self)._removeListeners()
        self.viewModel.onGoToPiggyView -= self.onGoToPiggyView
