# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/tooltips/finance_details.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.financial_tooltip_model import FinancialTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class FinancialTooltip(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__currencyType')
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueID, currencyType):
        contentResID = R.views.lobby.postbattle.tooltips.FinanceDetails()
        settings = ViewSettings(contentResID)
        settings.model = FinancialTooltipModel()
        super(FinancialTooltip, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__currencyType = currencyType

    def _onLoading(self, *args, **kwargs):
        super(FinancialTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__battleResults.presenter.setFinancialTooltipData(model, self.__arenaUniqueID, self.__currencyType)
