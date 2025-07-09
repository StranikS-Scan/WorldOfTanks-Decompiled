# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/crew_member_skill_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.crew_member_skill_tooltip_model import CrewMemberSkillTooltipModel
from gui.impl.pub import ViewImpl

class CrewMemberSkillTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.CrewMemberSkillTooltip())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = CrewMemberSkillTooltipModel()
        super(CrewMemberSkillTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CrewMemberSkillTooltip, self).getViewModel()

    def _onLoading(self, name, isZero, hasZeroPerk):
        with self.viewModel.transaction() as model:
            model.setName(name)
            model.setIsZero(isZero)
            model.setHasZeroPerk(hasZeroPerk)
