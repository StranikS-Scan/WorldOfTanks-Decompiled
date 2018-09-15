# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_filter_popover.py
from gui.Scaleform.daapi.view.meta.EventBoardsResultFilterPopoverViewMeta import EventBoardsResultFilterPopoverViewMeta
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.shared.utils.functions import makeTooltip
from .event_boards_vos import makeFiltersVO

class EventBoardsFilterPopover(EventBoardsResultFilterPopoverViewMeta):

    def __init__(self, ctx=None):
        super(EventBoardsFilterPopover, self).__init__(ctx)
        self.eventID = ctx.get('data')
        self.__onChangeFilter = None
        return

    def changeFilter(self, lid):
        self.__onChangeFilter(int(lid))

    def onWindowClose(self):
        self.destroy()

    def setData(self, eventData, onApply, leaderboardID=None):
        self.__onChangeFilter = onApply
        eventType = eventData.getType()
        leaderboards = eventData.getLeaderboards()
        if leaderboardID is None:
            leaderboardID = leaderboards[0][0]
        data = {'filters': makeFiltersVO(eventType, leaderboards, leaderboardID),
         'tooltip': makeTooltip(EVENT_BOARDS.POPOVER_BUTTONS_RATING, '#event_boards:popover/tooltip/{}'.format(eventType))}
        self.as_setInitDataS(data)
        return
