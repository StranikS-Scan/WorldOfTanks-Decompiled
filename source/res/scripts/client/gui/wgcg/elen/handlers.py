# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/elen/handlers.py
from gui.wgcg.base.handlers import RequestHandlers
from gui.wgcg.settings import WebRequestDataType

class ElenRequestHandlers(RequestHandlers):

    def get(self):
        handlers = {WebRequestDataType.EVENT_BOARDS_GET_EVENTS_DATA: self.__getEventsData,
         WebRequestDataType.EVENT_BOARDS_GET_PLAYER_DATA: self.__getPlayerData,
         WebRequestDataType.EVENT_BOARDS_JOIN_EVENT: self.__joinEvent,
         WebRequestDataType.EVENT_BOARDS_LEAVE_EVENT: self.__leaveEvent,
         WebRequestDataType.EVENT_BOARDS_GET_MY_EVENT_TOP: self.__getMyEventTop,
         WebRequestDataType.EVENT_BOARDS_GET_MY_LEADERBOARD_POSITION: self.__getMyLeaderboardPosition,
         WebRequestDataType.EVENT_BOARDS_GET_LEADERBOARD: self.__getLeaderboard,
         WebRequestDataType.EVENT_BOARDS_GET_HANGAR_FLAG: self.__getHangarFlag}
        return handlers

    def __getEventsData(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_events_data'))

    def __getPlayerData(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_player_data'))

    def __joinEvent(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'join_event'), ctx.getEventID())

    def __leaveEvent(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'leave_event'), ctx.getEventID())

    def __getMyEventTop(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_my_event_top'), ctx.getEventID())

    def __getMyLeaderboardPosition(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_my_leaderboard_position'), ctx.getEventID(), ctx.getLeaderboardID())

    def __getLeaderboard(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_leaderboard'), ctx.getEventID(), ctx.getPageNumber(), ctx.getLeaderboardID())

    def __getHangarFlag(self, ctx, callback):
        self._requester.doRequestEx(ctx, callback, ('wgelen', 'get_hangar_flag'))
