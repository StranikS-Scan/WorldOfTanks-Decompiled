# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/game_event/wt_loot_box_tooltip.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.wt_event.tooltips.wt_event_box_tooltip_view import WtEventBoxTooltipView
from gui.shared.tooltips import WulfTooltipData

class WtEventLootBoxTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(WtEventLootBoxTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX)

    def getTooltipContent(self, boxType, *args, **kwargs):
        return WtEventBoxTooltipView(boxType)
