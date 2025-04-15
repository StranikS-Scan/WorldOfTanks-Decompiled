# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/tooltips/refund_resources_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.refund_resources_tooltip_model import RefundResourcesTooltipModel

class RefundResourcesTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.lobby.feature.tooltips.RefundResourcesTooltip())
        settings.model = RefundResourcesTooltipModel()
        super(RefundResourcesTooltip, self).__init__(settings)
