# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/mobilization_tooltip.py
from crew2 import settings_globals
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.mobilization_tooltip_model import MobilizationTooltipModel
from gui.impl.pub import ViewImpl
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class MobilizationTooltip(ViewImpl):
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.MobilizationTooltip())
        settings.model = MobilizationTooltipModel()
        super(MobilizationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MobilizationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MobilizationTooltip, self)._onLoading()
        date = settings_globals.g_conversion.endConversion
        with self.viewModel.transaction() as model:
            model.setEndTimeConvert(date)
            model.setEndDate(backport.getLongDateFormat(date))

    def _initialize(self, *args, **kwargs):
        super(MobilizationTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(MobilizationTooltip, self)._finalize()
