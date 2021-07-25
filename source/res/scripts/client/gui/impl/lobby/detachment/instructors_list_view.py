# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/instructors_list_view.py
from copy import deepcopy
import nations
from frameworks.wulf import ViewFlags, ViewSettings
from gui import GUI_NATIONS_ORDER_INDICES
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentShortInfoModel
from gui.impl.auxiliary.instructors_helper import getInstructorState, fillInstructorCardModel, InstructorStates, canInsertInstructorToSlot, getInstructorTokenNationInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.instructors_list_view_model import InstructorsListViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.instructors_view_base import InstructorsViewBase
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.detachment.ttc_mixin import TTCMixin
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters.instructor_filters import defaultInstructorPopoverFilter, defaultInstructorToggleFilter
from gui.impl.lobby.detachment.popovers.vehicle_selector_popover_content import VehicleSelectorPopoverContent
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.shared.utils.requesters import REQ_CRITERIA
from items import ITEM_TYPES
from items.components.detachment_constants import NO_DETACHMENT_ID
from uilogging.detachment.loggers import InstructorListLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import GROUP

class InstructorsListView(TTCMixin, InstructorsViewBase):
    __slots__ = ('__detachmentInvID', '__detachment', '__slotID')
    _CLOSE_IN_PREBATTLE = True
    _popoverFilters = defaultInstructorPopoverFilter()
    _toggleFilters = defaultInstructorToggleFilter()
    uiLogger = InstructorListLogger(GROUP.INSTRUCTOR_CHOICE_LIST)

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.InstructorsListView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = InstructorsListViewModel()
        super(InstructorsListView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__detachmentInvID = ctx.get('detInvID', None)
        self.__detachment = self._detachmentCache.getDetachment(self.__detachmentInvID)
        self.__slotID = ctx.get('slotID', 0)
        super(InstructorsListView, self)._resetData()
        InstructorsListView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())
        return

    @property
    def viewModel(self):
        return super(InstructorsListView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(InstructorsListView, self)._initialize()
        vehicle = self._itemsCache.items.getVehicle(self.__detachment.vehInvID) if self.__detachment.isInTank else None
        self._updateTTCCurrentDetachment(self.__detachmentInvID)
        self._updateTTCVehicle(vehicle)
        return

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            instructorID = event.getArgument('instructorId')
            PerkTooltip.uiLogger.setGroup(self.uiLogger.group)
            return PerkTooltip(perkId, instructorInvID=instructorID, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)
        elif event.contentID == R.views.lobby.detachment.tooltips.CommanderPerkTooltip():
            perkType = event.getArgument('perkType')
            return CommanderPerkTooltip(perkType=perkType)
        elif contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=self.__detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            self._tooltip = tooltip
            return self._tooltip
        elif contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            selectedVehicle = g_detachmentTankSetupVehicle.defaultItem
            tooltip = SkillsBranchTooltipView(detachmentID=self.__detachmentInvID, branchID=int(course) + 1, vehIntCD=selectedVehicle.intCD if selectedVehicle else None)
            self._tooltip = tooltip
            return self._tooltip
        elif contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=self.__detachmentInvID)
        elif contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(self.__detachmentInvID)
        else:
            return super(InstructorsListView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        popover = super(InstructorsListView, self).createPopOverContent(event)
        if popover:
            return popover
        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.VEHICLE_SELECTOR_GF_POPOVER)
        return VehicleSelectorPopoverContent(self.__detachmentInvID, self.viewModel.rightPanelModel.popover.setIsActive, self.__handleChangeVehicle)

    def _resetData(self):
        super(InstructorsListView, self)._resetData()
        self._resetPopover()

    def _resetPopoverFilters(self):
        super(InstructorsListView, self)._resetPopoverFilters()
        self._resetPopover()

    def _resetPopover(self):
        cards = self._getInstructorCards(self._filterInstructorItems())
        if not cards:
            InstructorsListView._popoverFilters.update(self._defaultPopoverSetter())
        InstructorsListView._defaultPopoverFilterItems = deepcopy(self._popoverFilters.items())

    @property
    def _ttcModel(self):
        return self.viewModel.rightPanelModel.ttcModel

    def _addListeners(self):
        model = self.viewModel
        model.onInstructorHover += self.__onInstructorHover
        model.onInstructorOut += self.__onInstructorOut
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.vehicle): self._onClientUpdate,
         'inventory.{}'.format(ITEM_TYPES.detachment): self._onClientUpdate})
        super(InstructorsListView, self)._addListeners()

    def _removeListeners(self):
        model = self.viewModel
        model.onInstructorHover -= self.__onInstructorHover
        model.onInstructorOut -= self.__onInstructorOut
        super(InstructorsListView, self)._removeListeners()

    def _onClientUpdate(self, *args, **kwargs):
        self.__detachment = self._detachmentCache.getDetachment(self.__detachmentInvID)
        super(InstructorsListView, self)._onClientUpdate(*args, **kwargs)

    def _fillViewModel(self, model):
        model.setDetachmentNation(self.__detachment.nationName)
        vehicleGuiItem = self._itemsCache.items.getVehicle(self.__detachment.vehInvID)
        self.__updateSelectedVehicle(model.rightPanelModel.selectedVehicle, vehicleGuiItem)
        self._updateTTCVehicle(vehicleGuiItem)
        fillDetachmentShortInfoModel(model.detachmentInfo, self.__detachment)
        self._updateRose(model.rightPanelModel.roseModel)
        super(InstructorsListView, self)._fillViewModel(model)

    def _fillInstructorCardModel(self, instructor, instrCardData):
        fillInstructorCardModel(instructor, instrCardData, self.__detachmentInvID)

    def _getInstructorViewArgs(self, inst):
        args = super(InstructorsListView, self)._getInstructorViewArgs(inst)
        args.update({'slotID': self.__slotID,
         'detInvID': self.__detachmentInvID})
        return args

    def _addDefaultPopoverFilter(self):
        InstructorsListView._popoverFilters[PopoverFilterGroups.NATION].add(self.__detachment.nationName)

    def _getInstructorCriteria(self, popoverFilters=None, toggleFilters=None):
        criteria = super(InstructorsListView, self)._getInstructorCriteria(popoverFilters, toggleFilters)
        criteria |= ~REQ_CRITERIA.INSTRUCTOR.IS_UNREMOVABLE
        return criteria

    def _instructorCardSortingValue(self, instructorCard):
        _, _, item = instructorCard
        classID = -item.classID
        isToken = item.isToken()
        status = getInstructorState(item, self.__detachmentInvID)
        isNotSetNation = not item.descriptor.isNationSet()
        nationOrder = -GUI_NATIONS_ORDER_INDICES[item.nationID]
        isInSquad = status == InstructorStates.IN_SQUAD
        isInBattle = status == InstructorStates.IN_BATTLE
        isInCurrentDet = status == InstructorStates.ON_CURRENT_DET
        isRemovable = not item.isUnremovable
        isAvailableForRemove = isRemovable and not (isInSquad or isInBattle) and not isInCurrentDet
        isExcluded = item.isExcluded
        isAvailable = item.detInvID == NO_DETACHMENT_ID and not isExcluded
        isEqualNation = self.__detachment and self.__detachment.nationID == item.nationID
        isTokenNationCompatible = False
        if isNotSetNation and self.__detachment:
            detInvID = self.__detachment.invID
            isSingleNation, detNationInAvailableNations, tokenNation = getInstructorTokenNationInfo(item, detInvID)
            isTokenNationCompatible = self.__detachment.nationName == tokenNation or bool(detNationInAvailableNations)
            if isSingleNation:
                isEqualNation = self.__detachment.nationName == tokenNation
                nationOrder = -GUI_NATIONS_ORDER_INDICES[nations.INDICES.get(tokenNation, nations.NONE_INDEX)]
                isNotSetNation = False
        return (isToken,
         classID,
         isNotSetNation,
         isEqualNation,
         isTokenNationCompatible,
         nationOrder,
         isAvailable,
         isExcluded,
         isAvailableForRemove,
         isInSquad,
         isInBattle,
         isRemovable,
         isInCurrentDet,
         -item.descriptor.settingsID)

    def _isReverseSort(self):
        return True

    def _onEscape(self):
        if self._notRecruitedState:
            self.updateNotRecruitedState(False)
        else:
            self._onBack()

    def _onBack(self):
        from gui.shared.event_dispatcher import showDetachmentViewById
        if self.__detachmentInvID != NO_DETACHMENT_ID and self._navigationViewSettings.getPreviousViewSettings() is None:
            showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': self.__detachmentInvID})
        else:
            super(InstructorsListView, self)._onBack()
        return

    def _updateRose(self, model):
        fillRoseSheetsModel(model, self.__detachment, g_detachmentTankSetupVehicle.defaultItem)

    def _setIsEnoughtSlotsForCategoryModel(self, categoryModel, instructor):
        categoryModel.setIsEnoughSlots(canInsertInstructorToSlot(self.__detachmentInvID, instructor.invID, self.__slotID, checkNations=False))

    def _setRequiredLevelForCategoryModel(self, categoryModel, instructor):
        requiredSlots = instructor.descriptor.getSlotsCount()
        minLevelForInstructor = self.__detachment.progression.instructorUnlockLevels[requiredSlots - 1]
        if self.__detachment.level < minLevelForInstructor:
            categoryModel.setRequiredLevel(minLevelForInstructor)

    def updateNotRecruitedState(self, state):
        super(InstructorsListView, self).updateNotRecruitedState(state)
        ttcVisibility = True
        if not state:
            ttcVisibility = self._ctx.get('totalCount', 0) > 0
        self._setTTCVisibility(ttcVisibility)

    def __handleChangeVehicle(self, typeCompDescr):
        vehicleGuiItem = self._itemsCache.items.getStockVehicle(int(typeCompDescr))
        with self.viewModel.transaction() as model:
            self.__updateSelectedVehicle(model.rightPanelModel.selectedVehicle, vehicleGuiItem)
            self._updateTTCVehicle(vehicleGuiItem)
            self._updateRose(model.rightPanelModel.roseModel)

    @staticmethod
    def __updateSelectedVehicle(model, vehicleItem):
        if vehicleItem is not None:
            model.setName(vehicleItem.userName)
            model.setIcon(getIconResourceName(vehicleItem.name))
            model.setLevel(vehicleItem.level)
            model.setType(vehicleItem.type)
            model.setIsElite(vehicleItem.isElite)
        return

    def __onInstructorHover(self, event):
        instructorInvID = event.get('instructorInvID')
        instructor = self._detachmentCache.getInstructor(instructorInvID)
        if instructor.detInvID != self.__detachmentInvID and not instructor.isToken() and canInsertInstructorToSlot(self.__detachmentInvID, instructorInvID, self.__slotID, checkNations=True):
            g_detachmentTankSetupVehicle.addComparableInstructorID(instructorInvID)
            self._updateTTCPerks(comparableInstructor=True)
            with self.viewModel.transaction() as model:
                self._updateRose(model.rightPanelModel.roseModel)

    def __onInstructorOut(self, event):
        instructorInvID = event.get('instructorInvID')
        if instructorInvID not in g_detachmentTankSetupVehicle.comparableInstructors:
            return
        g_detachmentTankSetupVehicle.removeComparableInstructorID(instructorInvID)
        self._updateTTCPerks(comparableInstructor=bool(len(g_detachmentTankSetupVehicle.comparableInstructors)))
        with self.viewModel.transaction() as model:
            self._updateRose(model.rightPanelModel.roseModel)
