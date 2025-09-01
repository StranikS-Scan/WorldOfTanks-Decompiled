# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/tooltips/major_perk_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.base_perk_tooltip_model import BasePerkTooltipModel
from gui.impl.lobby.veh_skill_tree.tooltips.base_perk_tooltip import BasePerkTooltipView

class MajorPerkTooltipView(BasePerkTooltipView):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.vehicle_hub.tooltips.perk_tooltip())
        settings.model = BasePerkTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MajorPerkTooltipView, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()
