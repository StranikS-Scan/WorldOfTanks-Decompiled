# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tooltips/warning_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.warning_tooltip_view_model import WarningTooltipViewModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.warning_tooltip_view_model import WarningDescription

class WarningTooltipView(ViewImpl):

    def __init__(self, reason, isCritical):
        settings = ViewSettings(R.views.lobby.tanksetup.tooltips.WarningTooltipView())
        settings.model = WarningTooltipViewModel()
        settings.args = (reason, isCritical)
        super(WarningTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WarningTooltipView, self).getViewModel()

    def _onLoading(self, reason, isCritical, *args, **kwargs):
        super(WarningTooltipView, self)._onLoading(*args, **kwargs)
        self.viewModel.setReason(reason)
        self.viewModel.setIsCritical(isCritical)
