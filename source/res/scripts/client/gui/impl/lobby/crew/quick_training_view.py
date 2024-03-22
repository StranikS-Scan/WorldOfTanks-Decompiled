# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/quick_training_view.py
from itertools import chain
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from base_crew_view import BaseCrewView, IS_FROM_ESCAPE_PARAM
from constants import JUNK_TANKMAN_NOVELTY
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
from gui.impl.lobby.crew.crew_helpers.skill_helpers import isTmanMaxed, getAvailableSkillsNum, quickEarnCrewSkills, quickEarnTmanSkills, isCheckEffTankman
from gui.impl.lobby.crew.crew_helpers.stepper_calculator import FreeXpStepperCalculator
from gui.impl.lobby.crew.tooltips.experience_stepper_tooltip import ExperienceStepperTooltip
from gui.impl.lobby.crew.tooltips.quick_training_discount_tooltip import QuickTrainingDiscountTooltip
from gui.impl.lobby.crew.utils import jsonArgsConverter, TRAINING_TIPS, getTip, saveDoNotOpenTip
from gui.shared import event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, MAX_ROLE_LEVEL, NO_TANKMAN, NO_SLOT
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
from gui.impl.lobby.crew.widget.conversion_banner_widget import ConversionBannerWidget
from gui.impl.auxiliary.junk_tankman_helper import JunkTankmanHelper

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
    isCrewEffectiveSkills = property(lambda self: all((not tankman or isCheckEffTankman(tankman) for _, tankman in self.crew)))
    hasCrewInvalidSpec = property(lambda self: any((not self.__canTmanLearnSkills(tankman) for _, tankman in self.crew)))
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
        self.__conversionBannerWidget = ConversionBannerWidget()
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

    def __setIsConversionBannerVisible(self, visibleFlag=-1):
        canShow = JunkTankmanHelper().canShowConversionBanner if visibleFlag == -1 else visibleFlag > 0
        self.__conversionBannerWidget.setWidgetStates()
        if canShow:
            JunkTankmanHelper().setAsShowed(JUNK_TANKMAN_NOVELTY.WIDGET)
        with self.viewModel.transaction() as tx:
            tx.setIsConversionBannerVisible(canShow)

    def _onLoading(self, *args, **kwargs):
        super(QuickTrainingView, self)._onLoading(*args, **kwargs)
        crewBooksViewedCache().addViewedItems(self.nationID)
        self.setChildView(ConversionBannerWidget.LAYOUT_ID(), self.__conversionBannerWidget)
        self.__setIsConversionBannerVisible()

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
         (self.viewModel.onTipClose, self.__onTipClose),
         (JunkTankmanHelper().setIsConversionBannerVisible, self.__setIsConversionBannerVisible))

    def _fillViewModel(self, vm):
        super(QuickTrainingView, self)._fillViewModel(vm)
        self._stepper = FreeXpStepperCalculator()
        self._uiData = UiData()
        self.__setTankmanData(vm, selectedTankmanID=self.__selectedTankmanID)
        vm.setNationName(self.nationName)
        vm.setVehicleName(self.shortUserName)
        self.__setBooksViewModelData(vm)
        self.__setFreeXPModelData(vm)
        self.__updateCurentFreeXpCardState(vm)
        self.__allowSelectedSlotIdx()
        self.__updateTips(vm)

    def _setCrewWidget(self, **kwargs):
        from gui.impl.lobby.crew.widget.crew_widget import QuickTrainingCrewWidget
        tankmanInvID = kwargs.get('tankmanInvID', NO_TANKMAN)
        vehicleInvID = kwargs.get('vehicleInvID', NO_VEHICLE_ID)
        slotIdx = kwargs.get('slotIdx', NO_SLOT)
        previousViewID = kwargs.get('previousViewID', None)
        self._crewWidget = QuickTrainingCrewWidget(tankmanInvID, vehicleInvID, slotIdx, self._currentViewID, previousViewID, self._isHangar)
        if slotIdx == NO_SLOT:
            slotIdx, _, __ = self._crewWidget.getWidgetData()
        self.setChildView(QuickTrainingCrewWidget.LAYOUT_DYN_ACCESSOR(), self._crewWidget)
        self._crewWidget.updateSlotIdx(slotIdx)
        return

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
            compDescr = invDiff[GUI_ITEM_TYPE.TANKMAN].get('compDescr', {})
            vehicleCrew = invDiff[GUI_ITEM_TYPE.TANKMAN].get('vehicle', {})
            if any((value for value in compDescr.itervalues())) or vehicleCrew:
                self.__resetCardsStates(isFreeXP=True)
                if self.__isSelectionRequired():
                    self.__updateSlotIndex()
        if GUI_ITEM_TYPE.CREW_BOOKS in invDiff:
            self.__resetCardsStates(isFreeXP=False)
        return

    def __onFreeXpChanged(self, *_):
        with self.viewModel.transaction() as vm:
            self.__setFreeXPModelData(vm)
        self._updateTmanSkillsLevels('update')

    def __onLearnClicked(self):
        self._uiLogger.logClick(CrewQuickTrainingKeys.SUBMIT_BUTTON)
        SoundGroups.g_instance.playSound2D(SOUNDS.CREW_LEARN_CLICK)
        doActions = []
        if self.__selectedTankmanID != NO_TANKMAN and self.__canTmanUseFreeXP(self.tankman):
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

        BigWorld.player().doActions(doActions)
        self.__clearSelected(isLearningInProgress=True)
        with self.viewModel.transaction() as vm:
            vm.freeXpData.setCurrentXpValue(0)
            vm.learningData.setPersonalXpAmount(0)
            vm.learningData.setCrewXpAmount(0)

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
            if not isLearningInProgress:
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
            self._updateTmanSkillsLevels('reset', int(bool(self._uiData.freeXp)), updateLabels=False)
        else:
            self._updateTmanSkillsLevels('update', updateLabels=False)

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
        if not count and not isCheckEffTankman(self.tankman):
            tankmanInvID, slotIdx = self.__getValidTankman(isFromBegin=True)
            self._onTankmanSlotAutoSelect(tankmanInvID, slotIdx)
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
            prevTmanId = self.__selectedTankmanID
            self.__setTankmanData(vm, selectedTankmanID=self.__selectedTankmanID, isForXp=isFreeXP)
            if isBooks:
                self.__updateBooksViewModelData(vm)
            if isFreeXP:
                self.__setFreeXPModelData(vm)
                self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)
        self.__updateUiDataForNationBooks()
        if prevTmanId == self.__selectedTankmanID:
            self._updateTmanSkillsLevels('update')
        else:
            self._updateTmanSkillsLevels('reset', action=int(isFreeXP))

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
        self.__onSelectFreeXp(True, isUpdate=False, updateLabels=False)

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

    def __onSelectFreeXp(self, isSelected, isUpdate=True, updateLabels=True):
        if isSelected:
            if self.__canTmanUseFreeXP(self.tankman):
                self.__updateSlotIndex()
                self._updateTmanSkillsLevels('perk', int(isUpdate), updateLabels=updateLabels)
            else:
                self._updateFullTankmenData(isForXp=False)
                self._updateTmanSkillsLevels('reset')
        else:
            self._updateTmanSkillsLevels('reset')
            if not self.__isPersonalBookSelected() and not self._uiData.freeXp:
                self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)

    def _getCrewByTankmanID(self, tankmanID, selectedSlotIDX, isFromBegin):
        crew = self.crew
        slotIDX = 0
        for idx, item in enumerate(crew):
            tankmenIdx, tankmen = item
            if tankmen and tankmen.invID == tankmanID or selectedSlotIDX == tankmenIdx or isFromBegin:
                slotIDX = idx
                break

        return crew[slotIDX::] + crew[:slotIDX:] if slotIDX != NO_SLOT else crew

    def __getValidTankman(self, **kwargs):
        selectedTankmanID = kwargs.get('selectedTankmanID', NO_TANKMAN)
        selectedSlotIDX = kwargs.get('slotIdx', NO_SLOT)
        tman = self.itemsCache.items.getTankman(selectedTankmanID)
        effTankman = isCheckEffTankman(tman)
        isInTank = tman and tman.isInTank
        if isInTank and (effTankman or self.__isPersonalBookSelected()):
            return (selectedTankmanID, selectedSlotIDX)
        isFromBegin = True if isInTank and effTankman else kwargs.get('isFromBegin', False)
        isForXp = kwargs.get('isForXp', True)
        crew = self._getCrewByTankmanID(selectedTankmanID, selectedSlotIDX, isFromBegin)
        tankmanID, slotIDX = NO_TANKMAN, NO_SLOT
        for idx, tankman in crew:
            if not tankman:
                continue
            if self.__canTmanBeSelectedByContext(tankman, isForXp):
                if isCheckEffTankman(tankman) or self.__isPersonalBookSelected() and tankman.isInTank:
                    return (tankman.invID, idx)
                tankmanID, slotIDX = tankman.invID, idx
            if tankmanID != NO_TANKMAN and isForXp and self.__canTmanBeSelectedByContext(tankman, isForXp=False):
                tankmanID, slotIDX = tankman.invID, idx

        if isForXp:
            self.__onSelectFreeXp(False, isUpdate=False)
        return (tankmanID, slotIDX)

    def __setTankmanData(self, vm, selectedTankmanID=NO_TANKMAN, slotIdx=NO_SLOT, isForXp=True):
        tankmanId, _ = self.__getValidTankman(selectedTankmanID=selectedTankmanID, slotIdx=slotIdx, isForXp=isForXp)
        if tankmanId != NO_TANKMAN:
            self.__selectedTankmanID = tankmanId
            vm.setTankmanName(self.tankman.getFullUserNameWithSkin())
            if not isCheckEffTankman(self.tankman):
                self.__clearPreSelectedCard()

    def __updateFreeXpBaseModel(self, vm):
        freeXP = self.itemsCache.items.stats.freeXP
        discountRate = self.itemsCache.items.shop.freeXPToTManXPRate
        defaultRate = self.itemsCache.items.shop.defaults.freeXPToTManXPRate
        vm.freeXpData.setPlayerXp(freeXP)
        vm.freeXpData.setDiscountSize(int(round(abs(1 - float(defaultRate) / discountRate) * 100)))
        vm.freeXpData.setExchangeRate(discountRate)
        if self.tankman and isCheckEffTankman(self.tankman):
            vm.freeXpData.setIsEligibleToApplyFreeXp(not True)

    def __updateCurentFreeXpCardState(self, vm):
        if not isCheckEffTankman(self.tankman):
            canUseFreeXP = False
        elif self.__selectedVehicleID != NO_VEHICLE_ID and self.__selectedTankmanID == NO_TANKMAN:
            canUseFreeXP = any((self.__canTmanUseFreeXP(tankman) for _, tankman in self.crew))
        elif self.__selectedTankmanID != NO_TANKMAN:
            canUseFreeXP = self.__canTmanUseFreeXP(self.tankman) and not self.tankman.isDismissed
        else:
            canUseFreeXP = False
        vm.freeXpData.setHasError(not canUseFreeXP)
        vm.freeXpData.setIsEligibleToApplyFreeXp(not canUseFreeXP)

    def __setFreeXPModelData(self, vm):
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
        hasError = self.isCrewEmpty or not book.isPersonal() and (self.isCrewIncomplete or self.hasCrewInvalidSpec or not self.isCrewEffectiveSkills)
        bookItem.setHasError(hasError)

    def canTmanBeSelected(self, tman):
        return self.__canTmanBeSelectedByContext(tman, self._uiData.freeXp > 0)

    def __canTmanBeSelectedByContext(self, tman, isForXp=True):
        if tman is None:
            result = False
        elif isForXp and isCheckEffTankman(tman):
            result = self.__canTmanUseFreeXP(tman)
        else:
            result = self.hasPersonalBook or self.__canTmanUseFreeXP(tman)
        return result

    def __isPersonalBookSelected(self):
        for bookCD, count in self._uiData.getBooksData().iteritems():
            if count > 0:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if book.isPersonal():
                    return True

        return False

    def __isFreeXpSelected(self):
        return isCheckEffTankman(self.tankman) and (self._uiData.preSelectedFreeXp > 0 or self._uiData.freeXp > 0)

    @staticmethod
    def __canTmanLearnSkills(tankman):
        result = False
        if tankman:
            if not tankman.isInTank:
                result = tankman.realRoleLevel.lvl >= MAX_ROLE_LEVEL
            else:
                result = tankman.isInNativeTank and tankman.isMaxRoleLevel
        return result

    @staticmethod
    def __canTmanUseFreeXP(tankman):
        return tankman is not None and tankman.isMaxRoleLevel and isCheckEffTankman(tankman)

    def __allExistTankmanHasValidSpec(self):
        for _, tankman in self.crew:
            if tankman:
                if not tankman.isInTank:
                    if tankman.realRoleLevel.lvl < MAX_ROLE_LEVEL:
                        return False
                elif not tankman.isInNativeTank or not tankman.isMaxRoleLevel:
                    return False

        return True

    def __isSelectionRequired(self):
        return self._uiData.freeXp or self.__isPersonalBookSelected()

    def _onWidgetSlotClick(self, tankmanInvID, slotIdx):
        isForXp = bool(self._uiData.freeXp)
        if isForXp:
            self._crewWidget.updateTankmanId(tankmanInvID)
        self.__updateUiDataForNationBooks()
        with self.viewModel.transaction() as vm:
            self.__setTankmanData(vm, selectedTankmanID=tankmanInvID, slotIdx=slotIdx, isForXp=isForXp)
            self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)
        if self.__selectedTankmanID != NO_TANKMAN:
            if self.__isSelectionRequired():
                self._crewWidget.updateSlotIdx(slotIdx)
            canTmanUseFreeXP = self.__canTmanUseFreeXP(self.tankman)
            if not canTmanUseFreeXP and not self.__isPersonalBookSelected():
                self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
            self._updateTmanSkillsLevels('reset', isForXp and canTmanUseFreeXP)
        self._updateTmanSkillsLevels('reset', isForXp and self.__canTmanUseFreeXP(self.tankman))

    def _getAutoSelectWidget(self, tankmanID, slotIDX):
        return self.__getValidTankman(selectedTankmanID=tankmanID, slotIdx=slotIDX, isForXp=self._uiData.freeXp > 0)

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

    def __updateUiDataForNationBooks(self):
        for bookCD, count in self._uiData.getBooksData().iteritems():
            if count > 0:
                book = self.itemsCache.items.getItemByCD(bookCD)
                if self.isCrewEmpty or not book.isPersonal() and (self.isCrewIncomplete or self.hasCrewInvalidSpec):
                    self._uiData.updateBooks(bookCD, 0)

    def _updateFullTankmenData(self, selectedTankmanID=None, slotIdx=None, isForXp=True):
        with self.viewModel.transaction() as vm:
            self.__setTankmanData(vm, selectedTankmanID=selectedTankmanID, slotIdx=slotIdx, isForXp=isForXp)
            self.__updateFreeXpBaseModel(vm)
            self.__updateCurentFreeXpCardState(vm)
            self.__updateTips(vm, shouldInvalidate=True)

    def __allowSelectedSlotIdx(self):
        if not self._uiData.freeXp and not self.__isPersonalBookSelected():
            self._crewWidget.viewModel.setSelectedSlotIdx(NO_SLOT)
        elif self.__selectedTankmanID != NO_TANKMAN:
            self.__updateSlotIndex()

    def _updateTmanSkillsLevels(self, actionType='reset', action=0, updateLabels=True):
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
            skillsLevels, skillsEffLevels = quickEarnCrewSkills(self.crew, self.__selectedTankmanID, personalXP + freeXP, commonXP)
            self._stepper.setAvailableSkillsCount(getAvailableSkillsNum(self.tankman))
            self._stepper.setState(*skillsLevels[tmanSlotIdx])
            if actionType in ('reset', 'perk', 'percent'):
                if actionType == 'reset' and action == 1:
                    self._uiData.freeXp = self._stepper.getSkillUpXpState()
                if actionType == 'percent':
                    self._uiData.freeXp += self._stepper.getLevelDownXpState() if action == -1 else self._stepper.getLevelUpXpState()
                elif actionType == 'perk':
                    if not action:
                        self._uiData.preSelectedFreeXp = min(max(1, self._stepper.getSkillUpXpState()), maxValue)
                    else:
                        self._uiData.freeXp += self._stepper.getSkillDownXpState() if action == -1 else self._stepper.getSkillUpXpState()
                if action:
                    self._uiData.freeXp = min(max(1, self._uiData.freeXp), maxValue)
                freeXP = self.__calculateFreeXpValueXp()
                skillsLevels[tmanSlotIdx], skillsEffLevels[tmanSlotIdx] = quickEarnTmanSkills(self.tankman, personalXP + freeXP + commonXP)
            self.__setWidgetSkillsModel(skillsLevels, skillsEffLevels)
        if updateLabels:
            with self.viewModel.transaction() as vm:
                vm.freeXpData.setCurrentXpValue(self._uiData.freeXp)
                vm.learningData.setPersonalXpAmount(personalXP + freeXP if self.__isSelectionRequired() else 0)
                vm.learningData.setCrewXpAmount(commonXP)

    def __setWidgetSkillsModel(self, skillsLevels, skillsEffLevels):
        self._crewWidget.updateInteractiveTankmen(self.__isFreeXpSelected())
        self._crewWidget.updatePossibleSkillsLevel(skillsLevels, skillsEffLevels)

    def __playErrorPersonalFileTips(self):
        personalXP, _ = self.__calculateLearningBookValueXp()
        personalXP += self.__calculateFreeXpValueXp()
        return True if self.tankman and not isCheckEffTankman(self.tankman) and (personalXP or not self.tankman.isInTank) else None

    def __playErrorTips(self, tips, playSound):
        isCrewIncomplete = self.isCrewIncomplete
        isCrewEffectiveSkills = self.isCrewEffectiveSkills
        allExistTakmanHasValidSpec = self.__allExistTankmanHasValidSpec()
        if self.__playErrorPersonalFileTips():
            tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_TIPS_PERSONAL, TipType.ERROR, tankman=self.tankman.getFullUserNameWithSkin()))
        elif not isCrewEffectiveSkills:
            if isCrewIncomplete and not allExistTakmanHasValidSpec:
                tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_NOT_TRAINED_NOT_FULL, TipType.ERROR))
            elif isCrewIncomplete:
                tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_NOT_FULL_CREW, TipType.ERROR))
            elif not allExistTakmanHasValidSpec:
                tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_NOT_TRAINED_CREW, TipType.ERROR))
            else:
                tips.addViewModel(getTip(TRAINING_TIPS.LOW_PE_CREW, TipType.ERROR))
        elif isCrewIncomplete and not allExistTakmanHasValidSpec:
            tips.addViewModel(getTip(TRAINING_TIPS.NOT_FULL_AND_NOT_TRAINED_CREW, TipType.ERROR))
        elif isCrewIncomplete:
            tips.addViewModel(getTip(TRAINING_TIPS.NOT_FULL_CREW, TipType.ERROR))
        elif not allExistTakmanHasValidSpec:
            tips.addViewModel(getTip(TRAINING_TIPS.NOT_TRAINED_THIS_VEHICLE, TipType.ERROR))
        if playSound:
            SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_ERROR)

    def __onTipClose(self, args):
        tipID = int(args.get('id', 0))
        for key, value in TRAINING_TIPS.tips.items():
            if tipID == value:
                if TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER == key:
                    self.__doNotOpenTips.append(TRAINING_TIPS.CHOOSE_ANY_CREW_MEMBER)
                    saveDoNotOpenTip(key)
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
        self.__playNotificationTips(tips, playInfoSound)
        self.__playErrorTips(tips, playErrorSound)
        if shouldInvalidate:
            tips.invalidate()

    def __playNotificationTips(self, tips, playSound=False):
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
        if infoTip:
            tips.addViewModel(getTip(infoTip, TipType.INFO))
            if playSound:
                SoundGroups.g_instance.playSound2D(SOUNDS.CREW_TIPS_NOTIFICATION)
        return
