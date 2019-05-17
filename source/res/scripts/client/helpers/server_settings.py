# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/server_settings.py
import copy
import types
from collections import namedtuple
from Event import Event
from constants import IS_TUTORIAL_ENABLED, SWITCH_STATE, PremiumConfigs
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from gui import GUI_SETTINGS, SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.shared.utils.decorators import ReprInjector
from personal_missions import PM_BRANCH
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


class _FrontlineSettings(namedtuple('_FrontlineSettings', ('flHostUrl',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls('')


class _SpgRedesignFeatures(namedtuple('_SpgRedesignFeatures', ('stunEnabled', 'markTargetAreaEnabled'))):
    __slots__ = ()

    def isStunEnabled(self):
        return self.stunEnabled

    @classmethod
    def defaults(cls):
        return cls(False, False)


class _BwRankedBattles(namedtuple('_BwRankedBattles', ('rblbHostUrl', 'infoPageUrl', 'introPageUrl'))):
    __slots__ = ()

    def __new__(cls, rblbHostUrl=None, infoPageUrl=None, introPageUrl=None):
        return super(_BwRankedBattles, cls).__new__(cls, rblbHostUrl, infoPageUrl, introPageUrl)

    @classmethod
    def defaults(cls):
        return cls(None, None, None)


class _BwHallOfFame(namedtuple('_BwHallOfFame', ('hofHostUrl', 'isHofEnabled', 'isStatusEnabled'))):
    __slots__ = ()

    def __new__(cls, hofHostUrl=None, isHofEnabled=False, isStatusEnabled=False):
        return super(_BwHallOfFame, cls).__new__(cls, hofHostUrl, isHofEnabled, isStatusEnabled)

    @classmethod
    def defaults(cls):
        return cls()


class _BwIngameShop(namedtuple('_BwIngameShop', ('hostUrl', 'backendHostUrl', 'shopMode', 'isStorageEnabled', 'isPreviewEnabled'))):

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_BwIngameShop.__new__.__defaults__ = ('',
 '',
 'disabled',
 False,
 False)

class _RankedBattlesConfig(namedtuple('_RankedBattlesConfig', ('isEnabled', 'peripheryIDs', 'winnerRankChanges', 'loserRankChanges', 'minXP', 'unburnableRanks', 'unburnableStepRanks', 'unburnableVehRanks', 'unburnableVehStepRanks', 'minLevel', 'maxLevel', 'accRanks', 'accSteps', 'vehRanks', 'vehSteps', 'cycleFinishSeconds', 'primeTimes', 'seasons', 'cycleTimes', 'accLadderPts', 'vehLadderPts', 'shields', 'divisions', 'bonusBattlesMultiplier'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, winnerRankChanges=(), loserRankChanges=(), minXP=0, unburnableRanks={}, unburnableStepRanks={}, unburnableVehRanks={}, unburnableVehStepRanks={}, minLevel=0, maxLevel=0, accRanks=(), accSteps=(), vehRanks=(), vehSteps=(), cycleFinishSeconds=0, primeTimes={}, seasons={}, cycleTimes=(), accLadderPts=(), vehLadderPts=(), shields={}, divisions={}, bonusBattlesMultiplier=0)
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

class _EpicMetaGameConfig(namedtuple('_EpicMetaGameConfig', ['maxCombatReserveLevel',
 'seasonData',
 'metaLevel',
 'rewards'])):

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_EpicMetaGameConfig.__new__.__defaults__ = (0,
 (0, False),
 (0, 0, 0),
 {})

class _EpicGameConfig(namedtuple('_EpicGameConfig', ('isEnabled', 'validVehicleLevels', 'seasons', 'cycleTimes', 'peripheryIDs', 'primeTimes'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, validVehicleLevels=[], seasons={}, cycleTimes=(), peripheryIDs={}, primeTimes={})
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


class _TelecomConfig(object):
    __slots__ = ('__config',)

    def __init__(self, telecomConfig):
        self.__config = dict(((bundleId, bundleData['operator']) for bundleId, bundleData in telecomConfig['bundles'].iteritems()))

    def getInternetProvider(self, bundleId):
        if bundleId in self.__config:
            return self.__config[bundleId]
        LOG_ERROR('Telecom config: no internet provider info for bundleId: {}.'.format(bundleId))

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
        self.__frontlineSettings = _FrontlineSettings.defaults()
        self.__bwRankedBattles = _BwRankedBattles.defaults()
        self.__bwHallOfFame = _BwHallOfFame.defaults()
        self.__bwIngameShop = _BwIngameShop()
        self.__rankedBattlesSettings = _RankedBattlesConfig.defaults()
        self.__epicMetaGameSettings = _EpicMetaGameConfig()
        self.__epicGameSettings = _EpicGameConfig()
        self.__telecomConfig = _TelecomConfig.defaults()
        self.__squadPremiumBonus = _SquadPremiumBonus.defaults()
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
        if 'frontlineSettings' in self.__serverSettings:
            settings = self.__serverSettings['frontlineSettings']
            self.__frontlineSettings = _FrontlineSettings(settings.get('flHostUrl', ''))
        if 'rankedBattles' in self.__serverSettings:
            self.__bwRankedBattles = makeTupleByDict(_BwRankedBattles, self.__serverSettings['rankedBattles'])
        if 'hallOfFame' in self.__serverSettings:
            self.__bwHallOfFame = makeTupleByDict(_BwHallOfFame, self.__serverSettings['hallOfFame'])
        if 'ingameShop' in self.__serverSettings:
            self.__bwIngameShop = makeTupleByDict(_BwIngameShop, self.__serverSettings['ingameShop'])
        if 'ranked_config' in self.__serverSettings:
            self.__rankedBattlesSettings = makeTupleByDict(_RankedBattlesConfig, self.__serverSettings['ranked_config'])
        if 'epic_config' in self.__serverSettings:
            LOG_DEBUG('epic_config', self.__serverSettings['epic_config'])
            self.__epicMetaGameSettings = makeTupleByDict(_EpicMetaGameConfig, self.__serverSettings['epic_config']['epicMetaGame'])
            self.__epicGameSettings = makeTupleByDict(_EpicGameConfig, self.__serverSettings['epic_config'])
        if PremiumConfigs.PREM_SQUAD in self.__serverSettings:
            self.__squadPremiumBonus = _SquadPremiumBonus.create(self.__serverSettings[PremiumConfigs.PREM_SQUAD])
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
        if 'epic_config' in serverSettingsDiff:
            self.__updateEpic(serverSettingsDiff)
            self.__serverSettings['epic_config'] = serverSettingsDiff['epic_config']
        if 'telecom_config' in serverSettingsDiff:
            self.__telecomConfig = _TelecomConfig(self.__serverSettings['telecom_config'])
        if 'disabledPMOperations' in serverSettingsDiff:
            self.__serverSettings['disabledPMOperations'] = serverSettingsDiff['disabledPMOperations']
        if 'ingameShop' in serverSettingsDiff:
            self.__updateIngameShop(serverSettingsDiff)
        if 'disabledPersonalMissions' in serverSettingsDiff:
            self.__serverSettings['disabledPersonalMissions'] = serverSettingsDiff['disabledPersonalMissions']
        if 'blueprints_config' in serverSettingsDiff:
            self.__updateBlueprints(serverSettingsDiff['blueprints_config'])
        if 'lootBoxes_config' in serverSettingsDiff:
            self.__serverSettings['lootBoxes_config'] = serverSettingsDiff['lootBoxes_config']
        if 'progressive_reward_config' in serverSettingsDiff:
            self.__updateProgressiveReward(serverSettingsDiff)
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
    def epicMetaGame(self):
        return self.__epicMetaGameSettings

    @property
    def epicBattles(self):
        return self.__epicGameSettings

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

    def isLeaguesEnabled(self):
        return self.__getGlobalSetting('strongholdSettings', {}).get('isLeaguesEnabled', False)

    def isElenEnabled(self):
        return self.__getGlobalSetting('elenSettings', {}).get('isElenEnabled', True)

    def elenUpdateInterval(self):
        return self.__getGlobalSetting('elenSettings', {}).get('elenUpdateInterval', 60)

    def isGoldFishEnabled(self):
        return self.__getGlobalSetting('isGoldFishEnabled', False)

    def isIngameStorageEnabled(self):
        return self.__bwIngameShop.isStorageEnabled

    def isIngamePreviewEnabled(self):
        return self.__bwIngameShop.isPreviewEnabled

    def isLootBoxesEnabled(self):
        return self.__getGlobalSetting('isLootBoxesEnabled')

    def isSessionStatsEnabled(self):
        return self.__getGlobalSetting('sessionStats', {}).get('isSessionStatsEnabled', False)

    def isLinkWithHoFEnabled(self):
        return self.__getGlobalSetting('sessionStats', {}).get('isLinkWithHoFEnabled', False)

    @property
    def ingameShop(self):
        return self.__bwIngameShop

    def isIngameDataChangedInDiff(self, diff, fieldName=None):
        if 'ingameShop' in diff:
            if fieldName is not None:
                if fieldName in diff['ingameShop']:
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

    def getProgressiveRewardConfig(self):
        return self.__progressiveReward

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

    def __updateEpic(self, targetSettings):
        self.__epicMetaGameSettings = self.__epicMetaGameSettings.replace(targetSettings['epic_config'].get('epicMetaGame', {}))
        self.__epicGameSettings = self.__epicGameSettings.replace(targetSettings['epic_config'])

    def __updateSquadBonus(self, sourceSettings):
        self.__squadPremiumBonus = self.__squadPremiumBonus.replace(sourceSettings[PremiumConfigs.PREM_SQUAD])

    def __updateIngameShop(self, targetSettings):
        self.__bwIngameShop = self.__bwIngameShop.replace(targetSettings['ingameShop'])

    def __updateBlueprints(self, targetSettings):
        self.__blueprintsConfig = self.__blueprintsConfig._replace(**targetSettings)
        if self.__blueprintsConfig.isBlueprintModeChange(targetSettings):
            if not self.__blueprintsConfig.isEnabled or not self.__blueprintsConfig.useBlueprintsForUnlock:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_SWITCH_OFF, type=SM_TYPE.Information, priority='medium')
            else:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_SWITCH_ON, type=SM_TYPE.Information, priority='medium')

    def __updateProgressiveReward(self, targetSettings):
        self.__progressiveReward = self.__progressiveReward.replace(targetSettings['progressive_reward_config'])
