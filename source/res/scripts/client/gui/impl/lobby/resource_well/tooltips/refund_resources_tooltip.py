# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/tooltips/refund_resources_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.tooltips.refund_resources_tooltip_model import RefundResourcesTooltipModel
from gui.impl.pub import ViewImpl

class RefundResourcesTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.tooltips.RefundResourcesTooltip())
        settings.model = RefundResourcesTooltipModel()
        super(RefundResourcesTooltip, self).__init__(settings)
