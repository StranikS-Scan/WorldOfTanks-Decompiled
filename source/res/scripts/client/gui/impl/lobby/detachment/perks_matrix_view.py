# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/perks_matrix_view.py
from collections import defaultdict
import typing
from BWUtil import AsyncReturn
from async import async, await
from crew2 import settings_globals
from crew2.perk.builds import BuildPresetsKey
from debug_utils import LOG_DEBUG_DEV
from frameworks.wulf import ViewFlags, ViewSettings, View
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, fillDetachmentShortInfoModel, getDropSkillsPrice
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_instructor_model import DetachmentShortInfoInstructorModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.save_matrix_dialog_view_model import SaveMatrixDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.branch_model import BranchModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix.ultimate_perk_model import UltimatePerkModel
from gui.impl.gen.view_models.views.lobby.detachment.perks_matrix_view_model import PerksMatrixViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.popovers.vehicle_selector_popover_content import VehicleSelectorPopoverContent
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.discount_tooltip import DiscountTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.tooltips.ultimate_unlock_tooltip import UltimateUnlockTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.lobby.detachment.ttc_mixin import TTCMixin
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.gui_items.Vehicle import getTankCrewRoleTag, getIconResourceName
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.perk import PerkGUI
from helpers.dependency import descriptor
from items import ITEM_TYPES
from items.components.detachment_components import isPerksRepartition
from items.components.detachment_constants import ChangePerksMode
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if typing.TYPE_CHECKING:
    from typing import Optional
    from crew2.perk.build import PerkBuildPreset
    from frameworks.wulf import ViewEvent
    from gui.shared.gui_items.Vehicle import Vehicle
_BACKPORT_TOOLTIP_DIRECTLY_DELEGATED_IDS = (TOOLTIPS_CONSTANTS.RECERTIFICATION_FORM, TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN)

class PerksMatrixView(TTCMixin, NavigationViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __slots__ = ('__collectedPerks', '__items', '__closeConfirmatorHelper', '__tooltipByContentID', '__perkTooltip')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    uiLogger = DetachmentLogger(GROUP.PERK_MATRIX)

    def __init__(self, ctx):
        settings = ViewSettings(R.views.lobby.detachment.PerksMatrixView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = PerksMatrixViewModel()
        super(PerksMatrixView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__detInvID = ctx['detInvID']
        self._vehicleGuiItem = None
        self.__closeConfirmatorHelper = CloseConfirmatorsHelper()
        self.__perkTooltip = None
        rTooltips = R.views.lobby.detachment.tooltips
        self.__tooltipByContentID = {rTooltips.CommanderPerkTooltip(): self.__getCommanderPerkTooltip,
         rTooltips.PerkTooltip(): self.__getPerkTooltip,
         rTooltips.SkillsBranchTooltip(): self.__getSkillBranchTooltip,
         rTooltips.PointsInfoTooltip(): self.__getPintsInfoTooltip,
         rTooltips.InstructorTooltip(): self.__getInstructorTooltip,
         rTooltips.UltimateUnlockTooltip(): self.__getUltimateUnlockTooltip,
         rTooltips.DetachmentInfoTooltip(): self.__getDetachmentInfoTooltip,
         rTooltips.LevelBadgeTooltip(): self.__getLevelBadgeTooltip,
         rTooltips.DiscountTooltip(): self.__getDiscountTooltip,
         R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent(): self.__getBackportTooltip}
        return

    @property
    def viewModel(self):
        return super(PerksMatrixView, self).getViewModel()

    def createPopOverContent(self, event):
        return VehicleSelectorPopoverContent(self.__detInvID, self.viewModel.rightPanelModel.popover.setIsActive, self.__handleChangeVehicle)

    def createToolTipContent(self, event, contentID):
        createTooltip = self.__tooltipByContentID.get(contentID)
        return createTooltip(event) if createTooltip else super(PerksMatrixView, self).createToolTipContent(event, contentID)

    @property
    def _ttcModel(self):
        return self.viewModel.rightPanelModel.ttcModel

    def _initialize(self, *args, **kwargs):
        super(PerksMatrixView, self)._initialize()
        self.__items = self.__itemsCache.items
        self.__collectedPerks = defaultdict(int)
        with self.viewModel.transaction() as vm:
            self.__initializeView(vm)

    def _finalize(self):
        g_detachmentTankSetupVehicle.restoreCurrentVehicle()
        self.__tooltipByContentID.clear()
        super(PerksMatrixView, self)._finalize()

    def _onEscape(self):
        self._onBack()

    @async
    def _onClose(self):
        confirmationResult = yield await(self.__closeConfirmation())
        if confirmationResult:
            super(PerksMatrixView, self)._onClose()

    def _onLoadPage(self, args=None):
        if args and args['viewId'] != NavigationViewModel.BARRACK_DETACHMENT:
            args['detInvID'] = self.__detInvID
        super(PerksMatrixView, self)._onLoadPage(args)

    def _addListeners(self):
        super(PerksMatrixView, self)._addListeners()
        self.__closeConfirmatorHelper.start(self.__closeConfirmation)
        model = self.viewModel
        model.onAddPointToPerk += self.__addPointToPerk
        model.onAddMaxPointsToPerk += self.__onAddMaxPointsToPerk
        model.onRemovePointFromPerk += self.__onRemovePointFromPerk
        model.onRemoveUnsavedPointsFromPerk += self.__removeUnsavedPointsFromPerk
        model.onRemoveAllPointsFromPerk += self.__removeAllPointsFromPerk
        model.onSelectUltimatePerk += self.__selectUltimatePerk
        model.onUnselectUltimatePerk += self.__unselectUltimatePerk
        model.onTogglePerksHighlighting += self.__togglePerksHighlighting
        model.onSaveChangesClick += self.__saveChanges
        model.onCancelChangesClick += self.__cancelChanges
        model.onClearMatrixClick += self.__clearMatrix
        model.onGoToEditModeClick += self.__goToEditMode
        model.onHighlightInstructorsByPerk += self.__highlightInstructorsByPerk
        model.onHighlightPerksByInstructor += self.__highlightPerksByInstructor
        model.onHighlightBranchByRose += self.__highlightBranchByRose
        model.onHighlightRoseByBranch += self.__highlightRoseByBranch
        model.onHidePerkTooltip += self.__onHidePerkTooltip
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'inventory.{}.compDescr'.format(ITEM_TYPES.detachment): self.__onClientUpdate,
         'shop.detachmentPriceGroups': self.__onUpdatePrice})

    def _removeListeners(self):
        super(PerksMatrixView, self)._removeListeners()
        self.__closeConfirmatorHelper.stop()
        model = self.viewModel
        model.onAddPointToPerk -= self.__addPointToPerk
        model.onAddMaxPointsToPerk -= self.__onAddMaxPointsToPerk
        model.onRemovePointFromPerk -= self.__onRemovePointFromPerk
        model.onRemoveUnsavedPointsFromPerk -= self.__removeUnsavedPointsFromPerk
        model.onRemoveAllPointsFromPerk -= self.__removeAllPointsFromPerk
        model.onSelectUltimatePerk -= self.__selectUltimatePerk
        model.onUnselectUltimatePerk -= self.__unselectUltimatePerk
        model.onTogglePerksHighlighting -= self.__togglePerksHighlighting
        model.onSaveChangesClick -= self.__saveChanges
        model.onCancelChangesClick -= self.__cancelChanges
        model.onClearMatrixClick -= self.__clearMatrix
        model.onGoToEditModeClick -= self.__goToEditMode
        model.onHighlightInstructorsByPerk -= self.__highlightInstructorsByPerk
        model.onHighlightPerksByInstructor -= self.__highlightPerksByInstructor
        model.onHighlightBranchByRose -= self.__highlightBranchByRose
        model.onHighlightRoseByBranch -= self.__highlightRoseByBranch
        model.onHidePerkTooltip -= self.__onHidePerkTooltip
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __getCurrentDetachmentData(self):
        detachment = self.__detachmentCache.getDetachment(self.__detInvID)
        detDescr = detachment.getDescriptor()
        return (detachment, detDescr, detDescr.build)

    def __initializeView(self, vm):
        detachment, detDescr, _ = self.__getCurrentDetachmentData()
        perksMatrix = detDescr.getPerksMatrix()
        buildLevel = detDescr.getBuildLevel()
        freePoints = detDescr.level - buildLevel
        vm.setAvailablePoints(freePoints)
        branchesVL = vm.getBranchesList()
        for _, branch in perksMatrix.branches.iteritems():
            self.__updateBranch(branch, initialize=True)

        branchesVL.invalidate()
        vm.setHasSavedPoints(self.__hasSavedPoints())
        fillDetachmentShortInfoModel(vm.detachmentInfo, detachment)
        vm.setEditPriceInBlanks(1)
        self.__onUpdatePrice()
        self._updateTTCCurrentDetachment(self.__detInvID)
        if detachment.isInTank:
            curVehicle = self.__items.getVehicle(detachment.vehInvID)
            baseVehicle = self.__items.getStockVehicle(curVehicle.intCD)
            self._vehicleGuiItem = baseVehicle
            self.__updateSelectedVehicle(vm, baseVehicle)
        else:
            self._updateTTCVehicle(None)
            vm.setIsPerksHighlightingDisabled(True)
        self.__refreshRose(vm, detachment)
        self.__updatePerkBonuses()
        self.__onUpdateCurrency()
        return

    def __updatePerkBonuses(self):
        detachment, _, _ = self.__getCurrentDetachmentData()
        collectedPerks = self.__collectedPerks
        with self.viewModel.transaction() as vm:
            branchesVL = vm.getBranchesList()
            for branchVM in branchesVL:
                for perkVM in branchVM.getPerksList():
                    perkID = perkVM.getId()
                    vehicle = g_detachmentTankSetupVehicle.defaultItem if self._vehicleGuiItem else None
                    boosterInfluence = detachment.getPerkBoosterInfluence(perkID, collectedPerks, vehicle=vehicle)
                    instrInfluence = detachment.getPerkInstructorInfluence(perkID, collectedPerks, vehicle=vehicle)
                    perkVM.setInstructorPoints(sum((points for _, points, _ in instrInfluence)))
                    perkVM.setInstructorsAmount(len(instrInfluence))
                    perkVM.setBoosterPoints(sum((points for _, points, _ in boosterInfluence)))

            self.__checkOvercapForInstructor(vm)
            branchesVL.invalidate()
        return

    def __getDropSkillsItemPrice(self):
        isFirstDrop, currentDropCost, defaultDropCost = getDropSkillsPrice(self.__detInvID)
        return (isFirstDrop, ItemPrice(currentDropCost, defaultDropCost))

    def __onMoneyUpdate(self, *args, **kwargs):
        self.__onUpdateCurrency()

    def __onUpdateCurrency(self):
        _, currentDropCostPrice = self.__getDropSkillsItemPrice()
        self.viewModel.editPriceInCurrency.setIsEnough(currentDropCostPrice.price <= self.__items.stats.money)

    def __onUpdatePrice(self, *args, **kwargs):
        _, dropItemPrice = self.__getDropSkillsItemPrice()
        currency = dropItemPrice.getCurrency()
        with self.viewModel.transaction() as vm:
            vm.editPriceInCurrency.setType(currency)
            vm.editPriceInCurrency.setValue(dropItemPrice.price.get(currency))
            vm.editPriceInCurrency.setHasDiscount(dropItemPrice.isActionPrice())
            vm.editPriceInCurrency.setDiscountValue(dropItemPrice.getActionPrc())

    def __onClientUpdate(self, diff):
        if self.__detInvID in diff:
            self.__onUpdatePrice()
            self.__resetMatrix()

    def __updateTTCPerks(self):
        self._updateTTCPerks(self.__collectedPerks)

    def __updateBranch(self, branch, initialize=False):
        detachmnet, detDescr, build = self.__getCurrentDetachmentData()
        perksMatrix = detDescr.getPerksMatrix()
        matrixBranch = perksMatrix.branches[branch.id]
        totalPerks = detachmnet.getPerks()
        branchesList = self.viewModel.getBranchesList()
        if initialize:
            branchVM = BranchModel()
            branchVM.setName(R.strings.item_types.abilities.dyn(matrixBranch.name)())
            branchVM.setIcon(matrixBranch.icon)
            branchesList.addViewModel(branchVM)
        else:
            branchVM = branchesList.getValue(branch.index)
            branchVM.setHasUnsavedPoints(False)
        perksListVM = branchVM.getPerksList()
        branchPoints = 0
        perksIDs = sorted(perksMatrix.getNonUltimatePerksInBranch(branch.id))
        for perkIndex, perkID in enumerate(perksIDs):
            level = build.get(perkID, 0)
            matrixPerk = perksMatrix.perks[perkID]
            if initialize:
                perk = PerkGUI(perkID)
                perkVM = PerkModel()
                perkVM.setId(perkID)
                perkVM.setName(perk.name)
                perkVM.setIcon(perk.icon)
                perkVM.setMaxPoints(matrixPerk.max_points)
                perksListVM.addViewModel(perkVM)
            else:
                perkVM = perksListVM.getValue(perkIndex)
            perkVM.setIsOvercapped(totalPerks.get(perkID) > matrixPerk.max_points)
            perkVM.setPoints(level)
            perkVM.setTempPoints(level)
            branchPoints += level

        self.__updateBranchPerksState(branchVM)
        ultimatePerksListVM = branchVM.getUltimatePerksList()
        branchVM.setCurrentPoints(branchPoints)
        branchVM.setMaxPoints(matrixBranch.ultimate_threshold)
        ultimatePerksAreUnlocked = branchPoints >= branchVM.getMaxPoints()
        branchVM.setAreUltimatePerksUnlocked(ultimatePerksAreUnlocked)
        ultimatePerksIDs = sorted(perksMatrix.getUltimatePerksInBranch(branch.id))
        selectedUltimateIndex = -1
        for perkIndex, perkID in enumerate(ultimatePerksIDs):
            if initialize:
                perk = PerkGUI(perkID)
                ultimatePerkVM = UltimatePerkModel()
                ultimatePerkVM.setId(perkID)
                ultimatePerkVM.setName(perk.name)
                ultimatePerkVM.setIcon(perk.icon)
                ultimatePerksListVM.addViewModel(ultimatePerkVM)
            else:
                ultimatePerkVM = ultimatePerksListVM.getValue(perkIndex)
            if ultimatePerksAreUnlocked:
                ultimateLevel = build.get(perkID, 0)
                if ultimateLevel == 0:
                    state = UltimatePerkModel.STATE_OPENED
                else:
                    state = UltimatePerkModel.STATE_SELECTED
                    selectedUltimateIndex = perkIndex
            else:
                state = UltimatePerkModel.STATE_LOCKED
            ultimatePerkVM.setSavedState(state)
            ultimatePerkVM.setTemporaryState(state)

        if selectedUltimateIndex >= 0:
            notSelectedUltimatePerksIDs = (perkIndex for perkIndex, _ in enumerate(ultimatePerksIDs) if perkIndex != selectedUltimateIndex)
            for perkIndex in notSelectedUltimatePerksIDs:
                ultimatePerkVM = ultimatePerksListVM.getValue(perkIndex)
                ultimatePerkVM.setSavedState(UltimatePerkModel.STATE_NOT_SELECTED)
                ultimatePerkVM.setTemporaryState(UltimatePerkModel.STATE_NOT_SELECTED)

    def __refreshRose(self, vm, detachment):
        newBuild = {}
        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                perkID = perkVM.getId()
                newBuild[perkID] = perkVM.getPoints() + self.__collectedPerks.get(perkID, 0)

            for ultimatePerkVM in branchVM.getUltimatePerksList():
                ultimatePerkID = ultimatePerkVM.getId()
                savedState = ultimatePerkVM.getSavedState()
                collectedPerkPoints = self.__collectedPerks.get(ultimatePerkID, 0)
                if savedState == UltimatePerkModel.STATE_SELECTED and collectedPerkPoints == 0 or collectedPerkPoints == 1:
                    newBuild[ultimatePerkID] = 1

        vehicle = g_detachmentTankSetupVehicle.defaultItem if self._vehicleGuiItem else None
        fillRoseSheetsModel(vm.rightPanelModel.roseModel, detachment, vehicle, newBuild=newBuild, diffBuild=self.__collectedPerks)
        return

    def __getCurrentPerkLevel(self, perkID):
        _, _, build = self.__getCurrentDetachmentData()
        level = build[perkID] if perkID in build else 0
        return level + self.__collectedPerks[perkID]

    def __handleChangeVehicle(self, typeCompDescr):
        self._vehicleGuiItem = self.__items.getStockVehicle(int(typeCompDescr))
        with self.viewModel.transaction() as vm:
            self.__updateSelectedVehicle(vm, self._vehicleGuiItem)
            self.__updatePerksHighlighting(self.viewModel.getArePerksHighlighted())
            detachment, _, _ = self.__getCurrentDetachmentData()
            self.__refreshRose(vm, detachment)
            self.__updatePerkBonuses()

    def __addPointToPerk(self, args=None):
        perkIndex = args['perkIndex']
        branchIndex = args['branchIndex']
        self.__changePerkPoints(branchIndex, perkIndex, 1)

    def __onAddMaxPointsToPerk(self, args=None):
        perkIndex = args['perkIndex']
        branchIndex = args['branchIndex']
        currentBranchVM = self.viewModel.getBranchesList().getValue(branchIndex)
        currentPerkVM = currentBranchVM.getPerksList().getValue(perkIndex)
        points = currentPerkVM.getMaxPoints() - currentPerkVM.getTempPoints()
        availablePoints = self.viewModel.getAvailablePoints()
        if points > availablePoints:
            points = availablePoints
        self.__changePerkPoints(branchIndex, perkIndex, points)

    def __onRemovePointFromPerk(self, args=None):
        perkIndex = args['perkIndex']
        branchIndex = args['branchIndex']
        self.__changePerkPoints(branchIndex, perkIndex, -1)

    def __removeUnsavedPointsFromPerk(self, args=None):
        perkIndex = args['perkIndex']
        branchIndex = args['branchIndex']
        perkVM = self.viewModel.getBranchesList().getValue(branchIndex).getPerksList().getValue(perkIndex)
        self.__changePerkPoints(branchIndex, perkIndex, perkVM.getPoints() - perkVM.getTempPoints())

    def __removeAllPointsFromPerk(self, args=None):
        perkIndex = args['perkIndex']
        branchIndex = args['branchIndex']
        points = self.viewModel.getBranchesList().getValue(branchIndex).getPerksList().getValue(perkIndex).getTempPoints()
        self.__changePerkPoints(branchIndex, perkIndex, -points)

    def __changePerkPoints(self, branchIndex, perkIndex, perkLevel):
        detachment, _, _ = self.__getCurrentDetachmentData()
        with self.viewModel.transaction() as vm:
            currentBranchVM = vm.getBranchesList().getValue(branchIndex)
            currentPerkVM = currentBranchVM.getPerksList().getValue(perkIndex)
            newFreePoints = vm.getAvailablePoints() - perkLevel
            newPerkPoints = currentPerkVM.getTempPoints() + perkLevel
            if newFreePoints < 0 or newPerkPoints > currentPerkVM.getMaxPoints() or newPerkPoints < 0:
                return
            vm.setAvailablePoints(newFreePoints)
            vm.setUnsavedSetPoints(vm.getUnsavedSetPoints() + perkLevel)
            self.__addCollectedPerkPoints(vm, currentPerkVM.getId(), perkLevel)
            currentPerkVM.setTempPoints(newPerkPoints)
            self.__updateBranchPerksState(currentBranchVM)
            currentBranchVM.setCurrentPoints(currentBranchVM.getCurrentPoints() + perkLevel)
            ultimatePerksAreUnlocked = currentBranchVM.getCurrentPoints() >= currentBranchVM.getMaxPoints()
            if currentBranchVM.getAreUltimatePerksUnlocked() is not ultimatePerksAreUnlocked:
                ultimatePerksList = currentBranchVM.getUltimatePerksList()
                for ultimatePerkVM in ultimatePerksList:
                    if ultimatePerksAreUnlocked:
                        state = UltimatePerkModel.STATE_OPENED
                    else:
                        state = UltimatePerkModel.STATE_LOCKED
                        if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED:
                            self.__setCollectedPerkPoints(vm, ultimatePerkVM.getId(), -1)
                        else:
                            self.__setCollectedPerkPoints(vm, ultimatePerkVM.getId(), 0)
                    ultimatePerkVM.setTemporaryState(state)

                self.__checkUnsavedSelectedUltimatePerk(vm, ultimatePerksList)
            currentBranchVM.setAreUltimatePerksUnlocked(ultimatePerksAreUnlocked)
            perkID = currentPerkVM.getId()
            totalPerks = detachment.getPerks(self.__collectedPerks)
            maxPoints = currentPerkVM.getMaxPoints()
            currentPerkVM.setIsOvercapped(totalPerks.get(perkID) > maxPoints)
            self.__checkOvercapForInstructor(vm)
            perksListVM = currentBranchVM.getPerksList()
            hasUnsavedPoints = any((perkVM.getTempPoints() != perkVM.getPoints() for perkVM in perksListVM))
            currentBranchVM.setHasUnsavedPoints(hasUnsavedPoints)
            vm.setHasUnsavedEditPoints(self.__hasUnsavedEditPoints())
            if vm.getIsEditModeEnabled():
                vm.setIsOperationChargeable(self.__isOperationChargeable())
        self.__updatePerkBonuses()
        self.__updateInstructorHighlight(perkID)

    def __checkOvercapForInstructor(self, vm):
        instructorsList = vm.detachmentInfo.getInstructorsList()
        for instructorVM in instructorsList:
            instructor = self.__detachmentCache.getInstructor(instructorVM.getId())
            if instructor is None:
                continue
            hasOvercappedPerk = any((overcap for _, _, overcap in instructor.getPerksInfluence(self.__collectedPerks)))
            instructorVM.setHasOvercappedPerk(hasOvercappedPerk)

        instructorsList.invalidate()
        return

    def __isOperationChargeable(self):
        return any((count < 0 for _, count in self.__collectedPerks.iteritems()))

    def __updateBranchPerksState(self, branchVM):
        _, detDescr, _ = self.__getCurrentDetachmentData()
        perksMatrix = detDescr.getPerksMatrix()
        state = PerkModel.STATE_OPENED
        perksListVM = branchVM.getPerksList()
        for perkVM in perksListVM:
            if perksMatrix.perkMinThreshold > perkVM.getTempPoints() > 0:
                state = PerkModel.STATE_LOCKED
                break

        for perkVM in perksListVM:
            if perkVM.getTempPoints() == 0:
                perkVM.setState(state)

    def __selectUltimatePerk(self, args=None):
        ultimatePerkIndex = args['ultimatePerkIndex']
        branchIndex = args['branchIndex']
        with self.viewModel.transaction() as vm:
            ultimatePerksList = vm.getBranchesList().getValue(branchIndex).getUltimatePerksList()
            selectedUltimatePerkVM = ultimatePerksList.getValue(ultimatePerkIndex)
            selectedUltimatePerkVM.setTemporaryState(UltimatePerkModel.STATE_SELECTED)
            point = 0 if selectedUltimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED else 1
            self.__setCollectedPerkPoints(vm, selectedUltimatePerkVM.getId(), point)
            for ultimatePerkVM in ultimatePerksList:
                if ultimatePerkVM is not selectedUltimatePerkVM:
                    ultimatePerkVM.setTemporaryState(UltimatePerkModel.STATE_NOT_SELECTED)
                    if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED:
                        self.__setCollectedPerkPoints(vm, ultimatePerkVM.getId(), -1)

            vm.getBranchesList().invalidate()
            self.__checkUnsavedSelectedUltimatePerk(vm, ultimatePerksList)
            if vm.getIsEditModeEnabled():
                vm.setIsOperationChargeable(self.__isOperationChargeable())
            detachment, _, _ = self.__getCurrentDetachmentData()
            self.__refreshRose(vm, detachment)

    def __unselectUltimatePerk(self, args):
        branchIndex = args['branchIndex']
        with self.viewModel.transaction() as vm:
            branchVM = vm.getBranchesList().getValue(branchIndex)
            ultimatePerksList = branchVM.getUltimatePerksList()
            for ultimatePerkVM in ultimatePerksList:
                if ultimatePerkVM.getTemporaryState() == UltimatePerkModel.STATE_SELECTED:
                    if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED:
                        self.__setCollectedPerkPoints(vm, ultimatePerkVM.getId(), -1)
                    else:
                        self.__setCollectedPerkPoints(vm, ultimatePerkVM.getId(), 0)
                ultimatePerkVM.setTemporaryState(UltimatePerkModel.STATE_OPENED)

            vm.getBranchesList().invalidate()
            self.__checkUnsavedSelectedUltimatePerk(vm, ultimatePerksList)
            if vm.getIsEditModeEnabled():
                vm.setIsOperationChargeable(self.__isOperationChargeable())
            detachment, _, _ = self.__getCurrentDetachmentData()
            self.__refreshRose(vm, detachment)

    def __addCollectedPerkPoints(self, vm, perkID, perkLevel):
        detachment, _, _ = self.__getCurrentDetachmentData()
        self.__collectedPerks[int(perkID)] += int(perkLevel)
        self.__checkCollectedPerkPoints(perkID)
        self.__refreshRose(vm, detachment)
        self.__updateTTCPerks()

    def __setCollectedPerkPoints(self, vm, perkID, perkLevel):
        detachment, _, _ = self.__getCurrentDetachmentData()
        self.__collectedPerks[int(perkID)] = int(perkLevel)
        self.__checkCollectedPerkPoints(perkID)
        self.__refreshRose(vm, detachment)
        self.__updateTTCPerks()

    def __checkCollectedPerkPoints(self, perkID):
        if self.__collectedPerks[perkID] == 0:
            self.__collectedPerks.pop(perkID)

    def __togglePerksHighlighting(self):
        if not self._vehicleGuiItem:
            return
        arePerksHighlighted = not self.viewModel.getArePerksHighlighted()
        self.__updatePerksHighlighting(arePerksHighlighted)
        self.viewModel.setArePerksHighlighted(arePerksHighlighted)

    def __updatePerksHighlighting(self, highlightOn):
        if not self._vehicleGuiItem:
            return
        else:
            build = None
            if highlightOn:
                _, detDescr, detBuild = self.__getCurrentDetachmentData()
                tankRole = getTankCrewRoleTag(self._vehicleGuiItem.descriptor.type.tags)
                if tankRole is None:
                    LOG_DEBUG_DEV('Tank "{}" has no role specified. Skipped matching build search.'.format(self._vehicleGuiItem.name))
                else:
                    bpk = BuildPresetsKey(detDescr.getPerksMatrix().id, detDescr.progressionLayoutID, tankRole)
                    LOG_DEBUG_DEV('findMatchingBuild for detachment ID:{} in tank "{}" with role "{}"'.format(self.__detInvID, self._vehicleGuiItem.name, tankRole))
                    build = settings_globals.g_builds.findMatchingBuild(bpk, detBuild)
            with self.viewModel.transaction() as vm:
                branchesList = vm.getBranchesList()
                if highlightOn and build:
                    for branchVM in branchesList:
                        for perkVM in branchVM.getPerksList():
                            perkVM.setIsRecommended(perkVM.getId() in build.perks)

                        for ultimateVM in branchVM.getUltimatePerksList():
                            ultimateVM.setIsRecommended(ultimateVM.getId() in build.perks)

                else:
                    for branchVM in branchesList:
                        for perkVM in branchVM.getPerksList():
                            perkVM.setIsRecommended(False)

                        for ultimateVM in branchVM.getUltimatePerksList():
                            ultimateVM.setIsRecommended(False)

                branchesList.invalidate()
            return

    def __calculateConfirmParams(self):
        ultimatesList = []
        perksList = []
        arePerksRemoved = False
        areUltimatesRemoved = False
        for branchVM in self.viewModel.getBranchesList():
            for ultimatePerkVM in branchVM.getUltimatePerksList():
                ultimatePerkID = ultimatePerkVM.getId()
                if ultimatePerkVM.getTemporaryState() == UltimatePerkModel.STATE_SELECTED and ultimatePerkVM.getSavedState() != UltimatePerkModel.STATE_SELECTED and self.__collectedPerks[ultimatePerkID] == 1:
                    ultimatesList.append(ultimatePerkID)
                if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED and ultimatePerkVM.getTemporaryState() != UltimatePerkModel.STATE_SELECTED:
                    areUltimatesRemoved = True

        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                tempPoints = perkVM.getTempPoints()
                if tempPoints != perkVM.getPoints() and tempPoints > 0:
                    perksList.append((perkVM.getId(), tempPoints))
                if tempPoints < perkVM.getPoints():
                    arePerksRemoved = True

        return (perksList,
         ultimatesList,
         arePerksRemoved,
         areUltimatesRemoved)

    @async
    def __saveChanges(self, exitConfirm=False):
        if isViewLoaded(R.views.lobby.detachment.dialogs.SaveMatrixDialogView()):
            return
        perksList, ultimatesList, arePerksRemoved, areUltimatesRemoved = self.__calculateConfirmParams()
        _, _, build = self.__getCurrentDetachmentData()
        collectedPerks = self.__collectedPerks.copy()
        isEditModeEnabled = self.viewModel.getIsEditModeEnabled() and isPerksRepartition(build, collectedPerks)
        operationType = SaveMatrixDialogViewModel.EXIT_CONFIRM if exitConfirm else (SaveMatrixDialogViewModel.EDIT if isEditModeEnabled else SaveMatrixDialogViewModel.ADD)
        sdr = yield await(dialogs.saveMatrix(self.getParentWindow(), ctx={'operationType': operationType,
         'points': self.viewModel.getUnsavedSetPoints(),
         'perks': perksList,
         'ultimates': ultimatesList,
         'arePerksRemoved': arePerksRemoved,
         'areUltimatesRemoved': areUltimatesRemoved,
         'detInvID': self.__detInvID}))
        confirmationResult, args = sdr.result
        if confirmationResult == DialogButtons.SUBMIT:
            ItemsActionsFactory.doAction(ItemsActionsFactory.LEARN_PERKS, self.__detInvID, collectedPerks, ChangePerksMode.DROP_PARTIAL if isEditModeEnabled else ChangePerksMode.ADD_PERKS, args.get('useBlank', False), self.viewModel.getIsEditModeEnabled())
            self.__updatePerksHighlighting(False)
            self.viewModel.setArePerksHighlighted(False)
        raise AsyncReturn(confirmationResult)

    def __cancelChanges(self):
        self.__resetMatrix()
        self.__updateTTCPerks()

    @async
    def __clearMatrix(self):
        if isViewLoaded(R.views.lobby.detachment.dialogs.SaveMatrixDialogView()):
            return
        areUltimatesRemoved = False
        for branchVM in self.viewModel.getBranchesList():
            for ultimatePerkVM in branchVM.getUltimatePerksList():
                if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED:
                    areUltimatesRemoved = True
                    break

        arePerksRemoved = False
        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                if perkVM.getPoints() > 0:
                    arePerksRemoved = True
                    break

        g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.PERK_MATRIX_DIALOGS_CLEAR_ALL)
        sdr = yield await(dialogs.saveMatrix(self.getParentWindow(), ctx={'operationType': SaveMatrixDialogViewModel.CLEAR_ALL,
         'arePerksRemoved': arePerksRemoved,
         'areUltimatesRemoved': areUltimatesRemoved,
         'detInvID': self.__detInvID}))
        result, args = sdr.result
        if result != DialogButtons.SUBMIT:
            return
        perksDict = defaultdict(int)
        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                tempPoints = perkVM.getTempPoints()
                if tempPoints != perkVM.getPoints():
                    perksDict[perkVM.getId()] = tempPoints

        for branchVM in self.viewModel.getBranchesList():
            for ultimatePerkVM in branchVM.getUltimatePerksList():
                if ultimatePerkVM.getSavedState() == UltimatePerkModel.STATE_SELECTED:
                    perksDict[ultimatePerkVM.getId()] = 0

        self.__updatePerksHighlighting(False)
        self.viewModel.setArePerksHighlighted(False)
        ItemsActionsFactory.doAction(ItemsActionsFactory.LEARN_PERKS, self.__detInvID, perksDict, ChangePerksMode.DROP_ALL, args.get('useBlank', False))

    def __hasSavedPoints(self):
        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                if perkVM.getPoints() > 0:
                    return True

        return False

    def __hasUnsavedEditPoints(self):
        for branchVM in self.viewModel.getBranchesList():
            for perkVM in branchVM.getPerksList():
                if perkVM.getTempPoints() < perkVM.getPoints():
                    return True

        return False

    def __goToEditMode(self):
        with self.viewModel.transaction() as vm:
            vm.setIsEditModeEnabled(True)
            vm.setIsOperationChargeable(False)

    def __updateSelectedVehicle(self, vm, vehicleItem):
        vm.setIsPerksHighlightingDisabled(not vehicleItem)
        if vehicleItem:
            vm.rightPanelModel.selectedVehicle.setName(vehicleItem.userName)
            vm.rightPanelModel.selectedVehicle.setIcon(getIconResourceName(vehicleItem.name))
            vm.rightPanelModel.selectedVehicle.setLevel(vehicleItem.level)
            vm.rightPanelModel.selectedVehicle.setType(vehicleItem.type)
            vm.rightPanelModel.selectedVehicle.setIsElite(vehicleItem.isElite)
            self._updateTTCVehicle(vehicleItem)
        defaultItem = g_detachmentTankSetupVehicle.defaultItem
        if defaultItem:
            defaultPerksController = defaultItem.getPerksController()
            if defaultPerksController:
                defaultPerksController.setOnStartCallback(self.__updateTTCPerks)

    def __highlightInstructorsByPerk(self, args):
        self.__updateInstructorHighlight(args['perkId'])

    def __updateInstructorHighlight(self, perkID):
        detachment, _, _ = self.__getCurrentDetachmentData()
        with self.viewModel.transaction() as vm:
            instructorsList = vm.detachmentInfo.getInstructorsList()
            instructorInfluence = detachment.getPerksInstructorInfluence(self.__collectedPerks)
            for instructorVM in instructorsList:
                highlightType = DetachmentShortInfoInstructorModel.HIGHLIGHT_TYPE_NONE
                overcaps = [ overcap for _id, _perkID, _, overcap in instructorInfluence if perkID == _perkID and instructorVM.getId() == _id ]
                if any(overcaps):
                    highlightType = DetachmentShortInfoInstructorModel.HIGHLIGHT_TYPE_RED
                elif overcaps:
                    highlightType = DetachmentShortInfoInstructorModel.HIGHLIGHT_TYPE_BLUE
                instructorVM.setHighlightType(highlightType)

            instructorsList.invalidate()

    def __highlightPerksByInstructor(self, args):
        instructorId = args['instructorId']
        with self.viewModel.transaction() as vm:
            if instructorId == -1:
                for branchVM in vm.getBranchesList():
                    for perkVM in branchVM.getPerksList():
                        perkVM.setIsHighlightedByInstructor(False)

            else:
                instructorItem = self.__detachmentCache.getInstructor(instructorId)
                bonusPerks = instructorItem.bonusPerks
                for branchVM in vm.getBranchesList():
                    for perkVM in branchVM.getPerksList():
                        perkVM.setIsHighlightedByInstructor(bonusPerks.get(perkVM.getId()) is not None)

        return

    def __highlightBranchByRose(self, args):
        course = args['course']
        with self.viewModel.transaction() as vm:
            branchesList = vm.getBranchesList()
            for i in range(0, len(branchesList)):
                branchVM = branchesList.getValue(i)
                branchVM.setIsHighlighted(course == i)

    def __highlightRoseByBranch(self, args):
        branchIndex = args['branchIndex']
        with self.viewModel.rightPanelModel.roseModel.transaction() as vm:
            sheetsList = vm.getSheets()
            for sheetVM in sheetsList:
                sheetVM.setIsHighlighted(branchIndex == sheetVM.getCourse())

            sheetsList.invalidate()

    def __onHidePerkTooltip(self):
        if self.__perkTooltip:
            self.__perkTooltip.destroy()
            self.__perkTooltip = None
        return

    def __resetMatrix(self):
        self.__collectedPerks = defaultdict(int)
        detachment, detDescr, _ = self.__getCurrentDetachmentData()
        perksMatrix = detDescr.getPerksMatrix()
        buildLevel = detDescr.getBuildLevel()
        freePoints = detDescr.level - buildLevel
        self.__updatePerkBonuses()
        with self.viewModel.transaction() as vm:
            fillDetachmentShortInfoModel(vm.detachmentInfo, detachment)
            self.__checkOvercapForInstructor(vm)
            vm.setAvailablePoints(freePoints)
            branchesVL = vm.getBranchesList()
            for branch in perksMatrix.branches.itervalues():
                self.__updateBranch(branch)

            branchesVL.invalidate()
            vm.setHasSavedPoints(self.__hasSavedPoints())
            vm.setUnsavedSetPoints(0)
            vm.setHasUnsavedEditPoints(False)
            vm.setHasUnsavedSelectedUltimatePerk(False)
            vm.setIsEditModeEnabled(False)
            vm.setIsOperationChargeable(False)
            self.__refreshRose(vm, detachment)
            self.__updatePerksHighlighting(False)
            vm.setArePerksHighlighted(False)

    def __checkUnsavedSelectedUltimatePerk(self, vm, ultimatePerksList):
        hasUnsavedSelectedUltimatePerk = any((ultimatePerkVM.getTemporaryState() != ultimatePerkVM.getSavedState() for ultimatePerkVM in ultimatePerksList))
        vm.setHasUnsavedSelectedUltimatePerk(hasUnsavedSelectedUltimatePerk)

    def __getBackportTooltip(self, event):
        tooltipId = event.getArgument('tooltipId')
        specialArgs = None
        _, currentDropCostPrice = self.__getDropSkillsItemPrice()
        shortage = self.__items.stats.money.getShortage(currentDropCostPrice.price)
        if tooltipId in _BACKPORT_TOOLTIP_DIRECTLY_DELEGATED_IDS:
            if tooltipId == TOOLTIPS_CONSTANTS.CREDITS_INFO_FULL_SCREEN and bool(shortage):
                tooltipId = TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY
                currentCurrency = currentDropCostPrice.getCurrency()
                specialArgs = (shortage.get(currentCurrency), currentCurrency)
            return createBackportTooltipContent(tooltipId, specialArgs)
        else:
            return

    def __getUltimateUnlockTooltip(self, event):
        vm = self.viewModel
        branchID = event.getArgument('course')
        currentBranchVM = vm.getBranchesList().getValue(branchID)
        currentPoints = currentBranchVM.getCurrentPoints()
        maxPoints = currentBranchVM.getMaxPoints()
        ultimatePerksList = currentBranchVM.getUltimatePerksList()
        ultimatePerkSelected = any((perk.getTemporaryState() == UltimatePerkModel.STATE_SELECTED for perk in ultimatePerksList))
        UltimateUnlockTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return UltimateUnlockTooltipView(ultimatePerkSelected=ultimatePerkSelected, currentPoints=currentPoints, maxPoints=maxPoints)

    def __getDiscountTooltip(self, _):
        isFirstDrop, dropItemPrice = self.__getDropSkillsItemPrice()
        if isFirstDrop:
            infoText = backport.text(R.strings.tooltips.discount.firstOperationOnly())
            return DiscountTooltip(dropItemPrice, infoText)
        currency = dropItemPrice.getCurrency()
        shortage = self.__items.stats.money.getShortage(dropItemPrice.price).get(currency)
        shortageDef = self.__items.stats.money.getShortage(dropItemPrice.defPrice).get(currency)
        specialArgs = (int(dropItemPrice.price.get(currency)),
         int(dropItemPrice.defPrice.get(currency)),
         currency,
         not bool(shortage),
         not bool(shortageDef))
        return createBackportTooltipContent(TOOLTIPS_CONSTANTS.PRICE_DISCOUNT, specialArgs)

    def __getDetachmentInfoTooltip(self, _):
        DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
        return DetachmentInfoTooltip(detachmentInvID=self.__detInvID)

    def __getLevelBadgeTooltip(self, _):
        LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return LevelBadgeTooltipView(self.__detInvID)

    def __getInstructorTooltip(self, event):
        instructorID = event.getArgument('instructorInvID')
        detachment = self.__detachmentCache.getDetachment(self.__detInvID)
        tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=detachment, bonusPerks=self.__collectedPerks)
        if hasattr(tooltip, 'uiLogger'):
            tooltip.uiLogger.setGroup(self.uiLogger.group)
        return tooltip

    def __getPintsInfoTooltip(self, _):
        PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return PointInfoTooltipView(R.views.lobby.detachment.tooltips.PointsInfoTooltip(), state=PointsInfoTooltipModel.DEFAULT, isClickable=False, detachmentID=self.__detInvID)

    def __getSkillBranchTooltip(self, event):
        vehIntCD = self._vehicleGuiItem.intCD if self._vehicleGuiItem else None
        SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
        return SkillsBranchTooltipView(detachmentID=self.__detInvID, branchID=int(event.getArgument('course')) + 1, vehIntCD=vehIntCD, bonusPerks=self.__collectedPerks)

    def __getPerkTooltip(self, event):
        tempPoints = event.getArgument('tempPoints')
        vehIntCD = self._vehicleGuiItem.intCD if self._vehicleGuiItem else None
        PerkTooltip.uiLogger.setGroup(self.uiLogger.group)
        self.__perkTooltip = PerkTooltip(event.getArgument('id'), detachmentInvID=self.__detInvID, tempPoints=int(tempPoints) if tempPoints is not None else None, vehIntCD=vehIntCD, tooltipType=PerkTooltipModel.MATRIX_PERK_TOOLTIP)
        return self.__perkTooltip

    def __getCommanderPerkTooltip(self, event):
        perkType = event.getArgument('perkType')
        return CommanderPerkTooltip(perkType=perkType)

    @async
    def __closeConfirmation(self):
        vm = self.viewModel
        confirmationResult = DialogButtons.CANCEL
        if vm.getHasUnsavedEditPoints() or vm.getHasUnsavedSelectedUltimatePerk() or vm.getUnsavedSetPoints() > 0:
            confirmationResult = yield await(self.__saveChanges(exitConfirm=True))
        raise AsyncReturn(confirmationResult != DialogButtons.EXIT)
