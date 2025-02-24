# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/empty_skill_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.empty_skill_tooltip_view_model import EmptySkillTooltipViewModel
from gui.impl.lobby.crew.crew_helpers.model_setters import setSkillProgressionModel
from gui.impl.pub import ViewImpl

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
        isZero = self._skillIndex < self._tankman.freeSkillsCount
        with self.viewModel.transaction() as vm:
            vm.setIsZeroSkill(isZero)
            setSkillProgressionModel(vm=vm.skillProgression, tankman=self._tankman, skillIndex=self._skillIndex, isZero=isZero)
