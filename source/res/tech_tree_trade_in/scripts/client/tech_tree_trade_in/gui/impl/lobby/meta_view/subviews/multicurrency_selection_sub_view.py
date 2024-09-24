# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/meta_view/subviews/multicurrency_selection_sub_view.py
import json
from collections import OrderedDict
import nations
from gui import GUI_NATIONS
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_selection_view_model import BranchSelectionViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.multicurrency_selection_view_model import MulticurrencySelectionViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.resource_info_view_model import ResourceInfoViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.nation_item_info_view_model import NationItemInfoViewModel
from tech_tree_trade_in.gui.impl.lobby.meta_view.subviews import SubViewBase
from tech_tree_trade_in.gui.impl.lobby.tooltips.multicurrency_tooltip_view import MulticurrencyTooltipView
from tech_tree_trade_in.gui.shared.views.helper import getNationNameByVehCD
from tech_tree_trade_in.skeletons.gui.game_control import BranchType, ITechTreeTradeInController
UNIVERSAL_BLUEPRINTS = 'intelligence'
NATIONAL_BLUEPRINTS = 'fragments'

class MulticurrencySelectionView(SubViewBase):
    __slots__ = ('_stats', '_blueprints', '_price')
    __itemsCache = dependency.descriptor(IItemsCache)
    __techTreeTradeInController = dependency.descriptor(ITechTreeTradeInController)

    def __init__(self, viewModel, parentView):
        super(MulticurrencySelectionView, self).__init__(viewModel, parentView)
        self._stats = self.__itemsCache.items.stats
        self._blueprints = self.__itemsCache.items.blueprints
        self._price = None
        return

    def initialize(self, *args, **kwargs):
        super(MulticurrencySelectionView, self).initialize(*args, **kwargs)
        ctx = kwargs.get('ctx')
        if not ctx:
            return
        self._price = ctx.get('price')
        self.__update()

    @property
    def viewId(self):
        return MainViews.MULTICURRENCY_SELECTION

    @property
    def viewModel(self):
        return super(MulticurrencySelectionView, self).getViewModel()

    def clear(self):
        super(MulticurrencySelectionView, self).clear()
        self._price = None
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.tech_tree_trade_in.lobby.tooltips.MulticurrencyTooltipView():
            return MulticurrencyTooltipView(event.getArgument('isFullPriceReached', False), event.getArgument('resourceType', ''), event.getArgument('limit', 0), event.getArgument('maxValue', 0), event.getArgument('curValue', 0))
        super(MulticurrencySelectionView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onConfirm, self.__onConfirm),)

    @args2params(str)
    def __onConfirm(self, selectedResources):
        self.parentView.switchToSummaryView(self.__getMultiPrice(selectedResources))

    @staticmethod
    def __getMultiPrice(resources):
        data = json.loads(resources)
        return {key:val for key, val in data}

    def __update(self):
        with self.viewModel.transaction() as model:
            self.__setStats(model)

    def __setStats(self, model):
        self.__setBaseCurrency(model.baseCurrency)
        self.__setResources(model.getResources())

    def __setBaseCurrency(self, currency):
        currency.setType(Currency.GOLD)
        currency.setAmount(self._price.get('priceWBpDiscount'))

    def __setResources(self, resourcesArray):
        resourcesArray.clear()
        resourcesArray.addViewModel(self.__setFreeXP())
        resourcesArray.addViewModel(self.__setUniversalBlueprints())
        resourcesArray.addViewModel(self.__setNationalBlueprints())
        resourcesArray.addViewModel(self.__setCrystals())
        resourcesArray.invalidate()

    def __setFreeXP(self):
        resourcesModel = ResourceInfoViewModel()
        resourcesModel.setType(Currency.FREE_XP)
        resourcesModel.setBalance(int(self._stats.freeXP))
        resourcesModel.setRate(self._price.get('freeExpPerPercent'))
        resourcesModel.setLimit(self._price.get('freeExpCap'))
        resourcesModel.setPercent(1)
        return resourcesModel

    def __setUniversalBlueprints(self):
        resourcesModel = ResourceInfoViewModel()
        resourcesModel.setType(UNIVERSAL_BLUEPRINTS)
        resourcesModel.setBalance(self._blueprints.getIntelligenceCount())
        resourcesModel.setRate(self._price.get('universalFragmentsPerPercent'))
        resourcesModel.setLimit(self._price.get('universalFragmentsCap'))
        resourcesModel.setPercent(1)
        return resourcesModel

    def __setNationalBlueprints(self):
        resourcesModel = ResourceInfoViewModel()
        resourcesModel.setType(NATIONAL_BLUEPRINTS)
        resourcesModel.setRate(self._price.get('nationalFragmentsPerPercent'))
        resourcesModel.setLimit(self._price.get('nationalFragmentsCap'))
        resourcesModel.setPercent(1)
        self.__setListNations(resourcesModel.getNations())
        return resourcesModel

    def __setListNations(self, listNations):
        listNations.clear()
        receivedBranchNation = self.__getReceivedBranchNation()
        nationalFragments = self.__getNationalFragments()
        for nationName, amount in nationalFragments.items():
            isSelected = nationName == receivedBranchNation
            listNations.addViewModel(self.__getNationView(nationName, amount, isSelected))

        listNations.invalidate()

    def __getNationalFragments(self):
        result = OrderedDict()
        nationalFragments = self._blueprints.getAllNationalFragmentsData()
        for nationName in GUI_NATIONS:
            nationIdx = nations.INDICES[nationName]
            result[nationName] = nationalFragments.get(nationIdx, 0)

        return result

    def __getReceivedBranchNation(self):
        branchSelectionModel = self.parentView.viewModel.branchSelectionModel
        branchToReceiveId = branchSelectionModel.getSelectedBranchToReceiveId()
        branchToReceive = self.__techTreeTradeInController.getBranchById(branchToReceiveId, BranchType.BRANCHES_TO_RECEIVE)
        return getNationNameByVehCD(branchToReceive.vehCDs[0])

    def __getNationView(self, nationName, amount, isSelected):
        nationView = NationItemInfoViewModel()
        nationView.setType(nationName)
        nationView.setAmount(int(amount))
        nationView.setIsSelected(isSelected)
        return nationView

    def __setCrystals(self):
        resourcesModel = ResourceInfoViewModel()
        currencyType = Currency.CRYSTAL
        resourcesModel.setType(currencyType)
        resourcesModel.setBalance(int(self._stats.money.getSignValue(currencyType)))
        resourcesModel.setRate(self._price.get('bondsPerPercent'))
        resourcesModel.setLimit(self._price.get('bondsCap'))
        resourcesModel.setPercent(1)
        return resourcesModel
