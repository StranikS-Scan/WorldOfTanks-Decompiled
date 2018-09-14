# Embedded file name: scripts/client/helpers/ServerSettings.py
import types
from collections import namedtuple
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.simple(('centerID', 'centerID'), ('dbidMin', 'dbidMin'), ('dbidMin', 'dbidMin'), ('regionCode', 'regionCode'))

class _ServerInfo(object):
    __slots__ = ('centerID', 'dbidMin', 'dbidMax', 'regionCode')

    def __init__(self, centerID, dbidMin, dbidMax, regionCode):
        self.centerID = centerID
        self.dbidMin = dbidMin
        self.dbidMax = dbidMax
        self.regionCode = regionCode

    def isPlayerHome(self, playerDBID):
        return self.dbidMin <= playerDBID <= self.dbidMax


class _RoamingSettings(namedtuple('_RoamingSettings', 'homeCenterID curCenterID servers')):

    def getHomeCenterID(self):
        return self.homeCenterID

    def getCurrentCenterID(self):
        return self.curCenterID

    def getRoamingServers(self):
        return self.servers

    def getPlayerHome(self, playerDBID):
        for s in self.getRoamingServers():
            if s.isPlayerHome(playerDBID):
                return s.centerID

        return None


class FileServerSettings(object):

    def __init__(self, fsSettings):
        self.__urls = dict(((n, d.get('url_template', '')) for n, d in fsSettings.iteritems()))

    def getUrls(self):
        return self.__urls

    def getClanEmblem64x64Url(self, clanDBID):
        return self.__getUrl('clan_emblems_big', clanDBID)

    def getClanEmblem32x32Url(self, clanDBID):
        return self.__getUrl('clan_emblems_small', clanDBID)

    def getClanEmblem64x64VehicleUrl(self, clanDBID):
        return self.__getUrl('clan_emblems', clanDBID)

    def getRareAchievement67x71Url(self, rareAchieveID):
        return self.__getUrl('rare_achievements_images', rareAchieveID)

    def getRareAchievement128x128Url(self, rareAchieveID):
        return self.__getUrl('rare_achievements_images_big', rareAchieveID)

    def getRareAchievementTextsUrl(self, langID):
        raise isinstance(langID, types.StringType) or AssertionError('given langID type must be string')
        return self.__getUrl('rare_achievements_texts', langID)

    def __getUrl(self, urlKey, *args):
        if urlKey in self.__urls:
            return self.__urls[urlKey] % args
        else:
            return None


class ServerSettings(object):

    def __init__(self, serverSettings):
        self.__serverSettings = serverSettings
        roamingSettings = self.__serverSettings['roaming']
        self.__roamingSettings = _RoamingSettings(roamingSettings[0], roamingSettings[1], [ _ServerInfo(*s) for s in roamingSettings[2] ])
        self.__fileServerSettings = FileServerSettings(self.__serverSettings['file_server'])

    def getSettings(self):
        return self.__serverSettings

    @property
    def roaming(self):
        return self.__roamingSettings

    @property
    def fileServer(self):
        return self.__fileServerSettings

    def isPotapovQuestEnabled(self):
        return self.__getGlobalSetting('isPotapovQuestEnabled', False)

    def isFortBattlesEnabled(self):
        return not self.__getGlobalSetting('isFortBattlesDisabled', True)

    def isPromoAutoViewsEnabled(self):
        return True

    def __getGlobalSetting(self, settingsName, default = None):
        return self.__serverSettings.get(settingsName, default)
