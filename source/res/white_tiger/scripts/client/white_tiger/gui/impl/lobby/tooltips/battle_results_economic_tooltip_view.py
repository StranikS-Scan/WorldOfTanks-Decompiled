# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/battle_results_economic_tooltip_view.py
from frameworks.wulf import ViewSettings
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.white_tiger_economic_tooltip_view_model import WhiteTigerEconomicTooltipViewModel
from white_tiger.gui.shared.tooltips import TooltipType
from gui.battle_results.presenters.wrappers import hasPresenter
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class BattleResultsEconomicTooltipView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__currencyType')

    def __init__(self, arenaUniqueID, currencyType):
        settings = ViewSettings(layoutID=R.views.white_tiger.mono.lobby.tooltips.battle_results_economic_tooltip(), model=WhiteTigerEconomicTooltipViewModel())
        super(BattleResultsEconomicTooltipView, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__currencyType = currencyType

    @property
    def arenaUniqueID(self):
        return self.__arenaUniqueID

    @property
    def viewModel(self):
        return super(BattleResultsEconomicTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultsEconomicTooltipView, self)._onLoading(*args, **kwargs)
        self.__invalidateAll()

    @hasPresenter()
    def __invalidateAll(self, presenter=None):
        with self.viewModel.transaction() as model:
            presenter.packTooltips(TooltipType.WHITE_TIGER_EARNED_CURRENCY, model, ctx={'currencyType': self.__currencyType})
