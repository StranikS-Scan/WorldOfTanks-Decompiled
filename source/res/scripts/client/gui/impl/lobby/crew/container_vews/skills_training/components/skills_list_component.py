# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/skills_training/components/skills_list_component.py
import logging
from functools import partial
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.skill_training_model import SkillTrainingModel
from gui.impl.gen.view_models.views.lobby.crew.sort_dropdown_item_model import SortingTypeEnum
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.container_views.base.components import ComponentBase
from gui.impl.lobby.crew.container_vews.skills_training import loadSortingOrderType
from gui.impl.lobby.crew.crew_helpers import getTankmanCrewAssistOrderSets
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
    from gui.shared.gui_items.tankman_skill import TankmanSkill
    from skeletons.gui.game_control import IWotPlusController
_logger = logging.getLogger(__name__)

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
                 self.context.role,
                 self.context.tankman.invID,
                 None,
                 False,
                 True,
                 None,
                 -1,
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
        commonSkills = skillsByRoles[COMMON_ROLE]
        regularSkills = skillsByRoles[self.context.role]
        irrelevantSkills = [ skill for skill in self.context.tankman.skills if not skill.isRelevant ]
        self.__fillSkillsList(irrelevantSkillsList, irrelevantSkills)
        popularityData, popularitySortFunction = self.__getCrewAssistPopularityData()
        if popularitySortFunction:
            self.__fillSkillsList(regularSkillsList, commonSkills + regularSkills, popularityData=popularityData, sortFunction=popularitySortFunction)
        else:
            self.__fillSkillsList(commonSkillsList, commonSkills, popularityData=popularityData)
            self.__fillSkillsList(regularSkillsList, regularSkills, popularityData=popularityData)

    def __fillBonusSkillsList(self, skillsByRoles, regularSkillsList):
        bonusSkills = skillsByRoles[self.context.role]
        popularityData, popularitySortFunction = self.__getCrewAssistPopularityData()
        self.__fillSkillsList(regularSkillsList, bonusSkills, checkIrrelevant=False, popularityData=popularityData, sortFunction=popularitySortFunction)

    def __fillSkillsList(self, skillsListVM, skills, checkIrrelevant=True, popularityData=None, sortFunction=None):
        tankman = self.context.tankman
        bonusSlotsLevels = self.context.tankman.bonusSlotsLevels
        role = self.context.role
        if sortFunction:
            skills.sort(key=sortFunction)
        for skill in skills:
            skillVM = SkillTrainingModel()
            isSelected = skill.name in self.context.selectedSkills
            level = skill.level
            skillParams = getSkillParams(tankman, self.context.tankmanCurrentVehicle, None, skill, skill.name, MAX_SKILL_LEVEL, not skill.isLearnedAsMajor)
            isZero = None
            if not self.context.isMajorQualification and skill.isLearnedAsBonus:
                idx = tankman.bonusSkills[role].index(skill)
                level = bonusSlotsLevels[idx]
            elif isSelected:
                idx = self.context.selectedSkills.index(skill.name)
                level, isZero = self.context.availableSkillsData[idx]
            skillModelSetup(skillVM, skill=skill, tankman=tankman, role=role, skillLevel=level, isZero=isZero, checkIrrelevant=checkIrrelevant)
            skillVM.setIsSelected(isSelected)
            skillVM.setUserName(skill.userName)
            skillVM.setIsLearned(skill.isLearnedAsMajor if self.context.isMajorQualification else skill.isLearnedAsBonus)
            skillVM.setDescription(formatDescription(skill.maxLvlDescription, skillParams.get('keyArgs', {})))
            popularityListModel = skillVM.getPopularityList()
            popularityListModel.clear()
            if popularityData:
                pTypes = popularityData.get(skill.name, (0, 0))
                popularityListModel.reserve(len(pTypes))
                for pT in pTypes:
                    popularityListModel.addReal(pT)

            popularityListModel.invalidate()
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

    def __getCrewAssistPopularityData(self):
        skillTrainingView = self.parent
        wotPlustCtrl = skillTrainingView.wotPlus
        popularitySet = None
        if wotPlustCtrl.isCrewAssistEnabled():
            sortingType = loadSortingOrderType()
            popularitySet = getTankmanCrewAssistOrderSets(self.context.tankman, self.context.role)
            hasCommonSet, hasLegendarySet = wotPlustCtrl.validateCrewAssistOrderSets(popularitySet)
            if sortingType == SortingTypeEnum.COMMON.value and not hasCommonSet:
                sortingType = SortingTypeEnum.DEFAULT.value
            if sortingType == SortingTypeEnum.LEGENDARY.value and not hasLegendarySet:
                sortingType = SortingTypeEnum.DEFAULT.value
            orderSetDataIndex = -1
            if sortingType == SortingTypeEnum.COMMON.value:
                orderSetDataIndex = 0
            elif sortingType == SortingTypeEnum.LEGENDARY.value:
                orderSetDataIndex = 1
            if orderSetDataIndex != -1:

                def __getSortOrder(orderSet, dataIndex, tankmanSkill):
                    skillOrder = orderSet.get(tankmanSkill.name, None)
                    if skillOrder is not None:
                        return -skillOrder[dataIndex]
                    else:
                        _logger.warning("Couldn't find %s order for tankman skill=%s", 'common' if dataIndex == 0 else 'legendary', tankmanSkill.name)
                        return 0

                return (popularitySet, partial(__getSortOrder, popularitySet, orderSetDataIndex))
        return (popularitySet, None)
