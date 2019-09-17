# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_card_view.py
import time
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.hint_helper import FestivalHintHelper
from festivity.festival.item_info import FestivalItemInfo
from festivity.festival.processors import FestivalBuyItemProcessor, SetPlayerCardProcessor
from festivity.festival.requester import FestCriteria
from frameworks.wulf import ViewFlags, ViewStatus
from gui import SystemMessages
from gui.impl.backport.backport_tooltip import TooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_card_view_model import FestivalCardViewModel
from gui.impl.gen.view_models.views.lobby.festival.festival_tab_model import FestivalTabModel
from gui.impl.lobby.festival.festival_helper import fillItemsInfoModel, fillFestivalItemsArray, fillFestivalPlayerCard, FestSelectedFilters
from gui.impl.lobby.festival.festival_random_generator_view import showFestivalRandomGenerator
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showFestMiniGameOverlay
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from items.components.festival_constants import FEST_ITEM_TYPE
from skeletons.festival import IFestivalController
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from async import async
_UNDEFINED_INDEX = -1

class FestivalCardView(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__tempPlayerCard', '__currentTypeName', '__selectedFilter', '__notifier', '__isFocus')

    def __init__(self, viewKey=R.views.lobby.festival.festival_card_view.FestivalCardView(), viewModelClazz=FestivalCardViewModel, *args, **kwargs):
        super(FestivalCardView, self).__init__(viewKey, ViewFlags.COMPONENT, viewModelClazz, *args, **kwargs)
        self.__tempPlayerCard = None
        self.__currentTypeName = None
        self.__isFocus = False
        self.__selectedFilter = FestSelectedFilters()
        return

    @property
    def viewModel(self):
        return super(FestivalCardView, self).getViewModel()

    def isNotApplied(self):
        applyModel = self.viewModel.applyModel
        return bool(len(applyModel.getStorageItems()) + len(applyModel.getPaymentItems()))

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            itemID = int(event.getArgument('itemID'))
            typeID = event.getArgument('typeID')
            if typeID == TOOLTIPS_CONSTANTS.FESTIVAL_ITEM and itemID:
                tooltipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.FESTIVAL_ITEM, specialArgs=[itemID, 1, True])
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is not None:
                    window.load()
                return window
        return super(FestivalCardView, self).createToolTip(event)

    def setFocus(self, isFocus):
        self.__isFocus = isFocus
        if self.viewStatus == ViewStatus.LOADED:
            self.__updateTutorial()

    def _initialize(self, tabName=None):
        super(FestivalCardView, self)._initialize()
        self.viewModel.onBuyItem += self.__onBuyItem
        self.viewModel.onItemTypeChange += self.__onItemTypeChange
        self.viewModel.applyModel.onPlayerCardReset += self.__onPlayerCardReset
        self.viewModel.applyModel.onPlayerCardApply += self.__onPlayerCardApply
        self.viewModel.items.onUserSelectionChanged += self.__onUserSelectionChanged
        self.viewModel.filterModel.onFilterChanged += self.__onFilterChange
        self.viewModel.onDogtagGenerator += self.__onDogtagGenerator
        self.viewModel.onMarkAsSeenItem += self.__onMarkAsSeenItem
        self.viewModel.onOpenMiniGames += self.__onOpenMiniGames
        self.__festController.onDataUpdated += self.__onDataUpdated
        self.__festController.onMiniGamesUpdated += self.__onMiniGamesUpdated
        tabName = tabName or self.__festController.getCurrentCardTabState()
        self.__tempPlayerCard = self.__festController.getPlayerCard()
        self.__festController.setGlobalPlayerCard(self.__tempPlayerCard)
        self.__currentTypeName = tabName
        self.__notifier = SimpleNotifier(self.__getMiniGameCooldownPeriod, self.__updateMiniGameCooldown)
        with self.viewModel.transaction() as model:
            fillItemsInfoModel(model)
            model.setStartIndex(FEST_ITEM_TYPE.ALL.index(tabName))
            model.setLowestRandomPrice(self.__festController.getRandomCost(FEST_ITEM_TYPE.ANY))
            self.__updateRandomBtnEnabled(model)
            viewNames = model.getItemTypes()
            for name in FEST_ITEM_TYPE.ALL:
                viewModel = FestivalTabModel()
                viewModel.setName(name)
                viewNames.addViewModel(viewModel)

            viewNames.invalidate()
            self.__updatePlayerCard(model)
            self.__updateItems(tabName)
            self.__fillItems(model)
            self.__updateSeenItems(model)
            self.__updateTutorial()
            self.__updateMiniGames(model)
            self.__selectedFilter.initFilters(model.filterModel)

    def _finalize(self):
        self.viewModel.onBuyItem -= self.__onBuyItem
        self.viewModel.onItemTypeChange -= self.__onItemTypeChange
        self.viewModel.applyModel.onPlayerCardReset -= self.__onPlayerCardReset
        self.viewModel.applyModel.onPlayerCardApply -= self.__onPlayerCardApply
        self.viewModel.items.onUserSelectionChanged -= self.__onUserSelectionChanged
        self.viewModel.filterModel.onFilterChanged -= self.__onFilterChange
        self.viewModel.onDogtagGenerator -= self.__onDogtagGenerator
        self.viewModel.onMarkAsSeenItem -= self.__onMarkAsSeenItem
        self.viewModel.onOpenMiniGames -= self.__onOpenMiniGames
        self.__festController.onDataUpdated -= self.__onDataUpdated
        self.__festController.onMiniGamesUpdated -= self.__onMiniGamesUpdated
        self.__festController.setCurrentCardTabState(self.__currentTypeName)
        self.__festController.setGlobalPlayerCard(None)
        self.__selectedFilter.clear()
        self.__notifier.stopNotification()
        self.__notifier = None
        super(FestivalCardView, self)._finalize()
        return

    @async
    def __onDogtagGenerator(self):
        FestivalHintHelper.updateRndBuyHintVisible(False)
        FestivalHintHelper.setBuyRandom()
        result = yield showFestivalRandomGenerator(self.getParentWindow())
        if result:
            FestivalHintHelper.updateMiniGamesHintVisible(FestivalHintHelper.canShowMiniGames())

    def __onOpenMiniGames(self):
        if FestivalHintHelper.canShowMiniGames():
            FestivalHintHelper.updateMiniGamesHintVisible(False)
            FestivalHintHelper.setMiniGames()
        showFestMiniGameOverlay()

    @decorators.process('festival/buyFestivalItem')
    def __onBuyItem(self, args):
        itemID = int(args['itemID'])
        result = yield FestivalBuyItemProcessor(itemID, self.getParentWindow()).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __onMiniGamesUpdated(self):
        with self.viewModel.transaction() as model:
            self.__updateMiniGames(model)

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as model:
            if FestSyncDataKeys.ITEMS in keys:
                self.__updateItems(self.__currentTypeName)
                self.__updatePlayerCard(model)
                self.__fillItems(model)
                self.__updateSeenItems(model)
                self.__updateRandomBtnEnabled(model)
            if FestSyncDataKeys.SEEN_ITEMS in keys:
                self.__updateSeenItems(model)
            if FestSyncDataKeys.TICKETS in keys and FestSyncDataKeys.ITEMS not in keys:
                self.__updateTicketsInfo(model)

    def __onItemTypeChange(self, args):
        typeName = args['typeName']
        with self.viewModel.transaction() as model:
            self.__updateItems(typeName, model.filterModel)
            self.__fillItems(model)

    def __onUserSelectionChanged(self, item):
        if not item.getReceived() and item.getCost() == -1:
            return
        festItem = FestivalItemInfo(item.getId())
        self.__tempPlayerCard.setItem(item.getId())
        magicEmblemSwitch = festItem.getType() in (FEST_ITEM_TYPE.BASIS, FEST_ITEM_TYPE.EMBLEM) and self.__tempPlayerCard.getEmblem().isAlternative() and self.__tempPlayerCard.getBasis().isAlternative()
        with self.viewModel.transaction() as model:
            self.__updatePlayerCard(model, magicEmblemSwitch)

    def __onPlayerCardReset(self, args=None):
        typeNames = (args['typeName'],) if args else FEST_ITEM_TYPE.ALL
        for typeName in typeNames:
            itemID = self.__festController.getPlayerCard().getItemIDByType(typeName).getID()
            self.__tempPlayerCard.setItem(itemID)

        with self.viewModel.transaction() as model:
            self.__updatePlayerCard(model)

    @decorators.process('festival/applyPlayerCard')
    def __onPlayerCardApply(self, *_):
        rawData = self.__tempPlayerCard.getRawData()
        result = yield SetPlayerCardProcessor(rawData, self.getParentWindow()).request()
        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        if result.success:
            with self.viewModel.transaction() as tx:
                self.__updateApplyModel(tx)
                self.__fillItems(tx)

    def __onMarkAsSeenItem(self, args):
        itemID = int(args['itemID'])
        self.__festController.markItemsAsSeen([itemID])

    def __updateItems(self, typeName, model=None):
        items = self.__festController.getFestivalItems(FestCriteria.TYPE(typeName))
        self.__selectedFilter.setItems(items.values(), model)
        self.__currentTypeName = typeName

    def __updatePlayerCard(self, model, magicEmblemSwitch=False):
        fillFestivalPlayerCard(self.__tempPlayerCard, model.playerCard, magicEmblemSwitch)
        self.__fillSelectedIndex(model)
        self.__updateApplyModel(model)

    def __updateApplyModel(self, model):
        rawData = self.__tempPlayerCard.getRawData()
        storageItems = model.applyModel.getStorageItems()
        storageItems.clear()
        paymentItems = model.applyModel.getPaymentItems()
        paymentItems.clear()
        applyCost = 0
        for itemID in rawData:
            festItem = FestivalItemInfo(itemID)
            if festItem.isInPlayerCard():
                continue
            if festItem.isInInventory():
                storageItems.addString(festItem.getType())
            paymentItems.addString(festItem.getType())
            applyCost += festItem.getCost()

        storageItems.invalidate()
        paymentItems.invalidate()
        model.applyModel.setBuyCost(applyCost)
        model.applyModel.setIsCanBuy(applyCost <= self.__festController.getTickets())

    def __updateSeenItems(self, model):
        for tabModel in model.getItemTypes():
            tabModel.setUnseenCount(len(self.__festController.getUnseenItems(tabModel.getName())))

        model.getItemTypes().invalidate()
        selectedItems = self.__selectedFilter.getItems()
        for ind, itemModel in enumerate(model.items.getItems()):
            selectedItem = selectedItems[ind]
            itemModel.setUnseen(selectedItem.isInInventory() and not selectedItem.isSeen())

    def __updateRandomBtnEnabled(self, model):
        model.setIsRandomBtnEnabled(not self.__festController.isCommonItemCollected())

    def __updateTicketsInfo(self, model):
        self.__updateApplyModel(model)
        for item in model.items.getItems():
            festItem = FestivalItemInfo(item.getId())
            item.setIsCanBuy(festItem.getCost() <= self.__festController.getTickets())

    def __updateTutorial(self):
        isRndBuyHintEnabled = FestivalHintHelper.canShowIsBuyRandom(additionalCondition=self.__isFocus)
        FestivalHintHelper.updateRndBuyHintVisible(isRndBuyHintEnabled)
        FestivalHintHelper.updateMiniGamesHintVisible(self.__isFocus and FestivalHintHelper.canShowMiniGames())

    def __updateMiniGames(self, model):
        model.setTotalMiniGamesAttempts(self.__festController.getMiniGamesAttemptsMax())
        model.setRemainedMiniGamesAttempts(self.__festController.getMiniGamesAttemptsLeft())
        model.setIsMiniGamesEnabled(self.__festController.isMiniGamesEnabled())
        miniGamesCooldown = self.__festController.getMiniGamesCooldown()
        if miniGamesCooldown is not None:
            self.__notifier.startNotification()
            model.setMiniGamesCooldown(miniGamesCooldown if miniGamesCooldown > 0 else 0)
        else:
            self.__notifier.stopNotification()
            model.setMiniGamesCooldown(0)
        return

    def __getMiniGameCooldownPeriod(self):
        leftTime = self.viewModel.getMiniGamesCooldown()
        gmTime = time.gmtime(leftTime)
        return gmTime.tm_sec + 1

    def __updateMiniGameCooldown(self):
        miniGamesCooldown = self.__festController.getMiniGamesCooldown()
        if miniGamesCooldown is None:
            self.__notifier.stopNotification()
        else:
            self.viewModel.setMiniGamesCooldown(miniGamesCooldown if miniGamesCooldown > 0 else 0)
        return

    def __fillItems(self, model):
        fillFestivalItemsArray(self.__selectedFilter.getItems(), model.items)
        self.__fillSelectedIndex(model)

    def __fillSelectedIndex(self, model):
        index = _UNDEFINED_INDEX
        selectedItemID = self.__tempPlayerCard.getItemIDByType(self.__currentTypeName).getID()
        for ind, item in enumerate(model.items.getItems()):
            if item.getId() == selectedItemID:
                index = ind

        if index != _UNDEFINED_INDEX:
            model.items.getSelectedIndices().clear()
            model.items.getSelectedIndices().addNumber(index)
            model.items.getSelectedIndices().invalidate()

    def __onFilterChange(self, args):
        filterName = args['name']
        with self.viewModel.transaction() as model:
            self.__selectedFilter.changeFilter(filterName, model.filterModel)
            self.__fillItems(model)
