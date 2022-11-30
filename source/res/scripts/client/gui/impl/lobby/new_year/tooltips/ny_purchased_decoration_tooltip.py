# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_purchased_decoration_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_purchased_decoration_tooltip_model import NyPurchasedDecorationTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from helpers import time_utils
from new_year.ny_buy_toy_helper import getToyPrice
from new_year.ny_level_helper import getNYGeneralConfig
from new_year.ny_toy_info import NewYearCurrentToyInfo

class NyPurchasedDecorationTooltip(ViewImpl):

    def __init__(self, toyID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyPurchasedDecorationTooltip())
        settings.model = NyPurchasedDecorationTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyPurchasedDecorationTooltip, self).__init__(settings)
        self.__toyID = int(toyID)

    @property
    def viewModel(self):
        return super(NyPurchasedDecorationTooltip, self).getViewModel()

    def _initialize(self, state, *args, **kwargs):
        toy = NewYearCurrentToyInfo(self.__toyID)
        timeTillEndEvent = int(getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime())
        with self.viewModel.transaction() as model:
            model.setName(toy.getName())
            model.setType(toy.getToyType())
            model.setIcon(toy.getIcon(size='large'))
            model.setDescription(toy.getDesc())
            model.setTimeTill(timeTillEndEvent)
            model.setRentPrice(getToyPrice(self.__toyID).get(Currency.GOLD, 0))
            model.setState(state)
