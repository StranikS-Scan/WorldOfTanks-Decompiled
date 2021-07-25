# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/hangar_widget.py
from collections import namedtuple
from typing import TYPE_CHECKING, Tuple
from CurrentVehicle import g_currentVehicle
from crew2.detachment_states import CanProcessDetachmentResult
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillRoseSheetsModel, hasDetachmentInCurrentVehicle, fillDetachmentShortInfoModel, canProcessDetachment
from gui.impl.auxiliary.instructors_helper import fillInstructorList, showInstructorSlotsDisabledMessage, GUI_NO_INSTRUCTOR_ID
from gui.impl.backport import BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.hangar_widget_model import HangarWidgetModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.points_info_tooltip_model import PointsInfoTooltipModel
from gui.impl.lobby.detachment.navigation_view_settings import NavigationViewSettings
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.pub import ViewImpl
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers.dependency import descriptor
from items import ITEM_TYPES
from items.components import detachment_constants
from items.components.detachment_constants import PROGRESS_MAX
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.game_control import IDetachmentController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
if TYPE_CHECKING:
    from gui.shared.gui_items.detachment import Detachment
_ContextMenuData = namedtuple('ContextMenuData', ('type', 'args'))

class HangarWidget(ViewImpl):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __detachmentCache = descriptor(IDetachmentCache)
    __detachmentController = descriptor(IDetachmentController)
    __appLoader = descriptor(IAppLoader)
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.HangarWidget(), ViewFlags.COMPONENT, HangarWidgetModel())
        super(HangarWidget, self).__init__(settings)
        self._prevDetachmentInvID = detachment_constants.NO_DETACHMENT_ID

    @property
    def viewModel(self):
        return super(HangarWidget, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(HangarWidget, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.updateView(init=True)

    def _finalize(self):
        self.__removeListeners()
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        super(HangarWidget, self)._finalize()

    def __addListeners(self):
        self.viewModel.onCommanderClicked += self.__onCommanderClicked
        self.viewModel.onRoseClicked += self.__onRoseClicked
        self.viewModel.onSkillPointsClicked += self.__onSkillPointsClicked
        self.viewModel.onInstructorSlotClicked += self.__onInstructorSlotClicked
        self.viewModel.onDogClicked += self.__onDogClicked
        g_currentVehicle.onChangeStarted += self._onVehicleChangeStarted
        g_currentVehicle.onChanged += self._onCurrentVehicleChanged
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.detachment): self._onClientUpdate})

    def __removeListeners(self):
        self.viewModel.onCommanderClicked -= self.__onCommanderClicked
        self.viewModel.onRoseClicked -= self.__onRoseClicked
        self.viewModel.onSkillPointsClicked -= self.__onSkillPointsClicked
        self.viewModel.onInstructorSlotClicked -= self.__onInstructorSlotClicked
        self.viewModel.onDogClicked -= self.__onDogClicked
        g_currentVehicle.onChangeStarted -= self._onVehicleChangeStarted
        g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onRoseClicked(self):
        self.__openPerksMatrixView()

    def __onDogClicked(self):
        self.__appLoader.getApp().soundManager.playEffectSound(SoundEffectsId.RUDY_DOG)

    def __onSkillPointsClicked(self):
        self.__openPerksMatrixView()

    def __onInstructorSlotClicked(self, event):
        if not self.__lobbyContext.getServerSettings().isInstructorSlotsEnabled():
            showInstructorSlotsDisabledMessage()
            return
        from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
        from gui.shared.event_dispatcher import showDetachmentViewById, showInstructorPageWindow
        instructorInvId = int(event.get('invId'))
        slotId = int(event.get('index'))
        detInvID = g_currentVehicle.item.getLinkedDetachmentID()
        if instructorInvId == GUI_NO_INSTRUCTOR_ID:
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.INSTRUCTOR_CHOICE_LIST)
            showDetachmentViewById(NavigationViewModel.INSTRUCTORS_LIST, {'detInvID': detInvID,
             'slotID': slotId})
        else:
            g_detachmentFlowLogger.flow(self.uiLogger.group, target=GROUP.INSTRUCTOR_PAGE)
            showInstructorPageWindow({'navigationViewSettings': NavigationViewSettings(NavigationViewModel.INSTRUCTOR_PAGE, {'instructorInvID': instructorInvId,
                                        'detInvID': detInvID})})

    def __onCommanderClicked(self):
        detInvID, _ = self.__getVehicleInfo()
        if detInvID == detachment_constants.NO_DETACHMENT_ID:
            self.showSelectDetachment()
        else:
            self.showPersonalCase()

    def __openPerksMatrixView(self):
        from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
        from gui.shared.event_dispatcher import showDetachmentViewById
        showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PERKS_MATRIX, {'detInvID': g_currentVehicle.item.getLinkedDetachmentID()}, NavigationViewSettings(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': g_currentVehicle.item.getLinkedDetachmentID()}))

    def _onVehicleChangeStarted(self):
        with self.viewModel.transaction() as vm:
            vm.setIsDisabled(True)

    def _onCurrentVehicleChanged(self):
        self.updateView()

    def _onClientUpdate(self, *args, **kwargs):
        self.updateView()

    def updateView(self, init=False):
        with self.viewModel.transaction() as vm:
            hasDetachment = hasDetachmentInCurrentVehicle()
            vm.setIsLinked(hasDetachment)
            vm.setIsDisabled(g_currentVehicle.isInBattle() or g_currentVehicle.isInPrebattle())
            if hasDetachment:
                self._setDetachmentState(vm, init)
            else:
                self._setEmptyState(vm)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.ASSIGN_DETACHMENT)
    def showSelectDetachment(self):
        from gui.shared import event_dispatcher
        event_dispatcher.showAssignDetachmentToVehicleView(g_currentVehicle.invID)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.DETACHMENT_PERSONAL_CASE)
    def showPersonalCase(self):
        from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
        from gui.shared.event_dispatcher import showDetachmentViewById, isViewLoaded
        if isViewLoaded(R.views.lobby.detachment.dialogs.DemobilizeDetachmentDialogView()):
            return
        detInvID, _ = self.__getVehicleInfo()
        if detInvID != detachment_constants.NO_DETACHMENT_ID:
            showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': detInvID})

    def _setDetachmentState(self, vm, init=False):
        currentDetachmentInvID, _ = self.__getVehicleInfo()
        detachment = self.__detachmentCache.getDetachment(currentDetachmentInvID)
        if detachment is None:
            return
        else:
            prevInfo = self.__detachmentController.getShownProgress(currentDetachmentInvID)
            if currentDetachmentInvID != self._prevDetachmentInvID or not self._isEqualExp(detachment, prevInfo) or init:
                self._prevDetachmentInvID = currentDetachmentInvID
                fillDetachmentShortInfoModel(vm.detachmentInfo, detachment, fillInstructors=False)
                prevProgress, prevLvl, prevLvlIcon, prevMastery, prevExp = prevInfo
                vm.detachmentInfo.setPrevLevel(prevLvl)
                vm.detachmentInfo.setProgressDeltaFrom(prevProgress * PROGRESS_MAX)
                vm.detachmentInfo.setPrevLevelIconId(prevLvlIcon)
                vm.detachmentInfo.setPrevMastery(prevMastery)
                vm.detachmentInfo.setIsXpDown(prevExp > detachment.experience)
            self._setCommonData(detachment, vm)
            self._setRoseData(detachment, vm)
            return

    def _isEqualExp(self, detachment, prevInfo):
        _, _, _, _, prevExp = prevInfo
        return prevExp == detachment.experience

    def _setEmptyState(self, vm):
        self._prevDetachmentInvID, hasDogTag = self.__getVehicleInfo()
        vm.setIsDisabled(False)
        vm.setIsLastCrewInBarracks(self._isCrewInBarracks())
        vm.detachmentInfo.setHasDog(hasDogTag)
        if g_currentVehicle.isPresent():
            vm.detachmentInfo.setNation(g_currentVehicle.item.nationName)

    def _isCrewInBarracks(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return False
        else:
            lastCrew = vehicle.lastCrew
            if lastCrew is None:
                return False
            for tankmanInvID in lastCrew:
                tankman = self.__itemsCache.items.getTankman(tankmanInvID)
                if tankman is not None and not tankman.isInTank and not tankman.isDismissed:
                    return True

            return False

    def _setRoseData(self, detachment, vm):
        fillRoseSheetsModel(vm.roseModel, detachment)

    def _setCommonData(self, detachment, vm):
        vm.detachmentInfo.setLevelIconId(detachment.levelIconID)
        vm.detachmentInfo.setIsMaxLevel(detachment.hasMaxMasteryLevel)
        vm.detachmentInfo.setIsElite(detachment.hasMaxLevel)
        vm.detachmentInfo.setAvailablePoints(detachment.freePoints)
        vm.detachmentInfo.vehicle.setType(detachment.classTypeUnderscore)
        fillInstructorList(vm.detachmentInfo.getInstructorsList(), detachment, fillLocked=True)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = _ContextMenuData('hangarWidget', {})
            g_detachmentFlowLogger.flow(self.uiLogger.group, GROUP.HANGAR_DETACHMENT_WIDGET_CONTEXT_MENU)
            window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
            window.load()
            return window
        return super(HangarWidget, self).createContextMenu(event)

    def createToolTipContent(self, event, contentID):
        from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
        detachmentID = g_currentVehicle.item.getLinkedDetachmentID()
        if contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=detachmentID, vehicleInvID=g_currentVehicle.invID)
        elif contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            detachment = self.__detachmentCache.getDetachment(detachmentID)
            detStatus = canProcessDetachment(detachment, checkLockCrew=False) if detachment else False
            PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return PointInfoTooltipView(event.contentID, state=PointsInfoTooltipModel.DEFAULT, isClickable=detStatus == CanProcessDetachmentResult.OK, detachmentID=detachmentID)
        elif contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return SkillsBranchTooltipView(detachmentID=detachmentID, branchID=int(course) + 1, vehIntCD=g_currentVehicle.item.intCD)
        elif contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = int(event.getArgument('instructorInvID'))
            isLocked = event.getArgument('isLocked')
            detachment = self.__detachmentCache.getDetachment(detachmentID)
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=detachment if instructorID == GUI_NO_INSTRUCTOR_ID else None, isLocked=isLocked)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        elif contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(detachmentID)
        else:
            return super(HangarWidget, self).createToolTipContent(event, contentID)

    def __getVehicleInfo(self):
        currentVehicle = g_currentVehicle.item
        return (currentVehicle.getLinkedDetachmentID(), detachment_constants.DOG_TAG in currentVehicle.tags) if currentVehicle is not None else (detachment_constants.NO_DETACHMENT_ID, False)
