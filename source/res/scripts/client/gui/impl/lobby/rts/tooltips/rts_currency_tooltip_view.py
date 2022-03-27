# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/tooltips/rts_currency_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import CurrencyTypeEnum
from gui.impl.gen.view_models.views.lobby.rts.sub_mode_selector_view.strategist_currency_tooltip_model import StrategistCurrencyTooltipModel
from gui.impl.lobby.rts.model_helpers import CURRENCY_TYPE_TO_ARENA_TYPE
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController

class RTSCurrencyTooltipView(ViewImpl):
    __slots__ = ('_currencyType',)
    _rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, contentID, currencyType):
        super(RTSCurrencyTooltipView, self).__init__(ViewSettings(contentID, model=StrategistCurrencyTooltipModel()))
        self._currencyType = currencyType

    @property
    def viewModel(self):
        return super(RTSCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        arenaType = CURRENCY_TYPE_TO_ARENA_TYPE[self._currencyType]
        resource = R.strings.rts_battles.tooltip.strategistCurrency.dyn(self._currencyType.value)
        with self.viewModel.transaction() as model:
            model.setDescription(backport.text(resource.description()))
            model.setInstructions(backport.text(resource.instructions()))
            conversionRate = self._rtsController.getSettings().currencyAmountToBattle(arenaType, ignoreWarmup=True)
            exchangeText = backport.text(resource.exchangeText(), conversionRate=conversionRate)
            model.setExchangeText(exchangeText)
            currencyModel = model.currency
            currencyModel.setCurrencyValue(self._rtsController.getCurrency(arenaType))
            currencyModel.setCurrencyType(self._currencyType)
