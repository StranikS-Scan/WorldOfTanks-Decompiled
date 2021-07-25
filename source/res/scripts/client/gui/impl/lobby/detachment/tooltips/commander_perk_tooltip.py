# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/commander_perk_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.commander_perk_tooltip_model import CommanderPerkTooltipModel
from gui.impl.pub import ViewImpl

class CommanderPerkTooltip(ViewImpl):
    __slots__ = ('__type',)

    def __init__(self, perkType=CommanderPerkTooltipModel.SIXTH_SENSE):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.CommanderPerkTooltip())
        settings.model = CommanderPerkTooltipModel()
        self.__type = perkType
        super(CommanderPerkTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CommanderPerkTooltip, self).getViewModel()

    def _onLoading(self):
        super(CommanderPerkTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setType(self.__type)
