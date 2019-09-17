# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/advent_calendar/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class AdventCalendarRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.ADVENT_CALENDAR_FETCH_INFO: self.__fetchAdventCalendarInfo}
        return handlers

    def __fetchAdventCalendarInfo(self, ctx, callback):
        reqCtx = self._requester.doRequestEx(ctx, callback, ('advc', 'advent_calendar_fetch_info'))
        return reqCtx
