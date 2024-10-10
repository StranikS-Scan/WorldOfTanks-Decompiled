# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/server_settings.py
import copy
import functools
import logging
import types
from collections import namedtuple
import typing
import constants
import post_progression_common
from BonusCaps import BonusCapsConst
from Event import Event
from UnitBase import PREBATTLE_TYPE_TO_UNIT_ASSEMBLER, UNIT_ASSEMBLER_IMPL_TO_CONFIG
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from battle_pass_common import BATTLE_PASS_CONFIG_NAME, BattlePassConfig
from collections_common import CollectionsConfig
from collector_vehicle import CollectorVehicleConsts
from comp7_ranks_common import Comp7Division
from constants import BATTLE_NOTIFIER_CONFIG, ClansConfig, Configs, DAILY_QUESTS_CONFIG, DOG_TAGS_CONFIG, MAGNETIC_AUTO_AIM_CONFIG, MISC_GUI_SETTINGS, PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG, PLAYER_SUBSCRIPTIONS_CONFIG, TOURNAMENT_CONFIG, PREM_BONUS_TYPES, PREMIUM_ENTITLEMENTS, ENTITLEMENT_TO_PREM_TYPE
from debug_utils import LOG_DEBUG, LOG_NOTE
from gifts.gifts_common import ClientReqStrategy, GiftEventID, GiftEventState
from gui import GUI_SETTINGS, SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE
from gui.shared.utils.decorators import ReprInjector
from helpers import time_utils
from personal_missions import PM_BRANCH
from post_progression_common import FEATURE_BY_GROUP_ID, ROLESLOT_FEATURE
from ranked_common import SwitchState
from renewable_subscription_common.settings_constants import GOLD_RESERVE_GAINS_SECTION
from schema_manager import getSchemaManager
from shared_utils import makeTupleByDict, updateDict, findFirst
from soft_exception import SoftException
from telecom_rentals_common import TELECOM_RENTALS_CONFIG
from trade_in_common.constants_types import CONFIG_NAME as TRADE_IN_CONFIG_NAME
from achievements20.Achievements20GeneralConfig import Achievements20GeneralConfig
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List, Sequence
    from dict2model.types import ModelType
    from base_schema_manager import GameParamsSchema
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
        if isinstance(langID, unicode):
            langID = str(langID)
        return self.__getUrl('missions_token_descrs', langID)

    def getMissionsDecorationUrl(self, decorationID, size):
        return self.__getUrl('missions_decoration', size, decorationID)

    def getOffersRootUrl(self):
        return self.__getUrl('offers')

    def getGameLoadingConfigUrl(self):
        return self.__getUrl('game_loading_config')

    def getCollectionsContentConfigUrl(self):
        return self.__getUrl('collections_content_config')

    def __getUrl(self, urlKey, *args):
        try:
            return self.__urls[urlKey] % args
        except (KeyError, TypeError):
            LOG_NOTE('There is invalid url while getting emblem from web', urlKey, args)

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


class _Wgcg(namedtuple('_Wgcg', ('enabled',
 'url',
 'type',
 'loginOnStart',
 'isJwtAuthorizationEnabled'))):
    __slots__ = ()

    def isEnabled(self):
        return self.enabled

    def getAccessorType(self):
        return self.type

    def getGateUrl(self):
        return self.url

    def getLoginOnStart(self):
        return self.loginOnStart

    def isJwtEnabled(self):
        return self.isJwtAuthorizationEnabled

    @classmethod
    def defaults(cls):
        return cls(False, '', '', False, False)


class _Wgnp(namedtuple('_Wgnp', ('enabled', 'url', 'renameApiEnabled'))):
    __slots__ = ()

    def isEnabled(self):
        return self.enabled

    def getUrl(self):
        return self.url

    def isRenameApiEnabled(self):
        return self.enabled and self.renameApiEnabled

    @classmethod
    def defaults(cls):
        return cls(False, '', False)


class _UILogging(namedtuple('_UILogging', ('enabled',))):
    __slots__ = ()

    def isEnabled(self):
        return self.enabled

    @classmethod
    def defaults(cls):
        return cls(False)


class _EULA(namedtuple('_EULA', ('enabled', 'demoAccEnabled', 'steamAccEnabled'))):
    __slots__ = ()

    def isEnabled(self):
        return self.enabled

    def isDemoAccEnabled(self):
        return self.enabled and self.demoAccEnabled

    def isSteamAccEnabled(self):
        return self.enabled and self.steamAccEnabled

    @classmethod
    def defaults(cls):
        return cls(False, False, False)


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


class _TournamentSettings(namedtuple('_TournamentSettings', ('isExternalBattleEnabled', 'isTournamentEnabled', 'igbHostUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isExternalBattleEnabled=False, isTournamentEnabled=False, igbHostUrl='')
        defaults.update(**kwargs)
        return super(_TournamentSettings, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


class _FrontlineSettings(namedtuple('_FrontlineSettings', ('isEpicTrainingEnabled',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return cls(False)


class _SpgRedesignFeatures(namedtuple('_SpgRedesignFeatures', ('stunEnabled', 'markTargetAreaEnabled'))):
    __slots__ = ()

    def isStunEnabled(self):
        return self.stunEnabled

    @classmethod
    def defaults(cls):
        return cls(False, False)


class _BwHallOfFame(namedtuple('_BwHallOfFame', ('hofHostUrl', 'isHofEnabled', 'isStatusEnabled'))):
    __slots__ = ()

    def __new__(cls, hofHostUrl=None, isHofEnabled=False, isStatusEnabled=False):
        return super(_BwHallOfFame, cls).__new__(cls, hofHostUrl, isHofEnabled, isStatusEnabled)

    @classmethod
    def defaults(cls):
        return cls()


class _BwShop(namedtuple('_BwShop', ('hostUrl', 'isStorageEnabled'))):

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


_BwShop.__new__.__defaults__ = ('', '', False)

class _BwProductCatalog(namedtuple('_BwProductCatalog', ('url',))):

    @classmethod
    def defaults(cls):
        return cls('')


_BwProductCatalog.__new__.__defaults__ = ('',)

class RankedBattlesConfig(namedtuple('RankedBattlesConfig', ('isEnabled',
 'peripheryIDs',
 'winnerRankChanges',
 'loserRankChanges',
 'minXP',
 'unburnableRanks',
 'unburnableStepRanks',
 'minLevel',
 'maxLevel',
 'accRanks',
 'accSteps',
 'cycleFinishSeconds',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'shields',
 'divisions',
 'bonusBattlesMultiplier',
 'expectedSeasons',
 'yearAwardsMarks',
 'rankGroups',
 'qualificationBattles',
 'yearLBSize',
 'leaguesBonusBattles',
 'forbiddenClassTags',
 'forbiddenVehTypes',
 'shopState',
 'yearLBState',
 'yearRewardState',
 'leagueRewardEnabled',
 'seasonRatingPageUrl',
 'yearRatingPageUrl',
 'infoPageUrl',
 'introPageUrl',
 'seasonGapPageUrl',
 'shopPageUrl',
 'hasSpecialSeason'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, winnerRankChanges=(), loserRankChanges=(), minXP=0, unburnableRanks={}, unburnableStepRanks={}, minLevel=0, maxLevel=0, accRanks=0, accSteps=(), cycleFinishSeconds=0, primeTimes={}, seasons={}, cycleTimes=(), shields={}, divisions={}, bonusBattlesMultiplier=0, expectedSeasons=0, yearAwardsMarks=(), rankGroups=(), qualificationBattles=0, yearLBSize=0, leaguesBonusBattles=(), forbiddenClassTags=(), forbiddenVehTypes=(), shopState=SwitchState.DISABLED, yearLBState=SwitchState.DISABLED, yearRewardState=SwitchState.ENABLED, leagueRewardEnabled=True, seasonRatingPageUrl='', yearRatingPageUrl='', infoPageUrl='', introPageUrl='', seasonGapPageUrl='', shopPageUrl='', hasSpecialSeason=False)
        defaults.update(kwargs)
        return super(RankedBattlesConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _ProgressiveReward(namedtuple('_ProgressiveReward', ('isEnabled',
 'levelTokenID',
 'probabilityTokenID',
 'maxLevel'))):

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
 'rewards',
 'defaultSlots',
 'slots',
 'inBattleReservesByRank',
 'skipParamsValidation',
 'destructibleTypeId'])):

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
 {},
 {},
 {},
 0,
 0)

class EpicGameConfig(namedtuple('EpicGameConfig', ('isEnabled',
 'validVehicleLevels',
 'battlePassDataEnabled',
 'levelsToUpgrateAllReserves',
 'seasons',
 'cycleTimes',
 'unlockableInBattleVehLevels',
 'inBattleModifiers',
 'peripheryIDs',
 'primeTimes',
 'rentVehicles',
 'tooltips',
 'forbiddenVehTypes'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, validVehicleLevels=[], battlePassDataEnabled=True, levelsToUpgrateAllReserves=[], unlockableInBattleVehLevels=[], inBattleModifiers={}, seasons={}, cycleTimes=(), peripheryIDs={}, primeTimes={}, rentVehicles=[], tooltips={}, forbiddenVehTypes=set())
        defaults.update(kwargs)
        return super(EpicGameConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _UnitAssemblerConfig(namedtuple('_UnitAssemblerConfig', ('squad', 'epic'))):
    __slots__ = ()

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @staticmethod
    def isPrebattleSupported(prebattleType):
        return prebattleType in PREBATTLE_TYPE_TO_UNIT_ASSEMBLER

    def getConfigOfQueue(self, prebattleType):
        return {} if not self.isPrebattleSupported(prebattleType) else self.asDict().get(UNIT_ASSEMBLER_IMPL_TO_CONFIG[PREBATTLE_TYPE_TO_UNIT_ASSEMBLER[prebattleType]], {})

    def isVoicePreferenceEnabled(self, prebattleType):
        return self.getConfigOfQueue(prebattleType).get('voiceChatPreferenceEnabled', False)

    def isTankLevelPreferenceEnabled(self, prebattleType):
        return self.getConfigOfQueue(prebattleType).get('tankLevelPreferenceEnabled', False)

    def getAllowedTankLevels(self, prebattleType):
        return self.getConfigOfQueue(prebattleType).get('allowedTankLevels', 0)

    def isAssemblingEnabled(self, prebattleType):
        return self.getConfigOfQueue(prebattleType).get('isAssemblingEnabled', False)

    def getExtendTierFilter(self, prebattleType):
        return self.getConfigOfQueue(prebattleType).get('extendTierFilter', [])

    @classmethod
    def defaults(cls):
        return cls(squad={}, epic={})


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


class BattleRoyaleConfig(namedtuple('BattleRoyaleConfig', ('isEnabled',
 'peripheryIDs',
 'unburnableTitles',
 'eventProgression',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'maps',
 'battleXP',
 'coneVisibility',
 'loot',
 'defaultAmmo',
 'vehiclesSlotsConfig',
 'economics',
 'url',
 'respawns',
 'isShowTimeLeft',
 'progressionTokenAward'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, eventProgression={}, unburnableTitles=(), primeTimes={}, seasons={}, cycleTimes={}, maps=(), battleXP={}, coneVisibility={}, loot={}, defaultAmmo={}, vehiclesSlotsConfig={}, economics={}, url='', respawns={}, isShowTimeLeft=False, progressionTokenAward={})
        defaults.update(kwargs)
        return super(BattleRoyaleConfig, cls).__new__(cls, **defaults)

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
    __slots__ = ('__bundleIdToProvider',)

    def __init__(self, telecomConfig):
        self.__bundleIdToProvider = {bundleId:bundleData['operator'] for bundleId, bundleData in telecomConfig['bundles'].iteritems()}

    def getInternetProvider(self, bundleId):
        provider = self.__bundleIdToProvider.get(bundleId, '')
        return provider

    @classmethod
    def defaults(cls):
        return cls({'bundles': {}})


class _BlueprintsConfig(namedtuple('_BlueprintsConfig', ('allowBlueprintsConversion',
 'isEnabled',
 'useBlueprintsForUnlock',
 'levels'))):
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

    def getAllianceConversionCoeffs(self, level):
        return {} if not self.isBlueprintsAvailable() or level not in self.levels else self.levels[level][4]

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


class SeniorityAwardsConfig(typing.NamedTuple('SeniorityAwardsConfig', (('enabled', bool),
 ('endTime', int),
 ('reminders', list),
 ('clockOnNotification', int),
 ('showRewardNotification', bool),
 ('receivedRewardsToken', str),
 ('rewardEligibilityToken', str),
 ('claimRewardToken', str),
 ('rewardQuestsPrefix', str)))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, endTime=0, reminders=[], clockOnNotification=0, showRewardNotification=False, receivedRewardsToken='', rewardEligibilityToken='', claimRewardToken='', rewardQuestsPrefix='')
        defaults.update(kwargs)
        return super(SeniorityAwardsConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


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


_crystalRewardInfo = namedtuple('_crystalRewardInfo', 'level, arenaType, winTop3, loseTop3, winTop10, loseTop10, topLength firstTopLength')

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
                topWinRewards = list(scoreData[True].itervalues())
                winTop3 = max(topWinRewards)
                results.append(_crystalRewardInfo(level, arenaBonusType, winTop3=winTop3, loseTop3=max(scoreData[False].itervalues()), winTop10=min(scoreData[True].itervalues()), loseTop10=min(scoreData[False].itervalues()), topLength=len(scoreData[True]), firstTopLength=topWinRewards.count(winTop3)))

        return results

    def isCrystalEarnPossible(self, arenaType):
        return findFirst(lambda item: item.arenaType == arenaType, self.getRewardInfoData(), None) is not None


class _ReactiveCommunicationConfig(object):
    __slots__ = ('__isEnabled', '__url')

    def __init__(self, **kwargs):
        super(_ReactiveCommunicationConfig, self).__init__()
        self.__isEnabled = kwargs.get('isEnabled', False)
        self.__url = kwargs.get('url', '')
        if self.__isEnabled and not self.__url:
            _logger.error('Connection to web subscription service is enabled, but url is empty')
            self.__isEnabled = False

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def url(self):
        return self.__url


class _BlueprintsConvertSaleConfig(namedtuple('_BlueprintsConvertSaleConfig', ('enabled', 'options'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, options={})
        defaults.update(kwargs)
        return super(_BlueprintsConvertSaleConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    def isEnabled(self):
        return self.enabled

    def getOptions(self):
        return self.options


class _MapboxConfig(namedtuple('_MapboxConfig', ('isEnabled',
 'progressionUpdateInterval',
 'peripheryIDs',
 'forbiddenClassTags',
 'forbiddenVehTypes',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'levels',
 'geometryIDs'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, forbiddenClassTags=set(), forbiddenVehTypes=set(), primeTimes={}, seasons={}, cycleTimes={}, levels=[], geometryIDs={}, progressionUpdateInterval=time_utils.ONE_MINUTE * 2)
        defaults.update(kwargs)
        return super(_MapboxConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = {k:v for k, v in data.iteritems() if k in allowedFields}
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class VehiclePostProgressionConfig(namedtuple('_VehiclePostProgression', ('isPostProgressionEnabled',
 'enabledFeatures',
 'forbiddenVehicles',
 'enabledRentedVehicles'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isPostProgressionEnabled=False, enabledFeatures=frozenset(), forbiddenVehicles=frozenset(), enabledRentedVehicles=frozenset())
        defaults.update(kwargs)
        return super(VehiclePostProgressionConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(False, frozenset(), frozenset(), frozenset())

    @property
    def isEnabled(self):
        return self.isPostProgressionEnabled

    @property
    def isRoleSlotEnabled(self):
        return ROLESLOT_FEATURE in self.enabledFeatures

    def isSetupSwitchEnabled(self, groupID):
        return FEATURE_BY_GROUP_ID[groupID] in self.enabledFeatures

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


class _EventBattlesConfig(namedtuple('_EventBattlesConfig', ('isEnabled',
 'peripheryIDs',
 'primeTimes',
 'seasons',
 'cycleTimes',
 'progression',
 'specialVehicles',
 'stampsPerProgressionStage',
 'stamp',
 'ticketToken',
 'quickBossTicketToken',
 'quickHunterTicketToken',
 'ticketsToDraw',
 'lootBoxDailyPurchaseLimit',
 'lootBoxCounterEntitlementID'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, progression=[], specialVehicles=[], stampsPerProgressionStage=0, stamp='', ticketToken='', quickBossTicketToken='', quickHunterTicketToken='', ticketsToDraw=0, lootBoxDailyPurchaseLimit=0, lootBoxCounterEntitlementID='')
        defaults.update(kwargs)
        return super(_EventBattlesConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class GiftEventConfig(namedtuple('_GiftEventConfig', ('eventID',
 'giftEventState',
 'giftItemIDs',
 'clientReqStrategy'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(eventID=GiftEventID.UNKNOWN, giftEventState=GiftEventState.DISABLED, giftItemIDs=[], clientReqStrategy=ClientReqStrategy.AUTO)
        defaults.update(kwargs)
        return super(GiftEventConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(GiftEventID.UNKNOWN, GiftEventState.DISABLED, [], ClientReqStrategy.AUTO)

    @property
    def isEnabled(self):
        return self.giftEventState == GiftEventState.ENABLED

    @property
    def isSuspended(self):
        return self.giftEventState == GiftEventState.SUSPENDED

    @property
    def isDisabled(self):
        return self.giftEventState == GiftEventState.DISABLED


class GiftSystemConfig(namedtuple('_GiftSystemConfig', ('events',))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(events={})
        defaults.update(kwargs)
        cls.__packEventConfigs(defaults)
        return super(GiftSystemConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls({})

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        self.__packEventConfigs(dataToUpdate)
        return self._replace(**dataToUpdate)

    @classmethod
    def __packEventConfigs(cls, data):
        data['events'] = {eID:makeTupleByDict(GiftEventConfig, eData) for eID, eData in data['events'].iteritems()}


class _WellRewardConfig(namedtuple('_WellRewardConfig', ('bonus',
 'limit',
 'isSerial',
 'sequence',
 'rewardId'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(bonus={}, limit=0, isSerial=False, sequence='', rewardId='')
        defaults.update(kwargs)
        return super(_WellRewardConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()


class _ResourceConfig(namedtuple('_ResourceConfig', ('name', 'rate', 'limit'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(name='', rate=0, limit=0)
        defaults.update(kwargs)
        return super(_ResourceConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()


class ResourceWellConfig(namedtuple('_ResourceWellConfig', ('isEnabled',
 'season',
 'finishTime',
 'remindTime',
 'rewards',
 'points',
 'resources',
 'startTime'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, season=0, finishTime=0, remindTime=0, rewards={}, points=0, resources={}, startTime=0)
        defaults.update(kwargs)
        cls.__packResourceConfigs(defaults)
        cls.__packRewardsConfigs(defaults)
        return super(ResourceWellConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        self.__packResourceConfigs(dataToUpdate)
        self.__packRewardsConfigs(dataToUpdate)
        return self._replace(**dataToUpdate)

    @classmethod
    def __packResourceConfigs(cls, data):
        resources = {}
        for resourceType, resourceConfig in data['resources'].iteritems():
            resources[resourceType] = {name:_ResourceConfig(name=name, rate=resourceData.get('rate'), limit=resourceData.get('limit')) for name, resourceData in resourceConfig.iteritems()}

        data['resources'] = resources

    @classmethod
    def __packRewardsConfigs(cls, data):
        data['rewards'] = {rewardId:makeTupleByDict(_WellRewardConfig, reward) for rewardId, reward in data['rewards'].iteritems()}


class PlayLimitsConfig(namedtuple('PlayLimitsConfig', ('lockTimeBeforeBattle',))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(lockTimeBeforeBattle={})
        defaults.update(kwargs)
        return super(PlayLimitsConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _BattleMattersConfig(namedtuple('_BattleMattersConfig', ('isEnabled',
 'isPaused',
 'delayedRewardOfferVisibilityToken',
 'delayedRewardOfferCurrencyToken'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isPaused=False, delayedRewardOfferVisibilityToken='BattleMattersEmptyToken', delayedRewardOfferCurrencyToken='BattleMattersEmptyCurrencyToken')
        defaults.update(kwargs)
        return super(_BattleMattersConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _CollectiveGoalEntryPointConfig(namedtuple('_CollectiveGoalConfig', ('isEnabled',
 'startTime',
 'finishTime',
 'marathonPrefix',
 'hermodChannelName',
 'marathonName',
 'goalType',
 'goalDescription',
 'rulesCaption'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, startTime=None, finishTime=None, marathonPrefix=None, hermodChannelName=None, marathonName=None, goalType=None, goalDescription=None, rulesCaption=None)
        defaults.update(kwargs)
        return super(_CollectiveGoalEntryPointConfig, cls).__new__(cls, **defaults)

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _CollectiveGoalMarathonsConfig(namedtuple('_CollectiveGoalMarathonsConfig', ('isEnabled',
 'startTime',
 'finishTime',
 'url'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, startTime=None, finishTime=None, url=None)
        defaults.update(kwargs)
        return super(_CollectiveGoalMarathonsConfig, cls).__new__(cls, **defaults)

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class PeripheryRoutingConfig(namedtuple('_PeripheryRoutingConfig', ('isEnabled', 'peripheryRoutingGroups'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryRoutingGroups={})
        defaults.update(kwargs)
        return super(PeripheryRoutingConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls({})

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


def settingsBlock(className, fields):

    class SettingsBlock(namedtuple(className, fields)):
        __slots__ = ()

        def __new__(cls, **kwargs):
            defaults = cls.defaults()
            defaults.update(cls._preprocessData(kwargs))
            return super(SettingsBlock, cls).__new__(cls, **defaults)

        def asDict(self):
            return self._asdict()

        def replace(self, data):
            allowedFields = self._fields
            dataToUpdate = {k:v for k, v in self._preprocessData(data).iteritems() if k in allowedFields}
            return self._replace(**dataToUpdate)

        @classmethod
        def defaults(cls):
            raise NotImplementedError

        @classmethod
        def _preprocessData(cls, data):
            return data

    return SettingsBlock


class _Comp7QualificationConfig(settingsBlock('_Comp7QualificationConfig', ('battlesNumber',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return {'battlesNumber': 0}


class Comp7Config(settingsBlock('Comp7Config', ('isEnabled',
 'peripheryIDs',
 'primeTimes',
 'seasons',
 'battleModifiersDescr',
 'cycleTimes',
 'roleEquipments',
 'numPlayers',
 'levels',
 'forbiddenClassTags',
 'forbiddenVehTypes',
 'squadRatingRestriction',
 'squadSizes',
 'createVivoxTeamChannels',
 'qualification'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return dict(isEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, battleModifiersDescr=(), cycleTimes={}, roleEquipments={}, numPlayers=7, levels=[], forbiddenClassTags=set(), forbiddenVehTypes=set(), squadRatingRestriction={}, squadSizes=[], createVivoxTeamChannels=False, qualification=makeTupleByDict(_Comp7QualificationConfig, {}))

    @classmethod
    def _preprocessData(cls, data):
        qualificationConfig = data.get('qualification')
        if qualificationConfig is not None:
            data['qualification'] = makeTupleByDict(_Comp7QualificationConfig, qualificationConfig)
        return data


class Comp7RanksConfig(settingsBlock('Comp7RanksConfig', ('ranks',
 'ranksOrder',
 'eliteRankPercent',
 'divisionsByRank',
 'divisions',
 'rankInactivityNotificationThreshold'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return dict(ranks={}, ranksOrder=(), eliteRankPercent=0, divisionsByRank={}, divisions=(), rankInactivityNotificationThreshold=0)

    @classmethod
    def _preprocessData(cls, data):
        divisions = data.get('divisions')
        if divisions:
            data['divisions'] = cls.__dictDivisionsToComp7Divisions(divisions)
        divisionsByRank = data.get('divisionsByRank')
        if divisionsByRank:
            for rankID, divisions in divisionsByRank.iteritems():
                data['divisionsByRank'][rankID] = cls.__dictDivisionsToComp7Divisions(divisions)

        return data

    @classmethod
    def __dictDivisionsToComp7Divisions(cls, divisionsList):
        divs = []
        for dvsnDict in divisionsList:
            comp7Division = Comp7Division(dvsnDict)
            divs.append(comp7Division)

        return tuple(divs)


class Comp7RewardsConfig(settingsBlock('Comp7RewardsConfig', ('main', 'extra'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return {'main': [],
         'extra': []}


class WinbackConfig(namedtuple('WinbackConfig', ('isEnabled',
 'versusAIIsDefaultModeToken',
 'defaultProgression',
 'progressions'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, versusAIIsDefaultModeToken='', defaultProgression='', progressions={})
        defaults.update(kwargs)
        return super(WinbackConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class PersonalReservesConfig(namedtuple('_PersonalReserves', ('isReservesInBattleActivationEnabled', 'supportedQueueTypes'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isReservesInBattleActivationEnabled=False, supportedQueueTypes={})
        defaults.update(**kwargs)
        return super(PersonalReservesConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


class PreModerationConfig(namedtuple('_PreModerationConfig', ('prebattleDescriptionEnabled',))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(prebattleDescriptionEnabled=False)
        defaults.update(kwargs)
        return super(PreModerationConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)


GUI_LOOT_BOXES_CONFIG = 'gui_loot_boxes_config'

class _GuiLootBoxesConfig(object):
    __slots__ = ('__isEnabled', '__lootBoxBuyDayLimit', '__isBuyAvailable', '__shopCategoryUrl')

    def __init__(self, **kwargs):
        super(_GuiLootBoxesConfig, self).__init__()
        self.__isEnabled = kwargs.get('enabled', False)
        self.__lootBoxBuyDayLimit = kwargs.get('lootBoxBuyDayLimit', 0)
        self.__isBuyAvailable = kwargs.get('isBuyAvailable', False)
        self.__shopCategoryUrl = kwargs.get('shopCategoryUrl', '')

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def lootBoxBuyDayLimit(self):
        return self.__lootBoxBuyDayLimit

    @property
    def isBuyAvailable(self):
        return self.__isBuyAvailable

    def getShopCategoryUrl(self):
        return self.__shopCategoryUrl


EVENT_LOOT_BOXES_CONFIG = 'event_loot_boxes_config'

class _EventLootBoxesConfig(object):
    __slots__ = ('__isEnabled', '__startDateInUTC', '__finishDateInUTC', '__lootBoxBuyDayLimit')

    def __init__(self, **kwargs):
        super(_EventLootBoxesConfig, self).__init__()
        self.__isEnabled = kwargs.get('enabled', False)
        self.__startDateInUTC = kwargs.get('startDateInUTC', 0)
        self.__finishDateInUTC = kwargs.get('finishDateInUTC', 0)
        self.__lootBoxBuyDayLimit = kwargs.get('lootBoxBuyDayLimit', 0)

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def lootBoxBuyDayLimit(self):
        return self.__lootBoxBuyDayLimit

    def getEventActiveTime(self):
        return (self.__startDateInUTC, self.__finishDateInUTC)


class ArmoryYardConfig(namedtuple('ArmoryYardConfig', ('isEnabled',
 'isPaused',
 'seasons',
 'animations',
 'cycleTimes',
 'tokenBase',
 'receivedRewardTokenPostfix',
 'stageTokenPostfix',
 'currencyTokenPostfix',
 'tokenCost',
 'rewards',
 'introVideoLink',
 'infoPageLink',
 'activeHoursCountdown',
 'announcementCountdown',
 'starterPacks',
 'postProgression',
 'shop'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isPaused=False, seasons={}, animations={}, cycleTimes={}, tokenBase='', receivedRewardTokenPostfix='', stageTokenPostfix='', currencyTokenPostfix='', tokenCost={}, rewards={}, introVideoLink='', infoPageLink='', activeHoursCountdown=0, announcementCountdown=0, starterPacks={}, postProgression={}, shop={})
        defaults.update(kwargs)
        return super(ArmoryYardConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class _LimitedUIConfig(namedtuple('_LimitedUIConfig', ('enabled', 'rules', 'version'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(enabled=False, rules=[], version=0)
        defaults.update(kwargs)
        return super(_LimitedUIConfig, cls).__new__(cls, **defaults)

    def hasRules(self):
        return bool(self.rules)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class RPConfig(namedtuple('RPConfig', ('messageBarGUIEnabled', 'pgbCapacity', 'pgbDayLimit'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(messageBarGUIEnabled=True, pgbCapacity=0, pgbDayLimit=0)
        defaults.update(kwargs)
        return super(RPConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class RestoreConfig(namedtuple('RestoreConfig', ('tankmen', 'vehicles'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(tankmen={}, vehicles={})
        defaults.update(kwargs)
        return super(RestoreConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class VersusAIConfig(namedtuple('VersusAIConfig', ('isEnabled',
 'isDefaultModeForNoob',
 'levels',
 'forbiddenVehicleTags'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isDefaultModeForNoob=False, levels=tuple(), forbiddenVehicleTags=set())
        defaults.update(kwargs)
        return super(VersusAIConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class DebutBoxesConfig(namedtuple('DebutBoxesConfig', ('isEnabled',
 'startDate',
 'endDate',
 'infoPageUrl',
 'questIDs'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, startDate=0, endDate=0, infoPageUrl='', questIDs=[])
        defaults.update(kwargs)
        return super(DebutBoxesConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class EarlyAccessConfig(namedtuple('EarlyAccessConfig', ('isEnabled',
 'isPaused',
 'infoPageLink',
 'seasons'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isPaused=False, infoPageLink='', seasons={})
        defaults.update(kwargs)
        return super(EarlyAccessConfig, cls).__new__(cls, **defaults)

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    def getAffectedVehicles(self, seasonID):
        return self.seasons.get(seasonID, {}).get('affectedVehicles', {})

    def getBlockedVehicles(self, seasonID):
        return self.seasons.get(seasonID, {}).get('blockedVehicles', set())

    def getTokenCompensation(self, seasonID):
        return self.seasons.get(seasonID, {}).get('tokenCompensation', {})

    def getTokenCost(self, seasonID):
        return self.seasons.get(seasonID, {}).get('tokenCost', {})


class RandomBattlesConfig(namedtuple('RandomBattlesConfig', ('isEnabled', 'levels'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, levels=tuple())
        defaults.update(kwargs)
        return super(RandomBattlesConfig, cls).__new__(cls, **defaults)

    def getLevels(self):
        return self.levels

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class ModeSelectorConfig(namedtuple('ModeSelectorConfig', 'columnSettings')):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(columnSettings={})
        defaults.update(kwargs)
        return super(ModeSelectorConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()

    def isValid(self):
        if not isinstance(self.columnSettings, dict):
            return False
        if not all((isinstance(k, int) for k in self.columnSettings.keys())):
            return False
        return False if not all((isinstance(v, (tuple, list)) and len(v) == 2 and all((isinstance(i, int) for i in v)) for v in self.columnSettings.values())) else True


class ServerSettings(object):

    def __init__(self, serverSettings):
        self.onServerSettingsChange = Event()
        self.__serverSettings = {}
        self.__roamingSettings = RoamingSettings.defaults()
        self.__fileServerSettings = _FileServerSettings.defaults()
        self.__regionalSettings = _RegionalSettings.defaults()
        self.__eSportCurrentSeason = _ESportCurrentSeason.defaults()
        self.__wgcg = _Wgcg.defaults()
        self.__wgnp = _Wgnp.defaults()
        self.__uiLogging = _UILogging.defaults()
        self.__eula = _EULA.defaults()
        self.__clanProfile = _ClanProfile.defaults()
        self.__spgRedesignFeatures = _SpgRedesignFeatures.defaults()
        self.__strongholdSettings = _StrongholdSettings.defaults()
        self.__tournamentSettings = _TournamentSettings.defaults()
        self.__frontlineSettings = _FrontlineSettings.defaults()
        self.__bwHallOfFame = _BwHallOfFame.defaults()
        self.__bwShop = _BwShop()
        self.__rankedBattlesSettings = RankedBattlesConfig.defaults()
        self.__epicMetaGameSettings = _EpicMetaGameConfig()
        self.__adventCalendar = _AdventCalendarConfig()
        self.__epicGameSettings = EpicGameConfig()
        self.__unitAssemblerConfig = _UnitAssemblerConfig.defaults()
        self.__telecomConfig = _TelecomConfig.defaults()
        self.__squadPremiumBonus = _SquadPremiumBonus.defaults()
        self.__battlePassConfig = BattlePassConfig({})
        self.__crystalRewardsConfig = _crystalRewardsConfig()
        self.__reactiveCommunicationConfig = _ReactiveCommunicationConfig()
        self.__blueprintsConvertSaleConfig = _BlueprintsConvertSaleConfig()
        self.__bwProductCatalog = _BwProductCatalog()
        self.__vehiclePostProgressionConfig = VehiclePostProgressionConfig()
        self.__eventBattlesConfig = _EventBattlesConfig()
        self.__giftSystemConfig = GiftSystemConfig()
        self.__resourceWellConfig = ResourceWellConfig()
        self.__battleMattersConfig = _BattleMattersConfig()
        self.__collectiveGoalEntryPointConfig = _CollectiveGoalEntryPointConfig()
        self.__collectiveGoalMarathonsConfig = _CollectiveGoalMarathonsConfig()
        self.__peripheryRoutingConfig = PeripheryRoutingConfig()
        self.__comp7Config = Comp7Config()
        self.__comp7RanksConfig = Comp7RanksConfig()
        self.__comp7RewardsConfig = Comp7RewardsConfig()
        self.__personalReservesConfig = PersonalReservesConfig()
        self.__playLimitsConfig = PlayLimitsConfig()
        self.__preModerationConfig = PreModerationConfig()
        self.__guiLootBoxesConfig = _GuiLootBoxesConfig()
        self.__eventLootBoxesConfig = _EventLootBoxesConfig()
        self.__collectionsConfig = CollectionsConfig()
        self.__winbackConfig = WinbackConfig()
        self.__limitedUIConfig = _LimitedUIConfig()
        self.__referralProgramConfig = RPConfig()
        self.__restoreConfig = RestoreConfig()
        self.__versusAISettings = VersusAIConfig()
        self.__debutBoxesConfig = DebutBoxesConfig()
        self.__earlyAccessConfig = EarlyAccessConfig()
        self.__armoryYardSettings = ArmoryYardConfig.defaults()
        self.__randomBattlesConfig = RandomBattlesConfig()
        self.__modeSelectorConfig = ModeSelectorConfig()
        self.__schemaManager = getSchemaManager()
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
        if 'wgnp' in self.__serverSettings:
            self.__updateWgnp(self.__serverSettings)
        if Configs.UI_LOGGING.value in self.__serverSettings:
            self.__updateUILogging(self.__serverSettings)
        if 'eula_config' in self.__serverSettings:
            self.__updateEULA(self.__serverSettings)
        if 'clanProfile' in self.__serverSettings:
            self.__updateClanProfile(self.__serverSettings)
        if 'spgRedesignFeatures' in self.__serverSettings:
            self.__spgRedesignFeatures = makeTupleByDict(_SpgRedesignFeatures, self.__serverSettings['spgRedesignFeatures'])
        if 'strongholdSettings' in self.__serverSettings:
            settings = self.__serverSettings['strongholdSettings']
            self.__strongholdSettings = _StrongholdSettings(settings.get('wgshHostUrl', ''))
        if 'frontlineSettings' in self.__serverSettings:
            settings = self.__serverSettings['frontlineSettings']
            self.__frontlineSettings = _FrontlineSettings(settings.get('isEpicTrainingEnabled', True))
        if 'hallOfFame' in self.__serverSettings:
            self.__bwHallOfFame = makeTupleByDict(_BwHallOfFame, self.__serverSettings['hallOfFame'])
        if 'shop' in self.__serverSettings:
            self.__bwShop = makeTupleByDict(_BwShop, self.__serverSettings['shop'])
        if 'ranked_config' in self.__serverSettings:
            self.__rankedBattlesSettings = makeTupleByDict(RankedBattlesConfig, self.__serverSettings['ranked_config'])
        if 'advent_calendar_config' in self.__serverSettings:
            self.__adventCalendar = makeTupleByDict(_AdventCalendarConfig, self.__serverSettings['advent_calendar_config'])
        if 'epic_config' in self.__serverSettings:
            LOG_DEBUG('epic_config', self.__serverSettings['epic_config'])
            self.__epicMetaGameSettings = makeTupleByDict(_EpicMetaGameConfig, self.__serverSettings['epic_config']['epicMetaGame'])
            self.__epicGameSettings = makeTupleByDict(EpicGameConfig, self.__serverSettings['epic_config'])
        if 'unit_assembler_config' in self.__serverSettings:
            self.__unitAssemblerConfig = makeTupleByDict(_UnitAssemblerConfig, self.__serverSettings['unit_assembler_config'])
        if PremiumConfigs.PREM_SQUAD in self.__serverSettings:
            self.__squadPremiumBonus = _SquadPremiumBonus.create(self.__serverSettings[PremiumConfigs.PREM_SQUAD])
        if Configs.BATTLE_ROYALE_CONFIG.value in self.__serverSettings:
            LOG_DEBUG('battle_royale_config', self.__serverSettings[Configs.BATTLE_ROYALE_CONFIG.value])
            self.__battleRoyaleSettings = makeTupleByDict(BattleRoyaleConfig, self.__serverSettings[Configs.BATTLE_ROYALE_CONFIG.value])
        else:
            self.__battleRoyaleSettings = BattleRoyaleConfig.defaults()
        if Configs.VERSUS_AI_CONFIG.value in self.__serverSettings:
            self.__versusAISettings = makeTupleByDict(VersusAIConfig, self.__serverSettings[Configs.VERSUS_AI_CONFIG.value])
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
            self.__seniorityAwardsConfig = makeTupleByDict(SeniorityAwardsConfig, self.__serverSettings['seniority_awards_config'])
        else:
            self.__seniorityAwardsConfig = SeniorityAwardsConfig()
        if BATTLE_PASS_CONFIG_NAME in self.__serverSettings:
            self.__battlePassConfig = BattlePassConfig(self.__serverSettings.get(BATTLE_PASS_CONFIG_NAME, {}))
        else:
            self.__battlePassConfig = BattlePassConfig({})
        if _crystalRewardsConfig.CONFIG_NAME in self.__serverSettings:
            self.__crystalRewardsConfig = makeTupleByDict(_crystalRewardsConfig, self.__serverSettings[_crystalRewardsConfig.CONFIG_NAME])
        self.__updateReactiveCommunicationConfig(self.__serverSettings)
        self.__updateGuiLootBoxesConfig(self.__serverSettings)
        self.__updateEventLootBoxesConfig(self.__serverSettings)
        if BonusCapsConst.CONFIG_NAME in self.__serverSettings:
            BONUS_CAPS.OVERRIDE_BONUS_CAPS = self.__serverSettings[BonusCapsConst.CONFIG_NAME]
        else:
            BONUS_CAPS.OVERRIDE_BONUS_CAPS = dict()
        if 'blueprints_convert_sale_config' in self.__serverSettings:
            self.__blueprintsConvertSaleConfig = makeTupleByDict(_BlueprintsConvertSaleConfig, self.__serverSettings['blueprints_convert_sale_config'])
        else:
            self.__blueprintsConvertSaleConfig = _BlueprintsConvertSaleConfig()
        if Configs.MAPBOX_CONFIG.value in self.__serverSettings:
            LOG_DEBUG('mapbox_config', self.__serverSettings[Configs.MAPBOX_CONFIG.value])
            self.__mapboxSettings = makeTupleByDict(_MapboxConfig, self.__serverSettings[Configs.MAPBOX_CONFIG.value])
        else:
            self.__mapboxSettings = _MapboxConfig.defaults()
        if 'productsCatalog' in self.__serverSettings:
            self.__bwProductCatalog = makeTupleByDict(_BwProductCatalog, self.__serverSettings['productsCatalog'])
        if post_progression_common.SERVER_SETTINGS_KEY in self.__serverSettings:
            self.__vehiclePostProgressionConfig = makeTupleByDict(VehiclePostProgressionConfig, self.__serverSettings[post_progression_common.SERVER_SETTINGS_KEY])
        if 'event_battles_config' in self.__serverSettings:
            self.__eventBattlesConfig = makeTupleByDict(_EventBattlesConfig, self.__serverSettings['event_battles_config'])
        else:
            self.__eventBattlesConfig = _EventBattlesConfig.defaults()
        if Configs.GIFTS_CONFIG.value in self.__serverSettings:
            self.__giftSystemConfig = makeTupleByDict(GiftSystemConfig, {'events': self.__serverSettings[Configs.GIFTS_CONFIG.value]})
        if Configs.RESOURCE_WELL.value in self.__serverSettings:
            self.__resourceWellConfig = makeTupleByDict(ResourceWellConfig, self.__serverSettings[Configs.RESOURCE_WELL.value])
        if Configs.BATTLE_MATTERS_CONFIG.value in self.__serverSettings:
            self.__battleMattersConfig = makeTupleByDict(_BattleMattersConfig, self.__serverSettings[Configs.BATTLE_MATTERS_CONFIG.value])
        if Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value in self.__serverSettings:
            self.__collectiveGoalEntryPointConfig = makeTupleByDict(_CollectiveGoalEntryPointConfig, self.__serverSettings[Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value])
        if Configs.COLLECTIVE_GOAL_MARATHONS_CONFIG.value in self.__serverSettings:
            self.__collectiveGoalMarathonsConfig = makeTupleByDict(_CollectiveGoalMarathonsConfig, self.__serverSettings[Configs.COLLECTIVE_GOAL_MARATHONS_CONFIG.value])
        if Configs.PERIPHERY_ROUTING_CONFIG.value in self.__serverSettings:
            self.__peripheryRoutingConfig = makeTupleByDict(PeripheryRoutingConfig, self.__serverSettings[Configs.PERIPHERY_ROUTING_CONFIG.value])
        if Configs.COMP7_CONFIG.value in self.__serverSettings:
            LOG_DEBUG(Configs.COMP7_CONFIG.value, self.__serverSettings[Configs.COMP7_CONFIG.value])
            self.__comp7Config = makeTupleByDict(Comp7Config, self.__serverSettings[Configs.COMP7_CONFIG.value])
        else:
            self.__comp7Config = Comp7Config.defaults()
        if Configs.COMP7_RANKS_CONFIG.value in self.__serverSettings:
            LOG_DEBUG(Configs.COMP7_RANKS_CONFIG.value, self.__serverSettings[Configs.COMP7_RANKS_CONFIG.value])
            self.__comp7RanksConfig = makeTupleByDict(Comp7RanksConfig, self.__serverSettings[Configs.COMP7_RANKS_CONFIG.value])
        else:
            self.__comp7RanksConfig = Comp7RanksConfig.defaults()
        if Configs.COMP7_REWARDS_CONFIG.value in self.__serverSettings:
            LOG_DEBUG(Configs.COMP7_REWARDS_CONFIG.value, self.__serverSettings[Configs.COMP7_REWARDS_CONFIG.value])
            self.__comp7RewardsConfig = makeTupleByDict(Comp7RewardsConfig, self.__serverSettings[Configs.COMP7_REWARDS_CONFIG.value])
        else:
            self.__comp7RewardsConfig = Comp7RewardsConfig.defaults()
        if Configs.PERSONAL_RESERVES_CONFIG.value in self.__serverSettings:
            self.__personalReservesConfig = makeTupleByDict(PersonalReservesConfig, self.__serverSettings[Configs.PERSONAL_RESERVES_CONFIG.value])
        else:
            self.__personalReservesConfig = PersonalReservesConfig.defaults()
        if Configs.PLAY_LIMITS_CONFIG.value in self.__serverSettings:
            self.__playLimitsConfig = makeTupleByDict(PlayLimitsConfig, self.__serverSettings[Configs.PLAY_LIMITS_CONFIG.value])
        if Configs.PRE_MODERATION_CONFIG.value in self.__serverSettings:
            self.__preModerationConfig = makeTupleByDict(PreModerationConfig, self.__serverSettings[Configs.PRE_MODERATION_CONFIG.value])
        else:
            self.__preModerationConfig = PreModerationConfig.defaults()
        if TOURNAMENT_CONFIG in self.__serverSettings:
            self.__tournamentSettings = makeTupleByDict(_TournamentSettings, self.__serverSettings[TOURNAMENT_CONFIG])
        else:
            self.__tournamentSettings = _TournamentSettings.defaults()
        if Configs.COLLECTIONS_CONFIG.value in self.__serverSettings:
            self.__collectionsConfig = makeTupleByDict(CollectionsConfig, self.__serverSettings[Configs.COLLECTIONS_CONFIG.value])
        if Configs.WINBACK_CONFIG.value in self.__serverSettings:
            _logger.info(Configs.WINBACK_CONFIG.value, self.__serverSettings[Configs.WINBACK_CONFIG.value])
            self.__winbackConfig = makeTupleByDict(WinbackConfig, self.__serverSettings[Configs.WINBACK_CONFIG.value])
        else:
            self.__winbackConfig = WinbackConfig.defaults()
        if Configs.ARMORY_YARD_CONFIG.value in self.__serverSettings:
            self.__armoryYardSettings = makeTupleByDict(ArmoryYardConfig, self.__serverSettings[Configs.ARMORY_YARD_CONFIG.value])
        else:
            self.__armoryYardSettings = ArmoryYardConfig.defaults()
        if Configs.LIMITED_UI_CONFIG.value in self.__serverSettings:
            self.__limitedUIConfig = makeTupleByDict(_LimitedUIConfig, self.__serverSettings[Configs.LIMITED_UI_CONFIG.value])
        else:
            self.__limitedUIConfig = _LimitedUIConfig.defaults()
        if Configs.REFERRAL_PROGRAM_CONFIG.value in self.__serverSettings:
            self.__referralProgramConfig = makeTupleByDict(RPConfig, self.__serverSettings[Configs.REFERRAL_PROGRAM_CONFIG.value])
        else:
            self.__referralProgramConfig = RPConfig.defaults()
        if Configs.RESTORE_CONFIG.value in self.__serverSettings:
            self.__restoreConfig = makeTupleByDict(RestoreConfig, self.__serverSettings[Configs.RESTORE_CONFIG.value])
        if Configs.DEBUT_BOXES_CONFIG.value in self.__serverSettings:
            self.__debutBoxesConfig = makeTupleByDict(DebutBoxesConfig, self.__serverSettings[Configs.DEBUT_BOXES_CONFIG.value])
        else:
            self.__debutBoxesConfig = DebutBoxesConfig.defaults()
        if Configs.EARLY_ACCESS_CONFIG.value in self.__serverSettings:
            self.__earlyAccessConfig = makeTupleByDict(EarlyAccessConfig, self.__serverSettings[Configs.EARLY_ACCESS_CONFIG.value])
        if Configs.RANDOM_BATTLES_CONFIG.value in self.__serverSettings:
            self.__randomBattlesConfig = makeTupleByDict(RandomBattlesConfig, self.__serverSettings[Configs.RANDOM_BATTLES_CONFIG.value])
        if Configs.MODE_SELECTOR_CONFIG.value in self.__serverSettings:
            self.__modeSelectorConfig = makeTupleByDict(ModeSelectorConfig, self.__serverSettings[Configs.MODE_SELECTOR_CONFIG.value])
        else:
            self.__modeSelectorConfig = ModeSelectorConfig.defaults()
        self.__schemaManager.set(self.__serverSettings)
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
        if 'wgnp' in serverSettingsDiff:
            self.__updateWgnp(serverSettingsDiff)
        if Configs.UI_LOGGING.value in serverSettingsDiff:
            self.__updateUILogging(serverSettingsDiff)
        if 'eula_config' in serverSettingsDiff:
            self.__updateEULA(serverSettingsDiff)
        if 'advent_calendar_config' in serverSettingsDiff:
            self.__updateAdventCalendar(serverSettingsDiff)
            self.__serverSettings['advent_calendar_config'] = serverSettingsDiff['advent_calendar_config']
        if 'epic_config' in serverSettingsDiff:
            self.__updateEpic(serverSettingsDiff)
            self.__serverSettings['epic_config'] = serverSettingsDiff['epic_config']
        if Configs.BATTLE_ROYALE_CONFIG.value in serverSettingsDiff:
            self.__updateBattleRoyale(serverSettingsDiff)
        if Configs.MAPBOX_CONFIG.value in serverSettingsDiff:
            self.__updateMapbox(serverSettingsDiff)
        if 'unit_assembler_config' in serverSettingsDiff:
            self.__updateUnitAssemblerConfig(serverSettingsDiff)
            self.__serverSettings['unit_assembler_config'] = serverSettingsDiff['unit_assembler_config']
        if 'comp7_config' in serverSettingsDiff:
            self.__updateComp7(serverSettingsDiff)
        if Configs.COMP7_RANKS_CONFIG.value in serverSettingsDiff:
            self.__updateComp7PrestigeRanks(serverSettingsDiff)
        if Configs.COMP7_REWARDS_CONFIG.value in serverSettingsDiff:
            self.__updateComp7Rewards(serverSettingsDiff)
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
        if 'event_battles_config' in serverSettingsDiff:
            self.__updateEventBattles(serverSettingsDiff)
        if BonusCapsConst.CONFIG_NAME in serverSettingsDiff:
            BONUS_CAPS.OVERRIDE_BONUS_CAPS = serverSettingsDiff[BonusCapsConst.CONFIG_NAME]
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
            self.__crystalRewardsConfig = makeTupleByDict(_crystalRewardsConfig, serverSettingsDiff[_crystalRewardsConfig.CONFIG_NAME])
        if post_progression_common.SERVER_SETTINGS_KEY in serverSettingsDiff:
            self.__updateVehiclePostProgressionConfig(serverSettingsDiff)
        if Configs.GIFTS_CONFIG.value in serverSettingsDiff:
            self.__updateGiftSystemConfig(serverSettingsDiff)
        if Configs.BATTLE_MATTERS_CONFIG.value in serverSettingsDiff:
            self.__updateBattleMatters(serverSettingsDiff)
        if TRADE_IN_CONFIG_NAME in serverSettingsDiff:
            self.__serverSettings[TRADE_IN_CONFIG_NAME] = serverSettingsDiff[TRADE_IN_CONFIG_NAME]
        if Configs.RESOURCE_WELL.value in serverSettingsDiff:
            self.__updateResourceWellConfig(serverSettingsDiff)
        if Configs.PERIPHERY_ROUTING_CONFIG.value in serverSettingsDiff:
            self.__updatePeripheryRoutingConfig(serverSettingsDiff)
        if Configs.PLAY_LIMITS_CONFIG.value in serverSettingsDiff:
            self.__updatePlayLimitsConfig(serverSettingsDiff)
        if Configs.PRE_MODERATION_CONFIG.value in serverSettingsDiff:
            self.__updatePreModerationConfig(serverSettingsDiff)
        if TOURNAMENT_CONFIG in serverSettingsDiff:
            self.__updateTournamentsConfig(serverSettingsDiff)
        self.__updateBlueprintsConvertSaleConfig(serverSettingsDiff)
        self.__updateReactiveCommunicationConfig(serverSettingsDiff)
        if Configs.CUSTOMIZATION_QUESTS.value in serverSettingsDiff:
            key = Configs.CUSTOMIZATION_QUESTS.value
            self.__serverSettings[key] = serverSettingsDiff[key]
        if Configs.WINBACK_CONFIG.value in serverSettingsDiff:
            self.__updateWinbackConfig(serverSettingsDiff)
        if Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value in serverSettingsDiff:
            self.__updateCollectiveGoalEntryPointConfig(serverSettingsDiff)
        if Configs.COLLECTIVE_GOAL_MARATHONS_CONFIG.value in serverSettingsDiff:
            self.__updateCollectiveGoalMarathonsConfig(serverSettingsDiff)
        if Configs.ARMORY_YARD_CONFIG.value in serverSettingsDiff:
            self.__updateArmoryYard(serverSettingsDiff)
        if Configs.REFERRAL_PROGRAM_CONFIG.value in serverSettingsDiff:
            self.__updateRPConfig(serverSettingsDiff)
        if Configs.VERSUS_AI_CONFIG.value in serverSettingsDiff:
            self.__updateVersusAI(serverSettingsDiff)
        self.__updatePersonalReserves(serverSettingsDiff)
        self.__updateGuiLootBoxesConfig(serverSettingsDiff)
        self.__updateEventLootBoxesConfig(serverSettingsDiff)
        if Configs.COLLECTIONS_CONFIG.value in serverSettingsDiff:
            self.__updateCollectionsConfig(serverSettingsDiff)
        self.__updateLimitedUIConfig(serverSettingsDiff)
        if Configs.RESTORE_CONFIG.value in serverSettingsDiff:
            self.__updateRestoreConfig(serverSettingsDiff)
        if Configs.DEBUT_BOXES_CONFIG.value in serverSettingsDiff:
            self.__updateDebutBoxesConfig(serverSettingsDiff)
        if Configs.EARLY_ACCESS_CONFIG.value in serverSettingsDiff:
            self.__updateEarlyAccessConfig(serverSettingsDiff)
        if Configs.MODE_SELECTOR_CONFIG.value in serverSettingsDiff:
            self.__updateModeSelectorConfig(serverSettingsDiff)
        lbKeyConfig = Configs.LOOTBOX_KEYS_CONFIG.value
        if lbKeyConfig in serverSettingsDiff:
            self.__serverSettings[lbKeyConfig] = serverSettingsDiff[lbKeyConfig]
        if Configs.RANDOM_BATTLES_CONFIG.value in serverSettingsDiff:
            self.__updateRandomBattlesConfig(serverSettingsDiff)
        self.__schemaManager.update(serverSettingsDiff)
        self.onServerSettingsChange(serverSettingsDiff)

    def clear(self):
        self.__schemaManager.clear()
        self.onServerSettingsChange.clear()

    def getSettings(self):
        return self.__serverSettings

    def getConfigModel(self, schema):
        configModel = self.__schemaManager.get(schema)
        if configModel is None:
            raise SoftException('Schema %s was not registered. All schemas must be registered before ServerSettings inited.', schema.gpKey)
        return configModel

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
    def wgnp(self):
        return self.__wgnp

    @property
    def uiLogging(self):
        return self.__uiLogging

    @property
    def eula(self):
        return self.__eula

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
    def bwHallOfFame(self):
        return self.__bwHallOfFame

    @property
    def rankedBattles(self):
        return self.__rankedBattlesSettings

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
    def mapbox(self):
        return self.__mapboxSettings

    @property
    def unitAssemblerConfig(self):
        return self.__unitAssemblerConfig

    @property
    def comp7Config(self):
        return self.__comp7Config

    @property
    def comp7RanksConfig(self):
        return self.__comp7RanksConfig

    @property
    def comp7RewardsConfig(self):
        return self.__comp7RewardsConfig

    @property
    def telecomConfig(self):
        return self.__telecomConfig

    @property
    def blueprintsConfig(self):
        return self.__blueprintsConfig

    @property
    def squadPremiumBonus(self):
        return self.__squadPremiumBonus

    @property
    def vehiclePostProgression(self):
        return self.__vehiclePostProgressionConfig

    @property
    def eventBattlesConfig(self):
        return self.__eventBattlesConfig

    @property
    def giftSystemConfig(self):
        return self.__giftSystemConfig

    @property
    def resourceWellConfig(self):
        return self.__resourceWellConfig

    @property
    def playLimitsConfig(self):
        return self.__playLimitsConfig

    @property
    def battleMattersConfig(self):
        return self.__battleMattersConfig

    @property
    def collectiveGoalEntryPointConfig(self):
        return self.__collectiveGoalEntryPointConfig

    @property
    def collectiveGoalMarathonsConfig(self):
        return self.__collectiveGoalMarathonsConfig

    @property
    def peripheryRoutingConfig(self):
        return self.__peripheryRoutingConfig

    @property
    def personalReservesConfig(self):
        return self.__personalReservesConfig

    @property
    def preModerationConfig(self):
        return self.__preModerationConfig

    @property
    def collectionsConfig(self):
        return self.__collectionsConfig

    @property
    def winbackConfig(self):
        return self.__winbackConfig

    @property
    def armoryYard(self):
        return self.__armoryYardSettings

    @property
    def limitedUIConfig(self):
        return self.__limitedUIConfig

    @property
    def restoreConfig(self):
        return self.__restoreConfig

    @property
    def versusAIConfig(self):
        return self.__versusAISettings

    @property
    def debutBoxesConfig(self):
        return self.__debutBoxesConfig

    @property
    def earlyAccessConfig(self):
        return self.__earlyAccessConfig

    @property
    def randomBattlesConfig(self):
        return self.__randomBattlesConfig

    @property
    def modeSelectorConfig(self):
        return self.__modeSelectorConfig

    def isEpicBattleEnabled(self):
        return self.epicBattles.isEnabled

    def isPersonalMissionsEnabled(self, branch=None):
        if branch == PM_BRANCH.REGULAR:
            return self.__getGlobalSetting('isRegularQuestEnabled', True)
        return self.__getGlobalSetting('isPM2QuestEnabled', True) if branch == PM_BRANCH.PERSONAL_MISSION_2 else self.__getGlobalSetting('isRegularQuestEnabled', True) or self.__getGlobalSetting('isPM2QuestEnabled', True)

    def isPMBattleProgressEnabled(self):
        return self.__getGlobalSetting('isPMBattleProgressEnabled', True)

    def isStaticWeatherSwitchEnabled(self):
        return self.__getGlobalSetting('isStaticWeatherSwitchEnabled', True)

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

    def isWTREnabled(self):
        wtrSettings = self.__getGlobalSetting('sessionStats', {}).get('WTR', {})
        return wtrSettings.get('enabled', False)

    def isNationChangeEnabled(self):
        return self.__getGlobalSetting('isNationChangeEnabled', True)

    def getCrystalRewardConfig(self):
        return self.__crystalRewardsConfig

    @property
    def shop(self):
        return self.__bwShop

    @property
    def productCatalog(self):
        return self.__bwProductCatalog

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

    def isBootcampEnabled(self):
        return self.__getGlobalSetting('isBootcampEnabled', False)

    def getBootcampBonuses(self):
        return self.__getGlobalSetting('bootcampBonuses', {})

    def isMapsTrainingEnabled(self):
        return self.__getGlobalSetting('isMapsTrainingEnabled', False)

    def recertificationFormState(self):
        return self.__getGlobalSetting('recertificationFormState', constants.SwitchState.DISABLED.value)

    def getLootBoxConfig(self):
        return self.__getGlobalSetting('lootBoxes_config', {})

    def getLootBoxKeyConfig(self):
        return self.__getGlobalSetting(Configs.LOOTBOX_KEYS_CONFIG.value, {})

    def getPiggyBankConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PIGGYBANK, {})

    def getAdditionalBonusConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.DAILY_BONUS, {})

    def getPremQuestsConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PREM_QUESTS, {})

    def getDailyQuestConfig(self):
        return self.__getGlobalSetting(DAILY_QUESTS_CONFIG, {})

    def getDogTagsConfig(self):
        return self.__getGlobalSetting(DOG_TAGS_CONFIG, {})

    def getCustomizationQuestsConfig(self):
        return self.__getGlobalSetting(Configs.CUSTOMIZATION_QUESTS.value, {})

    def isDogTagEnabled(self):
        return self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enabled', True)

    def isDogTagCustomizationScreenEnabled(self):
        return self.isDogTagEnabled() and self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enableDogTagsCustomizationScreen', True)

    def isSkillComponentsEnabled(self):
        return self.isDogTagEnabled() and self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enableSkillComponents', True)

    def isDogTagInBattleEnabled(self):
        return self.isDogTagEnabled() and self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enableDogTagsInBattle', True)

    def isDogTagInPostBattleEnabled(self):
        return self.isDogTagEnabled() and self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enableDogTagsInPostBattle', True)

    def isDogTagComponentUnlockingEnabled(self):
        return self.isDogTagEnabled() and self.__getGlobalSetting(DOG_TAGS_CONFIG, {}).get('enableComponentUnlocking', True)

    def isRenewableSubEnabled(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enabled', False)

    def isWotPlusEnabledForSteam(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enabledForSteam', False)

    def isRenewableSubGoldReserveEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableGoldReserve', False)

    def isRenewableSubPassiveCrewXPEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enablePassiveCrewXP', False)

    def isWotPlusExcludedMapEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableExcludedMap', False)

    def isWoTPlusExclusiveVehicleEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableWoTPlusExclusiveVehicle', False)

    def isFreeEquipmentDemountingEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableFreeEquipmentDemounting', False)

    def isFreeDeluxeEquipmentDemountingEnabled(self):
        return self.isFreeEquipmentDemountingEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableFreeDeluxeEquipmentDemounting', False)

    def isDailyAttendancesEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableDailyAttendances', False)

    def isDailyQuestsExtraRewardsEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableDailyQuestsExtraRewards', False)

    def isTeamCreditsBonusEnabled(self):
        return self.isRenewableSubEnabled() and self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('enableTeamCreditsBonus', False)

    def getWotPlusExclusiveVehicleInfo(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('exclusiveVehicle', {})

    def getDailyAttendanceQuestPrefix(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('dailyAttendanceQuestPrefix', '')

    def getRenewableSubCrewXPPerMinute(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('crewXPPerMinute', 0)

    def getRenewableSubMaxGoldReserveCapacity(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('maxGoldReserveCapacity', 0)

    def getArenaTypesWithGoldReserve(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get(GOLD_RESERVE_GAINS_SECTION, {}).keys()

    def getWotPlusProductCode(self):
        return self.__getGlobalSetting(RENEWABLE_SUBSCRIPTION_CONFIG, {}).get('subscriptionProductCode', 'subscription_dev')

    def isTelecomRentalsEnabled(self):
        return self.__getGlobalSetting(TELECOM_RENTALS_CONFIG, {}).get('enabled', True)

    def isPlayerSubscriptionsEnabled(self):
        return self.__getGlobalSetting(PLAYER_SUBSCRIPTIONS_CONFIG, {}).get('enabled', True)

    def isPlayerSubscriptionsEntrypointHidden(self):
        return not self.isPlayerSubscriptionsEnabled() and self.__getGlobalSetting(PLAYER_SUBSCRIPTIONS_CONFIG, {}).get('hideEntrypoint', False)

    def isBattleNotifierEnabled(self):
        return self.__getGlobalSetting(BATTLE_NOTIFIER_CONFIG, {}).get('enabled', False)

    def isAutoSellCheckBoxEnabled(self):
        return self.getMiscGUISettings().get('buyModuleDialog', {}).get('enableAutoSellCheckBox', False)

    def getMiscGUISettings(self):
        return self.__getGlobalSetting(MISC_GUI_SETTINGS, {})

    def getMagneticAutoAimConfig(self):
        return self.__getGlobalSetting(MAGNETIC_AUTO_AIM_CONFIG, {})

    def getPreferredMapsConfig(self):
        return self.__getGlobalSetting(PremiumConfigs.PREFERRED_MAPS, {})

    def getPremiumPlusXPBonus(self):
        battleBonuses = self.__getGlobalSetting('prem_battle_bonuses', {})
        return battleBonuses.get(PREM_BONUS_TYPES.XP, {}).get(ENTITLEMENT_TO_PREM_TYPE[PREMIUM_ENTITLEMENTS.PLUS], 0)

    def getPremiumPlusCreditsBonus(self):
        battleBonuses = self.__getGlobalSetting('prem_battle_bonuses', {})
        return battleBonuses.get(PREM_BONUS_TYPES.CREDITS, {}).get(ENTITLEMENT_TO_PREM_TYPE[PREMIUM_ENTITLEMENTS.PLUS], 0)

    def getPremiumPlusTmenXPBonus(self):
        battleBonuses = self.__getGlobalSetting('prem_battle_bonuses', {})
        return battleBonuses.get(PREM_BONUS_TYPES.TMEN_XP, {}).get(ENTITLEMENT_TO_PREM_TYPE[PREMIUM_ENTITLEMENTS.PLUS], 0)

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

    def isOnly10ModeEnabled(self):
        return self.__getGlobalSetting('isOnly10ModeEnabled', False)

    def isMapsInDevelopmentEnabled(self):
        mapsInDevCongig = self.__getGlobalSetting(Configs.MAPS_IN_DEVELOPMENT_CONFIG.value, None)
        return bool(mapsInDevCongig['isEnabled']) if mapsInDevCongig else False

    def getMaxSPGinSquads(self):
        return self.__getGlobalSetting('maxSPGinSquads', 0)

    def getMaxScoutInSquads(self):
        return self.__getGlobalSetting('maxScoutInSquads', 0)

    def getMaxScoutInSquadsLevels(self):
        return self.__getGlobalSetting('maxScoutInSquadsLevels', [])

    def getPossibleSquadsVehicleLevels(self):
        return self.__getGlobalSetting('possibleSquadsVehicleLevels', [])

    def getRandomMapsForDemonstrator(self):
        return self.__getGlobalSetting('randomMapsForDemonstrator', {})

    def getRandomBattleLevelsForDemonstrator(self):
        return self.__getGlobalSetting('randomBattleLevelsForDemonstrator', {})

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

    def getPremiumXPBonus(self):
        return self.__getGlobalSetting('tankPremiumBonus', {}).get('xp', 0.5)

    def getPremiumCreditsBonus(self):
        return self.__getGlobalSetting('tankPremiumBonus', {}).get('credits', 0.5)

    def isPreferredMapsEnabled(self):
        return self.__getGlobalSetting('isPreferredMapsEnabled', False)

    def isGlobalMapEnabled(self):
        return self.__getGlobalSetting('isGlobalMapEnabled', False)

    def isBattleBoostersEnabled(self):
        return self.__getGlobalSetting('isBattleBoostersEnabled', False)

    def isCrewBooksPurchaseEnabled(self):
        return self.__getGlobalSetting('isCrewBooksPurchaseEnabled', False)

    def isCrewBooksSaleEnabled(self):
        return self.__getGlobalSetting('isCrewBooksSaleEnabled', False)

    def isTrophyDevicesEnabled(self):
        return self.__getGlobalSetting('isTrophyDevicesEnabled', False)

    def isTrainingBattleEnabled(self):
        return self.__getGlobalSetting('isTrainingBattleEnabled', False)

    def isCollectorVehicleEnabled(self):
        return self.__getGlobalSetting(CollectorVehicleConsts.CONFIG_NAME, {}).get(CollectorVehicleConsts.IS_ENABLED, False)

    def isOffersEnabled(self):
        return self.__getGlobalSetting(constants.OFFERS_ENABLED_KEY, False)

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

    def getReactiveCommunicationConfig(self):
        return self.__reactiveCommunicationConfig

    def isLegacyModeSelectorEnabled(self):
        return self.__getGlobalSetting('isLegacyModeSelectorEnabled', False)

    def getBlueprintsConvertSaleConfig(self):
        return self.__blueprintsConvertSaleConfig

    def getActiveTestConfirmationConfig(self):
        return self.__getGlobalSetting(constants.ACTIVE_TEST_CONFIRMATION_CONFIG, {})

    def getTradeInConfig(self):
        return self.__getGlobalSetting(TRADE_IN_CONFIG_NAME, {})

    def getGuiLootBoxesConfig(self):
        return self.__guiLootBoxesConfig

    def getEventLootBoxesConfig(self):
        return self.__eventLootBoxesConfig

    def getAchievements20GeneralConfig(self):
        return Achievements20GeneralConfig(self.__getGlobalSetting(Configs.ACHIEVEMENTS20_CONFIG.value, {}))

    def getRPConfig(self):
        return self.__referralProgramConfig

    def __getGlobalSetting(self, settingsName, default=None):
        return self.__serverSettings.get(settingsName, default)

    def __updateClanProfile(self, targetSettings):
        cProfile = targetSettings['clanProfile']
        self.__clanProfile = _ClanProfile(cProfile.get('isEnabled', False))

    def __updateWgcg(self, targetSettings):
        cProfile = targetSettings['wgcg']
        self.__wgcg = _Wgcg(cProfile.get('isEnabled', False), cProfile.get('gateUrl', ''), cProfile.get('type', 'gateway'), cProfile.get('loginOnStart', False), cProfile.get('isJwtAuthorizationEnabled', True))

    def __updateWgnp(self, targetSettings):
        cProfile = targetSettings['wgnp']
        self.__wgnp = _Wgnp(cProfile.get('enabled', False), cProfile.get('url', ''), cProfile.get('renameApiEnabled', False))

    def __updateUILogging(self, targetSettings):
        settings = targetSettings[Configs.UI_LOGGING.value]
        self.__uiLogging = _UILogging(settings.get('enabled', False))

    def __updateEULA(self, targetSettings):
        cProfile = targetSettings['eula_config']
        self.__eula = _EULA(cProfile.get('enabled', False), cProfile.get('demoAccEnabled', False), cProfile.get('steamAccEnabled', False))

    def __updateAdventCalendar(self, targetSettings):
        self.__adventCalendar = self.__adventCalendar.replace(targetSettings['advent_calendar_config'])

    def __updateRanked(self, targetSettings):
        self.__rankedBattlesSettings = self.__rankedBattlesSettings.replace(targetSettings['ranked_config'])

    def __updateEpic(self, targetSettings):
        self.__epicMetaGameSettings = self.__epicMetaGameSettings.replace(targetSettings['epic_config'].get('epicMetaGame', {}))
        self.__epicGameSettings = self.__epicGameSettings.replace(targetSettings['epic_config'])

    def __updateUnitAssemblerConfig(self, targetSettings):
        self.__unitAssemblerConfig = self.__unitAssemblerConfig.replace(targetSettings['unit_assembler_config'])

    def __updateComp7(self, targetSettings):
        config = targetSettings[Configs.COMP7_CONFIG.value]
        self.__comp7Config = self.__comp7Config.replace(copy.deepcopy(config))

    def __updateComp7PrestigeRanks(self, targetSettings):
        config = targetSettings[Configs.COMP7_RANKS_CONFIG.value]
        self.__comp7RanksConfig = self.__comp7RanksConfig.replace(copy.deepcopy(config))

    def __updateComp7Rewards(self, targetSettings):
        config = targetSettings[Configs.COMP7_REWARDS_CONFIG.value]
        self.__comp7RewardsConfig = self.__comp7RewardsConfig.replace(config)

    def __updateSquadBonus(self, sourceSettings):
        self.__squadPremiumBonus = self.__squadPremiumBonus.replace(sourceSettings[PremiumConfigs.PREM_SQUAD])

    def __updateShop(self, targetSettings):
        self.__bwShop = self.__bwShop.replace(targetSettings['shop'])

    def __updateBattleRoyale(self, targetSettings):
        data = targetSettings[Configs.BATTLE_ROYALE_CONFIG.value]
        self.__battleRoyaleSettings = self.__battleRoyaleSettings.replace(data)

    def __updateMapbox(self, targetSettings):
        self.__mapboxSettings = self.__mapboxSettings.replace(targetSettings[Configs.MAPBOX_CONFIG.value])

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

    def __updateReactiveCommunicationConfig(self, settings):
        if 'reactiveCommunicationConfig' in settings:
            config = settings['reactiveCommunicationConfig']
            if config is None:
                self.__reactiveCommunicationConfig = _ReactiveCommunicationConfig()
            elif isinstance(config, dict):
                self.__reactiveCommunicationConfig = _ReactiveCommunicationConfig(**config)
            else:
                _logger.error('Unexpected format of subscriptions service config: %r', config)
                self.__reactiveCommunicationConfig = _ReactiveCommunicationConfig()
        return

    def __updateBlueprintsConvertSaleConfig(self, targetSettings):
        if 'blueprints_convert_sale_config' in targetSettings:
            self.__blueprintsConvertSaleConfig = self.__blueprintsConvertSaleConfig.replace(targetSettings['blueprints_convert_sale_config'])

    def __updateVehiclePostProgressionConfig(self, serverSettingsDiff):
        self.__vehiclePostProgressionConfig = self.__vehiclePostProgressionConfig.replace(serverSettingsDiff[post_progression_common.SERVER_SETTINGS_KEY])

    def __updateEventBattles(self, targetSettings):
        self.__eventBattlesConfig = self.__eventBattlesConfig.replace(targetSettings['event_battles_config'])

    def __updateGiftSystemConfig(self, serverSettingsDiff):
        self.__giftSystemConfig = self.__giftSystemConfig.replace({'events': serverSettingsDiff[Configs.GIFTS_CONFIG.value]})

    def __updateResourceWellConfig(self, diff):
        self.__resourceWellConfig = self.__resourceWellConfig.replace(diff[Configs.RESOURCE_WELL.value])

    def __updatePlayLimitsConfig(self, serverSettingsDiff):
        self.__playLimitsConfig = self.__playLimitsConfig.replace(serverSettingsDiff[Configs.PLAY_LIMITS_CONFIG.value])

    def __updateBattleMatters(self, targetSettings):
        self.__battleMattersConfig = self.__battleMattersConfig.replace(targetSettings[Configs.BATTLE_MATTERS_CONFIG.value])

    def __updateCollectiveGoalEntryPointConfig(self, diff):
        self.__collectiveGoalEntryPointConfig = self.__collectiveGoalEntryPointConfig.replace(diff[Configs.COLLECTIVE_GOAL_ENTRY_POINT_CONFIG.value])

    def __updateCollectiveGoalMarathonsConfig(self, diff):
        self.__collectiveGoalMarathonsConfig = self.__collectiveGoalMarathonsConfig.replace(diff[Configs.COLLECTIVE_GOAL_MARATHONS_CONFIG.value])

    def __updatePeripheryRoutingConfig(self, diff):
        self.__peripheryRoutingConfig = self.__peripheryRoutingConfig.replace(diff[Configs.PERIPHERY_ROUTING_CONFIG.value])

    def __updatePersonalReserves(self, serverSettingsDiff):
        if Configs.PERSONAL_RESERVES_CONFIG.value in serverSettingsDiff:
            self.__personalReservesConfig = self.__personalReservesConfig.replace(serverSettingsDiff[Configs.PERSONAL_RESERVES_CONFIG.value])

    def __updatePreModerationConfig(self, serverSettingsDiff):
        if Configs.PRE_MODERATION_CONFIG.value in serverSettingsDiff:
            self.__preModerationConfig = self.__preModerationConfig.replace(serverSettingsDiff[Configs.PRE_MODERATION_CONFIG.value])

    def __updateTournamentsConfig(self, diff):
        self.__tournamentSettings = self.__tournamentSettings.replace(diff[TOURNAMENT_CONFIG])

    def __updateGuiLootBoxesConfig(self, settings):
        if GUI_LOOT_BOXES_CONFIG in settings:
            config = settings[GUI_LOOT_BOXES_CONFIG]
            if config is None:
                self.__guiLootBoxesConfig = _GuiLootBoxesConfig()
            elif isinstance(config, dict):
                self.__guiLootBoxesConfig = _GuiLootBoxesConfig(**config)
            else:
                _logger.error('Unexpected format of subscriptions service config: %r', config)
                self.__guiLootBoxesConfig = _GuiLootBoxesConfig()
        return

    def __updateEventLootBoxesConfig(self, settings):
        if EVENT_LOOT_BOXES_CONFIG in settings:
            config = settings[EVENT_LOOT_BOXES_CONFIG]
            if config is None:
                self.__eventLootBoxesConfig = _EventLootBoxesConfig()
            elif isinstance(config, dict):
                self.__eventLootBoxesConfig = _EventLootBoxesConfig(**config)
            else:
                _logger.error('Unexpected format of subscriptions service config: %r', config)
                self.__eventLootBoxesConfig = _EventLootBoxesConfig()
        return

    def __updateCollectionsConfig(self, diff):
        self.__collectionsConfig = self.__collectionsConfig.replace(diff[Configs.COLLECTIONS_CONFIG.value])

    def __updateRPConfig(self, diff):
        self.__referralProgramConfig = self.__referralProgramConfig.replace(diff[Configs.REFERRAL_PROGRAM_CONFIG.value])

    def __updateWinbackConfig(self, diff):
        self.__winbackConfig = self.__winbackConfig.replace(diff[Configs.WINBACK_CONFIG.value])

    def __updateArmoryYard(self, diff):
        self.__armoryYardSettings = self.__armoryYardSettings.replace(diff[Configs.ARMORY_YARD_CONFIG.value])

    def __updateLimitedUIConfig(self, serverSettingsDiff):
        if Configs.LIMITED_UI_CONFIG.value in serverSettingsDiff:
            self.__limitedUIConfig = self.__limitedUIConfig.replace(serverSettingsDiff[Configs.LIMITED_UI_CONFIG.value])

    def __updateRestoreConfig(self, serverSettingsDiff):
        self.__restoreConfig = self.__restoreConfig.replace(serverSettingsDiff[Configs.RESTORE_CONFIG.value])

    def __updateDebutBoxesConfig(self, diff):
        self.__debutBoxesConfig = self.__debutBoxesConfig.replace(diff[Configs.DEBUT_BOXES_CONFIG.value])

    def __updateVersusAI(self, targetSettings):
        data = targetSettings[Configs.VERSUS_AI_CONFIG.value]
        self.__versusAISettings = self.__versusAISettings.replace(data)

    def __updateEarlyAccessConfig(self, diff):
        self.__earlyAccessConfig = self.__earlyAccessConfig.replace(diff[Configs.EARLY_ACCESS_CONFIG.value])

    def __updateRandomBattlesConfig(self, diff):
        self.__randomBattlesConfig = self.__randomBattlesConfig.replace(diff[Configs.RANDOM_BATTLES_CONFIG.value])

    def __updateModeSelectorConfig(self, diff):
        self.__modeSelectorConfig = self.__modeSelectorConfig.replace(diff[Configs.MODE_SELECTOR_CONFIG.value])


def serverSettingsChangeListener(*configKeys):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(self, diff):
            if any((configKey in diff for configKey in configKeys)):
                func(self, diff)

        return wrapper

    return decorator
