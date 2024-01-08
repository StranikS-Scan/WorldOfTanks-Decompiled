# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/quick_training_view.py
from itertools import chain
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from base_crew_view import BaseCrewView, IS_FROM_ESCAPE_PARAM
from crew_sounds import SOUNDS
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import TipType
from gui.impl.gen.view_models.views.lobby.crew.help_navigate_from import HelpNavigateFrom
from gui.impl.gen.view_models.views.lobby.crew.quick_training_view_model import QuickTrainingViewModel, TrainingBookModel
from gui.impl.lobby.crew.crew_helpers.quick_training_helpers import UiData
from gui.impl.lobby.crew.crew_helpers.skill_helpers import isTmanMaxed, getAvailableSkillsNum, quickEarnCrewSkills, quickEarnTmanSkills
from gui.impl.lobby.crew.crew_helpers.stepper_calculator import FreeXpStepperCalculator
from gui.impl.lobby.crew.tooltips.experience_stepper_tooltip import ExperienceStepperTooltip
from gui.impl.lobby.crew.tooltips.quick_training_discount_tooltip import QuickTrainingDiscountTooltip
from gui.impl.lobby.crew.utils import jsonArgsConverter, TRAINING_TIPS, getTip
from gui.shared import event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, NO_TANKMAN, NO_SLOT
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.crew_book import sortItems
from gui.shared.gui_items.items_actions import factory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewQuickTrainingKeys

class QuickTrainingView(BaseCrewView):
    __slots__ = ('__selectedTankmanID', '__selectedVehicleID', '__doNotOpenTips', '__closedTips', '_stepper', '_uiData')
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    MIN_VALUE = 0.01
    IS_MUTUAL_CALCULATIONS_SUPPORTED = False
    tankman = property(lambda self: self._getTankman())
    vehicle = property(lambda self: self._getVehicle())
    crewBooks = property(lambda self: self._getCrewBooks())
    nationID = property(lambda self: self.vehicle.nationID)
    nationName = property(lambda self: self.vehicle.nationName)
    shortUserName = property(lambda self: self.vehicle.shortUserName)
    crew = property(lambda self: self._getCrew())
    isCrewEmpty = property(lambda self: not any((tankman is not None for _, tankman in self.crew)))
    isCrewIncomplete = property(lambda self: self.__selectedVehicleID == NO_VEHICLE_ID or any((tankman is None for _, tankman in self.crew)))
    hasCrewInvalidSpec = property(lambda self: any((not self.__isTankmanInSameClassTank(tankman) for _, tankman in self.crew)))
    hasCrewUntrained = property(lambda self: any((tankman.isUntrained for _, tankman in self.crew)))
    hasCrewMaxedTman = property(lambda self: any((isTmanMaxed(tankman) for _, tankman in self.crew)))
    notInShopItems = property(lambda self: self.itemsCache.items.shop.getHiddens())
    hasPersonalBook = property(lambda self: any((book.isPersonal() and book.getFreeCount() > 0 for book in self.crewBooks)))

    def __init__(self, layoutID, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = QuickTrainingViewModel()
        settings.kwargs = kwargs
        self.__selectedTankmanID = kwargs.get('tankmanInvID', NO_TANKMAN)
        self.__selectedVehicleID = kwargs.get('vehicleInvID', NO_VEHICLE_ID)
        if self.__selectedTankmanID == NO_TANKMAN and self.__selectedVehicleID == NO_VEHICLE_ID and g_currentVehicle.isPresent():
            self.__selectedVehicleID = g_currentVehicle.item.invID
        self.__doNotOpenTips = []
        self.__closedTips = []
        self._stepper = None
        self._uiData = None
        super(QuickTrainingView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(QuickTrainingView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.QuickTrainingDiscountTooltip():
            discountRate = self.itemsCache.items.shop.freeXPToTManXPRate
            defaultRate = self.itemsCache.items.shop.defaults.freeXPToTManXPRate
            return QuickTrainingDiscountTooltip(1, 1, defaultRate, discountRate)
        return ExperienceStepperTooltip() if contentID == R.views.lobby.crew.tooltips.ExperienceStepperTooltip() else super(QuickTrainingView, self).createToolTipContent(event=event, contentID=contentID)

    def onBringToFront(self, parentWindow):
        super(QuickTrainingView, self).onBringToFront(parentWindow)
        if parentWindow != self.getWindow():
            self.destroyWindow()

    def widgetAutoSelectSlot(self, **kwargs):
        if self.__isSelectionRequired():
            super(QuickTrainingView, self).widgetAutoSelectSlot(**kwargs)
        else:
            self._onEmptySlotAutoSelect(NO_SLOT)

    def _getCrewBooks(self):
        criteria = REQ_CRITERIA.CREW_ITEM.NATIONS([self.nationID])
        criteria ^= REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(CREW_BOOK_RARITY.NO_NATION_TYPES)
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, criteria)
        return sortItems(items.values())

    def _getTankman(self):
        return self.itemsCache.items.getTankman(self.__selectedTankmanID) if self.__selectedTankmanID != NO_TANKMAN else None

    def _getVehicle(self):
        if self.__selectedVehicleID != NO_VEHICLE_ID:
            return self.itemsCache.items.getVehicle(self.__selectedVehicleID)
        else:
            if self.__selectedTankmanID != NO_TANKMAN:
                if self.tankman:
                    if not self.tankman.isInTank:
                        return self.itemsCache.items.getItemByCD(self.tankman.vehicleNativeDescr.type.compactDescr)
                    return self.itemsCache.items.getVehicle(self.tankman.vehicleInvID)
            return None

    def _getCrew(self):
        if self.__selectedVehicleID != NO_VEHICLE_ID:
            if self.vehicle:
                return self.vehicle.crew
            return []
        if self.__selectedTankmanID != NO_TANKMAN:
            if self.tankman and not self.tankman.isInTank and not self.tankman.isDismissed:
                return [(0, self.tankman)]
            return []
        return []

    def _onLoading(self, *args, **kwargs):
        super(QuickTrainingView, self)._onLoading(*args, **kwargs)
        crewBooksViewedCache().addViewedItems(self.nationID)

    def _onLoaded(self, *args, **kwargs):
        super(QuickTrainingView, self)._onLoaded(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_BOOKS_ENTRANCE)

    def _getCallbacks(self):
        return (('inventory', self.__onInventoryUpdate), ('stats.freeXP', self.__onFreeXpChanged))

    def _getEvents(self):
        eventsTuple = super(QuickTrainingView, self)._getEvents()
        return eventsTuple + ((self.itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChange),
         (self.viewModel.onLearn, self.__onLearnClicked),
         (self.viewModel.onBuyBook, self.__onBuyClicked),
         (self.viewModel.onFreeXpSelected, self.__onFreeXpSelected),
         (self.viewModel.onFreeXpMouseEnter, self.__onFreeXpMouseEnter),
         (self.viewModel.onCardMouseLeave, self.__onCardMouseLeave),
         (self.viewModel.onBookSelected, self.__onBookSelected),
         (self.viewModel.onBookMouseEnter, self.__onBookMouseEnter),
         (self.viewModel.onCancel, self.__onCancel),
         (self.viewModel.onFreeXpUpdated, self.__onFreeXpStepperAction),
         (self.viewModel.onFreeXpManualInput, self.__onFreeXpManualInput),
         (self.viewModel.onTipClose, self.__onTipClose))

    def _fillViewModel(self, vm):
        super(QuickTrainingView, self)._fillViewModel(vm)
        self._stepper = FreeXpStepperCalculator()
        self._uiData = UiData()
        self.__setTankmanData(vm, self.__selectedTankmanID)
        vm.setNationName(self.nationName)
        vm.setVehicleName(self.shortUserName)
        self.__setBooksViewModelData(vm)
        self.__setFreeXPModelData(vm)
        self.__updateCurentFreeXpCardState(vm)
        self.__allowSelectedSlotIdx()
        self.__updateTips(vm)

    def _setBackButtonLabel(self, _):
        pass

    def _finalize(self):
        super(QuickTrainingView, self)._finalize()
        self._stepper = None
        self.__selectedTankmanID = None
        self._uiData.clear()
        return

    @staticmethod
    def _onAbout():
        event_dispatcher.showCrewAboutView(navigateFrom=HelpNavigateFrom.QUICKTRAINING)

    def __onServerSettingsChange(self, diff):
        if 'isCrewBooksPurchaseEnabled' in diff:
            with self.viewModel.transaction() as vm:
                self.__updateBooksViewModelData(vm)

    def __onCacheResync(self, reason, _):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            with self.viewModel.transaction() as vm:
                self.__setFreeXPModelData(vm)

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            vehsCompDescr = invDiff[GUI_ITEM_TYPE.VEHICLE].get('compDescr', {})
            if self.__selectedVehicleID != NO_VEHICLE_ID and self.vehicle and self.vehicle.invID in vehsCompDescr and vehsCompDescr[self.vehicle.invID] is None:
                super(QuickTrainingView, self)._onEmptySlotAutoSelect(NO_SLOT)
                return
        if GUI_ITEM_TYPE.TANKMAN in invDiff:
            compDescr = invDiff.get(GUI_ITEM_TYPE.TANKMAN, {}).get('compDescr', {})
            if any((value for value in compDescr.itervalues())):
                self.__resetCardsStates(isFreeXP=True)
        elif GUI_ITEM_TYPE.CREW_BOOKS in invDiff:
            self.__resetCardsStates(isFreeXP=False)
        if self.isCrewIncomplete:
            self.__clearSelected()
        return

    def __onFreeXpChanged(self, *_):
        with self.viewModel.transaction() as vm:
            self.__setFreeXPModelData(vm)
        self._updateTmanSkillsLevels('update')

    def __onLearnClicked(self):
        self._uiLogger.logClick(CrewQuickTrainingKeys.SUBMIT_BUTTON)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_LEARN_CLICK)
        doActions = []
        if self.__selectedTankmanID != NO_TANKMAN and self.tankman is not None:
            freeXpAmount = self._uiData.freeXp
            if freeXpAmount:
                doActions.append((factory.USE_FREE_XP_TO_TANKMAN, freeXpAmount, self.__selectedTankmanID))
        for bookCD, count in self._uiData.getBooksData().iteritems():
            if count > 0:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if not book.isPersonal() and not self.vehicle:
                    continue
                doActions.append((factory.USE_CREW_BOOK,
                 book.intCD,
                 self.vehicle.invID if self.vehicle and not book.isPersonal() else NO_VEHICLE_ID,
                 count,
                 self.__selectedTankmanID if self.__selectedTankmanID != NO_TANKMAN and book.isPersonal() else NO_TANKMAN))

        groupSize = len(doActions)
        groupID = int(BigWorld.serverTime())
        while doActions:
            factory.doAction(*(doActions.pop(0) + (groupID, groupSize)))

        self.__clearSelected(isLearningInProgress=True)
        with self.viewModel.transaction() as vm:
            vm.freeXpData.setCurrentXpValue(0)
            vm.learningData.setPersonalXpAmount(0)
            vm.learningData.setCrewXpAmount(0)
        return

    @jsonArgsConverter(('bookId',))
    def __onBuyClicked(self, crewBookCD):
        self._uiLogger.logClick(CrewQuickTrainingKeys.BUY_CREW_BOOK_BUTTON)
        dialogs.showCrewBooksPurchaseDialog(crewBookCD=int(crewBookCD))

    def __onCancel(self, params=None):
        isEsc = params.get(IS_FROM_ESCAPE_PARAM, False) if params else False
        self._uiLogger.logClick(CrewQuickTrainingKeys.ESC_BUTTON if isEsc else CrewQuickTrainingKeys.CANCEL_BUTTON)
        self.__clearSelected()

    def __clearSelected(self, isLearningInProgress=False):
        self._uiData.clear()
        with self.viewModel.transaction() as vm:
            self.__updateBooksViewModelData(vm)
            self.__updateFreeXpBaseModel(vm)
            self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)
        self.crewWidget.clearPossibleSkillsLevelCache()
        self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        if not isLearningInProgress:
            self._updateTmanSkillsLevels('reset')

    @jsonArgsConverter(('intCD',))
    def __onBookMouseEnter(self, intCD):
        self.__clearPreSelectedCard()
        self._uiData.preSelectedBook = int(intCD)
        book = self.itemsCache.items.getItemByCD(int(intCD))
        if book.isPersonal():
            self.__onPersonalBookSelect(1)
            with self.viewModel.transaction() as vm:
                self.__updateCurentFreeXpCardState(vm)
        elif not self._uiData.freeXp and not self.__isPersonalBookSelected():
            self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        if self.IS_MUTUAL_CALCULATIONS_SUPPORTED:
            self._updateTmanSkillsLevels('reset', int(bool(self._uiData.freeXp)))
        else:
            self._updateTmanSkillsLevels('update')

    @jsonArgsConverter(('intCD', 'count'))
    def __onBookSelected(self, intCD, count):
        self.__clearPreSelectedCard()
        book = self.itemsCache.items.getItemByCD(int(intCD))
        self._uiData.updateBooks(intCD, int(count))
        with self.viewModel.transaction() as vm:
            self.__updateBooksViewModelData(vm)
            self.__updateTips(vm, shouldInvalidate=True)
            if book.isPersonal():
                self.__onPersonalBookSelect(count)
                self.__updateCurentFreeXpCardState(vm)
            elif not self._uiData.freeXp and not self.__isPersonalBookSelected():
                self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        if self.IS_MUTUAL_CALCULATIONS_SUPPORTED:
            self._updateTmanSkillsLevels('reset', int(bool(self._uiData.freeXp)))
        else:
            self._updateTmanSkillsLevels('update')
        self._uiLogger.logClick(CrewQuickTrainingKeys.CREW_BOOK_CARD)

    def __onPersonalBookSelect(self, count=0):
        if count > 0:
            isValid = self.__selectedTankmanID and self.__canTmanBeSelectedByContext(self.tankman, False)
            if not self._uiData.freeXp and not isValid:
                self._updateFullTankmenData(isForXp=False)
            self.__updateSlotIndex()
        elif not self._uiData.freeXp:
            self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)

    def __updateSlotIndex(self):
        for slotIdx, tankman in self.crew:
            if tankman and tankman.invID == self.__selectedTankmanID:
                self._crewWidget.updateSlotIdx(slotIdx)
                break

    def __resetCardsStates(self, isBooks=True, isFreeXP=False):
        if isBooks:
            crewBooksViewedCache().addViewedItems(self.nationID)
        with self.viewModel.transaction() as vm:
            self.__setTankmanData(vm, self.__selectedTankmanID, isForXp=isFreeXP)
            if isBooks:
                self.__updateBooksViewModelData(vm)
            if isFreeXP:
                self.__setFreeXPModelData(vm)
                self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)
        self._updateTmanSkillsLevels('update')

    @jsonArgsConverter(('value',))
    def __onFreeXpManualInput(self, value):
        if self.tankman and not isTmanMaxed(self.tankman):
            value = max(min(value, self._stepper.getMaxAvailbleStateCostXp()), 1)
        self._uiData.freeXp = value
        self._updateTmanSkillsLevels('update')

    def __onFreeXpStepperAction(self, data):
        actionType = data.get('actionType', 'update')
        action = int(data.get('action', 0))
        self._updateTmanSkillsLevels(actionType, action)

    def __onFreeXpMouseEnter(self):
        self.__clearPreSelectedCard()
        self.__onSelectFreeXp(True, isUpdate=False)

    def __onCardMouseLeave(self):
        self.__clearPreSelectedCard()
        if self.IS_MUTUAL_CALCULATIONS_SUPPORTED:
            self._updateTmanSkillsLevels('reset', int(bool(self._uiData.freeXp)))
        else:
            self._updateTmanSkillsLevels('update')

    def __clearPreSelectedCard(self):
        if self._uiData.preSelectedBook:
            book = self.itemsCache.items.getItemByCD(self._uiData.preSelectedBook)
            if book.isPersonal():
                self.__onPersonalBookSelect()
        self.__allowSelectedSlotIdx()
        self._uiData.clearPreSelected()

    @jsonArgsConverter(('isSelected',))
    def __onFreeXpSelected(self, isSelected):
        self.__clearPreSelectedCard()
        self.__onSelectFreeXp(isSelected)
        self._uiLogger.logClick(CrewQuickTrainingKeys.FREE_XP_CARD)
        with self.viewModel.transaction() as vm:
            self.__updateTips(vm, shouldInvalidate=True)

    def __onSelectFreeXp(self, isSelected, isUpdate=True):
        if isSelected:
            if self.tankman is not None:
                self.__updateSlotIndex()
                self._updateTmanSkillsLevels('perk', int(isUpdate))
            else:
                self._updateFullTankmenData(isForXp=False)
                self._updateTmanSkillsLevels('reset')
        else:
            self._updateTmanSkillsLevels('reset')
            if not self.__isPersonalBookSelected() and not self._uiData.freeXp:
                self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        return

    def __getValidTankman(self, selectedTankmanID=NO_TANKMAN, slotIdx=NO_SLOT, isForXp=True):
        tankmanId = NO_TANKMAN
        slotId = NO_SLOT

        def _isTankmanValid(tankman, idx):
            if not tankman:
                return False
            isSlotValid = idx == slotIdx and slotIdx != NO_SLOT
            isSelectedTankmanValid = tankman.invID == selectedTankmanID and selectedTankmanID != NO_TANKMAN
            return tankman and (isSlotValid or isSelectedTankmanValid) and self.__canTmanBeSelectedByContext(tankman, isForXp)

        for idx, tankman in self.crew:
            if _isTankmanValid(tankman, idx):
                tankmanId = tankman.invID
                slotId = idx
                break

        if tankmanId == NO_TANKMAN:
            for idx, tankman in self._getCrewBySlotIDX(slotIdx):
                if isForXp and tankmanId == NO_TANKMAN and self.__canTmanBeSelectedByContext(tankman, isForXp=False):
                    tankmanId = tankman.invID
                    slotId = idx
                if self.__canTmanBeSelectedByContext(tankman, isForXp):
                    tankmanId = tankman.invID
                    slotId = idx
                    break
            else:
                if isForXp:
                    self.__onSelectFreeXp(False, isUpdate=False)
        return (tankmanId, slotId)

    def __setTankmanData(self, vm, selectedTankmanID=NO_TANKMAN, slotIdx=NO_SLOT, isForXp=True):
        tankmanId, _ = self.__getValidTankman(selectedTankmanID, slotIdx, isForXp)
        if tankmanId != NO_TANKMAN:
            self.__selectedTankmanID = tankmanId
            vm.setTankmanName(self.tankman.fullUserName)

    def __updateFreeXpBaseModel(self, vm):
        freeXP = self.itemsCache.items.stats.freeXP
        discountRate = self.itemsCache.items.shop.freeXPToTManXPRate
        defaultRate = self.itemsCache.items.shop.defaults.freeXPToTManXPRate
        vm.freeXpData.setPlayerXp(freeXP)
        vm.freeXpData.setDiscountSize(int(round(abs(1 - float(defaultRate) / discountRate) * 100)))
        vm.freeXpData.setExchangeRate(discountRate)

    def __updateCurentFreeXpCardState(self, vm):
        if self.__selectedVehicleID != NO_VEHICLE_ID and self.__selectedTankmanID == NO_TANKMAN:
            canUseFreeXP = any((tankman is not None for _, tankman in self.crew))
        elif self.__selectedTankmanID != NO_TANKMAN:
            canUseFreeXP = self.tankman is not None and not self.tankman.isDismissed
        else:
            canUseFreeXP = False
        vm.freeXpData.setIsEligibleToApplyFreeXp(not canUseFreeXP)
        return

    def __setFreeXPModelData(self, vm):
        if self.tankman:
            self.__updateFreeXpBaseModel(vm)

    def __calculateFreeXpValueXp(self):
        return (self._uiData.freeXp + self._uiData.preSelectedFreeXp) * self.itemsCache.items.shop.freeXPToTManXPRate

    def __calculateLearningBookValueXp(self):
        personalXP = 0
        commonXP = 0
        preSelectBooks = {int(self._uiData.preSelectedBook): 1}
        for bookCD, count in chain(self._uiData.getBooksData().iteritems(), preSelectBooks.iteritems()):
            if count > 0 and bookCD:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if book.isPersonal():
                    personalXP += book.getXP() * count
                else:
                    commonXP += book.getXP() * count

        return (personalXP, commonXP)

    def __setBooksViewModelData(self, vm):
        bookList = vm.getBooksList()
        bookList.clear()
        for book in self.crewBooks:
            bookItem = vm.getBooksListType()()
            self._uiData.addBook(book.intCD)
            self.__fillBookItemModel(bookItem, book)
            bookList.addViewModel(bookItem)

        bookList.invalidate()

    def __updateBooksViewModelData(self, vm):
        bookList = vm.getBooksList()
        for bookItem in bookList:
            book = self.itemsCache.items.getItemByCD(bookItem.getIntCD())
            self.__fillBookItemModel(bookItem, book)

        bookList.invalidate()

    def __fillBookItemModel(self, bookItem, book):
        bookItem.setIntCD(book.intCD)
        bookItem.setType(book.getBookType())
        bookItem.setIcon(book.icon)
        localRoot = R.strings.crew_books.card
        bookTypeRoot = localRoot.dyn(book.getBookSpread()) if book.hasNoNation() else localRoot.nationBook
        if bookTypeRoot.isValid:
            bookTitle = bookTypeRoot.title
            if bookTitle.isValid:
                bookItem.setTitle(backport.text(bookTitle()) if book.isPersonal() else backport.text(bookTitle.dyn(book.getBookType())()))
            bookItem.setMainText(backport.text(bookTypeRoot.mainText()))
            bookItem.setAdditionalText(backport.text(bookTypeRoot.additionalText()))
        bookItem.setBookAddedXp(book.getXP())
        bookItem.setAvailableCount(book.getFreeCount())
        selectCount = self._uiData.getBooksData().get(book.intCD)
        bookItem.setSelectedCount(selectCount)
        bookItem.setIsEligibleForBuy(book.intCD not in self.notInShopItems and book.isForPurchase)
        hasError = self.isCrewEmpty or not book.isPersonal() and (self.isCrewIncomplete or self.hasCrewInvalidSpec)
        bookItem.setHasError(hasError)

    def canTmanBeSelected(self, tman):
        return self.__canTmanBeSelectedByContext(tman, self._uiData.freeXp > 0)

    def __canTmanBeSelectedByContext(self, tman, isForXp=True):
        if tman is None:
            result = False
        elif isForXp:
            result = tman is not None
        else:
            result = self.hasPersonalBook or tman is not None
        return result

    def __isPersonalBookSelected(self):
        for bookCD, count in self._uiData.getBooksData().iteritems():
            if count > 0:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if book.isPersonal():
                    return True

        return False

    @staticmethod
    def __isTankmanInSameClassTank(tankman):
        result = False
        if tankman:
            result = tankman.isInSameClassTank if tankman.isInTank else True
        return result

    def __isSelectionRequired(self):
        return self._uiData.freeXp or self.__isPersonalBookSelected()

    def _onWidgetSlotClick(self, tankmanInvID, slotIdx):
        isForXp = bool(self._uiData.freeXp)
        if isForXp:
            self._crewWidget.updateTankmanId(tankmanInvID)
        self.__updateUiDataForNationBooks()
        with self.viewModel.transaction() as vm:
            self.__setTankmanData(vm, tankmanInvID, slotIdx, isForXp)
            self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)
        if self.__selectedTankmanID != NO_TANKMAN:
            if self.__isSelectionRequired():
                self._crewWidget.updateSlotIdx(slotIdx)
            self._updateTmanSkillsLevels('reset', isForXp and self.tankman is not None)
        self._updateTmanSkillsLevels('reset', isForXp and self.tankman is not None)
        return

    def _getAutoSelectWidget(self, tankmanID, slotIDX):
        return self.__getValidTankman(tankmanID, slotIDX, self._uiData.freeXp > 0)

    def _onTankmanSlotAutoSelect(self, tankmanInvID, slotIdx):
        if self.__selectedTankmanID != tankmanInvID:
            self.__selectedTankmanID = tankmanInvID
            self._onWidgetSlotClick(tankmanInvID, slotIdx)
        if self.__selectedTankmanID == NO_TANKMAN or not self.__isSelectionRequired():
            self.__clearSelected()
        else:
            self._updateTmanSkillsLevels('update')

    def _onEmptySlotAutoSelect(self, _):
        if self.isCrewEmpty:
            super(QuickTrainingView, self)._onEmptySlotAutoSelect(NO_SLOT)
        else:
            self.__resetCardsStates(isBooks=True, isFreeXP=True)
            self.__updateUiDataForNationBooks()

    def __updateUiDataForNationBooks(self):
        for bookCD, count in self._uiData.getBooksData().iteritems():
            if count > 0:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if self.isCrewEmpty or not book.isPersonal() and (self.isCrewIncomplete or self.hasCrewInvalidSpec):
                    self._uiData.updateBooks(bookCD, 0)

    def _updateFullTankmenData(self, selectedTankmanID=None, slotIdx=None, isForXp=True):
        with self.viewModel.transaction() as vm:
            self.__setTankmanData(vm, selectedTankmanID, slotIdx, isForXp)
            self.__updateFreeXpBaseModel(vm)
            self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)

    def __allowSelectedSlotIdx(self):
        if not self._uiData.freeXp and not self.__isPersonalBookSelected():
            self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        elif self.__selectedTankmanID != NO_TANKMAN:
            self.__updateSlotIndex()

    def _updateTmanSkillsLevels(self, actionType='reset', action=0):
        maxValue = self.itemsCache.items.stats.freeXP
        tmanSlotIdx = next((slotIdx for slotIdx, tankman in self.crew if tankman and tankman.invID == self.__selectedTankmanID), NO_SLOT)
        if actionType == 'reset':
            self._uiData.freeXp = 0
            self._uiData.preSelectedFreeXp = 0
        personalXP, commonXP = self.__calculateLearningBookValueXp()
        freeXP = self.__calculateFreeXpValueXp()
        if tmanSlotIdx != NO_SLOT:
            if actionType == 'update':
                if freeXP:
                    self._uiData.freeXp = min(max(1, self._uiData.freeXp), maxValue)
                    freeXP = self.__calculateFreeXpValueXp()
            skillsLevels = quickEarnCrewSkills(self.crew, self.__selectedTankmanID, personalXP + freeXP, commonXP)
            self._stepper.setAvailableSkillsCount(getAvailableSkillsNum(self.tankman))
            self._stepper.setState(*skillsLevels[tmanSlotIdx])
            if actionType in ('reset', 'perk', 'percent'):
                if actionType == 'reset' and action == 1:
                    self._uiData.freeXp = self._stepper.getSkillUpXpState()
                if actionType == 'percent':
                    self._uiData.freeXp += self._stepper.getLevelDownXpState() if action == -1 else self._stepper.getLevelUpXpState()
                elif actionType == 'perk':
                    if not action:
                        self._uiData.preSelectedFreeXp = self._stepper.getSkillUpXpState()
                        self._uiData.preSelectedFreeXp = min(max(1, self._uiData.preSelectedFreeXp), maxValue)
                    else:
                        self._uiData.freeXp += self._stepper.getSkillDownXpState() if action == -1 else self._stepper.getSkillUpXpState()
                if action:
                    self._uiData.freeXp = min(max(1, self._uiData.freeXp), maxValue)
                freeXP = self.__calculateFreeXpValueXp()
                skillsLevels[tmanSlotIdx] = quickEarnTmanSkills(self.tankman, personalXP + freeXP + commonXP)
            self.__setWidgetSkillsModel(skillsLevels)
        with self.viewModel.transaction() as vm:
            vm.freeXpData.setCurrentXpValue(self._uiData.freeXp)
            vm.learningData.setPersonalXpAmount(personalXP + freeXP if self.__isSelectionRequired() else 0)
            vm.learningData.setCrewXpAmount(commonXP)

    def __setWidgetSkillsModel(self, skillsLevels):
        self._crewWidget.updateInteractiveTankmen()
        self._crewWidget.updatePossibleSkillsLevel(skillsLevels)

    def __onTipClose(self, args):
        tipID = int(args.get('id', 0))
        for key, value in TRAINING_TIPS.tips.items():
            if tipID == value:
                if TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER == key:
                    self.__doNotOpenTips.append(TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER)
                    break
                else:
                    self.__closedTips.append(key)
                    break

        with self.viewModel.transaction() as vm:
            self.__updateTips(vm, shouldInvalidate=True, resetClosedTips=False)

    def __updateTips(self, vm, shouldInvalidate=False, resetClosedTips=True):
        tips = vm.getTips()
        playInfoSound = True
        playErrorSound = True
        if resetClosedTips:
            self.__closedTips = []
        for tip in tips:
            if tip.getType() == TipType.INFO:
                playInfoSound = False
            playErrorSound = False

        tips.clear()
        infoTip = None
        personalXP, commonXP = self.__calculateLearningBookValueXp()
        personalXP += self.__calculateFreeXpValueXp()
        if personalXP and self.tankman and isTmanMaxed(self.tankman):
            if TRAINING_TIPS.ENOUGH_EXPERIENCE not in self.__closedTips:
                infoTip = TRAINING_TIPS.ENOUGH_EXPERIENCE
        elif commonXP and self.hasCrewMaxedTman:
            if TRAINING_TIPS.MAXED_CREW_MEMBERS not in self.__closedTips:
                infoTip = TRAINING_TIPS.MAXED_CREW_MEMBERS
        elif self.tankman and self.tankman.isInTank and personalXP and TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER not in self.__doNotOpenTips:
            infoTip = TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER
        if infoTip is not None:
            tips.addViewModel(getTip(infoTip, TipType.INFO))
            if playInfoSound:
                SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_NOTIFICATION)
        errorTip = None
        if self.isCrewIncomplete or self.hasCrewInvalidSpec:
            errorTip = TRAINING_TIPS.NOT_SUITABLE_CREW
        elif self.hasCrewUntrained:
            errorTip = TRAINING_TIPS.NOT_ALL_CURRENT_CREW
        if errorTip is not None:
            tips.addViewModel(getTip(errorTip, TipType.ERROR, self.vehicle.shortUserName))
            if playErrorSound:
                SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_ERROR)
        if shouldInvalidate:
            tips.invalidate()
        return
