# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/early_access_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, early_access
from gui.shared.tooltips.builders import TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EARLY_ACCESS_COMMON_INFO, None, early_access.EarlyAccessCommonInfoTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EARLY_ACCESS_VEHICLE_LOCKED, None, early_access.EarlyAccessVehicleLockedTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EARLY_ACCESS_PAUSED, None, early_access.EarlyAccessPausedTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EARLY_ACCESS_CAROUSEL_VEHICLE_POST_PROGRESSION, None, early_access.EarlyAccessCarouselVehiclePostProgressionTooltipData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EARLY_ACCESS_CURRENCY, None, early_access.EarlyAccessCurrencyTooltipData(contexts.ToolTipContext(None))))
