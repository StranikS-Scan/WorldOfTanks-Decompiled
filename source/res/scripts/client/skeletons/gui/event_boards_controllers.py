# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/event_boards_controllers.py
from adisp import process, async

class IEventBoardController(object):

    def getPlayerEventsData(self):
        """Get player event data without sending request to wgelen server.
        :return: object with player event data.
        """
        raise NotImplementedError

    def hasEvents(self):
        """Get whether what events settings have from wgelen server.
        :return: bool.
        """
        raise NotImplementedError

    def getEventsSettingsData(self):
        """Get events settings without sending request to wgelen server.
        :return: object with events settings.
        """
        raise NotImplementedError

    def getMyEventsTopData(self):
        """Get my events top data without sending request to wgelen server.
        :return: object with my events top data.
        """
        raise NotImplementedError

    def getHangarFlagData(self):
        """Get hangar flag data without sending request to wgelen server.
        :return: object with hangar flag data.
        """
        raise NotImplementedError

    def updateHangarFlag(self):
        """Update hangar flag data by invoke listeners.
        """
        raise NotImplementedError

    def cleanEventsData(self):
        """Clean all wgelen data on logout.
        """
        raise NotImplementedError

    @async
    @process
    def joinEvent(self, eventID, callback):
        """Sends request to wglene server for join event.
        :param eventID: event id to join in.
        :param callback: callable object.
        """
        raise NotImplementedError

    @async
    @process
    def leaveEvent(self, eventID, callback):
        """Sends request to wglene server for leave event.
        :param eventID: event id to leave out.
        :param callback: callable object.
        """
        raise NotImplementedError

    @async
    @process
    def getHangarFlag(self, callback, onLogin=False):
        """Sends request to wglene server for get hangar flag data.
        :param callback: callable object
        :param onLogin: is call on login to client
        """
        raise NotImplementedError

    @async
    @process
    def getEvents(self, callback, onlySettings=True, isTabVisited=False, onLogin=False):
        """Sends request to wglene server for get events settings, player events data and my events top.
        :param callback: callable object
        :param onlySettings: need request only static data with wgelen settings
        :param isTabVisited: is events tab visited
        :param onLogin: is call on login to client
        """
        raise NotImplementedError

    @async
    @process
    def getMyLeaderboardInfo(self, eventID, leaderboardID, callback):
        """Sends request to wglene server for get leaderboard data.
        :param eventID: event id where is leaderboard
        :param leaderboardID: leaderboard id to get
        :param callback: callable object
        """
        raise NotImplementedError

    @async
    @process
    def getLeaderboard(self, eventID, leaderboardID, pageNumber, callback):
        """Sends request to wglene server for get leaderboard data.
        :param eventID: event id where is leaderboard
        :param leaderboardID: leaderboard id to get
        :param pageNumber: leaderboard page to get
        :param callback: callable object
        """
        raise NotImplementedError
