# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/game_event/wt_boss_ticket_tooltip.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_tooltip_view import WtEventCarouselTooltipView
from gui.shared.tooltips import WulfTooltipData
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WtEventBossTicketTooltipWindowData(WulfTooltipData):

    def __init__(self, context):
        super(WtEventBossTicketTooltipWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET)

    def getTooltipContent(self, *args, **kwargs):
        ticketsCount = dependency.instance(IGameEventController).getWtEventTokensCount()
        return WtEventCarouselTooltipView(ticketsCount)
