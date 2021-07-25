# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/assign_to_vehicle_view.py
from copy import deepcopy
from functools import partial
from async import await, async
from crew2 import settings_globals
from frameworks.wulf import ViewFlags, ViewSettings
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl.auxiliary.detachment_helper import fillDetachmentCardModel, fillRoseSheetsModel, getRecruitsForMobilization
from gui.impl.dialogs.dialogs import showTrainVehicleConfirmView, showDetachmentRestoreDialogView, showSelectAssignMethodView
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.assign_to_vehicle_view_model import AssignToVehicleViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_card_model import DetachmentCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_states import DetachmentStates
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.no_detachments_view_model import NoDetachmentsViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.list_filter_mixin import FiltersMixin, FilterContext
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers import getVehicleTypeSettings
from gui.impl.lobby.detachment.popovers.filters.detachment_filters import defaultAssignmentPopoverFilters, assingmentPopoverCriteria, defaultDetachmentToggleFilter, detachmentToggleCriteria, ORDER
from gui.impl.lobby.detachment.popovers.toggle_filter_popover_view import ToggleFilterPopoverViewBase
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.detachment_restore_tooltip import DetachmentRestoreTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.mobilization_tooltip import MobilizationTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.ttc_mixin import TTCMixin
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showNewCommanderWindow, showDetachmentMobilizationView, showAssignDetachmentToVehicleView, showAssignToVehicleView
from gui.shared.gui_items import Vehicle, ItemsCollection
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.processors.detachment import DetachmentAssignToVehicle, DetachmentSpecializeVehicleSlotAndAssign
from gui.shared.gui_items.processors.detachment import DetachmentCreate
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from items import ITEM_TYPES
from items.components.detachment_constants import NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import ACTION, GROUP
from uilogging.detachment.loggers import DetachmentToggleLogger, DetachmentLogger, g_detachmentFlowLogger
AUTO_SCROLL_DISABLE = -1

class AssignToVehicleView(TTCMixin, FiltersMixin, NavigationViewImpl):
    __slots__ = ('__detachmentsCollection', '__vehicle', '__scrollToCard', '__blur', '__hoveredDetachmentID')
    _CLOSE_IN_PREBATTLE = True
    _DISABLE_CAMERA_MOVEMENT = True
    _detachmentCache = dependency.descriptor(IDetachmentCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _defaultPopoverSetter = staticmethod(defaultAssignmentPopoverFilters)
    _defaultToggleSetter = staticmethod(defaultDetachmentToggleFilter)
    _popoverFilters = defaultAssignmentPopoverFilters()
    _toggleFilters = defaultDetachmentToggleFilter()
    uiLogger = DetachmentToggleLogger(GROUP.ASSIGN_DETACHMENT)

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.AssignToVehicleView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = AssignToVehicleViewModel()
        super(AssignToVehicleView, self).__init__(settings, topMenuVisibility=True, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__vehicle = self._itemsCache.items.getVehicle(ctx.get('vehicleInvID', -1))
        self.__detachmentsCollection = self._detachmentCache.getDetachments(REQ_CRITERIA.DETACHMENT.NATIONS([self.__vehicle.nationID]))
        super(AssignToVehicleView, self)._resetData()
        AssignToVehicleView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())
        self.__scrollToCard = (AUTO_SCROLL_DISABLE, AUTO_SCROLL_DISABLE)
        self.__blur = CachedBlur(enabled=True)
        self.__hoveredDetachmentID = NO_DETACHMENT_ID

    @property
    def viewModel(self):
        return super(AssignToVehicleView, self).getViewModel()

    def createPopOverContent(self, event):
        ToggleFilterPopoverViewBase.uiLogger.setGroup(self.uiLogger.group)
        return ToggleFilterPopoverViewBase(R.strings.detachment.toggleFilterPopover.header(), R.strings.detachment.filterStatus.detachment(), (getVehicleTypeSettings(),), self._changePopoverFilterCallback, self._activatePopoverViewCallback, AssignToVehicleView._popoverFilters, customResetFunc=self._resetPopoverFilters)

    def createToolTipContent(self, event, contentID):
        detachmentID = event.getArgument('detachmentId')
        if event.contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=detachmentID)
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        if contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return SkillsBranchTooltipView(detachmentID=detachmentID, branchID=int(course) + 1, vehIntCD=self.__vehicle.intCD)
        if contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=False, detachmentID=detachmentID)
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            detachment = self._detachmentCache.getDetachment(detachmentID)
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        if contentID == R.views.lobby.detachment.tooltips.MobilizationTooltip():
            MobilizationTooltip.uiLogger.setGroup(self.uiLogger.group)
            return MobilizationTooltip()
        if contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(detachmentID)
        return DetachmentRestoreTooltip(detachmentID) if contentID == R.views.lobby.detachment.tooltips.DetachmentRestoreTooltip() else super(AssignToVehicleView, self).createToolTipContent(event, contentID)

    @uiLogger.dStartAction(ACTION.OPEN)
    def _initialize(self, *args, **kwargs):
        super(AssignToVehicleView, self)._initialize()
        switchHangarOverlaySoundFilter(on=True)
        self.__onDetachmentCardOut()

    @uiLogger.dStopAction(ACTION.OPEN)
    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.__blur.fini()
        self.__blur = None
        super(AssignToVehicleView, self)._finalize()
        return

    def _initModel(self, vm):
        super(AssignToVehicleView, self)._initModel(vm)
        self.__fillModel(vm)
        self._initFilters(vm, ORDER, FilterContext.DETACHMENT)

    def _addListeners(self):
        super(AssignToVehicleView, self)._addListeners()
        self.viewModel.onMobilizeClick += self.__onMobilizeClick
        self.viewModel.onRecruitBtnClick += self.__onRecruitBtnClick
        self.viewModel.onDetachmentCardClick += self.__onDetachmentCardClick
        self.viewModel.onDetachmentRecoverClick += self.__onDetachmentRecoverClick
        self.viewModel.onDetachmentCardHover += self.__onDetachmentCardHover
        self.viewModel.onDetachmentCardOut += self.__onDetachmentCardOut
        self._subscribeFilterHandlers(self.viewModel)
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.detachment): self.__onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.vehicle): self.__onClientUpdate,
         'cache.vehsLock': self.__onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onMobilizeClick -= self.__onMobilizeClick
        self.viewModel.onRecruitBtnClick -= self.__onRecruitBtnClick
        self.viewModel.onDetachmentCardClick -= self.__onDetachmentCardClick
        self.viewModel.onDetachmentRecoverClick -= self.__onDetachmentRecoverClick
        self.viewModel.onDetachmentCardHover -= self.__onDetachmentCardHover
        self.viewModel.onDetachmentCardOut -= self.__onDetachmentCardOut
        self._unsubscribeFilterHandlers(self.viewModel)
        super(AssignToVehicleView, self)._removeListeners()

    def _fillList(self, model):
        detachmentsList = model.getDetachmentList()
        detachments = self.__getDetachments()
        model.filtersModel.setCurrent(len(detachments))
        detachmentsList.clear()
        _, scrollToDetachmentID = self.__scrollToCard
        for index in xrange(0, len(detachments)):
            invID, detachment = detachments[index]
            detachmentCardModel = DetachmentCardModel()
            fillDetachmentCardModel(cardModel=detachmentCardModel, detachmentGuiItem=detachment, inVehicle=self._itemsCache.items.getVehicle(detachment.vehInvID), assignVehicle=self.__vehicle)
            fillRoseSheetsModel(detachmentCardModel.roseModel, detachment, vehicle=self.__vehicle)
            detachmentsList.addViewModel(detachmentCardModel)
            if invID == scrollToDetachmentID:
                self.__scrollToCard = (index, scrollToDetachmentID)

        self.__scrollCard(model)
        detachmentsList.invalidate()

    def _onEscape(self):
        self._onClose()

    def __fillModel(self, model):
        model.setEndTimeConvert(settings_globals.g_conversion.endConversion)
        model.setAvailableForConvert(len(getRecruitsForMobilization(self.__vehicle)))
        model.filtersModel.setTotal(len(self.__detachmentsCollection))
        self._fillList(model)
        self.__setVehicleModel(model.vehicleModel)

    def __onClientUpdate(self, diff):
        self.__detachmentsCollection = self._detachmentCache.getDetachments(REQ_CRITERIA.DETACHMENT.NATIONS([self.__vehicle.nationID]))
        self.__vehicle = self._itemsCache.items.getVehicle(self.__vehicle.invID)
        with self.viewModel.transaction() as model:
            self.__fillModel(model)

    def _addDefaultPopoverFilter(self):
        AssignToVehicleView._popoverFilters[PopoverFilterGroups.VEHICLE_TYPE].add(self.__vehicle.type)

    def _resetData(self):
        super(AssignToVehicleView, self)._resetData()
        self._resetPopover()

    def _resetPopoverFilters(self):
        super(AssignToVehicleView, self)._resetPopoverFilters()
        self._resetPopover()

    def _resetPopover(self):
        if not self.__getDetachments():
            AssignToVehicleView._popoverFilters.update(self._defaultPopoverSetter())
        AssignToVehicleView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    def __getDetachments(self):
        criteria = assingmentPopoverCriteria(self._popoverFilters)
        criteria |= detachmentToggleCriteria([ f for f, active in self._toggleFilters.iteritems() if active ])
        detachments = self.__detachmentsCollection.filter(criteria)
        return sorted(detachments.iteritems(), key=partial(_detachmentSortingValue, self.__vehicle))

    def __setVehicleModel(self, model):
        model.setName(self.__vehicle.shortUserName)
        model.setType(self.__vehicle.type)
        model.setLevel(self.__vehicle.level)
        model.setNation(self.__vehicle.nationName)
        model.setIsElite(self.__vehicle.isElite)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW)
    def __onMobilizeClick(self):
        showDetachmentMobilizationView(True, navigationViewSettings=NavigationViewSettings(NavigationViewModel.MOBILIZATION, previousViewSettings=self._navigationViewSettings))

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.NEW_COMMANDER_LIST)
    def __onRecruitBtnClick(self):
        showNewCommanderWindow(self.__vehicle.invID)

    def __onDetachmentCardClick(self, event):
        cardModel = self.viewModel.getDetachmentList()[event['index']]
        state = cardModel.getState()
        if state == DetachmentStates.AVAILABLE:
            self.__assignToVehicle(event['detachmentID'])
        elif state == DetachmentStates.WRONG_CLASS:
            self.__showTrainToVehicleDialog(event['detachmentID'])
        else:
            self.__showSelectAssingMethodDialog(event['detachmentID'], self.__vehicle)

    def __scrollCard(self, model):
        index, detachmentID = self.__scrollToCard
        if index > AUTO_SCROLL_DISABLE and detachmentID > AUTO_SCROLL_DISABLE:
            model.autoScroll.setId(detachmentID)
            model.autoScroll.setIndex(index)
            self.__scrollToCard = (AUTO_SCROLL_DISABLE, AUTO_SCROLL_DISABLE)

    @uiLogger.dLog(ACTION.ASSIGN_TO_VEHICLE_NO_TRAINING)
    @decorators.process('updating')
    def __assignToVehicle(self, detInvID):
        processor = DetachmentAssignToVehicle(detInvID, self.__vehicle.invID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            event_dispatcher.showHangar()

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.SELECT_ASSIGN_METHOD_DIALOG)
    @async
    def __showSelectAssingMethodDialog(self, detInvID, vehicle):
        sdr = yield await(showSelectAssignMethodView(self.getParentWindow(), detInvID, vehicle))
        result, _ = sdr.result
        if result:
            event_dispatcher.showHangar()

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.TRAIN_VEHICLE_CONFIRM_DIALOG)
    @async
    def __showTrainToVehicleDialog(self, detInvID):
        sdr = yield await(showTrainVehicleConfirmView(self.getParentWindow(), detachmentInvID=detInvID, slotIndex=0, selectedVehicleCD=self.__vehicle.intCD))
        result, data = sdr.result
        if result:
            self.__detachmentSpecializeVehicleSlotAndAssign(detInvID, data['paymentOptionIdx'], data['isReset'])

    @decorators.process('updating')
    def __detachmentSpecializeVehicleSlotAndAssign(self, detInvID, paymentOptionIdx, isReset):
        vehicle = self.__vehicle
        processor = DetachmentSpecializeVehicleSlotAndAssign(detInvID, 0, vehicle.intCD, paymentOptionIdx, isReset, vehicle.invID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            event_dispatcher.showHangar()

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.RESTORE_DETACHMENT_DIALOG)
    @async
    def __onDetachmentRecoverClick(self, event):
        detachmentID = event['detachmentID']
        sdr = yield await(showDetachmentRestoreDialogView(detachmentID))
        if sdr.busy:
            return
        isOk, data = sdr.result
        if isOk == DialogButtons.SUBMIT:
            self.__scrollToCard = (AUTO_SCROLL_DISABLE, detachmentID)
            factory.doAction(factory.RESTORE_DETACHMENT, data['detInvID'], data['curPrice'], data['curCurrency'], data['specialTerm'])

    def __onDetachmentCardHover(self, event):
        detachmentID = event['detachmentID']
        if detachmentID == g_detachmentTankSetupVehicle.defaultItem.getLinkedDetachmentID():
            self.__onDetachmentCardOut()
        else:
            self.__hoveredDetachmentID = detachmentID
            super(AssignToVehicleView, self)._updateTTCBonusDetachment(self.__hoveredDetachmentID)

    def __onDetachmentCardOut(self):
        currentDetInvID = g_detachmentTankSetupVehicle.defaultItem.getLinkedDetachmentID()
        if self.__hoveredDetachmentID != currentDetInvID:
            self.__hoveredDetachmentID = currentDetInvID
            super(AssignToVehicleView, self)._updateTTCCurrentDetachment(currentDetInvID)
            super(AssignToVehicleView, self)._updateTTCVehicle(g_detachmentTankSetupVehicle.defaultItem)


class NoDetachmentsView(NavigationViewImpl):
    __slots__ = ('__vehicle', '__blur')
    _DISABLE_CAMERA_MOVEMENT = True
    _itemsCache = dependency.descriptor(IItemsCache)
    uiLogger = DetachmentLogger(GROUP.ASSIGN_DETACHMENT)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = NoDetachmentsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NoDetachmentsView, self).__init__(settings, topMenuVisibility=True, ctx=kwargs)
        vehicleInvID = self._navigationViewSettings.getViewContextSettings().get('vehicleInvID')
        self.__vehicle = self._itemsCache.items.getVehicle(vehicleInvID)
        self.__blur = CachedBlur(enabled=True)

    @property
    def viewModel(self):
        return super(NoDetachmentsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', '')) if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip() else super(NoDetachmentsView, self).createToolTipContent(event, contentID)

    @uiLogger.dStartAction(ACTION.OPEN)
    def _initialize(self, *args, **kwargs):
        super(NoDetachmentsView, self)._initialize()
        switchHangarOverlaySoundFilter(on=True)

    @uiLogger.dStopAction(ACTION.OPEN)
    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.__blur.fini()
        self.__blur = None
        super(NoDetachmentsView, self)._finalize()
        return

    def _initModel(self, vm):
        super(NoDetachmentsView, self)._initModel(vm)
        vm.setEndTimeConvert(settings_globals.g_conversion.endConversion)
        vm.setAvailableForConvert(len(getRecruitsForMobilization(self.__vehicle)))
        self.__setVehicleModel(vm.vehicleModel)

    def _addListeners(self):
        super(NoDetachmentsView, self)._addListeners()
        self.viewModel.onMobilizeClick += self.__onMobilizeClick
        self.viewModel.onRecruitBtnClick += self.__onRecruitBtnClick
        g_clientUpdateManager.addCallbacks({'inventory.15': self.__onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.viewModel.onMobilizeClick -= self.__onMobilizeClick
        self.viewModel.onRecruitBtnClick -= self.__onRecruitBtnClick
        super(NoDetachmentsView, self)._removeListeners()

    def __onClientUpdate(self, diff):
        if diff['compDescr']:
            showAssignToVehicleView(self.__vehicle.invID)

    def __setVehicleModel(self, model):
        model.setName(self.__vehicle.userName)
        model.setType(self.__vehicle.type)
        model.setLevel(self.__vehicle.level)
        model.setNation(self.__vehicle.nationName)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.MOBILIZE_CREW)
    def __onMobilizeClick(self):
        showDetachmentMobilizationView(True, navigationViewSettings=NavigationViewSettings(NavigationViewModel.MOBILIZATION, previousViewSettings=self._navigationViewSettings))

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.NEW_COMMANDER_LIST)
    def __onRecruitBtnClick(self):
        showNewCommanderWindow(self.__vehicle.invID)

    @decorators.process('updating')
    def __createDetachment(self):
        processor = DetachmentCreate(self.__vehicle.invID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            showAssignDetachmentToVehicleView(self.__vehicle.invID)


def _detachmentSortingValue(vehicle, item):
    invID, detachment = item
    expOrder = -detachment.getDescriptor().experience
    specOrder = vehicle.intCD not in detachment.getVehicleCDs()
    classOrder = detachment.classType != vehicle.type
    return (detachment.isInRecycleBin,
     classOrder,
     specOrder,
     expOrder,
     invID)
