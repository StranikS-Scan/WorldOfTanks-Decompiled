# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips.builders import AdvancedTooltipWindowBuilder
from gui.shared.tooltips import advanced, vehicle
from comp7.gui.Scaleform.daapi.view.tooltips.contexts import Comp7ParamContext
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (AdvancedTooltipWindowBuilder(TOOLTIPS_CONSTANTS.COMP7_VEHICLE_PARAMS_TOOLTIP, None, vehicle.VehicleAdvancedParametersTooltipData(Comp7ParamContext()), advanced.VehicleParametersAdvanced(Comp7ParamContext()), condition=vehicle.BaseVehicleParametersTooltipData.readyForAdvanced),)
