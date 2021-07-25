# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew_books/crew_books_view.py
from CurrentVehicle import g_currentVehicle
from async import async, await
from frameworks.wulf import ViewFlags, ViewStatus, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import TankmanModelPresenter, TankmanSkillListPresenter, crewBooksViewedCache
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew_books.crew_book_item_model import CrewBookItemModel
from gui.impl.gen.view_models.views.lobby.crew_books.crew_book_lack_item_model import CrewBookLackItemModel
from gui.impl.gen.view_models.views.lobby.crew_books.crew_books_lack_view_model import CrewBooksLackViewModel
from gui.impl.gen.view_models.views.lobby.crew_books.crew_books_tooltips import CrewBooksTooltips
from gui.impl.gen.view_models.views.lobby.crew_books.crew_books_view_model import CrewBooksViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel
from gui.shared import events, g_eventBus, event_dispatcher
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import sortCrew, getIconResourceName
from gui.shared.gui_items.crew_book import sortItems
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.filters import switchHangarFilteredFilter
from helpers.dependency import descriptor
from items.components.component_constants import EMPTY_STRING
from items.components.crew_books_constants import CREW_BOOK_INVALID_TYPE, CREW_BOOK_RARITY
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class CrewBooksView(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __gui = descriptor(IGuiLoader)
    MIN_ROLE_LEVEL = 100
    __slots__ = ('__vehicle', '__bookGuiItemList', '__selectedBookGuiItem', '__selectedTankmanVM', '__selectedBookIndex', '__selectedBookIndex', '__invalidTypes')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew_books.crew_books_view.CrewBooksView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CrewBooksViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CrewBooksView, self).__init__(settings)
        self.__selectedTankmanVM = None
        self.__selectedBookGuiItem = None
        self.__selectedBookIndex = None
        self.__vehicle = g_currentVehicle.item
        crewBooksViewedCache().addViewedItems(self.__vehicle.nationID)
        return

    @property
    def viewModel(self):
        return super(CrewBooksView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        return super(CrewBooksView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(CrewBooksView, self)._initialize()
        switchHangarFilteredFilter(on=True)
        with self.viewModel.transaction() as vm:
            vm.setFlagIcon(R.images.gui.maps.icons.crewBooks.flags.dyn(getIconResourceName(self.__vehicle.nationName))())
            self.__setBooksViewModelData(vm)
            self.__setTankmenListModelData(vm)
            self.__setInvalidTypes()
            vm.setScreenDesc(R.strings.crew_books.screen.description.empty_tank() if CREW_BOOK_INVALID_TYPE.EMPTY_CREW in self.__invalidTypes else R.strings.crew_books.screen.description())
        self.__addListeners()
        self.__updateFooterDescription()
        self.__updateIsBookUseEnable()

    def _finalize(self):
        self.__removeListeners()
        crewBooksViewedCache().addViewedItems(self.__vehicle.nationID)
        self.__vehicle = None
        self.__bookGuiItemList = None
        self.__selectedTankmanVM = None
        self.__selectedBookIndex = None
        self.__invalidTypes = None
        switchHangarFilteredFilter(on=False)
        super(CrewBooksView, self)._finalize()
        return

    def __setInvalidTypes(self):
        self.__invalidTypes = []
        emptyTankmen = 0
        invalidSkill = 0
        invalidSpeciality = 0
        for _, tankman in self.__vehicle.crew:
            if tankman is None:
                emptyTankmen += 1
            if tankman.roleLevel < self.MIN_ROLE_LEVEL:
                invalidSkill += 1
            if tankman.vehicleDescr.type.compactDescr != tankman.vehicleNativeDescr.type.compactDescr:
                invalidSpeciality += 1

        if emptyTankmen == len(self.__vehicle.crew):
            self.__invalidTypes.append(CREW_BOOK_INVALID_TYPE.EMPTY_CREW)
        elif emptyTankmen > 0:
            self.__invalidTypes.append(CREW_BOOK_INVALID_TYPE.INCOMPLETE_CREW)
        if invalidSkill > 0:
            self.__invalidTypes.append(CREW_BOOK_INVALID_TYPE.INVALID_SKILL)
        if invalidSpeciality > 0:
            self.__invalidTypes.append(CREW_BOOK_INVALID_TYPE.INVALID_SPECIALITY)
        return

    def __setBooksViewModelData(self, screenVM):
        bookListVM = screenVM.getCrewBookItemList()
        bookListVM.clear()
        booksIcons = R.images.gui.maps.icons.crewBooks.books.large
        self.__updateGuiItemList()
        notInShopItems = self.__itemsCache.items.shop.getHiddens()
        isCrewBooksPurchaseEnabled = self.__lobbyContext.getServerSettings().isCrewBooksPurchaseEnabled()
        for _, book in enumerate(self.__bookGuiItemList):
            amount = book.getFreeCount()
            bookSpread = book.getBookSpread()
            bookVM = CrewBookItemModel()
            bookVM.setAmount(amount)
            bookVM.setCompactDesc(book.intCD)
            bookVM.setIsSelected(False)
            bookVM.setIsDisabled(amount == 0)
            bookVM.setTitle(R.strings.crew_books.screen.bookType.dyn(book.getBookType())())
            purchaseEnable = True if book.intCD not in notInShopItems and isCrewBooksPurchaseEnabled else False
            bookVM.setIsInShop(purchaseEnable)
            descriptionFmtArgsVM = bookVM.getDescriptionFmtArgs()
            descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(book.getXP()), 'exp', R.styles.ExpTextStyle()))
            bookVM.setDescription(R.strings.crew_books.screen.bookType.dyn(bookSpread).info.title())
            bookNation = book.getNation()
            overlayDescriptionFmtArgsVM = bookVM.getOverlayDescriptionFmtArgs()
            overlayDescriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__vehicle.shortUserName, 'short_name', R.styles.NeutralTextStyle()))
            if bookNation is not None:
                bookVM.setOverlayDescription(R.strings.crew_books.screen.bookType.dyn(bookSpread).info.body.dyn(bookNation)())
            else:
                bookVM.setOverlayDescription(R.strings.crew_books.screen.bookType.dyn(bookSpread).info.body())
            bookVM.setBookIcon(booksIcons.dyn(getIconResourceName(book.icon))())
            bookListVM.addViewModel(bookVM)

        return

    def __setTankmenListModelData(self, screenVM):
        crewListVM = screenVM.crewBookTankmenList.getItems()
        roles = self.__vehicle.descriptor.type.crewRoles
        crew = sortCrew(self.__vehicle.crew, roles)
        for index, (_, tankman) in enumerate(crew):
            tankmanInvID = tankman.invID if tankman is not None else None
            tankmanVM = TankmanModelPresenter().getModel(index, tankmanInvID)
            if tankmanInvID is not None:
                self.__setSkillListViewModelData(tankmanVM)
            crewListVM.addViewModel(tankmanVM)

        return

    def __setSkillListViewModelData(self, tankmanVM, showGainedProgress=False):
        skillListVM = tankmanVM.tankmanSkillList.getItems()
        skillListVM.clear()
        if self.__selectedBookGuiItem is not None and showGainedProgress:
            bookIntCD = self.__selectedBookGuiItem.intCD
        else:
            bookIntCD = None
        tankmanVM.tankmanSkillList.setItems(TankmanSkillListPresenter().getList(int(tankmanVM.getInvID()), True, bookIntCD))
        isEmptySkills = len(tankmanVM.tankmanSkillList.getItems()) == 0
        tankmanVM.setIsSkillsEmpty(isEmptySkills)
        tankmanVM.tankmanSkillList.getItems().invalidate()
        return

    def __onInventoryUpdate(self, invDiff):
        with self.viewModel.transaction() as vm:
            if GUI_ITEM_TYPE.TANKMAN in invDiff:
                self.__updateTankmenListModelData(vm, invDiff[GUI_ITEM_TYPE.TANKMAN])
            if GUI_ITEM_TYPE.CREW_BOOKS in invDiff:
                self.__updateBooksViewModelData(vm)

    def __updateGuiItemList(self):
        criteria = REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT ^ ~REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(CREW_BOOK_RARITY.NO_NATION_TYPES)
        criteria |= REQ_CRITERIA.CREW_ITEM.NATIONS([self.__vehicle.nationID])
        items = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, criteria)
        self.__bookGuiItemList = sortItems(items.values())

    def __updateBooksViewModelData(self, screenVM):
        self.__setBooksViewModelData(screenVM)
        self.__selectedBookGuiItem = None
        self.__selectedBookIndex = None
        bookListVM = screenVM.getCrewBookItemList()
        availableBookCount = sum((not book.getIsDisabled() for book in bookListVM))
        if availableBookCount == 0 and self.viewStatus == ViewStatus.LOADED and not self.viewModel.getIsDialogOpen():
            self.__openLackView()
        else:
            self.__updateCrew()
            self.__updateIsBookUseEnable()
            self.__updateFooterDescription()
            bookListVM.invalidate()
        return

    def __openLackView(self):
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.crew_books.crew_books_lack_view.CrewBooksLackView(), CrewBooksLackView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateTankmenListModelData(self, screenVM, diff):
        crewListVM = screenVM.crewBookTankmenList.getItems()
        self.__vehicle = g_currentVehicle.item
        roles = self.__vehicle.descriptor.type.crewRoles
        crew = sortCrew(self.__vehicle.crew, roles)
        crewDiff = [ (i, tankman) for i, (_, tankman) in enumerate(crew) if tankman is not None and tankman.invID in diff['compDescr'] ]
        for slotIdx, tankman in crewDiff:
            tankmanVM = crewListVM[slotIdx]
            tankmanVM.setRoleLevel(str(tankman.roleLevel))
            tankmanVM.setIsLowRoleLevel(tankman.roleLevel < self.MIN_ROLE_LEVEL)
            self.__setSkillListViewModelData(tankmanVM)

        crewListVM.invalidate()
        self.__setInvalidTypes()
        return

    def __addListeners(self):
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onTankmanClick += self.__onTankmanClick
        self.viewModel.onCrewBookClick += self.__onCrewBookClick
        self.viewModel.onBookUse += self.__onBookUse
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})

    def __removeListeners(self):
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onTankmanClick -= self.__onTankmanClick
        self.viewModel.onCrewBookClick -= self.__onCrewBookClick
        self.viewModel.onBookUse -= self.__onBookUse
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        g_clientUpdateManager.removeCallback('inventory', self.__onInventoryUpdate)

    def __onWindowClose(self):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()

    @async
    def __onBuyBtnClick(self, args):
        self.viewModel.setIsDialogOpen(True)
        yield await(dialogs.buyCrewBook(parent=self, crewBookCD=int(args['compactDesc'])))
        self.viewModel.setIsDialogOpen(False)

    @async
    def __onBookUse(self):
        if self.__selectedTankmanVM is not None:
            tankmanInvId = self.__selectedTankmanVM.getInvID()
        else:
            tankmanInvId = 0
        self.viewModel.setIsDialogOpen(True)
        yield await(dialogs.useCrewBook(parent=self, crewBookCD=self.__selectedBookGuiItem.intCD, vehicleIntCD=self.__vehicle.intCD, tankmanInvId=tankmanInvId))
        self.viewModel.setIsDialogOpen(False)
        availableBookCount = sum((not book.getIsDisabled() for book in self.viewModel.getCrewBookItemList()))
        if availableBookCount == 0 and self.viewStatus == ViewStatus.LOADED:
            self.__openLackView()
        return

    def __onCrewBookClick(self, args):
        if self.__selectedBookIndex is not None:
            self.viewModel.getCrewBookItemList()[self.__selectedBookIndex].setIsSelected(False)
        self.__selectedBookIndex = int(args['index'])
        crewBookItemList = self.viewModel.getCrewBookItemList()
        crewBookItemList[self.__selectedBookIndex].setIsSelected(True)
        crewBookItemList.invalidate()
        self.__selectedBookGuiItem = self.__bookGuiItemList[self.__selectedBookIndex]
        self.__updateCrew()
        self.__updateIsBookUseEnable()
        self.__updateFooterDescription()
        return

    def __onTankmanClick(self, args):
        clickedTankmanIndex = int(args['index'])
        with self.viewModel.transaction() as vm:
            crewListVM = vm.crewBookTankmenList.getItems()
            for tankmanVM in crewListVM:
                if tankmanVM.getIsEmpty():
                    continue
                tankmanVM.setIsArrowAnimPlay(False)

            if self.__selectedTankmanVM is not None:
                self.__setStates(self.__selectedTankmanVM, False)
                self.__setSkillListViewModelData(self.__selectedTankmanVM)
            tankmanVM = crewListVM[clickedTankmanIndex]
            self.__setStates(tankmanVM, True)
            self.__selectedTankmanVM = tankmanVM
            self.__setTankmanGainExp(self.__selectedTankmanVM)
            self.__setSkillListViewModelData(self.__selectedTankmanVM, True)
        self.__updateIsBookUseEnable()
        self.__updateFooterDescription()
        return

    def __updateCrew(self):
        self.__selectedTankmanVM = None
        if self.__selectedBookGuiItem is None:
            self.__setNoBookSelectedStates()
        else:
            self.__setCrewBookSelectedStates()
        return

    def __setCrewBookSelectedStates(self):
        with self.viewModel.transaction() as vm:
            crewListVM = vm.crewBookTankmenList.getItems()
            for tankmanVM in crewListVM:
                if tankmanVM.getIsEmpty():
                    continue
                if tankmanVM.getIsLowRoleLevel() or tankmanVM.getIsWrongVehicle():
                    tankmanVM.setIsLearnDisable(True)
                    tankmanVM.setIsClickEnable(False)
                    tankmanVM.setIsTankamanSelected(False)
                    tankmanVM.setIsArrowAnimPlay(False)
                    self.__setSkillListViewModelData(tankmanVM)
                if self.__invalidTypes or self.__selectedBookGuiItem.getFreeCount() == 0:
                    tankmanVM.setIsClickEnable(False)
                    tankmanVM.setIsTankamanSelected(False)
                    tankmanVM.setIsArrowAnimPlay(False)
                    self.__setSkillListViewModelData(tankmanVM)
                tankmanVM.setIsArrowAnimPlay(False)
                self.__setStates(tankmanVM, True)
                self.__setSkillListViewModelData(tankmanVM, True)

    def __setPersonalBookSelectedStates(self):
        with self.viewModel.transaction() as vm:
            crewListVM = vm.crewBookTankmenList.getItems()
            for tankmanVM in crewListVM:
                if tankmanVM.getIsEmpty():
                    continue
                if self.__selectedBookGuiItem.getFreeCount() == 0:
                    tankmanVM.setIsClickEnable(False)
                    tankmanVM.setIsTankamanSelected(False)
                else:
                    tankmanVM.setIsLearnDisable(False)
                    tankmanVM.setIsArrowAnimPlay(True)
                    self.__setStates(tankmanVM, False)
                self.__setSkillListViewModelData(tankmanVM)

    def __setNoBookSelectedStates(self):
        with self.viewModel.transaction() as vm:
            crewListVM = vm.crewBookTankmenList.getItems()
            for tankmanVM in crewListVM:
                if tankmanVM.getIsEmpty():
                    continue
                tankmanVM.setIsClickEnable(False)
                tankmanVM.setIsTankamanSelected(False)
                tankmanVM.setIsArrowAnimPlay(False)
                self.__setSkillListViewModelData(tankmanVM)

    def __setStates(self, tankmanVM, isSelected):
        tankmanVM.setIsClickEnable(not isSelected)
        tankmanVM.setIsTankamanSelected(isSelected)
        if isSelected:
            self.__setTankmanGainExp(tankmanVM)

    def __setTankmanGainExp(self, tankmanVM):
        tankmanVM.setTankmanGainExp(self.__gui.systemLocale.getNumberFormat(self.__selectedBookGuiItem.getXP()))

    def __updateIsBookUseEnable(self):
        with self.viewModel.transaction() as vm:
            if self.__selectedBookGuiItem is None:
                vm.setIsBookUseEnable(False)
            elif self.__selectedBookGuiItem.getFreeCount() == 0:
                vm.setIsBookUseEnable(False)
            else:
                vm.setIsBookUseEnable(not self.__invalidTypes)
        return

    def __updateFooterDescription(self):
        footerTitleFmtArgs = self.viewModel.getFooterTitleFmtArgs()
        footerTitleFmtArgs.clear()
        footerTitleFmtArgs.invalidate()
        if self.__selectedBookGuiItem is None:
            self.__setNoBookSelectedFooterDescription()
        else:
            self.__setCrewBookFooterDescription()
        footerTitleFmtArgs.invalidate()
        return

    def __setNoBookSelectedFooterDescription(self):
        with self.viewModel.transaction() as vm:
            if CREW_BOOK_INVALID_TYPE.EMPTY_CREW in self.__invalidTypes:
                vm.setFooterIcon(R.images.gui.maps.icons.library.alertBigIcon())
                vm.setFooterTitle(R.strings.crew_books.screen.info.empty_tank.title())
                vm.setTooltipBody(R.strings.crew_books.screen.info.empty_tank.title())
                vm.setIsFooterAlert(True)
                vm.setIsInvalidTooltipEnable(True)
                vm.setIsSimpleInvalidTooltip(True)
            else:
                vm.setFooterIcon(R.images.gui.maps.icons.library.InformationIcon())
                vm.setFooterTitle(R.strings.crew_books.screen.info.selectBook.title())

    def __setCrewBookFooterDescription(self):
        with self.viewModel.transaction() as vm:
            vm.setIsSimpleInvalidTooltip(False)
            vm.setIsInvalidTooltipEnable(False)
            vm.setIsFooterAlert(False)
            vm.setFooterIcon(R.images.gui.maps.icons.library.InformationIcon())
            if self.__selectedBookGuiItem.getFreeCount() == 0:
                vm.setIsInvalidTooltipEnable(True)
                vm.setIsSimpleInvalidTooltip(True)
                vm.setFooterTitle(R.strings.tooltips.crewBooks.screen.invalidItem.title())
                vm.setTooltipBody(R.strings.tooltips.crewBooks.screen.invalidItem.title())
            elif self.__invalidTypes:
                vm.setFooterIcon(R.images.gui.maps.icons.library.alertBigIcon())
                vm.setIsFooterAlert(True)
                vm.setIsInvalidTooltipEnable(True)
                if CREW_BOOK_INVALID_TYPE.EMPTY_CREW in self.__invalidTypes:
                    vm.setIsSimpleInvalidTooltip(True)
                elif CREW_BOOK_INVALID_TYPE.INCOMPLETE_CREW in self.__invalidTypes:
                    vm.setFooterTitle(R.strings.crew_books.screen.info.incompleteCrew.title())
                else:
                    vm.setFooterTitle(R.strings.crew_books.screen.info.invalidCrew.title())
            else:
                vm.setFooterTitle(R.strings.crew_books.screen.info.crewBook.title())
                footerTitleFmtArgs = vm.getFooterTitleFmtArgs()
                footerTitleFmtArgs.addViewModel(UserFormatStringArgModel(self.__selectedBookGuiItem.userName, 'book_type'))
                footerTitleFmtArgs.addViewModel(UserFormatStringArgModel(self.__gui.systemLocale.getNumberFormat(self.__selectedBookGuiItem.getXP()), 'exp'))

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == CrewBooksTooltips.TOOLTIP_TANKMAN:
            args = [int(event.getArgument('invID'))]
        elif tooltipId == CrewBooksTooltips.TOOLTIP_TANKMAN_SKILL:
            args = [event.getArgument('skillName'), int(event.getArgument('tankmanInvId'))]
        elif tooltipId == CrewBooksTooltips.TOOLTIP_TANKMAN_NEW_SKILL:
            args = [int(event.getArgument('tankmanInvId'))]
        else:
            args = [self.__vehicle.invID]
        return TooltipData(tooltip=tooltipId, isSpecial=True, specialAlias=tooltipId, specialArgs=args)


class CrewBooksLackView(ViewImpl):
    STATE_INVALID_CREW = 'invalidCrew'
    STATE_NO_ITEMS = 'noItems'
    FIRST_SLOT = 1
    THIRD_SLOT = 3
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __slots__ = ('__vehicle', '__booksOnStock', '__existBooks')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew_books.crew_books_lack_view.CrewBooksLackView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CrewBooksLackViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CrewBooksLackView, self).__init__(settings)
        self.__vehicle = g_currentVehicle.item
        self.__booksOnStock = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        self.__existBooks = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.NATIONS([self.__vehicle.nationID]))

    @property
    def viewModel(self):
        return super(CrewBooksLackView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(CrewBooksLackView, self)._initialize()
        switchHangarFilteredFilter(on=True)
        self.__setNoBooksViewModelData()
        self.__addListeners()

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        self.__removeListeners()
        self.__vehicle = None
        self.__booksOnStock = None
        self.__existBooks = None
        super(CrewBooksLackView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.onBuyBtnClick += self.__onBuyBtnClick
        self.viewModel.onHangarBtnClick += self.__onHangarBtnClick
        self.viewModel.onCloseBtnClick += self.__onWindowClose

    def __removeListeners(self):
        self.viewModel.onBuyBtnClick -= self.__onBuyBtnClick
        self.viewModel.onHangarBtnClick -= self.__onHangarBtnClick
        self.viewModel.onCloseBtnClick -= self.__onWindowClose

    def __onWindowClose(self):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()

    @async
    def __onBuyBtnClick(self):
        crewBookCD = next((crewBook.intCD for crewBook in self.__existBooks.itervalues() if crewBook.getBookType() == CREW_BOOK_RARITY.CREW_EPIC), None)
        if crewBookCD is None:
            return
        else:
            self.viewModel.setIsDialogOpen(True)
            result = yield await(dialogs.buyCrewBook(parent=self, crewBookCD=int(crewBookCD)))
            self.viewModel.setIsDialogOpen(False)
            if result is True:
                g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.crew_books.crew_books_view.CrewBooksView(), CrewBooksView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def __onHangarBtnClick(self):
        event_dispatcher.selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()

    def __setNoBooksViewModelData(self):
        isCrewBooksPurchaseEnabled = self.__lobbyContext.getServerSettings().isCrewBooksPurchaseEnabled()
        with self.viewModel.transaction() as vm:
            vm.setFlagIcon(R.images.gui.maps.icons.crewBooks.flags.dyn(getIconResourceName(self.__vehicle.nationName))())
            if isCrewBooksPurchaseEnabled:
                vm.setFooterDescription(R.strings.crew_books.screen.slides.purchaseEnabled.info())
            else:
                vm.setIsCrewBooksPurchaseEnabled(False)
            if self.__booksOnStock:
                vm.setScreenDescription(R.strings.crew_books.screen.description.invalidCrew.dyn(self.__vehicle.nationName)())
                if not isCrewBooksPurchaseEnabled:
                    bookNationsOnStock = set((item.getNation() for item in self.__booksOnStock.itervalues() if item.getNation() is not None))
                    nationNames = EMPTY_STRING
                    for j, nation in enumerate(bookNationsOnStock):
                        formatter = '' if j == len(bookNationsOnStock) - 1 else ', '
                        nationNames += backport.text(R.strings.nations.dyn(nation)()) + formatter

                    descriptionFmtArgsVM = vm.getFooterDescriptionFmtArgs()
                    descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(nationNames, 'nation'))
                    descriptionFmtArgsVM.invalidate()
                    vm.setFooterDescription(R.strings.crew_books.screen.slides.invalidCrew.info())
                self.__setSlidesData(self.STATE_INVALID_CREW, vm)
            else:
                vm.setScreenDescription(R.strings.crew_books.screen.description.noItems())
                vm.setNoBooksOnStock(True)
                self.__setSlidesData(self.STATE_NO_ITEMS, vm)

    def __setSlidesData(self, state, vm):
        noBookList = vm.noBooksList.getItems()
        for i in xrange(1, 4):
            itemModel = CrewBookLackItemModel()
            itemModel.setIcon(R.images.gui.maps.icons.crewBooks.noBooks.dyn(state).num(i)())
            itemModel.setTitle(R.strings.crew_books.screen.slides.dyn(state).num(i).title())
            itemModel.setDescription(R.strings.crew_books.screen.slides.dyn(state).num(i).body())
            if state == self.STATE_INVALID_CREW and i == self.FIRST_SLOT:
                descriptionFmtArgsVM = itemModel.getDescriptionFmtArgs()
                descriptionFmtArgsVM.addViewModel(UserFormatStringArgModel(self.__vehicle.nationUserName, 'nation'))
                descriptionFmtArgsVM.invalidate()
            if i == self.THIRD_SLOT:
                itemModel.setHasArrow(False)
            noBookList.addViewModel(itemModel)
