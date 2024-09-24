# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/components/skills_list_component.py
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.skill_training_model import SkillTrainingModel
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.crew_helpers.skill_helpers import formatDescription, getSkillParams
from gui.impl.lobby.crew.crew_helpers.skill_model_setup import skillModelSetup
from helpers import dependency
from items.components.skills_constants import COMMON_ROLE
from items.tankmen import MAX_SKILL_LEVEL
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Tuple
    from gui.impl.gen.view_models.views.lobby.crew.skills_training_view_model import SkillsTrainingViewModel
    from gui.impl.gen.view_models.views.lobby.crew.skills_list_model import SkillsListModel
    from gui.shared.gui_items.Tankman import TankmanSkill

class SkillsListComponent(ComponentBase):
    __slots__ = ('__toolTipMgr',)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, key, parent):
        self.__toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
        super(SkillsListComponent, self).__init__(key, parent)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.SKILL_ALT:
                positionX = event.getArgument('positionX', event.mouse.positionX)
                args = [str(event.getArgument('skillName')),
                 self.context.tankman.invID,
                 None,
                 False,
                 True]
                self.__toolTipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.CREW_PERK_ALT_GF, args, int(positionX), event.mouse.positionY, parent=self.parent.getParentWindow())
                return TOOLTIPS_CONSTANTS.CREW_PERK_ALT_GF
        return super(SkillsListComponent, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(SkillsListComponent, self).createToolTipContent(event, contentID)

    def _getViewModel(self, vm):
        return vm.skillsList

    def _getEvents(self):
        return super(SkillsListComponent, self)._getEvents() + ((self.viewModel.onSkillHover, self._onSkillHover),
         (self.viewModel.onSkillOut, self._onSkillOut),
         (self.viewModel.onSkillClick, self._onSkillClick),
         (self.viewModel.onTrain, self.__onTrain),
         (self.viewModel.onCancel, self.__onCancel))

    def _fillViewModel(self, vm):
        commonSkillsList = vm.getCommonSkillsList()
        irrelevantSkillsList = vm.getIrrelevantSkillsList()
        regularSkillsList = vm.getRegularSkillsList()
        commonSkillsList.clear()
        irrelevantSkillsList.clear()
        regularSkillsList.clear()
        skillsByRoles = self.context.tankman.getPossibleSkillsByRole()
        if self.context.isMajorQualification:
            self.__fillMajorSkillsList(skillsByRoles, commonSkillsList, regularSkillsList, irrelevantSkillsList)
        else:
            self.__fillBonusSkillsList(skillsByRoles, regularSkillsList)

    def __fillMajorSkillsList(self, skillsByRoles, commonSkillsList, regularSkillsList, irrelevantSkillsList):
        role = self.context.role
        commonSkills = skillsByRoles[COMMON_ROLE]
        regularSkills = skillsByRoles[role]
        irrelevantSkills = [ skill for skill in self.context.tankman.skills if not skill.isRelevantForRole(role) ]
        self.__fillSkillsList(commonSkillsList, commonSkills)
        self.__fillSkillsList(regularSkillsList, regularSkills)
        self.__fillSkillsList(irrelevantSkillsList, irrelevantSkills)

    def __fillBonusSkillsList(self, skillsByRoles, regularSkillsList):
        bonusSkills = skillsByRoles[self.context.role]
        self.__fillSkillsList(regularSkillsList, bonusSkills)

    def __fillSkillsList(self, skillsListVM, skills):
        tankman = self.context.tankman
        bonusSlotsLevels = self.context.tankman.bonusSlotsLevels
        for skill in skills:
            skillVM = SkillTrainingModel()
            isSelected = skill.name in self.context.selectedSkills
            level = skill.level
            skillParams = getSkillParams(tankman, self.context.tankmanCurrentVehicle, None, skill, skill.name, MAX_SKILL_LEVEL, not skill.isLearnedAsMajor)
            isZero = None
            if not self.context.isMajorQualification and skill.isLearnedAsBonus:
                idx = tankman.bonusSkills[self.context.role].index(skill)
                level = bonusSlotsLevels[idx]
            elif isSelected:
                idx = self.context.selectedSkills.index(skill.name)
                level, isZero = self.context.availableSkillsData[idx]
            skillModelSetup(skillVM, skill=skill, tankman=tankman, role=self.context.role, skillLevel=level, isZero=isZero)
            skillVM.setIsSelected(isSelected)
            skillVM.setUserName(skill.userName)
            skillVM.setIsLearned(skill.isLearnedAsMajor if self.context.isMajorQualification else skill.isLearnedAsBonus)
            skillVM.setDescription(formatDescription(skill.maxLvlDescription, skillParams.get('keyArgs', {})))
            skillsListVM.addViewModel(skillVM)

        skillsListVM.invalidate()
        return

    def _onSkillHover(self, kwargs):
        self.events.onSkillHover(kwargs.get('id'))

    def _onSkillOut(self, kwargs):
        self.events.onSkillOut(kwargs.get('id'))

    def _onSkillClick(self, kwargs):
        self.events.onSkillClick(kwargs.get('id'))

    def __onTrain(self):
        self.events.onTrain()

    def __onCancel(self):
        self.events.onCancel()
