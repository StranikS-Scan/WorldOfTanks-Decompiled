# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/tooltips/vehicle_tooltip_wrapper.py
from fun_random.gui.impl.lobby.tooltips.fun_random_vehicle_tooltip_view import FunRandomVehicleTooltipView
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import ToolTipBaseData

class FunRandomVehicleTooltipWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(FunRandomVehicleTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.FUN_RANDOM_VEHICLE)

    def getDisplayableData(self, intCD, *args, **kwargs):
        return DecoratedTooltipWindow(FunRandomVehicleTooltipView(intCD, self.context), useDecorator=False)
