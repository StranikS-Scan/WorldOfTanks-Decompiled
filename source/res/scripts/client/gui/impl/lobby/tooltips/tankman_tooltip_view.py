# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/tankman_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_model import TankmanTooltipViewModel
from gui.impl.pub import ViewImpl

class TankmanTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.tooltips.TankmanTooltipView())
        settings.model = TankmanTooltipViewModel()
        super(TankmanTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmanTooltipView, self).getViewModel()
