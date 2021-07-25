# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/progression_view.py
import logging
import typing
import nations
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from async import async, await
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentTopPanelModel, fillDetachmentPreviewInfo
from gui.impl.dialogs.dialogs import showApplyCrewBookDetachmentDialogView, showConfirmCrewBookPurchaseDetachmentDialogView, showApplyExpExchangeDetachmentDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_crew_book_model import ProgressionCrewBookModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_experience_exchange_model import ProgressionExperienceExchangeModel
from gui.impl.gen.view_models.views.lobby.detachment.progression_view_model import ProgressionViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.experience_overflow_tooltip import ExperienceOverflowTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.rank_tooltip import RankTooltip
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.event_dispatcher import showDetachmentViewById
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.crew_book import sortItems
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.processors.detachment import DetachmentFreeToOwnXpConvertor
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.utils.decorators import process
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import descriptor
from items import ITEM_TYPES
from items.components.crew_books_constants import CREW_BOOK_RARITY
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
_logger = logging.getLogger(__name__)
_INITIAL_FREE_XP_RATE = 1
_CREWBOOK_AMOUNT_UNAVAILABLE = 0
_PROGRESS_DELTA_UNCHANGED = -1
_LEVEL_NO_GAINED = 0
_EXP_INPUT_MAX_VALUE = 999999999

class ProgressionView(NavigationViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __lobbyContext = descriptor(ILobbyContext)
    __slots__ = ('_detachmentInvID', '_detachment', '_crewBooks', '_purchasableItemCD', '_activeTab')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    _PROGRESS_MAX = 100
    uiLogger = DetachmentLogger(GROUP.RAISE_EFFICIENCY)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionViewModel()
        super(ProgressionView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self._detachmentInvID = ctx['detInvID']
        self._detachment = None
        self._crewBooks = None
        self._purchasableItemCD = None
        self._activeTab = ProgressionViewModel.EXCHANGE
        return

    def _initModel(self, vm):
        super(ProgressionView, self)._initModel(vm)
        self.__fillModel(vm)

    @property
    def viewModel(self):
        return super(ProgressionView, self).getViewModel()

    def _addListeners(self):
        super(ProgressionView, self)._addListeners()
        model = self.viewModel
        model.onTabActive += self.__onTabActive
        model.goToPersonalCase += self.__goToPersonalCase
        model.crewBooks.onCrewBookBuy += self.__onCrewBookBuy
        model.crewBooks.onCrewBookClick += self.__onCrewBookClick
        model.crewBooks.onApplyClick += self.__onApplyClick
        model.experienceExchange.onStepperValueChange += self.__onStepperValueChange
        model.experienceExchange.onSubmitExchange += self.__onSubmitExchange
        g_playerEvents.onShopResync += self.__fillExchangeModelTran
        g_clientUpdateManager.addCallbacks({'shop.freeXPToDetXPRate': self.__clientUpdate,
         'stats.freeXP': self.__clientUpdate,
         'stats.gold': self.__clientUpdate,
         'stats.credits': self.__clientUpdate,
         'inventory.{}'.format(ITEM_TYPES.detachment): self.__clientUpdate,
         'inventory.{}'.format(ITEM_TYPES.vehicle): self.__clientUpdate,
         'inventory.{}'.format(ITEM_TYPES.crewBook): self.__clientUpdate})
        self.__lobbyContext.onServerSettingsChanged += self.__onLobbyServerSettingsChange
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        super(ProgressionView, self)._removeListeners()
        model = self.viewModel
        model.onTabActive -= self.__onTabActive
        model.goToPersonalCase -= self.__goToPersonalCase
        model.crewBooks.onCrewBookBuy -= self.__onCrewBookBuy
        model.crewBooks.onCrewBookClick -= self.__onCrewBookClick
        model.crewBooks.onApplyClick -= self.__onApplyClick
        model.experienceExchange.onStepperValueChange -= self.__onStepperValueChange
        model.experienceExchange.onSubmitExchange -= self.__onSubmitExchange
        g_playerEvents.onShopResync -= self.__fillExchangeModelTran
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.onServerSettingsChanged -= self.__onLobbyServerSettingsChange
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _finalize(self):
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        super(ProgressionView, self)._finalize()

    def _onLoadPage(self, args=None):
        if args['viewId'] != NavigationViewModel.BARRACK_DETACHMENT:
            args['detInvID'] = self._detachmentInvID
        super(ProgressionView, self)._onLoadPage(args)

    def __onLobbyServerSettingsChange(self, newSettings):
        newSettings.onServerSettingsChange += self.__onServerSettingsChange

    def __onServerSettingsChange(self, _):
        self.__clientUpdate()

    def __clientUpdate(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillModel(model)

    def __fillModel(self, model):
        self.__updateDetachmentSource()
        self.__updateNewCrewBookCounter(model)
        self.__fillCrewBooks(model)
        self.__fillExchangeModel(model)
        self.__updateRose(model)

    def __getCurrentDetachment(self):
        detInvID = g_currentVehicle.item.getLinkedDetachmentID()
        return self.__detachmentCache.getDetachment(detInvID)

    def __updateDetachmentSource(self):
        if self._detachmentInvID is None:
            self._detachmentInvID = g_currentVehicle.item.getLinkedDetachmentID()
        self._detachment = self.__detachmentCache.getDetachment(self._detachmentInvID)
        return

    def __getCurrentBuild(self):
        return self._detachment.getDescriptor().build

    def __convertXPToProgressPercentage(self, additionalXP):
        detachmentDesc = self._detachment.getDescriptor()
        maxXP = detachmentDesc.getNextLevelXPGoal()
        return 1 if additionalXP >= maxXP else round(float(additionalXP) / maxXP, 2)

    def __updateTopPanel(self, tx, gainedXP=0):
        fillDetachmentTopPanelModel(model=tx.topPanelModel, detachment=self._detachment)
        fillDetachmentPreviewInfo(model=tx.topPanelModel, detachment=self._detachment, gainedXP=gainedXP)

    def __updateRose(self, vm):
        fillRoseSheetsModel(roseModel=vm.topPanelModel.roseModel, detachment=self._detachment, newBuild=self.__getCurrentBuild())

    def __fillCrewBooks(self, tx):
        self.__updateBookItems()
        notInShopItems = self.__itemsCache.items.shop.getHiddens()
        serverSettings = self.__lobbyContext.getServerSettings()
        isPurchaseEnabled = serverSettings.isCrewBooksPurchaseEnabled()
        availableCrewBooks = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        tx.setIsBooksAvailable(serverSettings.isCrewBooksEnabled())
        model = tx.crewBooks
        model.setCurrentNation(g_currentVehicle.item.nationName)
        model.setIsMaxLevelDetachment(self._detachment.hasMaxMasteryLevel)
        isEliteLevel = self._detachment.level >= self._detachment.progression.maxLevel
        model.setIsBooksAvailable(not isEliteLevel)
        crewBooksList = model.getCrewBooksList()
        crewBooksList.clear()
        hasAnyNationsCrewBook = bool(availableCrewBooks)
        if not hasAnyNationsCrewBook:
            crewBooksList.invalidate()
            self.__updateTopPanel(tx)
            return
        isBooksAvailable = any((book.getFreeCount() for book in self._crewBooks))
        if not isBooksAvailable:
            model.setIsInvalidDetachment(True)
            model.setAvailableNations('|'.join(set((nations.MAP.get(book.nationID, '') for book in availableCrewBooks.itervalues()))))
        else:
            for book in self._crewBooks:
                crewBookModel = ProgressionCrewBookModel()
                crewBookModel.setId(book.intCD)
                crewBookModel.setCrewBookType(book.getBookType())
                crewBookModel.setNation(nations.MAP.get(book.nationID, ''))
                crewBookModel.setExpBonus(book.getXP())
                crewBookModel.setAvailableAmount(book.getFreeCount())
                isBtnEnabled = book.intCD not in notInShopItems and isPurchaseEnabled
                crewBookModel.setHaveBuyButton(isBtnEnabled)
                crewBooksList.addViewModel(crewBookModel)

        crewBooksList.invalidate()
        if self._activeTab == ProgressionViewModel.CREW_BOOKS:
            self.__updateTopPanel(tx)

    def __fillExchangeModelTran(self):
        with self.viewModel.transaction() as model:
            self.__fillExchangeModel(model)

    def __fillExchangeModel(self, model):
        exchangeModel = model.experienceExchange
        detDesc = self._detachment.getDescriptor()
        freeXP = self.__itemsCache.items.stats.actualFreeXP
        rate = self.__itemsCache.items.shop.freeXPToDetXPRate
        defaultRate = self.__itemsCache.items.shop.defaults.freeXPToDetXPRate
        nextLevelDeltaXP = detDesc.getNextLevelXPGoal() - detDesc.getCurrentLevelXP()
        leftRate = nextLevelDeltaXP % rate
        roundedNextLevelDeltaXP = max(nextLevelDeltaXP + (rate - leftRate) * int(leftRate > 0), rate)
        previewGainedXP = min(roundedNextLevelDeltaXP, freeXP * rate)
        expToNextLvl = max(previewGainedXP, rate)
        model.setIsExchangeDiscount(rate > defaultRate)
        exchangeModel.setRate(rate)
        exchangeModel.setAvailableFreeExp(freeXP)
        exchangeModel.setExpToNextLvl(expToNextLvl)
        exchangeModel.setIsMaxLevelDetachment(self._detachment.hasMaxMasteryLevel)
        isLevelBeforeElite = detDesc.progression.maxLevel - detDesc.level == 1
        exchangeModel.setIsLastLevelToElite(isLevelBeforeElite)
        if self._activeTab == ProgressionViewModel.EXCHANGE:
            self.__updateTopPanel(model, previewGainedXP)
            self.__updateTopPanel(model, expToNextLvl)

    @async
    def __onApplyClick(self, args=None):
        bookItemCD = int(args.get('id'))
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        sdr = yield await(showApplyCrewBookDetachmentDialogView(self._detachmentInvID, bookItemCD))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            bookCount = int(data['bookCount'])
            self.__useCrewBook(bookItemCD, self._detachmentInvID, bookCount)

    def __useCrewBook(self, itemCD, detInvId, bookCount):
        ItemsActionsFactory.doAction(ItemsActionsFactory.USE_CREW_BOOK, itemCD, detInvId, bookCount)

    @async
    def __onCrewBookBuy(self, args=None):
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        yield self.__showConfirmCrewBookPurchaseDetachmentDialogView(args=args)

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            PerkTooltip.uiLogger.setGroup(self.uiLogger.group)
            return PerkTooltip(perkId, detachmentInvID=self._detachmentInvID)
        if event.contentID == R.views.lobby.detachment.tooltips.ExperienceOverflowTooltip():
            bookCD = int(event.getArgument('id'))
            return ExperienceOverflowTooltip(self._detachmentInvID, bookCD)
        if event.contentID == R.views.lobby.detachment.tooltips.CommanderPerkTooltip():
            perkType = event.getArgument('perkType')
            return CommanderPerkTooltip(perkType=perkType)
        if contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=self._detachmentInvID)
        if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(self._detachmentInvID)
        if event.contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=True, detachmentID=self._detachmentInvID)
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        if contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return SkillsBranchTooltipView(detachmentID=self._detachmentInvID, branchID=int(course) + 1)
        if contentID == R.views.lobby.detachment.tooltips.RankTooltip():
            RankTooltip.uiLogger.setGroup(self.uiLogger.group)
            return RankTooltip(self._detachment.rankRecord)
        return super(ProgressionView, self).createToolTipContent(event, contentID)

    @async
    def __showConfirmCrewBookPurchaseDetachmentDialogView(self, args=None):
        bookItemCD = int(args.get('id', self._purchasableItemCD)) if args is not None else self._purchasableItemCD
        if not bookItemCD:
            _logger.error('purchasable book item CD not found')
        sdr = yield await(showConfirmCrewBookPurchaseDetachmentDialogView(bookItemCD))
        if sdr.busy:
            return
        else:
            isOk, data = sdr.result
            if isOk == DialogButtons.SUBMIT:
                bookItem = self.__itemsCache.items.getItemByCD(bookItemCD)
                requiredCurrency = bookItem.buyPrices.itemPrice.getCurrency()
                self.__executeBuyCrewbook(bookItem, data['bookCount'], requiredCurrency)
            return

    def __onCrewBookClick(self, args):
        bookItemCD = int(args.get('id'))
        with self.viewModel.transaction() as model:
            for book in self._crewBooks:
                if book.intCD == bookItemCD:
                    progression = self._detachment.progression
                    detDescr = self._detachment.getDescriptor()
                    allowedXP = progression.getLevelStartingXP(progression.maxLevel) - detDescr.experience
                    gainedXP = min(book.getXP(), allowedXP)
                    return self.__updateTopPanel(model, gainedXP)

            self.__updateTopPanel(model)

    def __onStepperValueChange(self, event):
        exp = int(event['expToExchange']) * self.__itemsCache.items.shop.freeXPToDetXPRate
        with self.viewModel.transaction() as model:
            self.__updateTopPanel(model, exp)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.XP_EXCHANGE_CONFIRM_DIALOG)
    @async
    def __onSubmitExchange(self, event):
        expToExchange = int(event['expToExchange'])
        rate = self.__itemsCache.items.shop.freeXPToDetXPRate
        isOk = yield showApplyExpExchangeDetachmentDialogView(expToExchange, rate, self._detachment.hasMaxMasteryLevel)
        if isOk:
            self.__convertFreeToOwnXpConvertor(expToExchange)

    @process('buyItem')
    def __convertFreeToOwnXpConvertor(self, expToExchange):
        yield DetachmentFreeToOwnXpConvertor(self._detachmentInvID, expToExchange).request()

    def __goToPersonalCase(self):
        showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': self._detachmentInvID})

    def __onTabActive(self, args=None):
        self._activeTab = args.get('tabName')
        with self.viewModel.transaction() as model:
            if self._activeTab == ProgressionViewModel.EXCHANGE:
                self.__fillExchangeModel(model)
            else:
                self.__resetNewCrewBookCounter(model)
                self.__updateTopPanel(model)

    def __updateNewCrewBookCounter(self, model):
        if self._activeTab == ProgressionViewModel.EXCHANGE:
            booksCount = crewBooksViewedCache().getNewBooksCount()
            model.setNewCrewBooksAmount(booksCount)
        else:
            self.__resetNewCrewBookCounter(model)

    def __resetNewCrewBookCounter(self, model):
        crewBooksViewedCache().addViewedItems(self._detachment.nationID)
        model.setNewCrewBooksAmount(_CREWBOOK_AMOUNT_UNAVAILABLE)

    def __updateBookItems(self):
        criteria = REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT ^ ~REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(CREW_BOOK_RARITY.NO_NATION_TYPES)
        criteria |= REQ_CRITERIA.CREW_ITEM.NATIONS([self._detachment.nationID])
        items = self.__itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, criteria)
        self._crewBooks = sortItems(items.itervalues())
        self._purchasableItemCD = next((crewBook.intCD for crewBook in self._crewBooks if crewBook.getBookType() == CREW_BOOK_RARITY.CREW_EPIC), None)
        return

    @process('buyItem')
    def __executeBuyCrewbook(self, item, count, currency):
        result = yield ModuleBuyer(item, count, currency).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        crewBooksViewedCache().addViewedItems(self._detachment.nationID)
