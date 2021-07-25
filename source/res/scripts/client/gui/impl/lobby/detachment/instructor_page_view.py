# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/instructor_page_view.py
import WWISE
import nations
from async import await, async
from crew2 import settings_globals
from crew2.crew2_consts import GENDER_TO_TAG
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, View, ViewModel
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.auxiliary.instructors_helper import fillInstructorCommanderModel, showInstructorSlotsDisabledMessage, fillPerkShortModelArray, getInstructorPageBackground
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.demount_instructor_dialog_view_model import DemountInstructorDialogViewModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_page_view_model import InstructorPageViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.gen_utils import INVALID_RES_ID
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.auxiliary.instructors_helper import canInsertInstructorToSlot
from gui.shared.event_dispatcher import isViewLoaded
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.common import RecoverInstructorProcessor, AddInstructorToSlotProcessor
from gui.shared.gui_items.processors.detachment import SetActiveInstructorInDetachment
from gui.shared.utils import decorators
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers.dependency import descriptor
from helpers.time_utils import HOURS_IN_DAY
from items.components.detachment_constants import INVALID_INSTRUCTOR_SLOT_ID, NO_DETACHMENT_ID, PROGRESS_MAX
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import BARRACKS_SOUND_SPACE, INSTRUCTOR_VIEW_EVENT
from voiceover_mixin import VoiceoverMixin

class InstructorPageView(NavigationViewImpl, VoiceoverMixin):
    __slots__ = ('__instructorInvID', '__detachmentInvID', '__slotID', '__isInstructorActive')
    _CLOSE_IN_PREBATTLE = True
    _COMMON_SOUND_SPACE = BARRACKS_SOUND_SPACE
    __itemsCache = descriptor(IItemsCache)
    __detachmentCache = descriptor(IDetachmentCache)
    __lobbyContext = descriptor(ILobbyContext)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.model = InstructorPageViewModel()
        super(InstructorPageView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__instructorInvID = ctx['instructorInvID']
        self.__detachmentInvID = ctx.get('detInvID', NO_DETACHMENT_ID)
        self.__slotID = ctx.get('slotID', 0)
        self.__isInstructorActive = False

    @property
    def viewModel(self):
        return super(InstructorPageView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            return PerkTooltip(perkId, instructorInvID=self.__instructorInvID, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)
        if contentID == R.views.lobby.detachment.tooltips.InstructorVoiceTooltip():
            return View(ViewSettings(contentID, model=ViewModel()))
        if contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.INSTRUCTOR_BONUSES:
                instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
                return createBackportTooltipContent(TOOLTIPS_CONSTANTS.INSTRUCTOR_BONUSES, (instructorItem,))

    def _initialize(self):
        super(InstructorPageView, self)._initialize()
        WWISE.WW_eventGlobal(INSTRUCTOR_VIEW_EVENT)

    def _finalize(self):
        self._stopInstructorVoice()
        activated = self.viewModel.information.getIsVoiceActivated()
        if activated != self.__isInstructorActive:
            self.__setInstructorActive(activated)
            self._setInstructorSoundMode(self.__instructorInvID)
        else:
            self._restoreSoundMode()
        super(InstructorPageView, self)._finalize()

    def _initModel(self, vm):
        super(InstructorPageView, self)._initModel(vm)
        self.__setInstructor(vm)

    def _addListeners(self):
        super(InstructorPageView, self)._addListeners()
        model = self.viewModel
        model.onAssignClick += self.__onAssignClick
        model.onDemountClick += self.__onDemountClick
        model.onRecoverClick += self.__onRecoverClick
        model.onVoiceListenClick += self.__onVoiceListenClick
        model.onVoiceToggleClick += self.__onVoiceToggleClick
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})

    def _removeListeners(self):
        model = self.viewModel
        model.onAssignClick -= self.__onAssignClick
        model.onDemountClick -= self.__onDemountClick
        model.onRecoverClick -= self.__onRecoverClick
        model.onVoiceListenClick -= self.__onVoiceListenClick
        model.onVoiceToggleClick -= self.__onVoiceToggleClick
        g_clientUpdateManager.removeCallback('inventory', self.__onInventoryUpdate)
        super(InstructorPageView, self)._removeListeners()

    def _onClose(self):
        super(InstructorPageView, self)._onClose()
        self.destroyWindow()

    def _onBack(self):
        super(InstructorPageView, self)._onBack()
        self.destroyWindow()

    def _onBackUntil(self, viewId):
        super(InstructorPageView, self)._onBackUntil(viewId)
        self.destroyWindow()

    def _onLoadPage(self, args=None):
        super(InstructorPageView, self)._onLoadPage(args)
        self.destroyWindow()

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.DETACHMENT in invDiff or GUI_ITEM_TYPE.INSTRUCTOR in invDiff:
            with self.viewModel.transaction() as model:
                self.__setInstructor(model)

    def __setInstructor(self, model):
        instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
        linkedDetachmentItem = self.__detachmentCache.getDetachment(instructorItem.detInvID)
        model.setId(self.__instructorInvID)
        model.setBackground(getInstructorPageBackground(instructorItem.pageBackground))
        model.setIcon(instructorItem.getPortraitName())
        model.setGrade(instructorItem.classID)
        model.information.setName(instructorItem.fullName)
        descUid = instructorItem.getDescription()
        if descUid and descUid != INVALID_RES_ID:
            model.information.setDescription(descUid)
        model.information.setNation(nations.MAP[instructorItem.nationID])
        model.information.setBonusExperience(instructorItem.xpBonus * PROGRESS_MAX)
        model.information.setIsVoiced(bool(instructorItem.voiceOverID))
        if linkedDetachmentItem is not None:
            activeInstructorInvID = linkedDetachmentItem.getDescriptor().getActiveInstructorInvID()
            self.__isInstructorActive = activeInstructorInvID == instructorItem.invID
        model.information.setIsVoiceActivated(self.__isInstructorActive)
        model.setIsUnremovable(instructorItem.isUnremovable)
        model.setGender(GENDER_TO_TAG[instructorItem.gender].lower())
        model.setIsAssigned(instructorItem.detInvID != NO_DETACHMENT_ID)
        model.setIsInOtherDetachment(False)
        expDate = instructorItem.excludedExpData
        if expDate:
            model.setIsRemoved(True)
            model.setRemoveTime(expDate)
        else:
            model.setIsRemoved(False)
        requiredSlots = instructorItem.descriptor.getSlotsCount()
        model.information.setRequiredSlots(requiredSlots)
        if self.__detachmentInvID != NO_DETACHMENT_ID:
            model.setIsInOtherDetachment(instructorItem.detInvID != NO_DETACHMENT_ID and self.__detachmentInvID != instructorItem.detInvID)
            detachmentItem = self.__detachmentCache.getDetachment(self.__detachmentInvID)
            minLevelForInstructor = detachmentItem.progression.instructorUnlockLevels[requiredSlots - 1]
            levelRequired = detachmentItem.level < minLevelForInstructor
            if levelRequired:
                model.setSlotLevelNeeded(minLevelForInstructor)
            model.setIsAssignDisabled(not canInsertInstructorToSlot(self.__detachmentInvID, self.__instructorInvID, self.__slotID) or levelRequired)
        perksList = model.information.getPerks()
        perksList.clear()
        fillPerkShortModelArray(perksList, instructorItem)
        fillInstructorCommanderModel(model, linkedDetachmentItem)
        return

    def __onAssignClick(self, args=None):
        self.__mount()

    @async
    def __onDemountClick(self, args=None):
        if isViewLoaded(R.views.lobby.detachment.dialogs.DemountInstructorDialogView()):
            return
        if not self.__lobbyContext.getServerSettings().isInstructorSlotsEnabled():
            showInstructorSlotsDisabledMessage()
            return
        instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
        calledFromPersonalCase = self.__detachmentInvID != NO_DETACHMENT_ID
        instructorInOtherDetachment = calledFromPersonalCase and instructorItem.detInvID != NO_DETACHMENT_ID and instructorItem.detInvID != self.__detachmentInvID
        result, selectedItem = yield await(dialogs.demountInstructor(self.getParentWindow(), ctx={'instructorInvID': self.__instructorInvID,
         'isInOtherDetachment': instructorInOtherDetachment}, returnSelectedItem=True))
        if result:
            if calledFromPersonalCase and instructorInOtherDetachment:
                self.__processDemountResult(selectedItem)
            else:
                self._onBack()

    def __processDemountResult(self, instructorDemountType):
        if instructorDemountType == DemountInstructorDialogViewModel.WAIT:
            detachmentItem = self.__detachmentCache.getDetachment(self.__detachmentInvID)
            exclusionDays = settings_globals.g_instructorSettingsProvider.exclusionHours / HOURS_IN_DAY
            detAddInstructorR = R.strings.system_messages.detachment_add_instructor
            SystemMessages.pushMessage(type=SystemMessages.SM_TYPE.Warning, text=backport.text(detAddInstructorR.not_added_excluded_instructor(), detName=detachmentItem.cmdrFullName, exclusionDays=exclusionDays))
            self._onBackUntil(NavigationViewModel.PERSONAL_CASE_BASE)
        else:
            self.__mount()
            self._onBack()

    @decorators.process('updating')
    def __mount(self):
        isActive = self.viewModel.information.getIsVoiceActivated()
        processor = AddInstructorToSlotProcessor(self.__detachmentInvID, self.__instructorInvID, self.__slotID, isActive=isActive)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            self._onBackUntil(NavigationViewModel.PERSONAL_CASE_BASE)

    @async
    def __onRecoverClick(self, args=None):
        if isViewLoaded(R.views.lobby.detachment.dialogs.RecoverInstructorDialogView()):
            return
        result = yield await(dialogs.recoverInstructor(self.getParentWindow(), ctx={'instructorInvID': self.__instructorInvID,
         'isInBarracks': self.__detachmentInvID == NO_DETACHMENT_ID}))
        if result:
            self.__processRecovery()

    @decorators.process('updating')
    def __processRecovery(self):
        processor = RecoverInstructorProcessor(instructorID=self.__instructorInvID)
        result = yield processor.request()
        SystemMessages.pushMessages(result)
        if result.success:
            if self.__detachmentInvID != NO_DETACHMENT_ID:
                processor = AddInstructorToSlotProcessor(self.__detachmentInvID, self.__instructorInvID, self.__slotID, isActive=self.viewModel.information.getIsVoiceActivated())
                result = yield processor.request()
                SystemMessages.pushMessages(result)
                if result.success:
                    self._onBackUntil(NavigationViewModel.PERSONAL_CASE_BASE)
            else:
                self._onBack()

    def __onVoiceListenClick(self, args=None):
        self._playInstructorVoice(self.__instructorInvID)

    def __onVoiceToggleClick(self, args=None):
        model = self.viewModel
        model.information.setIsVoiceActivated(not model.information.getIsVoiceActivated())

    @decorators.process('updating')
    def __setInstructorActive(self, activated):
        instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
        detInvID = instructorItem.detInvID
        linkedDetachmentItem = self.__detachmentCache.getDetachments().get(detInvID, None)
        if linkedDetachmentItem is not None:
            slotId = INVALID_INSTRUCTOR_SLOT_ID
            if activated:
                slotId = linkedDetachmentItem.getDescriptor().getInstructorSlotIDByInvID(self.__instructorInvID)
            processor = SetActiveInstructorInDetachment(detInvID, slotId)
            result = yield processor.request()
            SystemMessages.pushMessages(result)
        return


class InstructorPageWindow(LobbyWindow):

    def __init__(self, args=None, parent=None):
        super(InstructorPageWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=InstructorPageView(R.views.lobby.detachment.InstructorPageView(), args), parent=parent, layer=WindowLayer.WINDOW)
