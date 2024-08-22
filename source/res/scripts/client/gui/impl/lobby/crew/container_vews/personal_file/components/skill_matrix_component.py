# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/personal_file/components/skill_matrix_component.py
import BigWorld
import typing
from itertools import chain
from constants import NEW_PERK_SYSTEM as NPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skill_model import TankmanSkillModel, AnimationType
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skills_group_model import TankmanSkillsGroupModel
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.crew_helpers.tankman_helpers import getPerksResetGracePeriod
from gui.impl.lobby.crew.tooltips.bonus_perks_tooltip import BonusPerksTooltip
from gui.impl.lobby.crew.tooltips.empty_skill_tooltip import EmptySkillTooltip
from gui.impl.lobby.crew.tooltips.perk_available_tooltip import PerkAvailableTooltip
from gui.impl.lobby.crew.tooltips.qualification_tooltip import QualificationTooltip
from gui.shared.gui_items.artefacts import TAG_CREW_BATTLE_BOOSTER
from gui.shared.gui_items.Tankman import TankmanSkill, getBattleBooster, isSkillLearnt
from helpers import dependency
from items.tankmen import MAX_SKILL_LEVEL, SKILLS_BY_ROLES, COMMON_SKILLS
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from uilogging.crew.loggers import CrewTankmanInfoLogger, CrewTooltipLogger
from uilogging.crew.logging_constants import CrewPersonalFileKeys, CrewViewKeys
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent
    from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_file_view_model import PersonalFileViewModel
    from gui.impl.gen.view_models.views.lobby.crew.personal_case.skills_matrix_model import SkillsMatrixModel
    from typing import Any, Callable, Iterable, Optional, Tuple

class SkillMatrixComponent(ComponentBase):
    itemsCache = dependency.descriptor(IItemsCache)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, key, parent, logUIEvents=False):
        self._uiLogger = CrewTankmanInfoLogger(logUIEvents)
        self._uiTooltipLogger = CrewTooltipLogger(CrewViewKeys.PERSONAL_FILE, {TooltipConstants.SKILL: CrewPersonalFileKeys.MATRIX_SKILL_TOOLTIP})
        self._toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        self.__isOnFocus = True
        super(SkillMatrixComponent, self).__init__(key, parent)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            self._uiTooltipLogger.onBeforeTooltipOpened(tooltipId)
            if tooltipId == TooltipConstants.SKILL:
                skillName = event.getArgument('skillName')
                args = [str(skillName),
                 self.context.tankmanID,
                 None,
                 True,
                 None,
                 event.getArgument('isBonus')]
                self._toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_GF, args, event.mouse.positionX, event.mouse.positionY, parent=self.parent.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_GF
            if tooltipId == TooltipConstants.DIRECTIVE:
                return createAndLoadBackportTooltipWindow(self.parent.getParentWindow(), isSpecial=True, tooltipId=TOOLTIPS_CONSTANTS.BATTLE_BOOSTER_BLOCK, specialArgs=[int(event.getArgument('intCD')),
                 0,
                 -1,
                 self.context.tankman.getVehicle()])
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.crew.tooltips.PerkAvailableTooltip():
            return PerkAvailableTooltip(self.context.tankmanID)
        if contentID == R.views.lobby.crew.tooltips.QualificationTooltip():
            return QualificationTooltip(event.getArgument('index'), event.getArgument('role'), event.getArgument('isBonusQualification'), self.context.tankman.isFemale)
        if contentID == R.views.lobby.crew.tooltips.BonusPerksTooltip():
            return BonusPerksTooltip()
        return EmptySkillTooltip(self.context.tankman, int(event.getArgument('skillIndex'))) if contentID == R.views.lobby.crew.tooltips.EmptySkillTooltip() else None

    def _getViewModel(self, vm):
        return vm.skills

    def _getEvents(self):
        return super(SkillMatrixComponent, self)._getEvents() + ((self.viewModel.onIncrease, self._onIncrease),
         (self.viewModel.onReset, self._onReset),
         (self.viewModel.onSkillClick, self._onSkillClick),
         (self.viewModel.onSetAnimationInProgress, self._onSetAnimationInProgress))

    def _getSkillAnimationType(self, tankmanSkillModel, index, isBonus=False):
        animationType = AnimationType.NONE
        if self.context.skillAnimationsSkipped or tankmanSkillModel.getIsLocked():
            return animationType
        else:
            currentAnimationType = tankmanSkillModel.getAnimationType()
            if currentAnimationType == AnimationType.SELECTED or currentAnimationType == AnimationType.UNLOCKED:
                return
            skillName = tankmanSkillModel.getSkillId()
            crewAccountController = BigWorld.player().crewAccountController
            unlockIndexBefore = crewAccountController.indexSkillsUnlockAnimation(self.context.tankman.invID)
            hasLearnedSkillAnimation = crewAccountController.hasLearnedSkillAnimation(self.context.tankman.invID, skillName)
            if skillName and hasLearnedSkillAnimation:
                animationType = AnimationType.SELECTED
            elif unlockIndexBefore is not None:
                index = index * 2 if isBonus else index
                animationType = AnimationType.UNLOCKED if unlockIndexBefore <= index else animationType
            return animationType

    def _fillViewModel(self, vm):
        perksResetGracePeriod = getPerksResetGracePeriod()
        hasFreeReset = not self.context.tankman.descriptor.firstSkillResetDisabled
        vm.setHasResetDiscount(not self.context.resetDisabled and (self.context.hasDropSkillDiscount or hasFreeReset or perksResetGracePeriod > 0))
        vm.setIsResetDisable(self.context.resetDisabled)
        vm.setHasIncreaseDiscount(self.context.hasIncreaseDiscount)
        vm.setResetGracePeriodLeft(perksResetGracePeriod)
        self._fillMajorSkills(vm)
        self._fillBonusSkills(vm)

    def _fillMajorSkills(self, vm):
        tman = self.context.tankman
        freeSkills = list(chain(tman.freeSkills, [None] * tman.freeSkillsCount))[:tman.freeSkillsCount]
        emptySkillsCount = max(0, NPS.MAX_MAJOR_PERKS - tman.earnedSkillsCount - tman.freeSkillsCount)
        skills = list(chain(freeSkills, tman.earnedSkills, [None] * emptySkillsCount))
        emptyLevelsCount = max(0, NPS.MAX_MAJOR_PERKS - len(tman.skillsLevels))
        levels = list(chain(tman.skillsLevels, [None] * emptyLevelsCount))
        self._fillSkillsGroupModel(tman.role, skills, vm.mainSkills, levels)
        return

    def _fillBonusSkills(self, vm):
        bonusSkills = vm.getBonusSkills()
        bonusSkills.clear()
        for role, skills in self.context.tankman.bonusSkills.iteritems():
            gm = TankmanSkillsGroupModel()
            self._fillSkillsGroupModel(role, skills, gm, self.context.tankman.bonusSlotsLevels)
            bonusSkills.addViewModel(gm)

        bonusSkills.invalidate()

    def _fillSkillsGroupModel(self, role, skills, gm, skillsLevels):
        gm.setRole(role)
        gm.setSelectedSkillsCount(len(filter(None, skills)))
        gm.setDirectiveId(0)
        gm.setDirectiveName('')
        isMajor = role == self.context.tankman.role
        skillsWithDirectives = []
        skillsList = gm.getSkills()
        skillsList.clear()
        for index, (skill, level) in enumerate(zip(skills, skillsLevels)):
            isFree = isMajor and index < self.context.tankman.freeSkillsCount
            level = MAX_SKILL_LEVEL if isFree else level
            tankmanSkillModel = self._getSkillModel(skill, level, role, isFree)
            animationType = self._getSkillAnimationType(tankmanSkillModel, index, not isMajor)
            if animationType is not None:
                tankmanSkillModel.setAnimationType(animationType)
            skillsWithDirectives.append(tankmanSkillModel.getWithDirective())
            skillsList.addViewModel(tankmanSkillModel)

        skillsList.invalidate()
        if not any(skillsWithDirectives):
            self._fillGroupDirective(gm, role, isMajor)
        return

    def _getSkillModel(self, skill, level, role, isFree):
        sm = TankmanSkillModel()
        sm.setSkillProgress(level or 0)
        sm.setIsLocked(level is None)
        sm.setIsZero(isFree)
        if skill:
            sm.setSkillId(skill.name)
            sm.setSkillUserName(skill.userName)
            sm.setSkillIcon(skill.extensionLessIconName)
            sm.setIsInProgress(skill.level < MAX_SKILL_LEVEL)
            sm.setWithDirective(getBattleBooster(self.context.tankmanCurrentVehicle, skill.name) is not None)
            if self.context.tankman.isInTank:
                sm.setIsFullDirective(isSkillLearnt(skill.name, self.context.tankmanCurrentVehicle))
            sm.setIsDisabled(not skill.isEnable)
            sm.setIsIrrelevant(not skill.isRelevantForRole(role))
        return sm

    def _fillGroupDirective(self, vm, role, isMajorRole):
        booster = self.context.getInstalledBooster()
        if isMajorRole:
            canShow = self.context.tankman.skillsCount < NPS.MAX_MAJOR_PERKS
        else:
            canShow = not all(self.context.tankman.bonusSkills[role])
        if not (canShow and booster):
            return
        if TAG_CREW_BATTLE_BOOSTER in booster.tags:
            skillName = booster.descriptor.skillName
            isCommonSkill = skillName in COMMON_SKILLS
            if isCommonSkill and isMajorRole or not isCommonSkill and skillName in SKILLS_BY_ROLES[role]:
                vm.setDirectiveId(booster.intCD)
                vm.setDirectiveName(booster.name)

    def _onIncrease(self):
        self._uiLogger.logClick(CrewPersonalFileKeys.MATRIX_INCREASE_BUTTON)
        self.events.onIncreaseClick()

    def _onReset(self):
        self.events.logClick(CrewPersonalFileKeys.MATRIX_RESET_BUTTON)
        self.events.onResetClick(self.context.tankmanID)

    def _onSkillClick(self, kwargs):
        data = {'tankmanInvID': int(self.context.tankman.invID),
         'role': kwargs.get('role')}
        self.events.onSkillClick(**data)

    def _onSetAnimationInProgress(self, kwargs):
        data = {'isEnabled': kwargs.get('isEnabled')}
        self.events.onSetAnimationInProgress(**data)

    def _onFocus(self, focused):
        if not self.__isOnFocus and focused:
            with self.viewModel.transaction() as vm:
                vm.setResetGracePeriodLeft(getPerksResetGracePeriod())
        self.__isOnFocus = focused
