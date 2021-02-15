# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/progression_styles_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.progression_styles_info_tooltipw_model import ProgressionStylesInfoTooltipwModel
from gui.impl.pub import ViewImpl

class ProgressionStylesInfoTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.tooltips.ProgressionStylesInfoTooltip())
        settings.model = ProgressionStylesInfoTooltipwModel()
        super(ProgressionStylesInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProgressionStylesInfoTooltip, self).getViewModel()
