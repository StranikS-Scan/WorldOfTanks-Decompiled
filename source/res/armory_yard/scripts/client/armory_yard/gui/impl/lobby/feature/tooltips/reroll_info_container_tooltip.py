# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/reroll_info_container_tooltip.py
from frameworks.wulf import ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.reroll_info_container_tooltip_model import RerollInfoContainerTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class RerollInfoContainerTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.RerollInfoContainerTooltip())
        settings.model = RerollInfoContainerTooltipModel()
        super(RerollInfoContainerTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RerollInfoContainerTooltip, self).getViewModel()
