# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/post_trade_view.py
from helpers import dependency
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.post_trade_view_model import PostTradeViewModel
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.shared import event_dispatcher
from tech_tree_trade_in.gui.shared.views.helper import fillVehiclesList, packVehicleIconUpperCase, getNationNameByVehCD
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController
from tech_tree_trade_in_common.helpers import getBranchFromSign

def getBranchData(token):

    def filterBranchBySummary(branch, summary):
        tiers = ['6',
         '7',
         '8',
         '9',
         '10']
        return tuple((branch[i] for i, tier in enumerate(tiers) if tier in summary))

    receivedBranch = getBranchFromSign(token.receivedBranch)
    vehCDs = filterBranchBySummary(receivedBranch, token.tradeSummary)
    nation = getNationNameByVehCD(vehCDs[0])
    return (nation, vehCDs)


class PostTradeView(SubModelPresenter):
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)

    @property
    def viewId(self):
        return MainViews.POST_TRADE

    @property
    def viewModel(self):
        return super(PostTradeView, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(PostTradeView, self).initialize(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onConfirm, self.__onConfirm),)

    def __onConfirm(self):
        event_dispatcher.showTechTreeView(self.viewModel.getNation())

    def __update(self):
        with self.viewModel.transaction() as model:
            token = self.__techTreeTradeInController.getTradeInToken()
            if token is not None:
                nation, vehCDs = getBranchData(token)
                model.setNation(nation)
                fillVehiclesList(model.branchToReceive.getVehiclesList(), vehCDs, bigIconPacker=packVehicleIconUpperCase)
        return
