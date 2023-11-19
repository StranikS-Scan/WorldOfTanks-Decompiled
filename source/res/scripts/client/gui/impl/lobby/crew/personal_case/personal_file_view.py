# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/personal_case/personal_file_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui import SystemMessages
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.dialogs.dialogs import showLearnPerkConfirmationDialog, showFreeSkillConfirmationDialog, showPerksDropDialog
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_file_view_model import PersonalFileViewModel, SkillsState
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skill_model import TankmanSkillModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skills_group_model import TankmanSkillsGroupModel
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from gui.impl.lobby.crew.tankman_info import TankmanInfo
from gui.impl.lobby.crew.tooltips.perk_available_tooltip import PerkAvailableTooltip
from gui.shared import event_dispatcher
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getTankmanSkill, TankmanSkill, NO_TANKMAN, MAX_ROLE_LEVEL
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.processors.tankman import TankmanAddSkill, TankmanLearnFreeSkill
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import decorators
from helpers import dependency
from items import tankmen
from items.components.skills_constants import COMMON_ROLE
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewTooltipLogger
from uilogging.crew.logging_constants import CrewPersonalFileKeys, CrewViewKeys
from wg_async import wg_async, wg_await

class PersonalFileView(IPersonalTab, BasePersonalCaseView):
    __slots__ = ('tankmanID', 'tankman', 'canLearn', '__uiTooltipLogger', '__toolTipMgr')
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.personalFile())
    itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID=R.views.lobby.crew.personal_case.PersonalFileView(), **kwargs):
        self.tankmanID = kwargs.get('tankmanID')
        self.canLearn = False
        self.tankman = self.itemsCache.items.getTankman(self.tankmanID)
        self.__uiTooltipLogger = CrewTooltipLogger(CrewViewKeys.PERSONAL_FILE, {TooltipConstants.SKILL: CrewPersonalFileKeys.MATRIX_SKILL_TOOLTIP})
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, PersonalFileViewModel())
        super(PersonalFileView, self).__init__(settings, **kwargs)

    @property
    def viewModel(self):
        return super(PersonalFileView, self).getViewModel()

    @property
    def tankmanInfo(self):
        return self.getParentView().getChildView(TankmanInfo.LAYOUT_DYN_ACCESSOR())

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            self.__uiTooltipLogger.onBeforeTooltipOpened(tooltipId)
            if tooltipId == TooltipConstants.SKILL:
                args = [str(event.getArgument('skillName')),
                 self.tankmanID,
                 None,
                 False,
                 True,
                 self.getParentWindow()]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY)
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
        return super(PersonalFileView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return PerkAvailableTooltip(self.tankmanID) if contentID == R.views.lobby.crew.tooltips.PerkAvailableTooltip() else super(PersonalFileView, self).createToolTipContent(event, contentID)

    def onChangeTankman(self, tankmanID):
        if tankmanID == NO_TANKMAN:
            return
        self.tankmanID = tankmanID
        self.__fillModel()
        self.tankmanInfo.setTankmanId(tankmanID)

    def _onLoading(self, *args, **kwargs):
        super(PersonalFileView, self)._onLoading(*args, **kwargs)
        self.__uiTooltipLogger.initialize()
        if not self.tankmanInfo:
            self.getParentView().setChildView(TankmanInfo.LAYOUT_DYN_ACCESSOR(), TankmanInfo(self.tankmanID, isUiLoggingDisabled=False))
        self.__fillModel()

    def _finalize(self):
        self.__uiTooltipLogger.finalize()
        super(PersonalFileView, self)._finalize()

    def _getEvents(self):
        eventsTuple = super(PersonalFileView, self)._getEvents()
        return eventsTuple + ((self.viewModel.onIncrease, self.__onIncrease),
         (self.viewModel.onReset, self.__onReset),
         (self.viewModel.onHoverSkill, self.__onHoverSkill),
         (self.viewModel.onLeaveSkill, self.__onLeaveSkill),
         (self.viewModel.onClickSkill, self.__onClickSkill),
         (self.itemsCache.onSyncCompleted, self.__update))

    def __update(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__fillModel()
            return
        if self.tankmanID in diff.get(GUI_ITEM_TYPE.TANKMAN, {}):
            if self.itemsCache.items.getTankman(self.tankmanID):
                self.__fillModel()

    @property
    def __resetDisabled(self):
        for skill in self.tankman.skills:
            if skill.name in self.tankman.freeSkillsNames:
                continue
            return False

        return True

    def __setSkillLearningStatus(self, vm):
        selectAvailableSkillsCount = 0
        newSkillCnt, _ = getTmanNewSkillCount(self.tankman)
        if self.tankman.newFreeSkillsCount > 0:
            vm.setSkillsState(SkillsState.ZEROSKILLS)
            selectAvailableSkillsCount = self.tankman.newFreeSkillsCount
        elif newSkillCnt > 0:
            vm.setSkillsState(SkillsState.LEARNAVAILABLE)
            selectAvailableSkillsCount = newSkillCnt
        elif self.tankman.allSkillsLearned():
            vm.setSkillsState(SkillsState.ALLSKILLS)
        elif self.tankman.roleLevel < MAX_ROLE_LEVEL:
            vm.setSkillsState(SkillsState.ACHIEVE)
        else:
            vm.setSkillsState(SkillsState.TRAINING)
        vm.setSelectAvailableSkillsCount(selectAvailableSkillsCount)

    def __fillSkillsMatrix(self, vm):
        commonSkills = vm.getCommonSkills()
        commonSkills.clear()
        relevantTankmanSkills = vm.getRelevantGroupedSkills()
        relevantTankmanSkills.clear()
        irrelevantTankmanSkills = vm.getIrrelevantGroupedSkills()
        irrelevantTankmanSkills.clear()
        vm.setIsTankmanWithDescription(bool(self.tankman.getDescription()))
        for group, skills in self.tankman.getPossibleSkillsByRole().iteritems():
            if group == COMMON_ROLE:
                self.__fillSkillsList(commonSkills, skills)
            skillsGroup = TankmanSkillsGroupModel()
            skillsGroup.setRole(group)
            self.__fillSkillsList(skillsGroup.getSkills(), skills)
            if group in self.tankman.roles():
                relevantTankmanSkills.addViewModel(skillsGroup)
            irrelevantTankmanSkills.addViewModel(skillsGroup)

        commonSkills.invalidate()
        relevantTankmanSkills.invalidate()
        irrelevantTankmanSkills.invalidate()

    def __fillSkillsList(self, skillsListVM, skills):
        for skill in skills:
            tankmanSkillModel = TankmanSkillModel()
            tankmanSkillModel.setSkillProgress(skill.level)
            tankmanSkillModel.setSkillId(skill.name)
            tankmanSkillModel.setSkillUserName(skill.userName)
            tankmanSkillModel.setSkillIcon(skill.extensionLessIconName)
            tankmanSkillModel.setIsInProgress(skill.name in self.tankman.skillsInProgress)
            tankmanSkillModel.setIsZero(skill.name in self.tankman.freeSkillsNames)
            skillsListVM.addViewModel(tankmanSkillModel)

        skillsListVM.invalidate()

    def __fillModel(self):
        self.tankman = self.itemsCache.items.getTankman(self.tankmanID)
        with self.viewModel.transaction() as vm:
            vm.setIsFemale(self.tankman.isFemale)
            vm.setHasIncreaseDiscount(self.__hasIncreaseDiscount())
            vm.setHasDropSkillDiscount(self.__hasDropSkillDiscount())
            vm.setIsTankmanInVehicle(self.tankman.vehicleDescr is not None)
            vm.setIsResetDisable(self.__resetDisabled)
            self.__setSkillLearningStatus(vm)
            self.__fillSkillsMatrix(vm)
        return

    def __hasIncreaseDiscount(self):
        return self.itemsCache.items.shop.freeXPToTManXPRate != self.itemsCache.items.shop.defaults.freeXPToTManXPRate

    def __hasDropSkillDiscount(self):
        for currency, dropCost in self.itemsCache.items.shop.dropSkillsCost.iteritems():
            defaultDropCost = self.itemsCache.items.shop.defaults.dropSkillsCost[currency]
            if dropCost != defaultDropCost:
                return True

        return False

    def __onIncrease(self):
        self.uiLogger.logClick(CrewPersonalFileKeys.MATRIX_INCREASE_BUTTON)
        vehicleInvID = self.tankman.vehicleInvID if self.tankman and self.tankman.isInTank else NO_VEHICLE_ID
        event_dispatcher.showQuickTraining(tankmanInvID=self.tankmanID, vehicleInvID=vehicleInvID, previousViewID=R.views.lobby.crew.TankmanContainerView())

    def __onReset(self):
        self.uiLogger.logClick(CrewPersonalFileKeys.MATRIX_RESET_BUTTON)
        showPerksDropDialog(self.tankmanID)

    def __onHoverSkill(self, args):
        skillId = args.get('skillId')
        if not any((skill.name == skillId and skill.level == tankmen.MAX_SKILL_LEVEL for skill in self.tankman.skills)):
            self.getParentView().updateTTCWithSkillName(skillId)

    def __onLeaveSkill(self, _):
        self.getParentView().updateTTCWithSkillName(None)
        return

    @wg_async
    def __onClickSkill(self, args):
        skillId = args.get('skillId')
        skillsState = self.viewModel.getSkillsState()
        skill = getTankmanSkill(skillId, tankman=self.tankman)
        if skillsState == SkillsState.LEARNAVAILABLE or skillsState == SkillsState.ZEROSKILLS:
            self.uiLogger.logClick(CrewPersonalFileKeys.MATRIX_SKILL)
        if skillsState == SkillsState.LEARNAVAILABLE:
            newSkillCnt, newSkillLvl = getTmanNewSkillCount(self.tankman)
            level = tankmen.MAX_SKILL_LEVEL if newSkillCnt > 1 else newSkillLvl.intSkillLvl
            result = yield wg_await(showLearnPerkConfirmationDialog(skill, int(level)))
            if not result.busy:
                isOk, _ = result.result
                if isOk:
                    self.__onLearnSkill(skill, self.tankman)
        elif skillsState == SkillsState.ZEROSKILLS:
            result = yield wg_await(showFreeSkillConfirmationDialog(skill=skill))
            if not result.busy:
                isOk, _ = result.result
                if isOk:
                    self.__onLearnFreeSkill(skill, self.tankman)

    @decorators.adisp_process('studying')
    def __onLearnSkill(self, skill, tankman):
        processor = TankmanAddSkill(tankman, skill.name)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @decorators.adisp_process('studying')
    def __onLearnFreeSkill(self, skill, tankman):
        processor = TankmanLearnFreeSkill(tankman, skill.name)
        result = yield processor.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
