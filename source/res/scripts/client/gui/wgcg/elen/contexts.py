# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/elen/contexts.py
from gui.wgcg.settings import WebRequestDataType
from gui.shared.utils.requesters import RequestCtx

class EventBoardsRequestCtx(RequestCtx):
    __slots__ = ('_needShowErrorNotification',)

    def __init__(self):
        super(EventBoardsRequestCtx, self).__init__()
        self._needShowErrorNotification = True

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def needShowErrorNotification(self):
        return self._needShowErrorNotification


class EventBoardsGetEventDataCtx(EventBoardsRequestCtx):

    def __init__(self, needShowErrorNotification=True):
        super(EventBoardsGetEventDataCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_EVENTS_DATA


class EventBoardsGetPlayerDataCtx(EventBoardsRequestCtx):

    def __init__(self, needShowErrorNotification=True):
        super(EventBoardsGetPlayerDataCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_PLAYER_DATA


class EventBoardsJoinEventCtx(EventBoardsRequestCtx):
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=True):
        super(EventBoardsJoinEventCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_JOIN_EVENT

    def getEventID(self):
        return self.__eventID


class EventBoardsLeaveEventCtx(EventBoardsRequestCtx):
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=True):
        super(EventBoardsLeaveEventCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_LEAVE_EVENT

    def getEventID(self):
        return self.__eventID


class EventBoardsGetMyEventTopCtx(EventBoardsRequestCtx):
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=False):
        super(EventBoardsGetMyEventTopCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_MY_EVENT_TOP

    def getEventID(self):
        return self.__eventID


class EventBoardsGetMyLeaderboardPositionCtx(EventBoardsRequestCtx):
    __slots__ = ('__eventID', '__leaderboardID')

    def __init__(self, eventID, leaderboardID, needShowErrorNotification=True):
        super(EventBoardsGetMyLeaderboardPositionCtx, self).__init__()
        self.__eventID = eventID
        self.__leaderboardID = leaderboardID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_MY_LEADERBOARD_POSITION

    def getEventID(self):
        return self.__eventID

    def getLeaderboardID(self):
        return self.__leaderboardID


class EventBoardsGetLeaderboardCtx(EventBoardsRequestCtx):
    __slots__ = ('__eventID', '__leaderboardID', '__pageNumber')

    def __init__(self, eventID, leaderboardID, pageNumber, needShowErrorNotification=True):
        super(EventBoardsGetLeaderboardCtx, self).__init__()
        self.__eventID = eventID
        self.__leaderboardID = leaderboardID
        self.__pageNumber = pageNumber
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_LEADERBOARD

    def getEventID(self):
        return self.__eventID

    def getLeaderboardID(self):
        return self.__leaderboardID

    def getPageNumber(self):
        return self.__pageNumber


class EventBoardsGetHangarFlagCtx(EventBoardsRequestCtx):

    def __init__(self, needShowErrorNotification=False):
        super(EventBoardsGetHangarFlagCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_HANGAR_FLAG


class EventBoardsGetFootballEventDataCtx(EventBoardsGetEventDataCtx):

    def isAuthorizationRequired(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.EVENT_BOARDS_GET_FOOTBALL_EVENTS_DATA
