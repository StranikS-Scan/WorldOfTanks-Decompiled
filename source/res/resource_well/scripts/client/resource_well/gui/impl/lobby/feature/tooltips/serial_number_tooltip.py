# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/tooltips/serial_number_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.serial_number_tooltip_model import SerialNumberTooltipModel

class SerialNumberTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.resource_well.lobby.feature.tooltips.SerialNumberTooltip())
        settings.model = SerialNumberTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SerialNumberTooltip, self).__init__(settings)
