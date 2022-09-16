# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/event_boards_controllers.py
from adisp import adisp_process, adisp_async

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

    @adisp_async
    @adisp_process
    def joinEvent(self, eventID, callback):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def leaveEvent(self, eventID, callback):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def getHangarFlag(self, callback, onLogin=False):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def getEvents(self, callback, onlySettings=True, isTabVisited=False, onLogin=False, prefetchKeyArtBig=True):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def getMyLeaderboardInfo(self, eventID, leaderboardID, callback, showNotification=True):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def getLeaderboard(self, eventID, leaderboardID, pageNumber, callback, leaderBoardClass=None, showNotification=True):
        raise NotImplementedError
