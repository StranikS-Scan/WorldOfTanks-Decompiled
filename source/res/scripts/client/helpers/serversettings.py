# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/ServerSettings.py
import types
from collections import namedtuple
from Event import Event
from constants import IS_TUTORIAL_ENABLED, SWITCH_STATE
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import GUI_SETTINGS
from gui.shared.utils.decorators import ReprInjector
from shared_utils import makeTupleByDict
_CLAN_EMBLEMS_SIZE_MAPPING = {16: 'clan_emblems_16',
 32: 'clan_emblems_small',
 64: 'clan_emblems_big',
 128: 'clan_emblems_128',
 256: 'clan_emblems_256'}

@ReprInjector.simple(('centerID', 'centerID'), ('dbidMin', 'dbidMin'), ('dbidMax', 'dbidMax'), ('regionCode', 'regionCode'))
class _ServerInfo(object):
    __slots__ = ('centerID', 'dbidMin', 'dbidMax', 'regionCode')

    def __init__(self, centerID, dbidMin, dbidMax, regionCode):
        self.centerID = centerID
        self.dbidMin = dbidMin
        self.dbidMax = dbidMax
        self.regionCode = regionCode

    def isPlayerHome(self, playerDBID):
        return self.dbidMin <= playerDBID <= self.dbidMax


class RoamingSettings(namedtuple('RoamingSettings', 'homeCenterID curCenterID servers')):

    def getHomeCenterID(self):
        return self.homeCenterID

    def getCurrentCenterID(self):
        return self.curCenterID

    def getRoamingServers(self):
        return self.servers

    def getPlayerHome(self, playerDBID):
        for s in self.getRoamingServers():
            if s.isPlayerHome(playerDBID):
                return (s.centerID, s.regionCode)

        return (None, None)

    def isEnabled(self):
        return GUI_SETTINGS.roaming

    def isSameRealm(self, playerDBID):
        centerID, _ = self.getPlayerHome(playerDBID)
        return centerID == self.getHomeCenterID()

    def isInRoaming(self):
        return self.getCurrentCenterID() != self.getHomeCenterID()

    def isPlayerInRoaming(self, playerDBID):
        centerID, _ = self.getPlayerHome(playerDBID)
        return centerID != self.getCurrentCenterID()

    @classmethod
    def defaults(cls):
        return cls(0, 0, [])


class _FileServerSettings(object):

    def __init__(self, fsSettings):
        self.__urls = dict(((n, d.get('url_template', '')) for n, d in fsSettings.iteritems()))

    def getUrls(self):
        return self.__urls

    def getClanEmblemBySize(self, clanDBID, size):
        return self.__getUrl(_CLAN_EMBLEMS_SIZE_MAPPING[size], clanDBID)

    def getClanEmblem64x64VehicleUrl(self, clanDBID):
        return self.__getUrl('clan_emblems', clanDBID)

    def getRareAchievement67x71Url(self, rareAchieveID):
        return self.__getUrl('rare_achievements_images', rareAchieveID)

    def getRareAchievement128x128Url(self, rareAchieveID):
        return self.__getUrl('rare_achievements_images_big', rareAchieveID)

    def getRareAchievementTextsUrl(self, langID):
        assert isinstance(langID, types.StringType), 'given langID type must be string'
        return self.__getUrl('rare_achievements_texts', langID)

    def __getUrl(self, urlKey, *args):
        try:
            return self.__urls[urlKey] % args
        except (KeyError, TypeError):
            LOG_WARNING('There is invalid url while getting emblem from web', urlKey, args)

        return None

    @classmethod
    def defaults(cls):
        return cls({})


class _RegionalSettings(namedtuple('_RegionalSettings', ['starting_day_of_a_new_week', 'starting_time_of_a_new_day', 'starting_time_of_a_new_game_day'])):

    def getWeekStartingDay(self):
        return self.starting_day_of_a_new_week

    def getDayStartingTime(self):
        return self.starting_time_of_a_new_day

    def getGameDayStartingTime(self):
        return self.starting_time_of_a_new_game_day

    @classmethod
    def defaults(cls):
        return cls(0, 0, 3)


class _ESportCurrentSeason(namedtuple('_ESportSeason', ['eSportSeasonID', 'eSportSeasonStart', 'eSportSeasonFinish'])):

    def getID(self):
        return self.eSportSeasonID

    def getStartTime(self):
        return self.eSportSeasonStart

    def getFinishTime(self):
        return self.eSportSeasonFinish

    @classmethod
    def defaults(cls):
        return cls(0, 0, 0)


class _ClanProfile(namedtuple('_ClanProfile', ['enabled', 'url', 'type'])):

    def isEnabled(self):
        return self.enabled

    def getAccessorType(self):
        return self.type

    def getGateUrl(self):
        return self.url

    @classmethod
    def defaults(cls):
        return cls(False, '', '')


class _StrongholdSettings(namedtuple('_StrongholdSettings', ('wgshHostUrl',))):

    @classmethod
    def defaults(cls):
        return cls('')


class _SpgRedesignFeatures(namedtuple('_SpgRedesignFeatures', ['stunEnabled', 'markTargetAreaEnabled'])):

    def isStunEnabled(self):
        return self.stunEnabled

    @classmethod
    def defaults(cls):
        return cls(False, False)


class ServerSettings(object):

    def __init__(self, serverSettings):
        self.onServerSettingsChange = Event()
        self.__serverSettings = serverSettings if serverSettings else {}
        if 'roaming' in self.__serverSettings:
            roamingSettings = self.__serverSettings['roaming']
            self.__roamingSettings = RoamingSettings(roamingSettings[0], roamingSettings[1], [ _ServerInfo(*s) for s in roamingSettings[2] ])
        else:
            self.__roamingSettings = RoamingSettings.defaults()
        if 'file_server' in self.__serverSettings:
            self.__fileServerSettings = _FileServerSettings(self.__serverSettings['file_server'])
        else:
            self.__fileServerSettings = _FileServerSettings.defaults()
        if 'regional_settings' in self.__serverSettings:
            self.__regionalSettings = makeTupleByDict(_RegionalSettings, self.__serverSettings['regional_settings'])
        else:
            self.__regionalSettings = _RegionalSettings.defaults()
        try:
            self.__eSportCurrentSeason = makeTupleByDict(_ESportCurrentSeason, self.__serverSettings)
        except TypeError:
            self.__eSportCurrentSeason = _ESportCurrentSeason.defaults()

        if 'clanProfile' in self.__serverSettings:
            self.__updateClanProfile(self.__serverSettings)
        else:
            self.__clanProfile = _ClanProfile.defaults()
        if 'spgRedesignFeatures' in self.__serverSettings:
            self.__spgRedesignFeatures = makeTupleByDict(_SpgRedesignFeatures, self.__serverSettings['spgRedesignFeatures'])
        else:
            self.__spgRedesignFeatures = _SpgRedesignFeatures.defaults()
        if 'strongholdSettings' in self.__serverSettings:
            settings = self.__serverSettings['strongholdSettings']
            self.__strongholdSettings = _StrongholdSettings(settings.get('wgshHostUrl', ''))
        else:
            self.__strongholdSettings = _StrongholdSettings.defaults()

    def update(self, serverSettingsDiff):
        self.__serverSettings.update(serverSettingsDiff)
        if 'clanProfile' in serverSettingsDiff:
            self.__updateClanProfile(serverSettingsDiff)
        if 'spgRedesignFeatures' in self.__serverSettings:
            self.__spgRedesignFeatures = makeTupleByDict(_SpgRedesignFeatures, self.__serverSettings['spgRedesignFeatures'])
        self.onServerSettingsChange(serverSettingsDiff)

    def clear(self):
        self.onServerSettingsChange.clear()

    def getSettings(self):
        return self.__serverSettings

    @property
    def roaming(self):
        return self.__roamingSettings

    @property
    def fileServer(self):
        return self.__fileServerSettings

    @property
    def regionals(self):
        return self.__regionalSettings

    @property
    def eSportCurrentSeason(self):
        return self.__eSportCurrentSeason

    @property
    def clanProfile(self):
        return self.__clanProfile

    @property
    def spgRedesignFeatures(self):
        return self.__spgRedesignFeatures

    @property
    def stronghold(self):
        return self.__strongholdSettings

    def isPotapovQuestEnabled(self):
        return self.isFalloutQuestEnabled() or self.isRegularQuestEnabled()

    def isRegularQuestEnabled(self):
        return self.__getGlobalSetting('isRegularQuestEnabled', True)

    def isFalloutQuestEnabled(self):
        return self.__getGlobalSetting('isFalloutQuestEnabled', True)

    def isBuyPotapovQuestTileEnabled(self):
        return self.__getGlobalSetting('isBuyPotapovQuestTileEnabled', False)

    def isBuyPotapovQuestSlotEnabled(self):
        return self.__getGlobalSetting('isBuyPotapovQuestSlotEnabled', False)

    def isFortsEnabled(self):
        return self.__getGlobalSetting('isFortsEnabled', True)

    def isStrongholdsEnabled(self):
        return self.__getGlobalSetting('isStrongholdsEnabled', True)

    def isGoldFishEnabled(self):
        return self.__getGlobalSetting('isGoldFishEnabled', False)

    def isTutorialEnabled(self):
        return self.__getGlobalSetting('isTutorialEnabled', IS_TUTORIAL_ENABLED)

    def isSandboxEnabled(self):
        return self.__getGlobalSetting('isSandboxEnabled', False)

    def isPromoAutoViewsEnabled(self):
        return True

    def getForbiddenFortDefenseHours(self):
        return self.__getGlobalSetting('forbiddenFortDefenseHours', tuple())

    def getForbiddenSortieHours(self):
        return self.__getGlobalSetting('forbiddenSortieHours', tuple())

    def getForbiddenSortiePeripheryIDs(self):
        return self.__getGlobalSetting('forbiddenSortiePeripheryIDs', tuple())

    def getForbiddenRatedBattles(self):
        return self.__getGlobalSetting('forbiddenRatedBattles', {})

    def isSPGForbiddenInSquads(self):
        return self.__getGlobalSetting('forbidSPGinSquads', False)

    def getRandomMapsForDemonstrator(self):
        return self.__getGlobalSetting('randomMapsForDemonstrator', {})

    def isPremiumInPostBattleEnabled(self):
        return self.__getGlobalSetting('isPremiumInPostBattleEnabled', True)

    def isVehicleComparingEnabled(self):
        return bool(self.__getGlobalSetting('isVehiclesCompareEnabled', True))

    def isEncyclopediaEnabled(self, tokensCount):
        switchState = self.__getGlobalSetting('isEncyclopediaEnabled')
        if switchState == SWITCH_STATE.ALL:
            state = True
        elif switchState == SWITCH_STATE.NONE:
            state = False
        elif switchState == SWITCH_STATE.TOKEN:
            state = tokensCount > 0
        else:
            LOG_ERROR('Wrong activation state for encyclopedia. Encyclopedia is considered to be disabled')
            state = False
        return state

    def isTemplateMatchmakerEnabled(self):
        return bool(self.__getGlobalSetting('isTemplateMatchmakerEnabled', True))

    def isTankmanRestoreEnabled(self):
        return self.__getGlobalSetting('isTankmanRestoreEnabled', True)

    def isVehicleRestoreEnabled(self):
        return self.__getGlobalSetting('isVehicleRestoreEnabled', True)

    def __getGlobalSetting(self, settingsName, default=None):
        return self.__serverSettings.get(settingsName, default)

    def __updateClanProfile(self, targetSettings):
        cProfile = targetSettings['clanProfile']
        self.__clanProfile = _ClanProfile(cProfile.get('isEnabled', False), cProfile.get('gateUrl', ''), cProfile.get('type', 'gateway'))
