# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/branch_selection_sub_view.py
import typing
import nations
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import NationTreeData
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps, SelectedNation
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from helpers import dependency
from collections import namedtuple
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from tech_tree_trade_in.gui.shared.views.helper import fillVehiclesList, packVehicleIconLowerCase, packVehicleIconBig
from tech_tree_trade_in.gui.shared.event_dispatcher import pushTechTreeTradeInErrorNotification
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews import SubViewBase
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews.view_helpers import PriceRequestDataCache, ResponseType
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_selection_view_model import BranchSelectionViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.trade_in_nation_view_model import TradeInNationViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.trade_in_branch_view_model import TradeInBranchViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.footer_view_model import FooterState
if typing.TYPE_CHECKING:
    from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.footer_view_model import FooterViewModel
_Node = namedtuple('Node', ['id', 'state', 'unlockProps'])

class BranchSelectionSubView(SubViewBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)
    __slots__ = ('__branchToTradeId', '__branchToReceiveId', '__priceRequestCache', '__summaryRequestCache', '__currentPrice')

    def __init__(self, viewModel, parentView):
        super(BranchSelectionSubView, self).__init__(viewModel, parentView)
        self.__branchToTradeId = -1
        self.__branchToReceiveId = -1
        self.__priceRequestCache = PriceRequestDataCache()
        self.__currentPrice = None
        return

    @property
    def viewId(self):
        return MainViews.BRANCH_SELECTION

    @property
    def viewModel(self):
        return super(BranchSelectionSubView, self).getViewModel()

    @property
    def footerVM(self):
        return self.parentView.viewModel.mainOverlayModel.footer

    def initialize(self, *args, **kwargs):
        super(BranchSelectionSubView, self).initialize(*args, **kwargs)
        self.__update()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BranchSelectionSubView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIPS_CONSTANTS.TECHTREE_VEHICLE:
            vehCD = int(event.getArgument('id'))
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            nationIdx = nations.INDICES[vehicle.nationName]
            SelectedNation.select(nationIdx)
            ntd = NationTreeData(dumpers.NationObjDumper())
            ntd.load(nationIdx)
            node = findFirst(lambda n: n['id'] == vehCD, ntd.dump()['nodes'])
            return createTooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=[_Node(id=node['id'], state=node['state'], unlockProps=UnlockProps(*node['unlockProps'])), 0])
        else:
            return None

    def onConfirm(self):
        if self.__branchToTradeId < 0 or self.__branchToReceiveId < 0 or not self.__currentPrice:
            return
        if self.__itemsCache.items.stats.mayConsumeWalletResources:
            self.parentView.switchContentWithContext(MainViews.MULTICURRENCY_SELECTION, ctx={'price': self.__currentPrice})
        else:
            pushTechTreeTradeInErrorNotification()

    def _getEvents(self):
        return ((self.viewModel.onConfirm, self.onConfirm), (self.viewModel.onSelectBranchToReceiveId, self.__onSelectBranchToReceiveId), (self.viewModel.onSelectBranchToTradeId, self.__onSelectBranchToTradeId))

    @args2params(int)
    def __onSelectBranchToReceiveId(self, branchId):
        self.viewModel.setSelectedBranchToReceiveId(branchId)
        if branchId == self.__branchToReceiveId:
            return
        self.__branchToReceiveId = branchId
        self.__requestPrice()

    @args2params(int)
    def __onSelectBranchToTradeId(self, branchId):
        self.viewModel.setSelectedBranchToTradeId(branchId)
        if branchId == self.__branchToTradeId:
            return
        self.__branchToTradeId = branchId
        self.__requestPrice()

    def __requestPrice(self):
        if self.__branchToTradeId == -1 or self.__branchToReceiveId == -1:
            return
        responseType = self.__priceRequestCache.request((self.__branchToTradeId, self.__branchToReceiveId), self.__onPriceReceived)
        if responseType == ResponseType.SERVER:
            with self.footerVM.transaction() as vm:
                vm.setState(FooterState.UPDATING)

    def __update(self):
        with self.viewModel.transaction() as model:
            self.__fillBranches(model.getBranchesToTrade(), self.__techTreeTradeInController.getBranchesToTradeSortedForNation().items())
            self.__fillBranches(model.getBranchesToReceive(), self.__techTreeTradeInController.getBranchesToReceiveSortedForNation().items())
            model.setSelectedBranchToReceiveId(self.__branchToReceiveId)
            model.setSelectedBranchToTradeId(self.__branchToTradeId)
        if not self.__currentPrice:
            with self.footerVM.transaction() as vm:
                vm.setState(FooterState.NO_PRICE)
            return
        self.__updateFooterWithPrice()

    def __fillBranches(self, branchesCollection, collection):
        branchesCollection.clear()
        for nation, branches in collection:
            nationVM = TradeInNationViewModel()
            nationVM.setNation(nation)
            self.__fillBranchesInNation(nationVM.getBranches(), branches)
            branchesCollection.addViewModel(nationVM)

        branchesCollection.invalidate()

    def __fillBranchesInNation(self, branchesInNation, branches):
        branchesInNation.clear()
        for branch in branches:
            branchVM = TradeInBranchViewModel()
            branchVM.setId(branch.branchId)
            fillVehiclesList(branchVM.getVehiclesList(), branch.vehCDs, smallIconPacker=packVehicleIconBig, bigIconPacker=packVehicleIconLowerCase)
            branchesInNation.addViewModel(branchVM)

        branchesInNation.invalidate()

    def __onPriceReceived(self, _, data):
        self.__currentPrice = data
        self.__updateFooterWithPrice()

    def __updateFooterWithPrice(self):
        itemPrice = ItemPrice(Money(gold=self.__currentPrice['priceWBpDiscount']), Money(gold=self.__currentPrice['baseTradePrice']))
        with self.footerVM.transaction() as vm:
            vm.setState(FooterState.BASIC_PRICE)
            PriceModelBuilder.clearPriceModel(vm.price)
            PriceModelBuilder.fillPriceModelByItemPrice(vm.price, itemPrice, checkBalanceAvailability=True)
