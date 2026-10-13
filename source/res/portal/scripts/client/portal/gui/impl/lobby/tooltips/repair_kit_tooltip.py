# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/repair_kit_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.repair_kit_tooltip_model import RepairKitTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class RepairKitTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.portal.lobby.tooltips.RepairKitTooltip())
        settings.model = RepairKitTooltipModel()
        super(RepairKitTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RepairKitTooltip, self).getViewModel()
