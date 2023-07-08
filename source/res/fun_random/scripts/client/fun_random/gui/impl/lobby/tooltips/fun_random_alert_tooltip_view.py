# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_alert_tooltip_view.py
from frameworks.wulf import ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_alert_tooltip_view_model import FunRandomAlertTooltipViewModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FunRandomAlertTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.tooltips.FunRandomAlertTooltipView(), model=FunRandomAlertTooltipViewModel())
        super(FunRandomAlertTooltipView, self).__init__(settings)
