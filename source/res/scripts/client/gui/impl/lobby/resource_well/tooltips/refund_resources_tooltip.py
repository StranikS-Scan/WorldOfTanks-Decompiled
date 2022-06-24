# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/tooltips/refund_resources_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.tooltips.refund_resources_tooltip_model import RefundResourcesTooltipModel
from gui.impl.pub import ViewImpl
from uilogging.resource_well.loggers import ResourceWellReturnTooltipLogger

class RefundResourcesTooltip(ViewImpl):
    __slots__ = ()
    __uiLogger = ResourceWellReturnTooltipLogger()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.tooltips.RefundResourcesTooltip())
        settings.model = RefundResourcesTooltipModel()
        super(RefundResourcesTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RefundResourcesTooltip, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(RefundResourcesTooltip, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onTooltipOpened()

    def _finalize(self):
        self.__uiLogger.onTooltipClosed()
        super(RefundResourcesTooltip, self)._finalize()
