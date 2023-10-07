# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/commander_bonus_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_model import CrewPerksTooltipModel
from gui.impl.pub import ViewImpl
from items.components.skills_constants import SkillTypeName

class CommanderBonusTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksTooltip(), args=args, kwargs=kwargs)
        settings.model = CrewPerksTooltipModel()
        super(CommanderBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CommanderBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CommanderBonusTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIcon(backport.image(R.images.gui.maps.icons.tankmen.skills.big.commander_bonus()))
            vm.setTitle(backport.text(R.strings.tooltips.commanderBonus.name()))
            vm.setSkillType(SkillTypeName.COMMANDER_SPECIAL)
            vm.setIsAdvancedTooltipEnable(True)
            vm.setDescription(backport.text(R.strings.tooltips.commanderBonus.description()))
