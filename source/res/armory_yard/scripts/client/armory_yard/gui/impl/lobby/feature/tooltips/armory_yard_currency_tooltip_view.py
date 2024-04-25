# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/armory_yard_currency_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.armory_yard_currency_tooltip_view_model import ArmoryYardCurrencyTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController

class ArmoryYardCurrencyTooltipView(ViewImpl):
    __slots__ = ()
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView())
        settings.model = ArmoryYardCurrencyTooltipViewModel()
        super(ArmoryYardCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardCurrencyTooltipView, self)._onLoading()
        if not self.__armoryYardCtrl.isEnabled():
            return
        with self.viewModel.transaction() as tx:
            seasonStart, seasonEnd = self.__armoryYardCtrl.getSeasonInterval()
            totalTokens, receivedTokens = self.__armoryYardCtrl.getTokensInfo()
            tx.setReceivedTokens(receivedTokens)
            tx.setTotalTokens(totalTokens)
            tx.setQuestsForToken(self.__armoryYardCtrl.totalTokensInChapter(self.__armoryYardCtrl.serverSettings.getCurrentSeason().getAllCycles().values()[0].ID))
            tx.setStartTimestamp(seasonStart)
            tx.setEndTimestamp(seasonEnd)
