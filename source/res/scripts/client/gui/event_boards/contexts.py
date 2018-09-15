# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/contexts.py
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE
from gui.shared.utils.requesters import RequestCtx

class EventBoardsRequestCtx(RequestCtx):
    """
    Base context for wg elen.
    """
    __slots__ = ('_needShowErrorNotification',)

    def __init__(self):
        super(EventBoardsRequestCtx, self).__init__()
        self._needShowErrorNotification = True

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def needShowErrorNotification(self):
        """
        Getter is need show notification error from wg elen service response.
        """
        return self._needShowErrorNotification


class EventBoardsGetEventDataCtx(EventBoardsRequestCtx):
    """
    Context for get events settings.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """

    def __init__(self, needShowErrorNotification=True):
        super(EventBoardsGetEventDataCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_EVENTS_DATA


class EventBoardsGetPlayerDataCtx(EventBoardsRequestCtx):
    """
    Context for get player events data.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """

    def __init__(self, needShowErrorNotification=True):
        super(EventBoardsGetPlayerDataCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_PLAYER_DATA


class EventBoardsJoinEventCtx(EventBoardsRequestCtx):
    """
    Context for join in to the event.
    :param eventID: event id to join.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=True):
        super(EventBoardsJoinEventCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_JOIN_EVENT

    def getEventID(self):
        """
        Getter for event ID
        """
        return self.__eventID


class EventBoardsLeaveEventCtx(EventBoardsRequestCtx):
    """
    Context for leave from the event.
    :param eventID: event id to leave.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=True):
        super(EventBoardsLeaveEventCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_LEAVE_EVENT

    def getEventID(self):
        """
        Getter for event ID
        """
        return self.__eventID


class EventBoardsGetMyEventTopCtx(EventBoardsRequestCtx):
    """
    Context for get my events top data.
    :param eventID: event id for my top data.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """
    __slots__ = ('__eventID',)

    def __init__(self, eventID, needShowErrorNotification=False):
        super(EventBoardsGetMyEventTopCtx, self).__init__()
        self.__eventID = eventID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_MY_EVENT_TOP

    def getEventID(self):
        """
        Getter for event ID
        """
        return self.__eventID


class EventBoardsGetMyLeaderboardPositionCtx(EventBoardsRequestCtx):
    """
    Context for get my position in leaderboard.
    :param eventID: event id for request.
    :param leaderboardID: leaderboard id to get data.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """
    __slots__ = ('__eventID', '__leaderboardID')

    def __init__(self, eventID, leaderboardID, needShowErrorNotification=True):
        super(EventBoardsGetMyLeaderboardPositionCtx, self).__init__()
        self.__eventID = eventID
        self.__leaderboardID = leaderboardID
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_MY_LEADERBOARD_POSITION

    def getEventID(self):
        """
        Getter for event ID
        """
        return self.__eventID

    def getLeaderboardID(self):
        """
        Getter for leaderboard ID
        """
        return self.__leaderboardID


class EventBoardsGetLeaderboardCtx(EventBoardsRequestCtx):
    """
    Context for get leaderboard data.
    :param eventID: event id where is leaderboard info.
    :param leaderboardID: leaderboard id to get data.
    :param pageNumber: leaderboard page.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """
    __slots__ = ('__eventID', '__leaderboardID', '__pageNumber')

    def __init__(self, eventID, leaderboardID, pageNumber, needShowErrorNotification=True):
        super(EventBoardsGetLeaderboardCtx, self).__init__()
        self.__eventID = eventID
        self.__leaderboardID = leaderboardID
        self.__pageNumber = pageNumber
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_LEADERBOARD

    def getEventID(self):
        """
        Getter for event ID
        """
        return self.__eventID

    def getLeaderboardID(self):
        """
        Getter for leaderboard ID
        """
        return self.__leaderboardID

    def getPageNumber(self):
        """
        Getter for page number
        """
        return self.__pageNumber


class EventBoardsGetHangarFlagCtx(EventBoardsRequestCtx):
    """
    Context for get hangar flag data.
    :param needShowErrorNotification: is need show notification error from wg elen service response.
    """

    def __init__(self, needShowErrorNotification=False):
        super(EventBoardsGetHangarFlagCtx, self).__init__()
        self._needShowErrorNotification = needShowErrorNotification

    def getRequestType(self):
        """
        Getter for request type
        """
        return CLAN_REQUESTED_DATA_TYPE.EVENT_BOARDS_GET_HANGAR_FLAG
