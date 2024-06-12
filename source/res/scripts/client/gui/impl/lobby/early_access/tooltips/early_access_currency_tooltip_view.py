# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/tooltips/early_access_currency_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_currency_tooltip_view_model import EarlyAccessCurrencyTooltipViewModel

class EarlyAccessCurrencyTooltipView(ViewImpl):
    __slots__ = ()
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessCurrencyTooltipView())
        settings.model = EarlyAccessCurrencyTooltipViewModel()
        super(EarlyAccessCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessCurrencyTooltipView, self)._onLoading()
        if not self.__earlyAccessCtrl.isEnabled():
            return
        with self.viewModel.transaction() as tx:
            startProgressionTime, endProgressionTime = self.__earlyAccessCtrl.getProgressionTimes()
            totalTokens = self.__earlyAccessCtrl.getTotalVehiclesPrice()
            receivedTokens = self.__earlyAccessCtrl.getReceivedTokensCount()
            tx.setReceivedTokens(receivedTokens)
            tx.setTotalTokens(totalTokens)
            tx.setStartTimestamp(startProgressionTime)
            tx.setEndTimestamp(endProgressionTime)
