# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/barrack_detachment_view.py
import logging
from functools import partial
from async import await, async
from crew2 import settings_globals
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_NATIONS_ORDER_INDEX
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.auxiliary.detachment_helper import fillDetachmentCardModel, fillRoseSheetsModel
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialogs import showDetachmentDemobilizeDialogView, showDetachmentRestoreDialogView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.barrack_detachments_view_model import BarrackDetachmentsViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_card_model import DetachmentCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_model import FilterStatusModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl, NavigationViewSettings
from gui.impl.lobby.detachment.popovers import getNationSettings, getVehicleTypeSettings
from gui.impl.lobby.detachment.popovers.filters.detachment_filters import defaultBarracksPopoverFilter, barracksPopoverCriteria, detachmentToggleCriteria, defaultDetachmentToggleFilter, ORDER, defaultSorts
from gui.impl.lobby.detachment.popovers.sorts import getDetachmentSorts, Sorts, SortType
from gui.impl.lobby.detachment.popovers.toggle_sort_filter_popover_view import ToggleSortFilterPopoverView
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.detachment_restore_tooltip import DetachmentRestoreTooltip
from gui.impl.lobby.detachment.tooltips.dismiss_tooltip import DismissTooltip
from gui.impl.lobby.detachment.tooltips.dormitory_info_tooltip import DormitoryInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.mobilization_tooltip import MobilizationTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.context_menu.context_menu_helper import getContextMenuData
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.gui_items import ItemsCollection
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import getTotalDormsRooms
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import ITEM_TYPES
from items.components.detachment_constants import DemobilizeReason
from items.components.dormitory_constants import DormitorySections, BuyDormitoryReason
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE
from uilogging.detachment.loggers import DetachmentToggleLogger, g_detachmentFlowLogger
from uilogging.detachment.loggers import GROUP
_logger = logging.getLogger(__name__)
AUTO_SCROLL_DISABLE = -1

class BarrackDetachmentsView(NavigationViewImpl, FiltersMixin):
    __slots__ = ('__detachmentsCollection', '__ctx', '__scrollToCard', '__lastRecoveredDetachment')
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _defaultPopoverSetter = staticmethod(defaultBarracksPopoverFilter)
    _defaultToggleSetter = staticmethod(defaultDetachmentToggleFilter)
    _popoverFilters = defaultBarracksPopoverFilter()
    _toggleFilters = defaultDetachmentToggleFilter()
    _sorts = defaultSorts()
    uiLogger = DetachmentToggleLogger(GROUP.DETACHMENT_BARRACKS)

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BarrackDetachmentsViewModel()
        super(BarrackDetachmentsView, self).__init__(settings, topMenuVisibility=True, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__detachmentsCollection = self.__detachmentCache.getDetachments()
        self.__ctx = {'currentCount': 0,
         'totalCount': len(self.__detachmentsCollection)}
        self.__scrollToCard = (AUTO_SCROLL_DISABLE, ctx.get('detInvID', AUTO_SCROLL_DISABLE))
        self.__lastRecoveredDetachment = None
        return

    @property
    def viewModel(self):
        return super(BarrackDetachmentsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        detachmentID = event.getArgument('detachmentId')
        if event.contentID == R.views.lobby.detachment.tooltips.DormitoryInfoTooltip():
            return DormitoryInfoTooltip()
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        if event.contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            return DetachmentInfoTooltip(detachmentInvID=detachmentID)
        if contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=False, detachmentID=detachmentID)
        if contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            return SkillsBranchTooltipView(detachmentID=detachmentID, branchID=int(course) + 1)
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            detachment = self.__detachmentCache.getDetachment(detachmentID)
            return getInstructorTooltip(instructorInvID=instructorID, detachment=detachment)
        if contentID == R.views.lobby.detachment.tooltips.MobilizationTooltip():
            return MobilizationTooltip()
        if contentID == R.views.lobby.detachment.tooltips.DismissTooltip():
            return DismissTooltip(detachmentID=detachmentID)
        if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            return LevelBadgeTooltipView(detachmentID)
        return DetachmentRestoreTooltip(detachmentID) if contentID == R.views.lobby.detachment.tooltips.DetachmentRestoreTooltip() else super(BarrackDetachmentsView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        ToggleSortFilterPopoverView.uiLogger.setGroup(self.uiLogger.group)
        return ToggleSortFilterPopoverView((getDetachmentSorts(),), BarrackDetachmentsView._sorts, self.__changeSortingCallback, R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.detachment(), FilterStatusModel.DIVIDER, (getVehicleTypeSettings(), getNationSettings()), self._changePopoverFilterCallback, self._activatePopoverViewCallback, BarrackDetachmentsView._popoverFilters, self.__ctx, customResetFunc=self._resetPopoverFilters)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getContextMenuData(event, self.__itemsCache, self.__detachmentCache)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(BarrackDetachmentsView, self).createContextMenuContent(event)

    def _initModel(self, vm):
        super(BarrackDetachmentsView, self)._initModel(vm)
        self._initFilters(vm, ORDER, FilterContext.DETACHMENT)
        self.__fillViewModel(vm)

    def _addListeners(self):
        super(BarrackDetachmentsView, self)._addListeners()
        self.viewModel.onDetachmentCardClick += self.__onDetachmentCardClick
        self.viewModel.onDetachmentDismissClick += self.__onDetachmentDismissClick
        self.viewModel.onDetachmentRecoverClick += self.__onDetachmentRecoverClick
        self.viewModel.onBuyDormitoryBtnClick += self.__onBuyDormitoryBtnClick
        self.viewModel.onMobilizeClick += self.__onMobilizeClick
        self._subscribeFilterHandlers(self.viewModel)
        g_clientUpdateManager.addCallbacks({'stats.dormitories': self.__onClientUpdate,
         'stats.slots': self.__onClientUpdate,
         'shop.dormitory': self.__onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.detachment): self.__onDetachmentUpdate,
         'inventory.{}'.format(ITEM_TYPES.vehicle): self.__onClientUpdate,
         'cache.vehsLock': self.__onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.tankman): self.__onClientUpdate})
        self.__lobbyContext.onServerSettingsChanged += self.__onLobbyServerSettingsChange
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onLobbyServerSettingsChange
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onDetachmentCardClick -= self.__onDetachmentCardClick
        self.viewModel.onDetachmentDismissClick -= self.__onDetachmentDismissClick
        self.viewModel.onDetachmentRecoverClick -= self.__onDetachmentRecoverClick
        self.viewModel.onBuyDormitoryBtnClick -= self.__onBuyDormitoryBtnClick
        self.viewModel.onMobilizeClick -= self.__onMobilizeClick
        self._unsubscribeFilterHandlers(self.viewModel)
        super(BarrackDetachmentsView, self)._removeListeners()

    def _resetData(self):
        super(BarrackDetachmentsView, self)._resetData()
        BarrackDetachmentsView._sorts = defaultSorts()

    def _resetPopoverFilters(self):
        super(BarrackDetachmentsView, self)._resetPopoverFilters()
        BarrackDetachmentsView._sorts.update(defaultSorts())

    def _fillList(self, model):
        detachments = self.__getDetachments()
        currentCount = len(detachments)
        model.filtersModel.setCurrent(currentCount)
        self.__ctx['currentCount'] = currentCount
        detachmentsList = model.getDetachmentList()
        detachmentsList.clear()
        _, scrollToDetachmentID = self.__scrollToCard
        for index in xrange(0, len(detachments)):
            invID, detachment = detachments[index]
            detachmentCardModel = DetachmentCardModel()
            fillDetachmentCardModel(cardModel=detachmentCardModel, detachmentGuiItem=detachment, inVehicle=self.__itemsCache.items.getVehicle(detachment.vehInvID))
            fillRoseSheetsModel(detachmentCardModel.roseModel, detachment)
            detachmentsList.addViewModel(detachmentCardModel)
            if invID == scrollToDetachmentID:
                self.__scrollToCard = (index, scrollToDetachmentID)

        self.__scrollCard(model)
        detachmentsList.invalidate()

    def __onLobbyServerSettingsChange(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self.__onServerSettingsChange

    def __onServerSettingsChange(self, _):
        with self.viewModel.transaction() as model:
            self.__fillViewModel(model)

    def __fillViewModel(self, model):
        self.viewModel.setCurrentViewId(NavigationViewModel.BARRACK_DETACHMENT)
        shopData = self.__itemsCache.items.shop
        model.bannerModel.setEndTimeConvert(settings_globals.g_conversion.endConversion)
        recruits = self.__itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.REGULAR)
        model.bannerModel.setAvailableForConvert(len(recruits.filter(REQ_CRITERIA.TANKMAN.ACTIVE)))
        model.dormRooms.setTotal(getTotalDormsRooms(itemsCache=self.__itemsCache))
        totalDetachment = len(self.__detachmentsCollection)
        model.filtersModel.setTotal(totalDetachment)
        model.dormRooms.setCurrent(totalDetachment - len(self.__getDemobilizeDetachment()))
        model.setIsBuyDormitoryEnable(shopData.getDormitoryBuyingSettings)
        model.setHasDormitoryDiscount(self.__isEnableDiscountForDormitory())
        model.setIsRecruitsTabEnabled(bool(recruits))
        self._fillList(model)

    def __onClientUpdate(self, diff):
        self.__detachmentsCollection = self.__detachmentCache.getDetachments()
        self.__ctx['totalCount'] = len(self.__detachmentsCollection)
        with self.viewModel.transaction() as model:
            self.__fillViewModel(model)

    def __onDetachmentUpdate(self, diff):
        self.__onClientUpdate(diff)
        recoveredDet = self.__lastRecoveredDetachment
        filteredDetachments = [ invID for invID, _ in self.__getDetachments() ]
        if recoveredDet in diff.get('recycleBin', {}) and recoveredDet not in filteredDetachments:
            self.__scrollToCard = (AUTO_SCROLL_DISABLE, recoveredDet)
            self._resetData()
            with self.viewModel.transaction() as model:
                self._resetModel(model)
            self.__lastRecoveredDetachment = None
        return

    def __getDetachments(self):
        criteria = barracksPopoverCriteria(self._popoverFilters)
        criteria |= detachmentToggleCriteria([ f for f, active in self._toggleFilters.iteritems() if active ])
        detachments = self.__detachmentsCollection.filter(criteria)
        expBeforeNation = BarrackDetachmentsView._sorts[SortType.DETACHMENT] == Sorts.EXPERIENCE
        return sorted(detachments.iteritems(), key=partial(_detachmentSortingValue, expBeforeNation=expBeforeNation))

    def __getDemobilizeDetachment(self):
        return self.__detachmentCache.getDetachments(REQ_CRITERIA.DETACHMENT.DEMOBILIZE)

    def __onDetachmentCardClick(self, event):
        detachmentId = event.get('detachmentID')
        self._showDetachmentView(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': detachmentId})

    @async
    def __onDetachmentDismissClick(self, event):
        if isViewLoaded(R.views.lobby.detachment.PersonalCase()):
            return
        detachmentId = event.get('detachmentID')
        sdr = yield await(showDetachmentDemobilizeDialogView(detachmentId, DemobilizeReason.DISMISS))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            ActionsFactory.doAction(ActionsFactory.DEMOBILIZED_DETACHMENT, data['detInvID'], data['allowRemove'], data['freeExcludeInstructors'])
            if not data['allowRemove']:
                self.__scrollToCard = (AUTO_SCROLL_DISABLE, detachmentId)

    @async
    def __onDetachmentRecoverClick(self, event):
        detachmentId = event.get('detachmentID')
        sdr = yield await(showDetachmentRestoreDialogView(detachmentId))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            ActionsFactory.doAction(ActionsFactory.RESTORE_DETACHMENT, data['detInvID'], data['curPrice'], data['curCurrency'], data['specialTerm'])
            self.__lastRecoveredDetachment = int(detachmentId)
            self.__scrollToCard = (AUTO_SCROLL_DISABLE, detachmentId)

    def __onMobilizeClick(self):
        g_detachmentFlowLogger.flow(GROUP.DETACHMENT_BARRACKS, GROUP.MOBILIZE_CREW)
        navigationSettings = NavigationViewSettings(NavigationViewModel.MOBILIZATION, previousViewSettings=self._navigationViewSettings)
        event_dispatcher.showDetachmentMobilizationView(False, navigationViewSettings=navigationSettings)

    def __scrollCard(self, model):
        index, detachmentID = self.__scrollToCard
        if index > AUTO_SCROLL_DISABLE and detachmentID > AUTO_SCROLL_DISABLE:
            model.autoScroll.setId(detachmentID)
            model.autoScroll.setIndex(index)
            self.__scrollToCard = (AUTO_SCROLL_DISABLE, AUTO_SCROLL_DISABLE)

    def __changeSortingCallback(self, settings):
        BarrackDetachmentsView._sorts.update(settings)
        self._changePopoverFilterCallback()

    @async
    def __onBuyDormitoryBtnClick(self):
        if isViewLoaded(R.views.lobby.detachment.dialogs.BuyDormitoryDialogView()):
            return
        sdr = yield await(dialogs.buyDormitory(self.getParentWindow(), reason=BuyDormitoryReason.GENERAL_BUY))
        if sdr.result:
            ActionsFactory.doAction(ActionsFactory.BUY_DORMITORY)

    def __isEnableDiscountForDormitory(self):
        price = self.__itemsCache.items.shop.getDormitoryPrice[DormitorySections.PRICE]
        defPrice = self.__itemsCache.items.shop.defaults.getDormitoryPrice[DormitorySections.PRICE]
        return defPrice > price


def _detachmentSortingValue(item, expBeforeNation=False):
    _, detachment = item
    nationOrder = GUI_NATIONS_ORDER_INDEX[detachment.nationName]
    detDescr = detachment.getDescriptor()
    pm = detDescr.getPerksMatrix()
    ultimatePerks = sum((pid in detDescr.build for bid in pm.branches.iterkeys() for pid in pm.getUltimatePerksInBranch(bid)))
    freePoints = detDescr.level - detDescr.getBuildLevel()
    return (detachment.isInRecycleBin,
     -detDescr.experience,
     nationOrder,
     -ultimatePerks,
     freePoints) if expBeforeNation else (detachment.isInRecycleBin,
     nationOrder,
     -detDescr.experience,
     -ultimatePerks,
     freePoints)
