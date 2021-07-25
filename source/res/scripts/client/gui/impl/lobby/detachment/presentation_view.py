# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/presentation_view.py
from collections import namedtuple
import typing
from frameworks.wulf import ViewSettings, View, WindowFlags
from goodies.goodie_constants import RECERTIFICATION_FORM_ID
from gui import GUI_NATIONS_ORDER_INDICES
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.instructors_helper import fillInstructorCardModel, getInstructorCards
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_card_model import InstructorCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_category_model import InstructorsCategoryModel
from gui.impl.gen.view_models.views.lobby.detachment.presentation_bonus_model import PresentationBonusModel
from gui.impl.gen.view_models.views.lobby.detachment.presentation_view_model import PresentationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.presentation_crew_subheader_tooltip_model import PresentationCrewSubheaderTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.presentation_instructions_subheader_tooltip_model import PresentationInstructionsSubheaderTooltipModel
from gui.impl.lobby.detachment.tooltips.barrack_places_tooltip import BarrackPlacesTooltip
from gui.impl.lobby.detachment.tooltips.dormitory_new_tooltip import DormitoryNewTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.title_convert_books_tooltip_view import TitleConvertBooksTooltipView
from gui.impl.lobby.detachment.voiceover_mixin import VoiceoverMixin
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.items_cache import getTotalDormsRooms
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.game_control import IDetachmentController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from sound_constants import HANGAR_OVERLAY_SOUND_SPACE
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import DetachmentLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent
promoScreens = [PresentationViewModel.SCREEN_BOOKS,
 PresentationViewModel.SCREEN_BUNKS,
 PresentationViewModel.SCREEN_SHEETS,
 PresentationViewModel.SCREEN_BOOSTERS,
 PresentationViewModel.SCREEN_INSTRUCTORS]
_CONVERTED_CREW_BATTLE_BOOSTERS = (129275,
 130043,
 128763,
 128507,
 129531,
 129019,
 129787)
_CONVERTED_CREW_BOOKS = (5406,
 10526,
 286,
 5662,
 10782,
 542,
 5918,
 11038,
 798,
 6174,
 11294,
 1054,
 7198,
 12318,
 2078,
 6430,
 11550,
 1310,
 6686,
 11806,
 1566,
 6942,
 12062,
 1822,
 7710,
 12830,
 2590,
 7454,
 12574,
 2334,
 7966,
 13086,
 2846,
 15646,
 16158,
 15902)
_VERSION_UPDATER_TOKEN_PREFIX = 'token:crew_conversion'
_VERSION_UPDATER_CREWBOOK_PREFIX = 'crewBooks'
_VERSION_UPDATER_FULFILLED_PREFIX = 'success'
_VERSION_UPDATER_PERSONAL_CREW_BOOK_PREFIX = 'personalCrewBook'
_VERSION_UPDATER_TRASH_TANKMEN_PREFIX = 'trashTankmen'
_VERSION_UPDATER_TANKMEN_TOKEN_PREFIX = 'tankmenToken'
_VERSION_UPDATER_CONVERSION_REASONS = (_VERSION_UPDATER_PERSONAL_CREW_BOOK_PREFIX, _VERSION_UPDATER_TRASH_TANKMEN_PREFIX, _VERSION_UPDATER_TANKMEN_TOKEN_PREFIX)
_RibbonEntryInfo = namedtuple('_RibbonEntryInfo', ('id',
 'icon',
 'amount',
 'name'))

class PresentationView(ViewImpl, VoiceoverMixin):
    __slots__ = ('__screenIndex', '__ribbonEntryData', '__additionalAwardsTooltipData', '__instructorsData', '__screens', '__crewBooksRibbonComposedType', '__tooltipByContentID', '__backportTooltipByID')
    _COMMON_SOUND_SPACE = HANGAR_OVERLAY_SOUND_SPACE
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __detachmentController = dependency.descriptor(IDetachmentController)
    __gui = dependency.descriptor(IGuiLoader)
    uiLogger = DetachmentLogger(GROUP.PRESENTATION)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = PresentationViewModel()
        super(PresentationView, self).__init__(settings)
        self.__screenIndex = 0
        self.__ribbonEntryData = {}
        self.__additionalAwardsTooltipData = {}
        self.__instructorsData = []
        self.__screens = []
        self.__crewBooksRibbonComposedType = None
        rTooltips = R.views.lobby.detachment.tooltips
        self.__tooltipByContentID = {rTooltips.PerkTooltip(): self.__getPerkTooltip,
         rTooltips.InstructorTooltip(): self.__getInstructorTooltip,
         R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent(): self._getBackportTooltip}
        self.__backportTooltipByID = {PresentationViewModel.TOOLTIP_SUB_HEADER: self.__getSubHeaderTooltip,
         PresentationViewModel.TOOLTIP_ADDITIONAL_REWARDS: self.__getAdditionalRewardTooltip,
         PresentationViewModel.TOOLTIP_ITEM: self.__getItemTooltip}
        return

    @property
    def currentScreenKey(self):
        return self.__screens[self.__screenIndex]

    @property
    def viewModel(self):
        return super(PresentationView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        createTooltip = self.__tooltipByContentID.get(contentID)
        return createTooltip(event) if createTooltip else super(PresentationView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        Waiting.show('loadContent')
        self.__addRibbonData()
        self.__addAdditionalAwardsTooltipData()
        self.__addInstructorsData()
        self.__addScreens()
        self.__setModel()
        self.__updateScreen()

    def _onLoaded(self, *args, **kwargs):
        super(PresentationView, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadContent')

    def _initialize(self, *args, **kwargs):
        super(PresentationView, self)._initialize()
        self.__addListeners()

    def _finalize(self):
        super(PresentationView, self)._finalize()
        self.__removeListeners()
        self.uiLogger.reset()
        self.__tooltipByContentID.clear()
        self.__backportTooltipByID.clear()

    def __addListeners(self):
        model = self.viewModel
        model.onBack += self.__onBack
        model.onNext += self.__onNext
        model.onDone += self.__finishPresentation
        model.onClose += self.__finishPresentation
        model.onVoiceListenClick += self.__onVoiceListenClick

    def __removeListeners(self):
        model = self.viewModel
        model.onBack -= self.__onBack
        model.onNext -= self.__onNext
        model.onDone -= self.__finishPresentation
        model.onClose -= self.__finishPresentation
        model.onVoiceListenClick -= self.__onVoiceListenClick

    def __addScreens(self):
        self.__screens = [ screen for screen, entries in self.__ribbonEntryData.iteritems() if len(entries) > 0 ]
        if self.__instructorsData:
            self.__screens.append(PresentationViewModel.SCREEN_INSTRUCTORS)

    def __setModel(self):
        with self.viewModel.transaction() as vm:
            vm.setAmountOfScreens(len(self.__screens))

    @uiLogger.dStartAction(ACTION.OPEN)
    def __updateScreen(self):
        for tooltipWindow in self.__gui.windowsManager.findWindows(lambda wnd: wnd.typeFlag == WindowFlags.TOOLTIP):
            tooltipWindow.destroy()

        with self.viewModel.transaction() as vm:
            vm.setCurrentScreenIndex(self.__screenIndex + 1)
            vm.setScreenKey(self.currentScreenKey)
            if self.currentScreenKey != PresentationViewModel.SCREEN_INSTRUCTORS:
                self.__setRibbonModel()
            else:
                self.__setInstructorsModel(vm)

    def __setRibbonModel(self):
        with self.viewModel.transaction() as model:
            bonuses = model.getBonusesList()
            bonuses.clear()
            ribbonEntries = self.__ribbonEntryData[self.currentScreenKey]
            if self.currentScreenKey == PresentationViewModel.SCREEN_BOOKS:
                model.setCrewBooksType(self.__crewBooksRibbonComposedType)
            for ribbon in ribbonEntries:
                bonus = PresentationBonusModel()
                bonus.setItemCD(ribbon.id)
                bonus.setIcon(ribbon.icon)
                bonus.setAmount(ribbon.amount)
                bonuses.addViewModel(bonus)

            bonuses.invalidate()

    def __setInstructorsModel(self, model):
        instructorsCategories = model.getInstructorsCategories()
        instructorsCategories.clear()
        groupedCardsByGrades = {}
        for instrCardData in self.__instructorsData:
            instrCardModel = InstructorCardModel()
            fillInstructorCardModel(instrCardModel, instrCardData)
            groupedCardsByGrades.setdefault(instrCardModel.getGrade(), []).append((instrCardModel, instrCardData))

        for grade, instructorCards in sorted(groupedCardsByGrades.iteritems()):
            categoryModel = InstructorsCategoryModel()
            categoryModel.setGrade(grade)
            items = categoryModel.getItems()
            for cardModel, _ in instructorCards:
                items.addViewModel(cardModel)

            instructorsCategories.addViewModel(categoryModel)

        instructorsCategories.invalidate()

    def __onBack(self):
        self.uiLogger.stopAction(ACTION.OPEN, presentation_slide_id=self.currentScreenKey)
        self.__screenIndex -= 1
        self.__updateScreen()

    def __onNext(self):
        self.uiLogger.stopAction(ACTION.OPEN, presentation_slide_id=self.currentScreenKey)
        self.__screenIndex += 1
        self.__updateScreen()

    def __finishPresentation(self):
        self.uiLogger.stopAction(ACTION.OPEN, presentation_slide_id=self.currentScreenKey)
        self.__detachmentController.setPromoScreenIsShown()
        self.destroyWindow()

    def __onVoiceListenClick(self, data):
        self._playInstructorVoice(int(data['instructorInvID']))

    def __addInstructorsData(self):
        self.__instructorsData = sorted(getInstructorCards(self.__detachmentCache.getInstructors()), key=lambda card: (card.item.classID,
         card.item.isToken(),
         card.item.descriptor.isNationSet(),
         GUI_NATIONS_ORDER_INDICES[card.item.nationID],
         card.item.descriptor.settingsID))

    def __addRibbonData(self):
        self.__ribbonEntryData = {PresentationViewModel.SCREEN_BOOKS: self.__getCrewBooksData(),
         PresentationViewModel.SCREEN_BUNKS: self.__getDormitoriesData(),
         PresentationViewModel.SCREEN_SHEETS: self.__getRecertificationFormsData(),
         PresentationViewModel.SCREEN_BOOSTERS: self.__getScreenBoostersData()}

    def __addAdditionalAwardsTooltipData(self):
        self.__additionalAwardsTooltipData = {screen:self.__getAdditionalAwardsTooltipData(entries) for screen, entries in self.__ribbonEntryData.iteritems()}

    def __getScreenBoostersData(self):
        boosters = []
        for boosterCD in _CONVERTED_CREW_BATTLE_BOOSTERS:
            booster = self.__itemsCache.items.getItemByCD(boosterCD)
            if booster and booster.inventoryCount:
                boosters.append(booster)

        boostersData = [ _RibbonEntryInfo(id=booster.intCD, icon=R.images.gui.maps.icons.quests.bonuses.big.dyn(booster.descriptor.icon[0].split('_')[0])(), amount=booster.inventoryCount, name=booster.userName) for booster in sorted(boosters, key=lambda b: b.descriptor.perkId) ]
        return boostersData

    def __getRecertificationFormsData(self):
        recertificationFormsData = []
        activeGoodies = self.__goodiesCache.getRecertificationForms(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT)
        recertificationForms = activeGoodies.get(RECERTIFICATION_FORM_ID)
        formsCount = recertificationForms.count if recertificationForms else 0
        if formsCount > 0:
            recertificationFormsData.append(_RibbonEntryInfo(id=0, icon=R.images.gui.maps.icons.quests.bonuses.big.reward_sheet(), amount=formsCount, name=''))
        return recertificationFormsData

    def __getDormitoriesData(self):
        dormitoriesData = []
        dormRoomsCount = getTotalDormsRooms(itemsCache=self.__itemsCache)
        if dormRoomsCount > 0:
            dormitoriesData.append(_RibbonEntryInfo(id=0, icon=R.images.gui.maps.icons.quests.bonuses.big.dormitories(), amount=dormRoomsCount, name=''))
        return dormitoriesData

    def __getCrewBooksData(self):
        conversionReasons = set()
        bookItems = []
        bookCount = {}
        for bookCD in _CONVERTED_CREW_BOOKS:
            for reasonPrefix in _VERSION_UPDATER_CONVERSION_REASONS:
                tokenName = '{}:{}:{}:{}'.format(_VERSION_UPDATER_TOKEN_PREFIX, _VERSION_UPDATER_CREWBOOK_PREFIX, reasonPrefix, bookCD)
                count = self.__itemsCache.items.tokens.getTokenCount(tokenName)
                if not count:
                    continue
                bookItem = self.__itemsCache.items.getItemByCD(bookCD)
                if bookItem is None:
                    raise SoftException("Invalid Book CD: '{}'".format(bookCD))
                if bookItem not in bookItems:
                    bookItems.append(bookItem)
                bookCount[bookCD] = bookCount.get(bookCD, 0) + count
                conversionReasons.add(reasonPrefix)

        crewBooksData = [ _RibbonEntryInfo(id=bookItem.intCD, icon=R.images.gui.maps.icons.crewBooks.books.big.dyn(bookItem.getBonusIconName())(), amount=bookCount[bookItem.intCD], name=bookItem.userName) for bookItem in sorted(bookItems, key=lambda book: (-book.getBookTypeOrder(), GUI_NATIONS_ORDER_INDICES[book.getNationID()], book.getXP())) ]
        if conversionReasons:
            if len(conversionReasons) == 1:
                if _VERSION_UPDATER_PERSONAL_CREW_BOOK_PREFIX in conversionReasons:
                    self.__crewBooksRibbonComposedType = PresentationViewModel.CREW_BOOKS_UNIVERSAL
                elif _VERSION_UPDATER_TRASH_TANKMEN_PREFIX in conversionReasons:
                    self.__crewBooksRibbonComposedType = PresentationViewModel.CREW_BOOKS_NATIONAL
                elif _VERSION_UPDATER_TANKMEN_TOKEN_PREFIX in conversionReasons:
                    self.__crewBooksRibbonComposedType = PresentationViewModel.CREW_BOOKS_NATIONAL
            else:
                self.__crewBooksRibbonComposedType = PresentationViewModel.CREW_BOOKS_MIXED
        if self.__crewBooksRibbonComposedType is None:
            self.__crewBooksRibbonComposedType = PresentationViewModel.CREW_BOOKS_MIXED
        return crewBooksData

    def __getAdditionalAwardsTooltipData(self, entries):
        bonuses = []
        for entry in entries:
            shortData = {'name': entry.name,
             'label': backport.getNiceNumberFormat(entry.amount) if entry.amount > 1 else '',
             'imgSource': backport.image(entry.icon)}
            bonuses.append(shortData)

        return bonuses

    def __getItemTooltip(self, event):
        if self.currentScreenKey == PresentationViewModel.SCREEN_SHEETS:
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.RECERTIFICATION_FORM)
        elif self.currentScreenKey == PresentationViewModel.SCREEN_BUNKS:
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.DORMITORY_INFO)
        itemCD = int(event.getArgument('itemCD'))
        if self.currentScreenKey == PresentationViewModel.SCREEN_BOOKS:
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.BOOK_ITEM, [itemCD])
        else:
            return createBackportTooltipContent(TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK_SHORTENED, [itemCD]) if self.currentScreenKey == PresentationViewModel.SCREEN_BOOSTERS else None

    def __getAdditionalRewardTooltip(self, event):
        maxItems = int(event.getArgument('itemsNumber'))
        tooltipEntries = self.__additionalAwardsTooltipData[self.currentScreenKey]
        return createBackportTooltipContent(TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, tooltipEntries[maxItems:])

    def __getSubHeaderTooltip(self, event):
        if self.currentScreenKey == PresentationViewModel.SCREEN_BOOSTERS:
            model = PresentationInstructionsSubheaderTooltipModel()
            boosters = self.__ribbonEntryData[self.currentScreenKey]
            count = sum((booster.amount for booster in boosters))
            model.setCount(count)
            return View(ViewSettings(R.views.lobby.detachment.tooltips.PresentationInstructionsSubheaderTooltip(), model=model))
        elif self.currentScreenKey == PresentationViewModel.SCREEN_BUNKS:
            return DormitoryNewTooltip()
        elif self.currentScreenKey == PresentationViewModel.SCREEN_BOOKS:
            if self.__crewBooksRibbonComposedType == PresentationViewModel.CREW_BOOKS_NATIONAL:
                return TitleConvertBooksTooltipView(showPersonal=False)
            if self.__crewBooksRibbonComposedType == PresentationViewModel.CREW_BOOKS_UNIVERSAL:
                return TitleConvertBooksTooltipView(showNation=False)
            return TitleConvertBooksTooltipView()
        elif self.currentScreenKey == PresentationViewModel.CREW_BOOKS_NATIONAL:
            return TitleConvertBooksTooltipView(showPersonal=False)
        elif self.currentScreenKey == PresentationViewModel.CREW_BOOKS_UNIVERSAL:
            return TitleConvertBooksTooltipView(showNation=False)
        elif self.currentScreenKey == PresentationViewModel.SCREEN_SHEETS:
            return BarrackPlacesTooltip()
        elif self.currentScreenKey == PresentationViewModel.SCREEN_INSTRUCTORS:
            model = PresentationCrewSubheaderTooltipModel()
            count = sum((card.count for card in self.__instructorsData))
            instructor = self.__detachmentCache.getInstructor(first(self.__instructorsData).invID)
            model.setIcon(instructor.getPortraitResID(R.images.gui.maps.icons.instructors.c_158x118))
            model.setCount(count)
            return View(ViewSettings(R.views.lobby.detachment.tooltips.PresentationCrewSubheaderTooltip(), model=model))
        else:
            return None

    def _getBackportTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        createTooltip = self.__backportTooltipByID.get(tooltipId)
        return createTooltip(event) if createTooltip else None

    def __getInstructorTooltip(self, event):
        instructorID = event.getArgument('instructorInvID')
        return getInstructorTooltip(instructorInvID=instructorID)

    def __getPerkTooltip(self, event):
        perkId = event.getArgument('id')
        if int(perkId) <= 0:
            return None
        else:
            instructorID = event.getArgument('instructorId')
            return PerkTooltip(perkId, instructorInvID=instructorID, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)


class PresentationWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PresentationWindow, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=PresentationView(R.views.lobby.detachment.PresentationView()), parent=parent)
