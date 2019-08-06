# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_helper.py
from collections import OrderedDict
import typing
import BigWorld
from frameworks.wulf import ViewFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.currency_item_model import CurrencyItemModel
from gui.impl.gen.view_models.views.lobby.festival.festival_item_renderer import FestivalItemRenderer
from gui.impl.gen.view_models.views.lobby.selected_filters_model import SelectedFiltersModel
from gui.impl.gen.view_models.views.lobby.sub_filter_model import SubFilterModel
from gui.impl.lobby.festival.festival_tickets_tooltip import FestivalTicketsTooltip
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.festival import IFestivalController
if typing.TYPE_CHECKING:
    from festivity.festival.player_card import PlayerCard
    from gui.impl.gen.view_models.views.lobby.festival.festival_player_card_view_model import FestivalPlayerCardViewModel
    from gui.impl.wrappers.user_list_model import UserListModel

class FestivalViews(object):
    CARD = 'card'
    INFO = 'info'
    REWARDS = 'rewards'
    BONUS = 'bonus'
    SHOP = 'shop'
    ALL = (CARD,
     REWARDS,
     SHOP,
     INFO)


@dependency.replace_none_kwargs(festivalController=IFestivalController)
def fillItemsInfoModel(model, festivalController=None):
    receivedItems = festivalController.getReceivedItemsCount()
    totalItems = festivalController.getTotalItemsCount()
    model.setReceivedItems(receivedItems)
    model.setTotalItems(totalItems)


@dependency.replace_none_kwargs(festController=IFestivalController)
def fillFestivalItemsArray(items, array, festController=None):
    array.getItems().clear()
    for item in items:
        itemRenderer = FestivalItemRenderer()
        itemRenderer.setId(item.getID())
        itemRenderer.setResId(item.getDefaultResId())
        itemRenderer.setReceived(item.isInInventory())
        itemRenderer.setIsInPlayerCard(item.isInPlayerCard())
        itemRenderer.setType(item.getType())
        itemRenderer.setCost(item.getCost())
        itemRenderer.setIsCanBuy(item.getCost() <= festController.getTickets())
        itemRenderer.setIsAlternative(item.isAlternative())
        itemRenderer.setUnseen(item.isInInventory() and not item.isSeen())
        array.addViewModel(itemRenderer)

    array.invalidate()


def fillFestivalPlayerCard(playerCard, model, magicEmblemSwitch=False):
    model.setRankID(playerCard.getRank().getID())
    model.setDefaultEmblemID(playerCard.getEmblem().getDefaultResId())
    model.setEmblemID(playerCard.getEmblem().getResId())
    model.setBasisID(playerCard.getBasis().getResId())
    model.setTitleID(playerCard.getTitle().getResId())
    model.setUserName(BigWorld.player().name)
    if magicEmblemSwitch:
        model.setTriggerEmblemAnimation(not model.getTriggerEmblemAnimation())


class FestivalRandomGeneratorBalanceContent(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalRandomGeneratorBalanceContent, self).__init__(R.views.lobby.festival.festival_components.FestivalRandomGeneratorBalanceContent(), ViewFlags.VIEW, CurrencyItemModel, *args, **kwargs)

    @property
    def viewModel(self):
        return super(FestivalRandomGeneratorBalanceContent, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return FestivalTicketsTooltip(backport.getIntegralFormat(self.__festController.getTickets())) if contentID == R.views.lobby.festival.festival_tickets_tooltip.FestivalTicketsTooltip() else super(FestivalRandomGeneratorBalanceContent, self).createToolTipContent(event=event, contentID=contentID)


class BaseSelectedFilters(object):
    __slots__ = ('__items', '__filters', '__filteredItems', '__selectedFilters')

    def __init__(self):
        self.__items = tuple()
        self.__filteredItems = tuple()
        self.__selectedFilters = []
        self.__filters = OrderedDict()

    def setItems(self, items, model=None):
        self.__items = tuple(items)
        self.__filteredItems = self._createFilteredItems()
        if model is not None:
            model.setSelectedFilterCount(len(self.__filteredItems))
            model.setTotalFilterCount(len(self.__items))
        return

    def changeFilter(self, filterName, model):
        filters = model.getFilters()
        self.__selectedFilters = []
        for filterModel in filters:
            if filterName == filterModel.getName():
                filterModel.setSelected(not filterModel.getSelected())
            if filterModel.getSelected():
                self.__selectedFilters.append(filterModel.getName())

        filters.invalidate()
        if not self.__selectedFilters:
            model.setFilterIsEnabled(False)
            self.__filteredItems = self.__items
        else:
            model.setFilterIsEnabled(True)
            self.__filteredItems = self._createFilteredItems()
        model.setSelectedFilterCount(len(self.__filteredItems))
        model.setTotalFilterCount(len(self.__items))

    def initFilters(self, model):
        filters = model.getFilters()
        filters.clear()
        for filterName in self.__filters:
            filterModel = self._createSubFilterModel(filterName)
            filters.addViewModel(filterModel)

        filters.invalidate()
        model.setSelectedFilterCount(len(self.__filteredItems))
        model.setTotalFilterCount(len(self.__items))

    def resetFilters(self, model):
        for filterModel in model.getFilters():
            filterModel.setSelected(False)

        model.getFilters().invalidate()
        self.__filteredItems = self.__items

    def getItems(self):
        return self.__filteredItems

    def clear(self):
        self.__filteredItems = None
        self.__items = None
        self.__filters = None
        self.__selectedFilters = None
        return

    @staticmethod
    def _createSubFilterModel(filterName):
        filterModel = SubFilterModel()
        filterModel.setName(filterName)
        filterModel.setSelected(False)
        return filterModel

    def _createFilteredItems(self):
        result = tuple((item for item in self.__items if self._checkItem(item)))
        return result

    def _checkItem(self, item):
        result = True
        for filterName in self.__selectedFilters:
            result &= self.__filters[filterName](item)

        return result

    def _addFilter(self, filterName, filterMethod):
        self.__filters[filterName] = filterMethod

    def _delFilter(self, filterName):
        del self.__filters[filterName]

    def _clearFilters(self):
        self.__filters.clear()


class FestSelectedFilters(BaseSelectedFilters):
    INVENTORY = 'inventory'

    def __init__(self):
        super(FestSelectedFilters, self).__init__()
        self._addFilter(self.INVENTORY, self.__inventoryFilter)

    def setItems(self, items, model=None):
        items.sort(key=self.__festivalItemKey)
        super(FestSelectedFilters, self).setItems(items, model)

    @staticmethod
    def __inventoryFilter(item):
        return item.isInInventory()

    @staticmethod
    def __festivalItemKey(festItem):
        return festItem.getWeight()
