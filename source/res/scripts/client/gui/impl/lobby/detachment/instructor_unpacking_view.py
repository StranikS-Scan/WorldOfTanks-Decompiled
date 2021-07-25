# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/instructor_unpacking_view.py
import typing
import nations
from async import async, await
from crew2 import settings_globals
from crew2.instructor.professions import InstructorProfessions
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel, fillRoseSheetsModel
from gui.impl.auxiliary.instructors_helper import canInsertInstructorToSlot, getInstructorPageBackground
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_unpacking.unpacking_perk_model import UnpackingPerkModel
from gui.impl.gen.view_models.views.lobby.detachment.instructor_unpacking_view_model import InstructorUnpackingViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.detachment_info_tooltip import DetachmentInfoTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.level_badge_tooltip_view import LevelBadgeTooltipView
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from gui.impl.lobby.detachment.tooltips.skills_branch_view import SkillsBranchTooltipView
from gui.impl.lobby.detachment.tooltips.commander_perk_tooltip import CommanderPerkTooltip
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import isViewLoaded, getLoadedView
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.gui_items.processors.common import AddInstructorToSlotProcessor
from gui.shared.gui_items.processors.detachment import UnpackedInstructor
from gui.shared.utils import decorators
from helpers.dependency import descriptor
from items.components.detachment_constants import NO_DETACHMENT_ID
from skeletons.gui.detachment import IDetachmentCache
from uilogging.detachment.constants import GROUP
from uilogging.detachment.loggers import DetachmentLogger
from voiceover_mixin import VoiceoverMixin
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.instructor import Instructor

class InstructorUnpackingView(NavigationViewImpl, VoiceoverMixin):
    __slots__ = ('__instructorInvID', '__detachmentInvID', '__slotID', '__instructorItem', '__professionID', '__nationID', '__bonusID', '__detachment')
    _CLOSE_IN_PREBATTLE = True
    __detachmentCache = descriptor(IDetachmentCache)
    uiLogger = DetachmentLogger(GROUP.INSTRUCTOR_UNPACKING)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.model = InstructorUnpackingViewModel()
        super(InstructorUnpackingView, self).__init__(settings, ctx=ctx)
        ctx = self._navigationViewSettings.getViewContextSettings()
        self.__instructorInvID = ctx['instructorInvID']
        self.__detachmentInvID = ctx.get('detInvID', NO_DETACHMENT_ID)
        self.__detachment = self.__detachmentCache.getDetachment(self.__detachmentInvID)
        self.__slotID = ctx.get('slotID', 0)
        self.__instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
        self.__professionID = 0
        self.__nationID = nations.NONE_INDEX
        self.__bonusID = 0
        self.__selectedPerks = []
        self.__currentStep = 0

    @property
    def viewModel(self):
        return super(InstructorUnpackingView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            PerkTooltip.uiLogger.setGroup(self.uiLogger.group)
            return PerkTooltip(perkId, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)
        elif contentID == R.views.lobby.detachment.tooltips.ColoredSimpleTooltip():
            return ColoredSimpleTooltip(event.getArgument('header', ''), event.getArgument('body', ''))
        elif event.contentID == R.views.lobby.detachment.tooltips.CommanderPerkTooltip():
            perkType = event.getArgument('perkType')
            return CommanderPerkTooltip(perkType=perkType)
        elif contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            tooltip = getInstructorTooltip(instructorInvID=instructorID, detachment=self.__detachment)
            if hasattr(tooltip, 'uiLogger'):
                tooltip.uiLogger.setGroup(self.uiLogger.group)
            return tooltip
        elif contentID == R.views.lobby.detachment.tooltips.DetachmentInfoTooltip():
            DetachmentInfoTooltip.uiLogger.setGroup(self.uiLogger.group)
            return DetachmentInfoTooltip(detachmentInvID=self.__detachmentInvID)
        elif contentID == R.views.lobby.detachment.tooltips.LevelBadgeTooltip():
            LevelBadgeTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return LevelBadgeTooltipView(self.__detachmentInvID)
        elif contentID == R.views.lobby.detachment.tooltips.SkillsBranchTooltip():
            course = event.getArgument('course')
            SkillsBranchTooltipView.uiLogger.setGroup(self.uiLogger.group)
            selectedVehicle = g_detachmentTankSetupVehicle.defaultItem
            return SkillsBranchTooltipView(detachmentID=self.__detachmentInvID, branchID=int(course) + 1, vehIntCD=selectedVehicle.intCD if selectedVehicle else None)
        else:
            if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                tooltipId = event.getArgument('tooltipId')
                if tooltipId == TOOLTIPS_CONSTANTS.INSTRUCTOR_BONUSES:
                    instructorItem = self.__detachmentCache.getInstructor(self.__instructorInvID)
                    return createBackportTooltipContent(TOOLTIPS_CONSTANTS.INSTRUCTOR_BONUSES, (instructorItem,))
            return None

    def _initModel(self, vm):
        super(InstructorUnpackingView, self)._initModel(vm)
        self.__initInstructorModel(vm)

    def _finalize(self):
        self._stopInstructorVoice()
        super(InstructorUnpackingView, self)._finalize()

    def _onLoadPage(self, args=None):
        super(InstructorUnpackingView, self)._onLoadPage(args)
        self.destroyWindow()

    def _onClose(self):
        super(InstructorUnpackingView, self)._onClose()
        self.destroyWindow()

    def _onBackUntil(self, viewId):
        super(InstructorUnpackingView, self)._onBackUntil(viewId)
        self.destroyWindow()

    def _onBack(self):
        super(InstructorUnpackingView, self)._onBack()
        self.destroyWindow()

    def _addListeners(self):
        super(InstructorUnpackingView, self)._addListeners()
        model = self.viewModel
        model.onNationClick += self.__onNationClick
        model.onTabClick += self.__onTabClick
        model.onPerkClick += self.__onPerkClick
        model.onNextClick += self.__onNextClick
        model.onPreviousClick += self.__onPreviousClick
        model.onLearnClick += self.__onLearnClick
        model.onVoiceListenClick += self.__onVoiceListenClick

    def _removeListeners(self):
        model = self.viewModel
        model.onNationClick -= self.__onNationClick
        model.onTabClick -= self.__onTabClick
        model.onPerkClick -= self.__onPerkClick
        model.onNextClick -= self.__onNextClick
        model.onPreviousClick -= self.__onPreviousClick
        model.onLearnClick -= self.__onLearnClick
        model.onVoiceListenClick -= self.__onVoiceListenClick
        super(InstructorUnpackingView, self)._removeListeners()

    def __initInstructorModel(self, model):
        instructorItem = self.__instructorItem
        if not instructorItem:
            return
        if self.__detachment:
            fillDetachmentShortInfoModel(model.detachmentInfo, self.__detachment)
            fillRoseSheetsModel(model.roseModel, self.__detachment, g_detachmentTankSetupVehicle.defaultItem)
        model.setId(instructorItem.invID)
        model.setBackground(getInstructorPageBackground(instructorItem.pageBackground))
        instructorSettings = instructorItem.getInstructorSettings()
        model.setIcon(instructorItem.getPortraitName())
        celebrityName = instructorItem.getCelebrityTokenName()
        if celebrityName:
            model.information.setName(celebrityName)
        model.information.setGrade(instructorItem.classID)
        descUid = instructorItem.getDescription()
        if descUid:
            model.information.setDescription(descUid)
        model.information.setBonusExperience(instructorItem.xpBonus * 100)
        model.information.setIsVoiced(bool(instructorItem.voiceOverID))
        self.__fillProfessions(model, instructorItem, instructorSettings)
        self.__fillNations(model, instructorItem, instructorSettings)

    def __fillProfessions(self, model, instructorItem, instructorSettings):
        professions = model.perksInfo.getProfessions()
        if instructorItem.perksIDs:
            return
        for professionID in instructorSettings.professionVariants:
            professions.addString(InstructorProfessions.getProfessionNameByID(professionID))

    def __fillNations(self, model, instructorItem, instructorSettings):
        modelNations = model.getNations()
        if instructorItem.descriptor.isNationSet():
            self.__nationID = instructorItem.nationID
            nation = nations.MAP[instructorItem.nationID]
            modelNations.addString(nation)
            model.setSelectedNation(nation)
        else:
            availableNations = instructorSettings.getAvailableNations()
            for nationID in availableNations:
                modelNations.addString(nations.MAP[nationID])

            if len(availableNations) == 1:
                self.__nationID = availableNations[0]
                model.setSelectedNation(nations.MAP[availableNations[0]])
            elif self.__detachment and self.__detachment.nationID in availableNations:
                self.__nationID = self.__detachment.nationID
                model.setSelectedNation(nations.MAP[self.__detachment.nationID])

    def __onTabClick(self, args=None):
        profession = args['profession']
        if self.__professionID == profession:
            return
        model = self.viewModel
        model.perksInfo.setSelectedTab(profession)
        self.__professionID = InstructorProfessions.getProfessionIDByName(profession)
        stepsCount = len(self.__instructorItem.bonusClass.perkPoints)
        self.__selectedPerks = [0] * stepsCount
        model.perksInfo.setSteps(stepsCount)
        self.__updateStep()

    def __updateStep(self):
        model = self.viewModel
        perkPoints = self.__instructorItem.bonusClass.perkPoints
        overcapPoints = self.__instructorItem.bonusClass.overcapPoints
        levelRules = self.__instructorItem.bonusClass.levelRules
        model.perksInfo.setCurrentStep(self.__currentStep + 1)
        model.perksInfo.setMainPoints(perkPoints[self.__currentStep])
        model.perksInfo.setOvercapPoints(overcapPoints[self.__currentStep])
        model.perksInfo.setBreakPoints(levelRules[self.__currentStep])
        isp = settings_globals.g_instructorSettingsProvider
        perksIDs = isp.professions.getPerksByProfessionID(self.__professionID)
        modelPerks = model.perksInfo.getPerksList()
        modelPerks.clear()
        duplicatePerksIDs = set()
        hidePerksIDs = [ perkID for step, perkID in enumerate(self.__selectedPerks) if step < self.__currentStep ]
        for perkID in perksIDs:
            if perkID in duplicatePerksIDs or perkID in hidePerksIDs:
                continue
            duplicatePerksIDs.add(perkID)
            modelPerk = UnpackingPerkModel()
            perk = PerkGUI(perkID)
            modelPerk.setId(perkID)
            modelPerk.setName(perk.name)
            modelPerk.setIsSelected(False)
            modelPerk.setIcon(backport.image(R.images.gui.maps.icons.perks.normal.c_48x48.dyn(perk.icon)()))
            modelPerks.addViewModel(modelPerk)

        modelPerks.invalidate()
        perkID = self.__selectedPerks[self.__currentStep]
        if perkID:
            self.__onPerkClick(args={'perkId': perkID})
        with self.viewModel.perksInfo.transaction() as vm:
            vm.setSelectedPerk(perkID)

    def __onNationClick(self, args=None):
        model = self.viewModel
        nation = args['nation']
        self.__nationID = nations.INDICES[nation]
        model.setSelectedNation(nation)

    @async
    def __confirmInstructorNationChangeDialog(self):
        if isViewLoaded(R.views.lobby.detachment.dialogs.ConfirmInstructorNationChangeView()):
            return
        result = yield await(dialogs.confirmInstructorNationChange(self.getParentWindow(), ctx={'nation': nations.NAMES[self.__nationID],
         'detInvID': self.__detachmentInvID}))
        if result:
            self.__sendUnpackRequest()

    @async
    def __confrimInstructorUnpackingDialog(self):
        ctx = {'detInvID': self.__detachmentInvID,
         'instrInvID': self.__instructorInvID,
         'slotID': self.__slotID,
         'perksIDs': self.__selectedPerks,
         'nationID': self.__nationID}
        sdr = yield await(dialogs.showDetachmentConfirmUnpackingDialogView(ctx=ctx))
        if sdr.busy:
            return
        isOk, _ = sdr.result
        if isOk:
            isWrongNation = self.__detachment and self.__detachment.nationID != self.__nationID
            if isWrongNation:
                self.__confirmInstructorNationChangeDialog()
            else:
                self.__sendUnpackRequest()

    def __onPerkClick(self, args=None):
        perkID = args['perkId']
        with self.viewModel.perksInfo.transaction() as vm:
            perksList = vm.getPerksList()
            for perkVM in perksList:
                perkVM.setIsSelected(perkVM.getId() == perkID)

            vm.setSelectedPerk(perkID)
            perksList.invalidate()
        self.__selectedPerks[self.__currentStep] = perkID

    def __onNextClick(self, args=None):
        self.__currentStep += 1
        if self.__selectedPerks[self.__currentStep] in self.__selectedPerks[:self.__currentStep]:
            self.__selectedPerks[self.__currentStep] = 0
        self.__updateStep()

    def __onPreviousClick(self, args=None):
        self.__currentStep -= 1
        self.__updateStep()

    def __onLearnClick(self, args=None):
        if not self.__instructorItem:
            return
        self.__confrimInstructorUnpackingDialog()

    @decorators.process('updating')
    def __sendUnpackRequest(self):
        instructorItem = self.__instructorItem
        nation = self.__nationID if not instructorItem.descriptor.isNationSet() else instructorItem.nationID
        result = yield UnpackedInstructor(instructorItem.invID, nation, self.__professionID, self.__selectedPerks).request()
        SystemMessages.pushMessages(result)
        if result.success:
            if canInsertInstructorToSlot(self.__detachmentInvID, self.__instructorInvID, self.__slotID):
                result = yield AddInstructorToSlotProcessor(self.__detachmentInvID, self.__instructorInvID, self.__slotID, isAnim=True).request()
                SystemMessages.pushMessages(result)
                self._onBackUntil(NavigationViewModel.PERSONAL_CASE_BASE)
            else:
                parentView = getLoadedView(R.views.lobby.detachment.InstructorsListView())
                if parentView:
                    parentView.updateNotRecruitedState(False)
                self._onBack()

    def __onVoiceListenClick(self):
        self._playInstructorVoice(self.__instructorInvID)


class InstructorUnpackingWindow(LobbyWindow):

    def __init__(self, args=None, parent=None):
        super(InstructorUnpackingWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=InstructorUnpackingView(R.views.lobby.detachment.InstructorUnpackingView(), args), parent=parent, layer=WindowLayer.WINDOW)
