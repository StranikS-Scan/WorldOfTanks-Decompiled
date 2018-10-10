# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/fortifications_builder.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import fortifications
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.DIRECT_MODULE, TOOLTIPS_CONSTANTS.REF_SYS_DIRECTS_UI, fortifications.ToolTipRefSysDirects(contexts.FortificationContext())), DataBuilder(TOOLTIPS_CONSTANTS.FORT_SORTIE_SLOT, TOOLTIPS_CONSTANTS.SUITABLE_VEHICLE_UI, fortifications.FortificationsSlotToolTipData(contexts.FortificationContext())))
