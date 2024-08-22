# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/empty_skill_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.empty_skill_tooltip_view_model import EmptySkillTooltipViewModel
from gui.impl.pub import ViewImpl
from items.tankmen import MAX_SKILL_LEVEL

class EmptySkillTooltip(ViewImpl):
    __slots__ = ('_tankman', '_skillIndex')

    def __init__(self, tankman, skillIndex):
        self._tankman = tankman
        self._skillIndex = skillIndex
        settings = ViewSettings(R.views.lobby.crew.tooltips.EmptySkillTooltip(), model=EmptySkillTooltipViewModel())
        super(EmptySkillTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EmptySkillTooltip, self).getViewModel()

    def _onLoading(self):
        currentXp = 0
        discountXpCost = 0
        fullPriceXpCost = 0
        isLocked = False
        isZero = self._skillIndex < self._tankman.freeSkillsCount
        skillProgress = MAX_SKILL_LEVEL if isZero else 0
        tankmanDescriptor = self._tankman.descriptor
        if not isZero:
            levelIndex = self._skillIndex - self._tankman.freeSkillsCount
            discountXpCost = tankmanDescriptor.skillUpXpCost(levelIndex + 1)
            fullPriceXpCost = tankmanDescriptor.skillUpXpCost(self._skillIndex + 1)
            prevSkillFullXpCost = 0 if not levelIndex else tankmanDescriptor.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, levelIndex)
            currSkillFullXpCost = tankmanDescriptor.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, levelIndex + 1)
            if 0 <= self._skillIndex < len(self._tankman.skillsLevels):
                skillProgress = self._tankman.skillsLevels[self._skillIndex]
            else:
                isLocked = True
            tankmanTotalXp = tankmanDescriptor.totalXP()
            if not isLocked and tankmanTotalXp > 0:
                currentXp = discountXpCost
                if tankmanTotalXp < currSkillFullXpCost:
                    currentXp = tankmanTotalXp - prevSkillFullXpCost
        with self.viewModel.transaction() as vm:
            vm.setCurrentXpValue(currentXp)
            vm.setTotalXpValue(fullPriceXpCost)
            vm.setSkillProgress(skillProgress)
            vm.setDiscountValue(discountXpCost)
            vm.setZeroSkillsCount(self._tankman.freeSkillsCount)
            vm.setIsZeroSkill(isZero)
            vm.setIsLocked(isLocked)
