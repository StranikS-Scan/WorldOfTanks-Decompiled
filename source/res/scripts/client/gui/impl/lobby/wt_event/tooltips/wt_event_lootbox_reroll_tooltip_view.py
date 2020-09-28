# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_lootbox_reroll_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_lootbox_reroll_view_model import WtEventLootboxRerollViewModel
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_helpers import fillLootBoxRewards
from helpers import dependency
from skeletons.gui.game_control import IEventLootBoxesController

class WtEventLootboxRerollTooltipView(ViewImpl):
    __lootBoxesController = dependency.descriptor(IEventLootBoxesController)
    __slots__ = ('__boxType', '__box')

    def __init__(self, boxType):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventLootboxOpenRerollTooltipView())
        settings.model = WtEventLootboxRerollViewModel()
        self.__boxType = boxType
        self.__box = self.__lootBoxesController.getOwnedLootBoxByType(self.__boxType)
        super(WtEventLootboxRerollTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventLootboxRerollTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventLootboxRerollTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillLootBoxRewards(model, self.__boxType, False)
            maxReRolls = self.__box.getReRollCount()
            model.setMaxReRolls(maxReRolls)
            reRolls = model.getReRolls()
            for reRollCount in range(1, maxReRolls + 1):
                currencyModel = CurrencyModel()
                currencyType, price = self.__box.getReRollPrice(reRolledAttempts=reRollCount)
                currencyModel.setAmount(price)
                currencyModel.setType(currencyType)
                reRolls.addViewModel(currencyModel)

            reRolls.invalidate()
