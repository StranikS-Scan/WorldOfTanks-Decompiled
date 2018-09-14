# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/clubs.py


class IClubsController(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self, isDisconnected=False):
        raise NotImplementedError

    def markAppsNotificationShown(self):
        raise NotImplementedError

    def isAppsNotificationShown(self):
        raise NotImplementedError

    def getAvailabilityCtrl(self):
        raise NotImplementedError

    def addListener(self, listener, forceResync=False):
        raise NotImplementedError

    def removeListener(self, listener):
        raise NotImplementedError

    def addClubListener(self, clubDbID, listener, subscriptionType, forceResync=False):
        raise NotImplementedError

    def removeClubListener(self, clubDbID, listener):
        raise NotImplementedError

    def getClub(self, clubDbID):
        raise NotImplementedError

    def requestClubSeasons(self, clubDbID, callback):
        raise NotImplementedError

    def getProfile(self):
        raise NotImplementedError

    def isSubscribed(self, clubDbID):
        raise NotImplementedError

    @classmethod
    def getSeasonState(cls):
        raise NotImplementedError

    @classmethod
    def getSeasons(cls):
        raise NotImplementedError

    @classmethod
    def getSeasonInfo(cls, seasonID):
        raise NotImplementedError

    def sendRequest(self, ctx, callback=None, allowDelay=None):
        raise NotImplementedError

    def getRequestCtrl(self):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getLimits(self):
        raise NotImplementedError

    def getSeasonUserName(self, seasonID):
        raise NotImplementedError

    def getCompletedSeasons(self):
        raise NotImplementedError
