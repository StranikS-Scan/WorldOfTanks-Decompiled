# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/server_settings.py
import copy
import types
from collections import namedtuple
import logging
from Event import Event
from constants import IS_TUTORIAL_ENABLED, PremiumConfigs, DAILY_QUESTS_CONFIG, ClansConfig, MAGNETIC_AUTO_AIM_CONFIG, Configs
from collector_vehicle import CollectorVehicleConsts
from debug_utils import LOG_WARNING, LOG_DEBUG
from battle_pass_common import BattlePassConfig, BATTLE_PASS_CONFIG_NAME
from gui import GUI_SETTINGS, SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.utils.decorators import ReprInjector
from personal_missions import PM_BRANCH
from shared_utils import makeTupleByDict, updateDict
_logger = logging.getLogger(__name__)
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


class RoamingSettings(namedtuple('RoamingSettings', ('homeCenterID', 'curCenterID', 'servers'))):
    __slots__ = ()

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

    def getOffersRootUrl(self):
        return self.__getUrl('offers')

    def __getUrl(self, urlKey, *args):
        try:
            return self.__urls[urlKey] % args
        except (KeyError, TypeError):
            LOG_WARNING('There is invalid url while getting emblem from web', urlKey, args)

        return None

    @classmethod
    def defaults(cls):
        return cls({})


class _RegionalSettings(namedtuple('_RegionalSettings', ('starting_day_of_a_new_week', 'starting_time_of_a_new_day', 'starting_time_of_a_new_game_day'))):
    __slots__ = ()

    def getWeekStartingDay(self):
        return self.starting_day_of_a_new_week

    def getDayStartingTime(self):
        return self.starting_time_of_a_new_day

    def getGameDayStartingTime(self):
        return self.starting_time_of_a_new_game_day

    @classmethod
    def defaults(cls):
        return cls(0, 0, 3)


class _ESportCurrentSeason(namedtuple('_ESportSeason', ('eSportSeasonID', 'eSportSeasonStart', 'eSportSeasonFinish'))):
    __slots__ = ()

    def getID(self):
        return self.eSportSeasonID

    def getStartTime(self):
        return self.eSportSeasonStart

    def getFinishTime(self):
        return self.eSportSeasonFinish

    @classmethod
    def defaults(cls):
        return cls(0, 0, 0)


class _Wgcg(namedtuple('_Wgcg', ('enabled', 'url', 'type', 'loginOnStart'))):
    __slots__ = ()

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
    __slots__ = ()

    def isEnabled(self):
        return self.enabled

    @classmethod
    def defaults(cls):
        return cls(False)


class _StrongholdSettings(namedtuple('_StrongholdSettings', ('wgshHostUrl',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls('')


class _TournamentSettings(namedtuple('_TournamentSettings', ('tmsHostUrl',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls('')


class _FrontlineSettings(namedtuple('_FrontlineSettings', ('flHostUrl', 'isEpicTrainingEnabled'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls('', False)


class _SpgRedesignFeatures(namedtuple('_SpgRedesignFeatures', ('stunEnabled', 'markTargetAreaEnabled'))):
    __slots__ = ()

    def isStunEnabled(self):
        return self.stunEnabled

    @classmethod
    def defaults(cls):
        return cls(False, False)


class _BwRankedBattles(namedtuple('_BwRankedBattles', ('rblbHostUrl', 'infoPageUrl', 'introPageUrl', 'seasonGapPageUrl', 'yearRatingPageUrl', 'shopPageUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(rblbHostUrl=None, infoPageUrl=None, introPageUrl=None, seasonGapPageUrl=None, yearRatingPageUrl=None, shopPageUrl=None)
        defaults.update(kwargs)
        return super(_BwRankedBattles, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()


class _BwHallOfFame(namedtuple('_BwHallOfFame', ('hofHostUrl', 'isHofEnabled', 'isStatusEnabled'))):
    __slots__ = ()

    def __new__(cls, hofHostUrl=None, isHofEnabled=False, isStatusEnabled=False):
        return super(_BwHallOfFame, cls).__new__(cls, hofHostUrl, isHofEnabled, isStatusEnabled)

    @classmethod
    def defaults(cls):
        return cls()


class _BwShop(namedtuple('_BwShop', ('hostUrl', 'backendHostUrl', 'isStorageEnabled'))):

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_BwShop.__new__.__defaults__ = ('', '', False)

class _RankedBattlesConfig(namedtuple('_RankedBattlesConfig', ('isEnabled', 'peripheryIDs', 'winnerRankChanges', 'loserRankChanges', 'minXP', 'unburnableRanks', 'unburnableStepRanks', 'minLevel', 'maxLevel', 'accRanks', 'accSteps', 'cycleFinishSeconds', 'primeTimes', 'seasons', 'cycleTimes', 'shields', 'divisions', 'bonusBattlesMultiplier', 'expectedSeasons', 'yearAwardsMarks', 'rankGroups', 'qualificationBattles', 'yearLBSize', 'leaguesBonusBattles', 'forbiddenClassTags', 'forbiddenVehTypes', 'isShopEnabled', 'isYearLBEnabled'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, winnerRankChanges=(), loserRankChanges=(), minXP=0, unburnableRanks={}, unburnableStepRanks={}, minLevel=0, maxLevel=0, accRanks=0, accSteps=(), cycleFinishSeconds=0, primeTimes={}, seasons={}, cycleTimes=(), shields={}, divisions={}, bonusBattlesMultiplier=0, expectedSeasons=0, yearAwardsMarks=(), rankGroups=(), qualificationBattles=0, yearLBSize=0, leaguesBonusBattles=(), forbiddenClassTags=(), forbiddenVehTypes=(), isShopEnabled=False, isYearLBEnabled=False)
        defaults.update(kwargs)
        return super(_RankedBattlesConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _ProgressiveReward(namedtuple('_ProgressiveReward', ('isEnabled', 'levelTokenID', 'probabilityTokenID', 'maxLevel'))):

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_ProgressiveReward.__new__.__defaults__ = (True,
 'pr:level',
 'pr:probability',
 0)

class _EventProgressionConfig(namedtuple('_EventProgressionConfig', ('isEnabled', 'isFrontLine', 'isSteelHunter', 'url', 'questPrefix', 'exchange', 'rewardVehicles', 'rewardPointsTokenID', 'seasonPointsTokenID', 'maxRewardPoints'))):

    def __new__(cls, *args, **kwargs):
        defaults = {attr:copy.deepcopy(cls.__new__.__defaults__[i]) for i, attr in enumerate(cls._fields)}
        defaults.update(kwargs)
        return super(_EventProgressionConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_EventProgressionConfig.__new__.__defaults__ = (False,
 False,
 False,
 '',
 '',
 {},
 [],
 '',
 '',
 0)

class _EpicMetaGameConfig(namedtuple('_EpicMetaGameConfig', ['maxCombatReserveLevel',
 'seasonData',
 'metaLevel',
 'rewards',
 'defaultSlots'])):

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_EpicMetaGameConfig.__new__.__defaults__ = (0,
 (0, False),
 (0, 0, 0),
 {},
 {})

class _EpicGameConfig(namedtuple('_EpicGameConfig', ('isEnabled', 'validVehicleLevels', 'seasons', 'cycleTimes', 'peripheryIDs', 'primeTimes', 'reservesAvailableInFLMenu'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, validVehicleLevels=[], seasons={}, cycleTimes=(), peripheryIDs={}, primeTimes={}, reservesAvailableInFLMenu=False)
        defaults.update(kwargs)
        return super(_EpicGameConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _SquadPremiumBonus(namedtuple('_SquadPremiumBonus', ('isEnabled', 'ownCredits', 'mateCredits'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=True, ownCredits=0, mateCredits=0)
        defaults.update(kwargs)
        return super(_SquadPremiumBonus, cls).__new__(cls, **defaults)

    def replace(self, data):
        return self._replace(**self.__extractFields(data))

    @classmethod
    def create(cls, data):
        return cls(**cls.__extractFields(data))

    @classmethod
    def defaults(cls):
        return cls()

    @staticmethod
    def __extractFields(data):
        creditsSettings = data.get('creditsFactor', {})
        result = {}
        if 'enabled' in data:
            result['isEnabled'] = data['enabled']
        if 'premium_plus' in creditsSettings:
            result['ownCredits'] = creditsSettings['premium_plus']
        if 'premium_owner_squadmate' in creditsSettings:
            result['mateCredits'] = creditsSettings['premium_owner_squadmate']
        return result


class _BattleRoyaleConfig(namedtuple('_BattleRoyaleConfig', ('isEnabled', 'peripheryIDs', 'unburnableTitles', 'eventProgression', 'primeTimes', 'seasons', 'cycleTimes', 'maps', 'battleXP', 'coneVisibility', 'loot', 'defaultAmmo', 'vehiclesSlotsConfig'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, eventProgression={}, unburnableTitles=(), primeTimes={}, seasons={}, cycleTimes={}, maps=(), battleXP={}, coneVisibility={}, loot={}, defaultAmmo={}, vehiclesSlotsConfig={})
        defaults.update(kwargs)
        return super(_BattleRoyaleConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _TelecomConfig(object):
    __slots__ = ('__vehCDToProvider',)

    def __init__(self, telecomConfig):
        self.__vehCDToProvider = {}
        for _, bundleData in telecomConfig['bundles'].iteritems():
            for vehCD in bundleData['vehicles']:
                self.__vehCDToProvider[vehCD] = bundleData['operator']

    def getInternetProvider(self, vehCD):
        provider = self.__vehCDToProvider.get(vehCD, '')
        return provider

    @classmethod
    def defaults(cls):
        return cls({'bundles': {}})


class _BlueprintsConfig(namedtuple('_BlueprintsConfig', ('allowBlueprintsConversion', 'isEnabled', 'useBlueprintsForUnlock', 'levels'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls(False, False, False, {})

    def allowConversion(self):
        return self.allowBlueprintsConversion

    def enabled(self):
        return self.isEnabled

    def useBlueprints(self):
        return self.useBlueprintsForUnlock

    def countAndDiscountByLevels(self):
        return self.levels

    def getRequiredFragmentsForConversion(self, level):
        return (0, 0) if not self.isBlueprintsAvailable() or level not in self.levels else self.levels[level][2]

    def getFragmentCount(self, level):
        if not self.isBlueprintsAvailable():
            return 0
        if level == 1:
            return 1
        return self.levels[level][0] if level in self.levels else 0

    def getFragmentDiscount(self, level):
        discount = 0
        if self.isBlueprintsAvailable() and level > 1 and level in self.levels:
            discount = self.levels[level][1]
        return discount

    def isBlueprintsAvailable(self):
        return self.isEnabled and self.useBlueprintsForUnlock

    @staticmethod
    def isBlueprintModeChange(diff):
        return 'isEnabled' in diff or 'useBlueprintsForUnlock' in diff


class _SeniorityAwardsConfig(namedtuple('_SeniorityAwardsConfig', ('enabled', 'autoOpenTime', 'hangarWidgetVisibility'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, autoOpenTime=0, hangarWidgetVisibility=False)
        defaults.update(kwargs)
        return super(_SeniorityAwardsConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    def isEnabled(self):
        return self.enabled

    def autoOpenTimestamp(self):
        return self.autoOpenTime

    def hangarWidgetIsVisible(self):
        return self.hangarWidgetVisibility


class _AdventCalendarConfig(namedtuple('_AdventCalendarConfig', ('calendarURL', 'popupIntervalInHours'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(calendarURL='', popupIntervalInHours=24)
        defaults.update(kwargs)
        return super(_AdventCalendarConfig, cls).__new__(cls, **defaults)

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_crystalRewardInfo = namedtuple('_crystalRewardInfo', 'level, arenaType, winTop3, loseTop3, winTop10, loseTop10')

class _crystalRewardConfigSection(namedtuple('_crystalRewardConfigSection', ('level', 'vehicle'))):
    __slots__ = ()

    def __new__(cls, params):
        defaults = {'level': {},
         'vehicle': {}}
        defaults.update(params)
        return super(_crystalRewardConfigSection, cls).__new__(cls, **defaults)


class _crystalRewardsConfig(namedtuple('_crystalRewardsConfig', ('limits', 'rewards'))):
    __slots__ = ()
    CONFIG_NAME = 'crystal_rewards_config'

    def __new__(cls, **kwargs):
        defaults = {'limits': _crystalRewardConfigSection(kwargs.get('limits', {})),
         'rewards': _crystalRewardConfigSection(kwargs.get('rewards', {}))}
        return super(_crystalRewardsConfig, cls).__new__(cls, **defaults)

    def getRewardInfoData(self):
        results = []
        for level, rewardData in self.rewards.level.iteritems():
            for arenaBonusType, scoreData in rewardData.iteritems():
                results.append(_crystalRewardInfo(level, arenaBonusType, winTop3=max(scoreData[True].itervalues()), loseTop3=max(scoreData[False].itervalues()), winTop10=min(scoreData[True].itervalues()), loseTop10=min(scoreData[False].itervalues())))

        return results


class ServerSettings(object):

    def __init__(self, serverSettings):
        self.onServerSettingsChange = Event()
        self.__serverSettings = {}
        self.__roamingSettings = RoamingSettings.defaults()
        self.__fileServerSettings = _FileServerSettings.defaults()
        self.__regionalSettings = _RegionalSettings.defaults()
        self.__eSportCurrentSeason = _ESportCurrentSeason.defaults()
        self.__wgcg = _Wgcg.defaults()
        self.__clanProfile = _ClanProfile.defaults()
        self.__spgRedesignFeatures = _SpgRedesignFeatures.defaults()
        self.__strongholdSettings = _StrongholdSettings.defaults()
        self.__tournamentSettings = _TournamentSettings.defaults()
        self.__frontlineSettings = _FrontlineSettings.defaults()
        self.__bwRankedBattles = _BwRankedBattles.defaults()
        self.__bwHallOfFame = _BwHallOfFame.defaults()
        self.__bwShop = _BwShop()
        self.__rankedBattlesSettings = _RankedBattlesConfig.defaults()
        self.__epicMetaGameSettings = _EpicMetaGameConfig()
        self.__eventProgressionSettings = _EventProgressionConfig()
        self.__adventCalendar = _AdventCalendarConfig()
        self.__epicGameSettings = _EpicGameConfig()
        self.__telecomConfig = _TelecomConfig.defaults()
        self.__squadPremiumBonus = _SquadPremiumBonus.defaults()
        self.__battlePassConfig = BattlePassConfig({})
        self.__crystalRewardsConfig = _crystalRewardsConfig()
        self.set(serverSettings)

    def set(self, serverSettings):
        self.__serverSettings = copy.deepcopy(serverSettings) if serverSettings else {}
        if 'roaming' in self.__serverSettings:
            roamingSettings = self.__serverSettings['roaming']
            self.__roamingSettings = RoamingSettings(roamingSettings[0], roamingSettings[1], [ _ServerInfo(*s) for s in roamingSettings[2] ])
        if 'file_server' in self.__serverSettings:
            self.__fileServerSettings = _FileServerSettings(self.__serverSettings['file_server'])
        if 'regional_settings' in self.__serverSettings:
            self.__regionalSettings = makeTupleByDict(_RegionalSettings, self.__serverSettings['regional_settings'])
        try:
            self.__eSportCurrentSeason = makeTupleByDict(_ESportCurrentSeason, self.__serverSettings)
        except TypeError:
            self.__eSportCurrentSeason = _ESportCurrentSeason.defaults()

        if 'wgcg' in self.__serverSettings:
            self.__updateWgcg(self.__serverSettings)
        if 'clanProfile' in self.__serverSettings:
            self.__updateClanProfile(self.__serverSettings)
        if 'spgRedesignFeatures' in self.__serverSettings:
            self.__spgRedesignFeatures = makeTupleByDict(_SpgRedesignFeatures, self.__serverSettings['spgRedesignFeatures'])
        if 'strongholdSettings' in self.__serverSettings:
            settings = self.__serverSettings['strongholdSettings']
            self.__strongholdSettings = _StrongholdSettings(settings.get('wgshHostUrl', ''))
        if 'tournamentSettings' in self.__serverSettings:
            settings = self.__serverSettings['tournamentSettings']
            self.__tournamentSettings = _TournamentSettings(settings.get('tmsHostUrl', ''))
        if 'frontlineSettings' in self.__serverSettings:
            settings = self.__serverSettings['frontlineSettings']
            self.__frontlineSettings = _FrontlineSettings(settings.get('flHostUrl', ''), settings.get('isEpicTrainingEnabled', False))
        if 'rankedBattles' in self.__serverSettings:
            self.__bwRankedBattles = makeTupleByDict(_BwRankedBattles, self.__serverSettings['rankedBattles'])
        if 'hallOfFame' in self.__serverSettings:
            self.__bwHallOfFame = makeTupleByDict(_BwHallOfFame, self.__serverSettings['hallOfFame'])
        if 'shop' in self.__serverSettings:
            self.__bwShop = makeTupleByDict(_BwShop, self.__serverSettings['shop'])
        if 'ranked_config' in self.__serverSettings:
            self.__rankedBattlesSettings = makeTupleByDict(_RankedBattlesConfig, self.__serverSettings['ranked_config'])
        if 'event_progression_config' in self.__serverSettings:
            self.__eventProgressionSettings = makeTupleByDict(_EventProgressionConfig, self.__serverSettings['event_progression_config'])
        if 'advent_calendar_config' in self.__serverSettings:
            self.__adventCalendar = makeTupleByDict(_AdventCalendarConfig, self.__serverSettings['advent_calendar_config'])
        if 'epic_config' in self.__serverSettings:
            LOG_DEBUG('epic_config', self.__serverSettings['epic_config'])
            self.__epicMetaGameSettings = makeTupleByDict(_EpicMetaGameConfig, self.__serverSettings['epic_config']['epicMetaGame'])
            self.__epicGameSettings = makeTupleByDict(_EpicGameConfig, self.__serverSettings['epic_config'])
        if PremiumConfigs.PREM_SQUAD in self.__serverSettings:
            self.__squadPremiumBonus = _SquadPremiumBonus.create(self.__serverSettings[PremiumConfigs.PREM_SQUAD])
        if Configs.BATTLE_ROYALE_CONFIG.value in self.__serverSettings:
            LOG_DEBUG('battle_royale_config', self.__serverSettings[Configs.BATTLE_ROYALE_CONFIG.value])
            self.__battleRoyaleSettings = makeTupleByDict(_BattleRoyaleConfig, self.__serverSettings[Configs.BATTLE_ROYALE_CONFIG.value])
        else:
            self.__battleRoyaleSettings = _BattleRoyaleConfig.defaults()
        if 'telecom_config' in self.__serverSettings:
            self.__telecomConfig = _TelecomConfig(self.__serverSettings['telecom_config'])
        if 'blueprints_config' in self.__serverSettings:
            self.__blueprintsConfig = makeTupleByDict(_BlueprintsConfig, self.__serverSettings['blueprints_config'])
        else:
            self.__blueprintsConfig = _BlueprintsConfig.defaults()
        if 'progressive_reward_config' in self.__serverSettings:
            self.__progressiveReward = makeTupleByDict(_ProgressiveReward, self.__serverSettings['progressive_reward_config'])
        else:
            self.__progressiveReward = _ProgressiveReward()
        if 'seniority_awards_config' in self.__serverSettings:
            self.__seniorityAwardsConfig = makeTupleByDict(_SeniorityAwardsConfig, self.__serverSettings['seniority_awards_config'])
        else:
            self.__seniorityAwardsConfig = _SeniorityAwardsConfig()
        if BATTLE_PASS_CONFIG_NAME in self.__serverSettings:
            self.__battlePassConfig = BattlePassConfig(self.__serverSettings.get(BATTLE_PASS_CONFIG_NAME, {}))
        else:
            self.__battlePassConfig = BattlePassConfig({})
        if _crystalRewardsConfig.CONFIG_NAME in self.__serverSettings:
            self.__crystalRewardsConfig = makeTupleByDict(_crystalRewardsConfig, self.__serverSettings[_crystalRewardsConfig.CONFIG_NAME])
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
        if 'event_progression_config' in serverSettingsDiff:
            self.__updateEventProgression(serverSettingsDiff)
            self.__serverSettings['event_progression_config'] = serverSettingsDiff['event_progression_config']
        if 'advent_calendar_config' in serverSettingsDiff:
            self.__updateAdventCalendar(serverSettingsDiff)
            self.__serverSettings['advent_calendar_config'] = serverSettingsDiff['advent_calendar_config']
        if 'epic_config' in serverSettingsDiff:
            self.__updateEpic(serverSettingsDiff)
            self.__serverSettings['epic_config'] = serverSettingsDiff['epic_config']
        if Configs.BATTLE_ROYALE_CONFIG.value in serverSettingsDiff:
            self.__updateBattleRoyale(serverSettingsDiff)
        if 'telecom_config' in serverSettingsDiff:
            self.__telecomConfig = _TelecomConfig(self.__serverSettings['telecom_config'])
        if 'disabledPMOperations' in serverSettingsDiff:
            self.__serverSettings['disabledPMOperations'] = serverSettingsDiff['disabledPMOperations']
        if 'shop' in serverSettingsDiff:
            self.__updateShop(serverSettingsDiff)
        if 'disabledPersonalMissions' in serverSettingsDiff:
            self.__serverSettings['disabledPersonalMissions'] = serverSettingsDiff['disabledPersonalMissions']
        if 'blueprints_config' in serverSettingsDiff:
            self.__updateBlueprints(serverSettingsDiff['blueprints_config'])
        if 'lootBoxes_config' in serverSettingsDiff:
            self.__serverSettings['lootBoxes_config'] = serverSettingsDiff['lootBoxes_config']
        if 'progressive_reward_config' in serverSettingsDiff:
            self.__updateProgressiveReward(serverSettingsDiff)
        if 'seniority_awards_config' in serverSettingsDiff:
            self.__updateSeniorityAwards(serverSettingsDiff)
        if PremiumConfigs.PIGGYBANK in serverSettingsDiff:
            self.__serverSettings[PremiumConfigs.PIGGYBANK] = serverSettingsDiff[PremiumConfigs.PIGGYBANK]
        if PremiumConfigs.DAILY_BONUS in serverSettingsDiff:
            self.__serverSettings[PremiumConfigs.DAILY_BONUS] = serverSettingsDiff[PremiumConfigs.DAILY_BONUS]
        if PremiumConfigs.PREM_QUESTS in serverSettingsDiff:
            self.__serverSettings[PremiumConfigs.PREM_QUESTS] = serverSettingsDiff[PremiumConfigs.PREM_QUESTS]
        if PremiumConfigs.PREM_SQUAD in serverSettingsDiff:
            self.__updateSquadBonus(serverSettingsDiff)
        if PremiumConfigs.PREFERRED_MAPS in serverSettingsDiff:
            self.__serverSettings[PremiumConfigs.PREFERRED_MAPS] = serverSettingsDiff[PremiumConfigs.PREFERRED_MAPS]
        if BATTLE_PASS_CONFIG_NAME in serverSettingsDiff:
            self.__serverSettings[BATTLE_PASS_CONFIG_NAME] = serverSettingsDiff[BATTLE_PASS_CONFIG_NAME]
            self.__battlePassConfig = BattlePassConfig(self.__serverSettings.get(BATTLE_PASS_CONFIG_NAME, {}))
        if CollectorVehicleConsts.CONFIG_NAME in serverSettingsDiff:
            self.__serverSettings[CollectorVehicleConsts.CONFIG_NAME] = serverSettingsDiff[CollectorVehicleConsts.CONFIG_NAME]
        if _crystalRewardsConfig.CONFIG_NAME in serverSettingsDiff:
            self.__crystalRewardsConfig = makeTupleByDict(_crystalRewardsConfig, self.__serverSettings[_crystalRewardsConfig.CONFIG_NAME])
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
    def tournament(self):
        return self.__tournamentSettings

    @property
    def frontline(self):
        return self.__frontlineSettings

    @property
    def bwRankedBattles(self):
        return self.__bwRankedBattles

    @property
    def bwHallOfFame(self):
        return self.__bwHallOfFame

    @property
    def rankedBattles(self):
        return self.__rankedBattlesSettings

    @property
    def eventProgression(self):
        return self.__eventProgressionSettings

    @property
    def adventCalendar(self):
        return self.__adventCalendar

    @property
    def epicMetaGame(self):
        return self.__epicMetaGameSettings

    @property
    def epicBattles(self):
        return self.__epicGameSettings

    @property
    def battleRoyale(self):
        return self.__battleRoyaleSettings

    @property
    def telecomConfig(self):
        return self.__telecomConfig

    @property
    def blueprintsConfig(self):
        return self.__blueprintsConfig

    @property
    def squadPremiumBonus(self):
        return self.__squadPremiumBonus

    def isEpicBattleEnabled(self):
        return self.epicBattles.isEnabled

    def isPersonalMissionsEnabled(self, branch=None):
        if branch == PM_BRANCH.REGULAR:
            return self.__getGlobalSetting('isRegularQuestEnabled', True)
        return self.__getGlobalSetting('isPM2QuestEnabled', True) if branch == PM_BRANCH.PERSONAL_MISSION_2 else self.__getGlobalSetting('isRegularQuestEnabled', True) or self.__getGlobalSetting('isPM2QuestEnabled', True)

    def isPMBattleProgressEnabled(self):
        return self.__getGlobalSetting('isPMBattleProgressEnabled', True)

    def getDisabledPMOperations(self):
        return self.__getGlobalSetting('disabledPMOperations', dict())

    def getDisabledPersonalMissions(self):
        return self.__getGlobalSetting('disabledPersonalMissions', dict())

    def isStrongholdsEnabled(self):
        return self.__getGlobalSetting('strongholdSettings', {}).get('isStrongholdsEnabled', False)

    def isTournamentEnabled(self):
        return self.__getGlobalSetting('tournamentSettings', {}).get('isTournamentEnabled', False)

    def isLeaguesEnabled(self):
        return self.__getGlobalSetting('strongholdSettings', {}).get('isLeaguesEnabled', False)

    def isElenEnabled(self):
        return self.__getGlobalSetting('elenSettings', {}).get('isElenEnabled', True)

    def elenUpdateInterval(self):
        return self.__getGlobalSetting('elenSettings', {}).get('elenUpdateInterval', 60)

    def isGoldFishEnabled(self):
        return self.__getGlobalSetting('isGoldFishEnabled', False)

    def isStorageEnabled(self):
        return self.__bwShop.isStorageEnabled

    def isLootBoxesEnabled(self):
        return self.__getGlobalSetting('isLootBoxesEnabled')

    def isAnonymizerEnabled(self):
        return self.__getGlobalSetting('isAnonymizerEnabled', False)

    def isSessionStatsEnabled(self):
        return self.__getGlobalSetting('sessionStats', {}).get('isSessionStatsEnabled', False)

    def isLinkWithHoFEnabled(self):
        return self.__getGlobalSetting('sessionStats', {}).get('isLinkWithHoFEnabled', False)

    def isNationChangeEnabled(self):
        return self.__getGlobalSetting('isNationChangeEnabled', True)

    def getCrystalRewardConfig(self):
        return self.__crystalRewardsConfig

    @property
    def shop(self):
        return self.__bwShop

    def isShopDataChangedInDiff(self, diff, fieldName=None):
        if 'shop' in diff:
            if fieldName is not None:
                if fieldName in diff['shop']:
                    return True
            else:
                return True
        return False

    def isBlueprintDataChangedInDiff(self, diff):
        return 'blueprints_config' in diff

    def isTutorialEnabled(self):
        return self.__getGlobalSetting('isTutorialEnabled', IS_TUTORIAL_ENABLED)

    def isSandboxEnabled(self):
        return self.__getGlobalSetting('isSandboxEnabled', False)

    def isBootcampEnabled(self):
        return self.__getGlobalSetting('isBootcampEnabled', False)

    def isLinkedSetEnabled(self):
        return self.__getGlobalSetting('isLinkedSetEnabled', False)

    def getBootcampBonuses(self):
        return self.__getGlobalSetting('bootcampBonuses', {})

    def getLootBoxConfig(self):
        return self.__getGlobalSetting('lootBoxes_config', {})

    def getPiggyBankConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PIGGYBANK, {})

    def getAdditionalBonusConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.DAILY_BONUS, {})

    def getPremQuestsConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PREM_QUESTS, {})

    def getDailyQuestConfig(self):
        return self.__getGlobalSetting(DAILY_QUESTS_CONFIG, {})

    def getMagneticAutoAimConfig(self):
        return self.__getGlobalSetting(MAGNETIC_AUTO_AIM_CONFIG, {})

    def getPreferredMapsConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PREFERRED_MAPS, {})

    def isEpicRandomEnabled(self):
        return self.__getGlobalSetting('isEpicRandomEnabled', False)

    def isEpicRandomAchievementsEnabled(self):
        return self.__getGlobalSetting('isEpicRandomAchievementsEnabled', False)

    def isEpicRandomMarkOfMasteryEnabled(self):
        return self.__getGlobalSetting('isEpicRandomMarkOfMasteryEnabled', False)

    def isEpicRandomMarksOnGunEnabled(self):
        return self.__getGlobalSetting('isEpicRandomMarksOnGunEnabled', False)

    def isCommandBattleEnabled(self):
        return self.__getGlobalSetting('isCommandBattleEnabled', False)

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

    def isTankmanRestoreEnabled(self):
        return self.__getGlobalSetting('isTankmanRestoreEnabled', True)

    def isVehicleRestoreEnabled(self):
        return self.__getGlobalSetting('isVehicleRestoreEnabled', True)

    def isCustomizationEnabled(self):
        return self.__getGlobalSetting('isCustomizationEnabled', True)

    def getHeroVehicles(self):
        return self.__getGlobalSetting('hero_vehicles', {})

    def isManualEnabled(self):
        return self.__getGlobalSetting('isManualEnabled', False)

    def isFieldPostEnabled(self):
        return self.__getGlobalSetting('isFieldPostEnabled', True)

    def isPromoLoggingEnabled(self):
        return self.__getGlobalSetting('isPromoLoggingEnabled', False)

    def isReferralProgramEnabled(self):
        return self.__getGlobalSetting('isReferralProgramEnabled', False)

    def isCrewSkinsEnabled(self):
        return self.__getGlobalSetting('isCrewSkinsEnabled', False)

    def getPremiumXPBonus(self):
        return self.__getGlobalSetting('tankPremiumBonus', {}).get('xp', 0.5)

    def getPremiumCreditsBonus(self):
        return self.__getGlobalSetting('tankPremiumBonus', {}).get('credits', 0.5)

    def isPreferredMapsEnabled(self):
        return self.__getGlobalSetting('isPreferredMapsEnabled', False)

    def isBattleBoostersEnabled(self):
        return self.__getGlobalSetting('isBattleBoostersEnabled', False)

    def isCrewBooksEnabled(self):
        return self.__getGlobalSetting('isCrewBooksEnabled', False)

    def isCrewBooksPurchaseEnabled(self):
        return self.__getGlobalSetting('isCrewBooksPurchaseEnabled', False)

    def isCrewBooksSaleEnabled(self):
        return self.__getGlobalSetting('isCrewBooksSaleEnabled', False)

    def isTrophyDevicesEnabled(self):
        return self.__getGlobalSetting('isTrophyDevicesEnabled', False)

    def isCollectorVehicleEnabled(self):
        return self.__getGlobalSetting(CollectorVehicleConsts.CONFIG_NAME, {}).get(CollectorVehicleConsts.IS_ENABLED, False)

    def isOffersEnabled(self):
        return self.__getGlobalSetting('isOffersEnabled', False)

    def getFriendlyFireBonusTypes(self):
        return self.__getGlobalSetting('isNoAllyDamage', set())

    def getProgressiveRewardConfig(self):
        return self.__progressiveReward

    def getMarathonConfig(self):
        return self.__getGlobalSetting('marathon_config', {})

    def getClansConfig(self):
        return self.__getGlobalSetting(ClansConfig.SECTION_NAME, {})

    def getSeniorityAwardsConfig(self):
        return self.__seniorityAwardsConfig

    def getBattlePassConfig(self):
        return self.__battlePassConfig

    def __getGlobalSetting(self, settingsName, default=None):
        return self.__serverSettings.get(settingsName, default)

    def __updateClanProfile(self, targetSettings):
        cProfile = targetSettings['clanProfile']
        self.__clanProfile = _ClanProfile(cProfile.get('isEnabled', False))

    def __updateWgcg(self, targetSettings):
        cProfile = targetSettings['wgcg']
        self.__wgcg = _Wgcg(cProfile.get('isEnabled', False), cProfile.get('gateUrl', ''), cProfile.get('type', 'gateway'), cProfile.get('loginOnStart', False))

    def __updateEventProgression(self, targetSettings):
        self.__eventProgressionSettings = self.__eventProgressionSettings.replace(targetSettings['event_progression_config'])

    def __updateAdventCalendar(self, targetSettings):
        self.__adventCalendar = self.__adventCalendar.replace(targetSettings['advent_calendar_config'])

    def __updateRanked(self, targetSettings):
        self.__rankedBattlesSettings = self.__rankedBattlesSettings.replace(targetSettings['ranked_config'])

    def __updateEpic(self, targetSettings):
        self.__epicMetaGameSettings = self.__epicMetaGameSettings.replace(targetSettings['epic_config'].get('epicMetaGame', {}))
        self.__epicGameSettings = self.__epicGameSettings.replace(targetSettings['epic_config'])

    def __updateSquadBonus(self, sourceSettings):
        self.__squadPremiumBonus = self.__squadPremiumBonus.replace(sourceSettings[PremiumConfigs.PREM_SQUAD])

    def __updateShop(self, targetSettings):
        self.__bwShop = self.__bwShop.replace(targetSettings['shop'])

    def __updateBattleRoyale(self, targetSettings):
        self.__battleRoyaleSettings = self.__battleRoyaleSettings.replace(targetSettings['battle_royale_config'])

    def __updateBlueprints(self, targetSettings):
        self.__blueprintsConfig = self.__blueprintsConfig._replace(**targetSettings)
        if self.__blueprintsConfig.isBlueprintModeChange(targetSettings):
            if not self.__blueprintsConfig.isEnabled or not self.__blueprintsConfig.useBlueprintsForUnlock:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_SWITCH_OFF, type=SM_TYPE.Information, priority='medium')
            else:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_SWITCH_ON, type=SM_TYPE.Information, priority='medium')

    def __updateProgressiveReward(self, targetSettings):
        self.__progressiveReward = self.__progressiveReward.replace(targetSettings['progressive_reward_config'])

    def __updateSeniorityAwards(self, targetSettings):
        self.__seniorityAwardsConfig = self.__seniorityAwardsConfig.replace(targetSettings['seniority_awards_config'])
