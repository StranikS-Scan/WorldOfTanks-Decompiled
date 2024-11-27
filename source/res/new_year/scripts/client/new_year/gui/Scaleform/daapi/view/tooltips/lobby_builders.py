# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
from gui.shared.tooltips import contexts, vehicle
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    from new_year.gui.shared.tooltips import NYCreditBonusTooltipWindowData, NewYearFillers
    return (DataBuilder(TOOLTIPS_CONSTANTS.NEW_YEAR_AWARD_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(contexts.AwardContext(simplifiedOnly=False))), DataBuilder(TOOLTIPS_CONSTANTS.NY_FILLERS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, NewYearFillers(contexts.ToolTipContext(None))), TooltipWindowBuilder(TOOLTIPS_CONSTANTS.NY_CREDIT_BONUS, None, NYCreditBonusTooltipWindowData(contexts.ToolTipContext(None))))
