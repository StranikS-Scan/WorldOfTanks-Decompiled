# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/comp7_charge_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.comp7_charge_tooltip_model import Comp7ChargeTooltipModel
from gui.impl.pub import ViewImpl

class Comp7ChargeTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.comp7.tooltips.Comp7ChargeTooltip())
        settings.model = Comp7ChargeTooltipModel()
        super(Comp7ChargeTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Comp7ChargeTooltip, self).getViewModel()
