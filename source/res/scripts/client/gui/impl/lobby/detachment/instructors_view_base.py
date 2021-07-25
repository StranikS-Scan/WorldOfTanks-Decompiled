# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/instructors_view_base.py
from gui import GUI_NATIONS_ORDER_INDICES, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.auxiliary.instructors_helper import fillInstructorCardModel, getInstructorLocation, getInstructorState, isInstructorsEqual, getInstructorCards, showInstructorSlotsDisabledMessage, countInstructors, fillInstructorsTokenList, InstructorStates
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_card_model import InstructorCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_category_model import InstructorsCategoryModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_view_base_model import InstructorsViewBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.lobby.detachment.popovers import getNationSettings, getInstructorGradeSettings
from gui.impl.lobby.detachment.popovers.filters.instructor_filters import defaultInstructorPopoverFilter, defaultInstructorToggleFilter, toggleCriteria, popoverCriteria, TOGGLE_FILTERS_ORDER
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewStatus
from gui.impl.lobby.detachment.sound_constants import BARRACKS_SOUND_SPACE
from gui.impl.lobby.detachment.tooltips.list_category_tooltip import ListCategoryTooltip
from gui.shared.event_dispatcher import showInstructorUnpackingWindow, showInstructorPageWindow
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import descriptor
from items import ITEM_TYPES
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP, ACTION
from uilogging.detachment.loggers import g_detachmentFlowLogger, InstructorListNullLogger
from voiceover_mixin import VoiceoverMixin

class InstructorsViewBase(FiltersMixin, NavigationViewImpl, VoiceoverMixin):
    __slots__ = ('_instructorCollection', '_notRecruitedState', '_ctx')
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    _COUNTED_RESULT_FILTERS = ()
    _itemsCache = descriptor(IItemsCache)
    _detachmentCache = descriptor(IDetachmentCache)
    _lobbyContext = descriptor(ILobbyContext)
    _defaultPopoverSetter = staticmethod(defaultInstructorPopoverFilter)
    _defaultToggleSetter = staticmethod(defaultInstructorToggleFilter)
    uiLogger = InstructorListNullLogger()

    def __init__(self, settings, ctx):
        super(InstructorsViewBase, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self._instructorCollection = self._detachmentCache.getInstructors()
        self._notRecruitedState = ctx.get('notRecruitedState', False)
        self._ctx = {'currentCount': 0,
         'totalCount': 0}
        self._tooltip = None
        return

    @property
    def viewModel(self):
        return super(InstructorsViewBase, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.detachment.tooltips.ListCategoryTooltip():
            ToggleFilterPopoverViewStatus.uiLogger.setGroup(self.uiLogger.group)
            grade = event.getArgument('grade')
            return ListCategoryTooltip(grade)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.detachment.popovers.ToggleFilterPopover():
            ToggleFilterPopoverViewStatus.uiLogger.setGroup(self.uiLogger.group)
            return ToggleFilterPopoverViewStatus(R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.instructors(), FilterStatusModel.DIVIDER, (getInstructorGradeSettings(), getNationSettings(R.strings.tooltips.filterToggle.crew.instructorsNation.body())), self._changePopoverFilterCallback, self._activatePopoverViewCallback, type(self)._popoverFilters, self._ctx, customResetFunc=self._resetPopoverFilters)

    def createToolTip(self, event):
        if event.contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            inst = self._detachmentCache.getInstructor(event.getArgument('instructorInvID'))
            if inst and inst.isToken() and not self._lobbyContext.getServerSettings().isUnpackInstructorEnabled():
                tooltipText = makeTooltip(TOOLTIPS.DETACHMENT_INSTRUCTORUNPACKING_DISABLED_HEADER, TOOLTIPS.DETACHMENT_INSTRUCTORUNPACKING_DISABLED_BODY)
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipText)
        super(InstructorsViewBase, self).createToolTip(event)

    def _initialize(self):
        super(InstructorsViewBase, self)._initialize()
        self.uiLogger.startAction(ACTION.OPEN)

    def _finalize(self):
        self._stopInstructorVoice()
        self._restoreSoundMode()
        self.uiLogger.stopAction(ACTION.OPEN)
        self.uiLogger.reset()
        super(InstructorsViewBase, self)._finalize()

    def _addListeners(self):
        super(InstructorsViewBase, self)._addListeners()
        model = self.viewModel
        self._subscribeFilterHandlers(model)
        model.onInstructorClick += self.__onInstructorClick
        model.onSubViewBackClick += self.__onSubViewBackClick
        model.onVoiceListenClick += self.__onVoiceListenClick
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self._onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.instructor): self._onInstructorsUpdate})
        self._onClientUpdate()

    def _removeListeners(self):
        model = self.viewModel
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._unsubscribeFilterHandlers(model)
        model.onInstructorClick -= self.__onInstructorClick
        model.onSubViewBackClick -= self.__onSubViewBackClick
        model.onVoiceListenClick -= self.__onVoiceListenClick
        super(InstructorsViewBase, self)._removeListeners()

    def _onClientUpdate(self, *args, **kwargs):
        self._instructorCollection = self._detachmentCache.getInstructors()
        with self.viewModel.transaction() as model:
            self._fillViewModel(model)

    def _onInstructorsUpdate(self, *args, **kwargs):
        oldTokens = set(self._instructorCollection.filter(REQ_CRITERIA.INSTRUCTOR.TOKENS).keys())
        self._instructorCollection = self._detachmentCache.getInstructors()
        newTokens = set(self._instructorCollection.filter(REQ_CRITERIA.INSTRUCTOR.TOKENS).keys())
        removedTokens = oldTokens.difference(newTokens)
        with self.viewModel.transaction() as model:
            if removedTokens:
                lastUnpackedInstId = removedTokens.pop()
                self._notRecruitedState = False
                self.uiLogger.switchUnpacking(self._notRecruitedState, False)
                inst = self._detachmentCache.getInstructor(lastUnpackedInstId)
                if inst not in self._filterInstructorItems().itervalues():
                    self._resetData()
                    if inst not in self._filterInstructorItems().itervalues():
                        type(self)._popoverFilters = self._defaultPopoverSetter()
                    self._resetModel(model)
                cardId = self._getCardId(lastUnpackedInstId)
                if cardId is not None:
                    model.setLastUnpackedInvID(cardId)
            self._fillViewModel(model)
        return

    def _initModel(self, vm):
        super(InstructorsViewBase, self)._initModel(vm)
        self._initFilters(vm, TOGGLE_FILTERS_ORDER, FilterContext.INSTRUCTORS)
        self._fillViewModel(vm)

    def _getCardId(self, instructorInvID):
        instructor = self._detachmentCache.getInstructor(instructorInvID)
        cards = self._getInstructorCards(self._filterInstructorItems())
        for card in cards:
            if isInstructorsEqual(instructor, card.item):
                return card.invID

    def _fillViewModel(self, model):
        model.setIsSubView(self._notRecruitedState)
        self._fillList(model)
        if not self._notRecruitedState:
            self._fillBannerUnpackedInstructors(model)

    def _fillList(self, model):
        self._fillFilterModel(model)
        self._fillInstructors(model)

    def _fillInstructors(self, model):
        categoriesList = model.getCategories()
        categoriesList.clear()
        cards = self._getInstructorCards(self._filterInstructorItems())
        groupedCardsByGrades = {}
        for instrCardData in cards:
            instrCardModel = InstructorCardModel()
            self._fillInstructorCardModel(instrCardModel, instrCardData)
            groupedCardsByGrades.setdefault(instrCardModel.getGrade(), []).append((instrCardModel, instrCardData))

        for grade, instructorCards in sorted(groupedCardsByGrades.iteritems()):
            categoryModel = InstructorsCategoryModel()
            categoryModel.setGrade(grade)
            if instructorCards:
                _, exampleInstructorCard = instructorCards[0]
                self._setIsEnoughtSlotsForCategoryModel(categoryModel, exampleInstructorCard.item)
                self._setRequiredLevelForCategoryModel(categoryModel, exampleInstructorCard.item)
            items = categoryModel.getItems()
            for cardModel, _ in instructorCards:
                items.addViewModel(cardModel)

            categoriesList.addViewModel(categoryModel)

        categoriesList.invalidate()

    def _setIsEnoughtSlotsForCategoryModel(self, categoryModel, instructor):
        categoryModel.setIsEnoughSlots(True)

    def _setRequiredLevelForCategoryModel(self, categoryModel, instructor):
        categoryModel.setRequiredLevel(0)

    def _fillInstructorCardModel(self, instructorModel, instrCardData):
        fillInstructorCardModel(instructorModel, instrCardData)

    def _fillFilterModel(self, model):
        currentCards = getInstructorCards(self._filterInstructorItems())
        allInstructors = self._filterInstructorItems(self._defaultPopoverSetter(), self._defaultToggleSetter())
        allCards = getInstructorCards(allInstructors)
        currentCount = countInstructors(currentCards, tokens=self._notRecruitedState)
        totalCount = countInstructors(allCards, tokens=self._notRecruitedState)
        self._ctx.update({'currentCount': currentCount,
         'totalCount': totalCount})
        model.filtersModel.setCurrent(currentCount)
        model.filtersModel.setTotal(totalCount)
        for toggleFilterModel in model.filtersModel.getFilters():
            fName = toggleFilterModel.getId()
            if fName in self._COUNTED_RESULT_FILTERS:
                filteredCards = getInstructorCards(self._filterInstructorItems(self._defaultPopoverSetter(), {fName: True}))
                filteredCount = countInstructors(filteredCards, tokens=self._notRecruitedState)
                toggleFilterModel.setCounter(filteredCount)

    def _getInstructorCards(self, items):
        cards = getInstructorCards(items)
        return sorted(cards, key=self._instructorCardSortingValue, reverse=self._isReverseSort())

    def _filterInstructorItems(self, popoverFilters=None, toggleFilters=None):
        criteria = self._getInstructorCriteria(popoverFilters, toggleFilters)
        return self._instructorCollection.filter(criteria)

    def _getInstructorCriteria(self, popoverFilters=None, toggleFilters=None):
        if self._notRecruitedState:
            criteria = REQ_CRITERIA.INSTRUCTOR.TOKENS
        else:
            popoverFilters = self._popoverFilters if popoverFilters is None else popoverFilters
            toggleFilters = self._toggleFilters if toggleFilters is None else toggleFilters
            criteria = ~REQ_CRITERIA.INSTRUCTOR.TOKENS
            criteria |= popoverCriteria(popoverFilters)
            criteria |= toggleCriteria([ f for f, active in toggleFilters.iteritems() if active ])
        return criteria

    def _getInstructorViewArgs(self, inst):
        return {'instructorInvID': inst.invID}

    def __clearTooltip(self):
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None
        return

    def updateNotRecruitedState(self, state):
        self.__clearTooltip()
        self.uiLogger.switchUnpacking(state)
        self._notRecruitedState = state
        with self.viewModel.transaction() as model:
            self._fillViewModel(model)

    def _instructorCardSortingValue(self, instructorCard):
        _, _, item = instructorCard
        classID = item.classID
        locationOrder = getInstructorLocation(item).value
        statusOrder = getInstructorState(item).value
        nationOrder = GUI_NATIONS_ORDER_INDICES[item.nationID]
        if statusOrder == InstructorStates.TOKEN:
            availableNationIDs = item.getAvailableNationIDs()
            if len(availableNationIDs) == 1:
                nationOrder = GUI_NATIONS_ORDER_INDICES[availableNationIDs[0]]
        return (classID,
         locationOrder,
         item.isUnremovable,
         statusOrder,
         nationOrder,
         item.descriptor.settingsID)

    def _isReverseSort(self):
        return False

    def _fillBannerUnpackedInstructors(self, model):
        instructors = model.getUnpackedInstructorsList()
        instructorsCards = getInstructorCards(self._instructorCollection)
        fillInstructorsTokenList(instructors, instructorsCards, self._instructorCardSortingValue, self._isReverseSort())
        model.setUnpackedInstructorsCount(countInstructors(instructorsCards, tokens=True))

    def __onInstructorClick(self, event):
        instructorInvID = event.get('instructorInvID')
        inst = self._detachmentCache.getInstructor(instructorInvID)
        if inst is not None:
            if inst.isToken() and not self._lobbyContext.getServerSettings().isUnpackInstructorEnabled():
                SystemMessages.pushMessage(type=SystemMessages.SM_TYPE.FeatureSwitcherOff, text=backport.text(R.strings.tooltips.detachment.instructorUnpacking.disabled.body()), messageData={'header': backport.text(R.strings.tooltips.detachment.instructorUnpacking.disabled.header())})
            elif not self._lobbyContext.getServerSettings().isInstructorSlotsEnabled():
                showInstructorSlotsDisabledMessage()
            elif inst.isToken():
                g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.INSTRUCTOR_UNPACKING)
                showInstructorUnpackingWindow({'navigationViewSettings': NavigationViewSettings(NavigationViewModel.INSTRUCTOR_UNPACKING, self._getInstructorViewArgs(inst), self._navigationViewSettings)})
            else:
                g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.INSTRUCTOR_PAGE)
                showInstructorPageWindow({'navigationViewSettings': NavigationViewSettings(NavigationViewModel.INSTRUCTOR_PAGE, self._getInstructorViewArgs(inst), self._navigationViewSettings)})
        else:
            self.updateNotRecruitedState(True)
        return

    def __onSubViewBackClick(self):
        self.updateNotRecruitedState(False)

    def __onVoiceListenClick(self, data):
        self._playInstructorVoice(int(data['instructorInvID']))
