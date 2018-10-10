# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/event_boards_controllers.py
from adisp import process, async

class IEventBoardController(object):

    def getPlayerEventsData(self):
        raise NotImplementedError

    def hasEvents(self):
        raise NotImplementedError

    def getEventsSettingsData(self):
        raise NotImplementedError

    def getMyEventsTopData(self):
        raise NotImplementedError

    def getHangarFlagData(self):
        raise NotImplementedError

    def updateHangarFlag(self):
        raise NotImplementedError

    def cleanEventsData(self):
        raise NotImplementedError

    @async
    @process
    def joinEvent(self, eventID, callback):
        raise NotImplementedError

    @async
    @process
    def leaveEvent(self, eventID, callback):
        raise NotImplementedError

    @async
    @process
    def getHangarFlag(self, callback, onLogin=False):
        raise NotImplementedError

    @async
    @process
    def getEvents(self, callback, onlySettings=True, isTabVisited=False, onLogin=False, prefetchKeyArtBig=True):
        raise NotImplementedError

    @async
    @process
    def getMyLeaderboardInfo(self, eventID, leaderboardID, callback):
        raise NotImplementedError

    @async
    @process
    def getLeaderboard(self, eventID, leaderboardID, pageNumber, callback):
        raise NotImplementedError
