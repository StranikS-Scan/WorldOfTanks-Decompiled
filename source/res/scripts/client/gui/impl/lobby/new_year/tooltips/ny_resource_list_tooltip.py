# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_resource_list_tooltip.py
from frameworks.wulf import ViewSettings, ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_list_tooltip_model import NyResourceListTooltipModel
from gui.impl.pub import ViewImpl

class NyResourceListTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyResourceListTooltip(), model=ViewModel())
        super(NyResourceListTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourceListTooltip, self).getViewModel()
