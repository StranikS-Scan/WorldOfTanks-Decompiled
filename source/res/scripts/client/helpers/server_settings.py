# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/server_settings.py
import types
from collections import namedtuple
import copy
from Event import Event
from constants import IS_TUTORIAL_ENABLED, SWITCH_STATE
from debug_utils import LOG_WARNING, LOG_ERROR
from gui import GUI_SETTINGS
from gui.shared.utils.decorators import ReprInjector
from shared_utils import makeTupleByDict, updateDict
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
        return self.__getUrl('rare_achievements_texts', langID)

    def getMissionsTokenImageUrl(self, tokenID, size):
        return self.__getUrl('missions_token_image', size, tokenID)

    def getMissionsTokenDescrsUrl(self, langID):
        return self.__getUrl('missions_token_descrs', langID)

    def getMissionsDecorationUrl(self, decorationID, size):
        return self.__getUrl('missions_decoration', size, decorationID)

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


class _Wgcg(namedtuple('_Wgcg', ['enabled',
 'url',
 'type',
 'loginOnStart'])):

    def isEnabled(self):
        return self.enabled

    def getAccessorType(self):
        return self.type

    def getGateUrl(self):
        return self.url

    def getLoginOnStart(self):
        return self.loginOnStart

    @classmethod
    def defaults(cls):
        return cls(False, '', '', False)


class _ClanProfile(namedtuple('_ClanProfile', ('enabled',))):

    def isEnabled(self):
        return self.enabled

    @classmethod
    def defaults(cls):
        return cls(False)


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


_BwRankedBattles = namedtuple('_BwRankedBattles', ('rblbHostUrl',))
_BwRankedBattles.__new__.__defaults__ = (None,)
_BwHallOfFame = namedtuple('_BwHallOfFame', ('hofHostUrl', 'isHofEnabled', 'isStatusEnabled'))
_BwHallOfFame.__new__.__defaults__ = (None, False, False)

class _RankedBattlesConfig(namedtuple('_RankedBattlesConfig', ['isEnabled',
 'peripheryIDs',
 'winnerRankChanges',
 'loserRankChanges',
 'minXP',
 'unburnableRanks',
 'unburnableStepRanks',
 'unburnableVehRanks',
 'unburnableVehStepRanks',
 'minLevel',
 'maxLevel',
 'accRanks',
 'accSteps',
 'vehRanks',
 'vehSteps',
 'cycleFinishSeconds',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'accLadderPts',
 'vehLadderPts',
 'shields'])):

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_RankedBattlesConfig.__new__.__defaults__ = (False,
 {},
 (),
 (),
 0,
 {},
 {},
 {},
 {},
 0,
 0,
 (),
 (),
 (),
 (),
 0,
 {},
 {},
 (),
 (),
 (),
 {})

class ServerSettings(object):

    def __init__(self, serverSettings):
        self.onServerSettingsChange = Event()
        self.set(serverSettings)

    def set(self, serverSettings):
        self.__serverSettings = copy.deepcopy(serverSettings) if serverSettings else {}
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

        if 'wgcg' in self.__serverSettings:
            self.__updateWgcg(self.__serverSettings)
        else:
            self.__wgcg = _Wgcg.defaults()
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
        if 'rankedBattles' in self.__serverSettings:
            self.__bwRankedBattles = makeTupleByDict(_BwRankedBattles, self.__serverSettings['rankedBattles'])
        else:
            self.__bwRankedBattles = _BwRankedBattles()
        if 'hallOfFame' in self.__serverSettings:
            self.__bwHallOfFame = makeTupleByDict(_BwHallOfFame, self.__serverSettings['hallOfFame'])
        else:
            self.__bwHallOfFame = _BwHallOfFame()
        if 'ranked_config' in self.__serverSettings:
            self.__rankedBattlesSettings = makeTupleByDict(_RankedBattlesConfig, self.__serverSettings['ranked_config'])
        else:
            self.__rankedBattlesSettings = _RankedBattlesConfig()
        self.onServerSettingsChange(serverSettings)

    def update(self, serverSettingsDiff):
        self.__serverSettings = updateDict(self.__serverSettings, serverSettingsDiff)
        if 'clanProfile' in serverSettingsDiff:
            self.__updateClanProfile(serverSettingsDiff)
        if 'spgRedesignFeatures' in self.__serverSettings:
            self.__spgRedesignFeatures = makeTupleByDict(_SpgRedesignFeatures, self.__serverSettings['spgRedesignFeatures'])
        if 'ranked_config' in serverSettingsDiff:
            self.__updateRanked(serverSettingsDiff)
        if 'hallOfFame' in serverSettingsDiff:
            self.__bwHallOfFame = makeTupleByDict(_BwHallOfFame, serverSettingsDiff['hallOfFame'])
        if 'wgcg' in serverSettingsDiff:
            self.__updateWgcg(serverSettingsDiff)
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
    def wgcg(self):
        return self.__wgcg

    @property
    def spgRedesignFeatures(self):
        return self.__spgRedesignFeatures

    @property
    def stronghold(self):
        return self.__strongholdSettings

    @property
    def bwRankedBattles(self):
        return self.__bwRankedBattles

    @property
    def bwHallOfFame(self):
        return self.__bwHallOfFame

    @property
    def rankedBattles(self):
        return self.__rankedBattlesSettings

    def isPersonalMissionsEnabled(self):
        return self.isRegularQuestEnabled()

    def isRegularQuestEnabled(self):
        return self.__getGlobalSetting('isRegularQuestEnabled', True)

    def isStrongholdsEnabled(self):
        return self.__getGlobalSetting('strongholdSettings', {}).get('isStrongholdsEnabled', False)

    def isElenEnabled(self):
        return self.__getGlobalSetting('elenSettings', {}).get('isElenEnabled', True)

    def elenUpdateInterval(self):
        return self.__getGlobalSetting('elenSettings', {}).get('elenUpdateInterval', 60)

    def isGoldFishEnabled(self):
        return self.__getGlobalSetting('isGoldFishEnabled', False)

    def isTutorialEnabled(self):
        return self.__getGlobalSetting('isTutorialEnabled', IS_TUTORIAL_ENABLED)

    def isSandboxEnabled(self):
        return self.__getGlobalSetting('isSandboxEnabled', False)

    def isBootcampEnabled(self):
        return self.__getGlobalSetting('isBootcampEnabled', False)

    def isEpicRandomEnabled(self):
        return self.__getGlobalSetting('isEpicRandomEnabled', False)

    def isEpicRandomAchievementsEnabled(self):
        return self.__getGlobalSetting('isEpicRandomAchievementsEnabled', False)

    def isEpicRandomMarkOfMasteryEnabled(self):
        return self.__getGlobalSetting('isEpicRandomMarkOfMasteryEnabled', False)

    def isEpicRandomMarksOnGunEnabled(self):
        return self.__getGlobalSetting('isEpicRandomMarksOnGunEnabled', False)

    def isPromoAutoViewsEnabled(self):
        if self.isBootcampEnabled():
            from bootcamp.Bootcamp import g_bootcamp
            if g_bootcamp.isRunning():
                return False
        return True

    def isHofEnabled(self):
        return self.__getGlobalSetting('hallOfFame', {}).get('isHofEnabled', False)

    def getMaxSPGinSquads(self):
        return self.__getGlobalSetting('maxSPGinSquads', 0)

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

    def isCustomizationEnabled(self):
        return self.__getGlobalSetting('isCustomizationEnabled', True)

    def getHeroVehicles(self):
        return self.__getGlobalSetting('hero_vehicles', {})

    def __getGlobalSetting(self, settingsName, default=None):
        return self.__serverSettings.get(settingsName, default)

    def __updateClanProfile(self, targetSettings):
        cProfile = targetSettings['clanProfile']
        self.__clanProfile = _ClanProfile(cProfile.get('isEnabled', False))

    def __updateWgcg(self, targetSettings):
        cProfile = targetSettings['wgcg']
        self.__wgcg = _Wgcg(cProfile.get('isEnabled', False), cProfile.get('gateUrl', ''), cProfile.get('type', 'gateway'), cProfile.get('loginOnStart', False))

    def __updateRanked(self, targetSettings):
        self.__rankedBattlesSettings = self.__rankedBattlesSettings.replace(targetSettings['ranked_config'])
