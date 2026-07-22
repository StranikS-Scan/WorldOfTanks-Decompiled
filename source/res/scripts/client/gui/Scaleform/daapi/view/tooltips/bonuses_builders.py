# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/bonuses_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.lobby.tooltips.preferred_map_slot_reward_tooltip import PreferredMapSlotTooltip
from gui.shared.tooltips import ToolTipBaseData, contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

class PreferredMapSlotTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(PreferredMapSlotTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.PREFERRED_MAP_SLOT_TOOLTIP)

    def getDisplayableData(self, *args, **kwargs):
        return DecoratedTooltipWindow(PreferredMapSlotTooltip(*args, **kwargs), useDecorator=False)


def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.PREFERRED_MAP_SLOT_TOOLTIP, None, PreferredMapSlotTooltipData(contexts.ToolTipContext(None))),)
