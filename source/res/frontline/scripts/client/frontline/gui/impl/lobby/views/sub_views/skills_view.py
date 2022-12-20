# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/skills_view.py
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.frontline_helpers import geFrontlineState
from frontline.gui.frontline_skill_packer import packSkills
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryType
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_model import SkillCategoryModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skills_view_model import SkillsViewModel
from frontline.gui.impl.lobby.tooltips.skill_order_tooltip import SkillOrderTooltip
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IEpicBattleMetaGameController

class SkillsView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('_selectedSkillId',)

    def __init__(self, layoutID=R.views.frontline.lobby.SkillsView()):
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, SkillsViewModel())
        super(SkillsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SkillsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            tooltipID = event.getArgument('tooltipID')
            return createBackportTooltipContent(tooltipID)
        return SkillOrderTooltip() if contentID == R.views.frontline.lobby.tooltips.SkillOrderTooltip() else super(SkillsView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onSkillSelect, self.__onSkillSelect), (self.viewModel.onSkillActivate, self.__onSkillActivate), (self.__epicController.onUpdated, self.__onUpdate))

    def _onLoading(self, *args, **kwargs):
        super(SkillsView, self)._onLoading(*args, **kwargs)
        pointsAmount = self.__epicController.getSkillPoints()
        with self.viewModel.transaction() as vm:
            self._updateFrontlineState(vm)
            vm.setPointsAmount(pointsAmount)
            categories = vm.getCategories()
            for category, skillsData in self.__epicController.getOrderedSkillTree():
                categoryModel = SkillCategoryModel()
                categoryModel.setType(SkillCategoryType(category))
                skills = categoryModel.getSkills()
                packSkills(skills, skillsData, pointsAmount)
                categories.addViewModel(categoryModel)

            if categories and categories[0].getSkills():
                skills = categories[0].getSkills()
                self._selectedSkillId = skills[0].getId()
                vm.setSelectedSkillId(self._selectedSkillId)

    def _updateFrontlineState(self, model):
        state, _, _ = geFrontlineState()
        model.setFrontlineState(state.value)

    def __onUpdate(self, diff):
        with self.viewModel.transaction() as vm:
            categories = vm.getCategories()
            isUpdated = False
            if 'abilityPts' in diff:
                pointsAmount = diff['abilityPts']
                vm.setPointsAmount(pointsAmount)
                for category in categories:
                    skills = category.getSkills()
                    for skill in skills:
                        isUpdated = True
                        skill.setIsDisabled(skill.getPrice() > pointsAmount and not skill.getIsActivated())

            if 'abilities' in diff:
                for category in categories:
                    skills = category.getSkills()
                    for skill in skills:
                        if skill.getId() in diff['abilities']:
                            skill.setIsActivated(True)
                            skill.setIsDisabled(False)
                            isUpdated = True
                            break

            if isUpdated:
                categories.invalidate()
            if 'seasons' in diff:
                self._updateFrontlineState(vm)

    def __onSkillSelect(self, args):
        with self.viewModel.transaction() as vm:
            vm.setSelectedSkillId(args.get('id', self._selectedSkillId))

    def __onSkillActivate(self, args):
        self.__epicController.increaseSkillLevel(args.get('id', self._selectedSkillId))
