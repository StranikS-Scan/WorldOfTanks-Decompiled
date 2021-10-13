# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/items.py
from collections import namedtuple
from datetime import datetime
from gui.impl import backport
from helpers import time_utils, int2roman
from messenger.ext import passCensor
from shared_utils import makeTupleByDict
from predefined_hosts import g_preDefinedHosts
from debug_utils import LOG_WARNING
from gui.clans import formatters as clans_fmts
from gui.clans.settings import MAX_CLAN_MEMBERS_COUNT, CLAN_INVITE_STATES_SORT_RULES, CLAN_INVITE_STATES
from debug_utils import LOG_ERROR
from helpers.time_utils import getTimeDeltaTillNow, ONE_DAY

def _getTimestamp(datetimeValue):
    return time_utils.getTimestampFromUTC(datetimeValue.timetuple())


def _toPercents(value):
    return 100 * value if value else value


def _getEfficiency(dividend, delimiter):
    return float(dividend) / delimiter


_defDateTime = datetime.fromtimestamp(0)

def formatField(getter, dummy=None, formatter=None):
    return str(getter(doFmt=True, dummy=dummy, formatter=formatter))


def isValueAvailable(getter):
    return getter(checkAvailability=True)


class FieldsCheckerMixin(object):

    def __init__(self, *args, **kwargs):
        super(FieldsCheckerMixin, self).__init__()
        self.__class = self.__class__
        if hasattr(self, '_fields'):
            self._invalidFields = set((arg for arg in self._fields if arg not in kwargs))
        else:
            self._invalidFields = set()

    def isFieldValid(self, fieldName):
        return fieldName not in self._invalidFields

    def isValid(self):
        return not set(self._getCriticalFields()) & self._invalidFields

    def update(self, *args, **kwargs):
        obj = self._replace(**kwargs)
        obj._invalidFields = self._invalidFields
        return obj

    def _getCriticalFields(self):
        LOG_ERROR('Method must be override!', '_getCriticalFields', self.__class__)
        return tuple()


def fmtUnavailableValue(fields=tuple(), dummy=clans_fmts.DUMMY_UNAVAILABLE_DATA):

    def decorator(func):

        def wrapper(self, *args, **kwargs):

            def _isAvailable(fields):
                for field in fields:
                    if not self.isFieldValid(field):
                        return False

                return True

            checkAvailability = kwargs.pop('checkAvailability', False)
            if checkAvailability:
                return _isAvailable(fields)
            doFmt = kwargs.get('doFmt', False)
            placeholder = kwargs.get('dummy', dummy) or dummy
            f = kwargs.get('formatter', None)
            if doFmt and not _isAvailable(fields):
                return placeholder
            try:
                value = func(self)
            except ValueError:
                value = None

            if value is None:
                return placeholder
            else:
                return f(value) if f is not None else value

        return wrapper

    return decorator


def fmtNullValue(nullValue=0, dummy=clans_fmts.DUMMY_NULL_DATA):

    def decorator(func):

        def wrapper(*args, **kwargs):
            checkAvailability = kwargs.get('checkAvailability', False)
            doFmt = kwargs.get('doFmt', False)
            value = func(*args, **kwargs)
            if not checkAvailability and doFmt and value == nullValue:
                value = dummy
            return value

        return wrapper

    return decorator


def fmtZeroDivisionValue(defValue=0, dummy=clans_fmts.DUMMY_NULL_DATA):

    def decorator(func):

        def wrapper(*args, **kwargs):
            try:
                value = func(*args, **kwargs)
            except ZeroDivisionError:
                if kwargs.get('doFmt', False):
                    return kwargs.get('dummy', dummy) or dummy
                return defValue

            return value

        return wrapper

    return decorator


def _formatString(value):
    return clans_fmts.DUMMY_UNAVAILABLE_DATA if not value else passCensor(value)


def fmtDelegat(path, dummy=clans_fmts.DUMMY_UNAVAILABLE_DATA):

    def decorator(func):

        def wrapper(self, *args, **kwargs):

            def _getGetter(path):
                return reduce(getattr, path.split('.'), self)

            checkAvailability = kwargs.pop('checkAvailability', False)
            doFmt = kwargs.pop('doFmt', False)
            placeholder = kwargs.pop('dummy', dummy) or dummy
            f = kwargs.pop('formatter', None)
            if checkAvailability:
                return _getGetter(path)(checkAvailability=checkAvailability)
            else:
                return _getGetter(path)(doFmt=doFmt, dummy=placeholder, formatter=f) if doFmt else func(self, *args, **kwargs)

        return wrapper

    return decorator


def formatter(formatter=None):

    def decorator(func):

        def wrapper(self, *args, **kwargs):
            doFmt = kwargs.get('doFmt', False)
            fmt = kwargs.get('formatter', None) or formatter
            value = func(self)
            if doFmt and fmt:
                value = fmt(value)
            return value

        return wrapper

    return decorator


def simpleFormatter(formatter=None):

    def decorator(func):

        def wrapper(self):
            value = func(self)
            if formatter and value is not None:
                value = formatter(value)
            return value

        return wrapper

    return decorator


_ClanExtInfoData = namedtuple('ClanExtInfoData', ['name',
 'tag',
 'motto',
 'members_count',
 'created_at',
 'leader_id',
 'treasury',
 'accepts_join_requests',
 'clan_id'])
_ClanExtInfoData.__new__.__defaults__ = ('',
 '',
 '',
 0,
 _defDateTime,
 0,
 0,
 False,
 0)
_ClanExtInfoDataCritical = ('name', 'tag', 'members_count', 'clan_id')

class ClanExtInfoData(_ClanExtInfoData, FieldsCheckerMixin):

    def getDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('name',))
    def getClanName(self):
        return passCensor(self.name)

    @fmtUnavailableValue(fields=('name', 'tag'))
    def getFullName(self):
        return '%s %s' % (clans_fmts.getClanAbbrevString(self.getTag()), self.getClanName()) if self.tag else ''

    @fmtUnavailableValue(fields=('tag',))
    def getTag(self):
        return passCensor(self.tag)

    @fmtUnavailableValue(fields=('motto',))
    def getMotto(self):
        return passCensor(self.motto)

    @fmtUnavailableValue(fields=('members_count',))
    def getMembersCount(self):
        return self.members_count

    @fmtUnavailableValue(fields=('leader_id',))
    def getLeaderDbID(self):
        return self.leader_id

    @fmtUnavailableValue(fields=('treasury',))
    def getTreasuryValue(self):
        return self.treasury

    def isOpened(self):
        return self.accepts_join_requests

    @fmtUnavailableValue(fields=('members_count',))
    def getFreePlaces(self):
        return MAX_CLAN_MEMBERS_COUNT - self.members_count

    def hasFreePlaces(self):
        return self.getFreePlaces() > 0

    @fmtUnavailableValue(fields=('created_at',))
    def getCreatedAt(self):
        return _getTimestamp(self.created_at) if self.created_at else 0

    def _getCriticalFields(self):
        return _ClanExtInfoDataCritical


_ClanRatingsData = namedtuple('ClanRatingsData', ['clan_id',
 'efficiency',
 'battles_count_avg',
 'wins_ratio_avg',
 'xp_avg',
 'gm_elo_rating_6',
 'gm_elo_rating_8',
 'gm_elo_rating_10',
 'gm_elo_rating_6_rank',
 'gm_elo_rating_8_rank',
 'gm_elo_rating_10_rank',
 'fb_elo_rating_8',
 'fb_elo_rating_10',
 'fb_battles_count_10_28d',
 'fs_battles_count_10_28d',
 'gm_battles_count_28d',
 'fs_battles_count_28d',
 'fb_battles_count_28d'])
_ClanRatingsData.__new__.__defaults__ = tuple([0] * len(_ClanRatingsData._fields))
_ClanRatingsDataCriticalFields = ('efficiency', 'battles_count_avg', 'wins_ratio_avg', 'xp_avg')

class ClanRatingsData(_ClanRatingsData, FieldsCheckerMixin):

    def getClanDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('efficiency',))
    def getEfficiency(self):
        return self.efficiency

    @fmtUnavailableValue(fields=('fb_elo_rating_10',))
    def getEloRating10(self):
        return self.fb_elo_rating_10

    @fmtUnavailableValue(fields=('fb_elo_rating_8',))
    def getEloRating8(self):
        return self.fb_elo_rating_8

    @fmtUnavailableValue(fields=('gm_battles_count_28d',))
    def getGlobalMapBattlesFor28Days(self):
        return self.gm_battles_count_28d

    @fmtUnavailableValue(fields=('gm_elo_rating_10',))
    def getGlobalMapEloRating10(self):
        return self.gm_elo_rating_10

    @fmtUnavailableValue(fields=('gm_elo_rating_8',))
    def getGlobalMapEloRating8(self):
        return self.gm_elo_rating_8

    @fmtUnavailableValue(fields=('gm_elo_rating_6',))
    def getGlobalMapEloRating6(self):
        return self.gm_elo_rating_6

    @fmtUnavailableValue(fields=('battles_count_avg',))
    def getBattlesCountAvg(self):
        return self.battles_count_avg

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('wins_ratio_avg', 'battles_count_avg'))
    def getWinsRatioAvg(self):
        if self.battles_count_avg > 0:
            return self.wins_ratio_avg
        raise ZeroDivisionError()

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('xp_avg', 'battles_count_avg'))
    def getBattlesPerformanceAvg(self):
        if self.battles_count_avg > 0:
            return self.xp_avg
        raise ZeroDivisionError()

    @fmtUnavailableValue(fields=('gm_elo_rating_10_rank',))
    def getGlobalMapEloRatingRank10(self):
        return self.gm_elo_rating_10_rank

    @fmtUnavailableValue(fields=('gm_elo_rating_8_rank',))
    def getGlobalMapEloRatingRank8(self):
        return self.gm_elo_rating_8_rank

    @fmtUnavailableValue(fields=('gm_elo_rating_6_rank',))
    def getGlobalMapEloRatingRank6(self):
        return self.gm_elo_rating_6_rank

    def isActive(self):
        return self.gm_battles_count_28d > 0

    def isGlobalMapOutdated(self):
        return self.gm_battles_count_28d <= 0

    def isBattlesOutdated(self):
        return self.fb_battles_count_10_28d <= 0

    def isSortiesOutdated(self):
        return self.fs_battles_count_10_28d <= 0

    def hasFortRating(self):
        for gtr in (self.getEloRating10, self.getEloRating8):
            if not isValueAvailable(gtr):
                return False

        return self.fb_elo_rating_10 != 1000 or self.fb_elo_rating_8 != 1000

    def _getCriticalFields(self):
        return _ClanRatingsDataCriticalFields


_ClanGlobalMapStatsData = namedtuple('ClanGlobalMapStatsData', ['battles_lost',
 'influence_points',
 'provinces_captured',
 'battles_played',
 'battles_won',
 'battles_played_on_6_level',
 'battles_won_on_6_level',
 'battles_played_on_8_level',
 'battles_won_on_8_level',
 'battles_played_on_10_level',
 'battles_won_on_10_level',
 'provinces_count'])
_ClanGlobalMapStatsData.__new__.__defaults__ = tuple([0] * len(_ClanGlobalMapStatsData._fields))

class ClanGlobalMapStatsData(_ClanGlobalMapStatsData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('battles_played', 'provinces_captured'))
    def hasGlobalMap(self):
        return self.battles_played > 0 or self.provinces_captured > 0

    @fmtUnavailableValue(fields=('battles_played',))
    def getBattlesCount(self):
        return self.battles_played

    @fmtUnavailableValue(fields=('battles_won',))
    def getWinsCount(self):
        return self.battles_won

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battles_won', 'battles_played'))
    def getWinsEfficiency(self):
        return _getEfficiency(self.battles_won, self.battles_played)

    @fmtUnavailableValue(fields=('battles_lost',))
    def getLoosesCount(self):
        return self.battles_lost

    @fmtUnavailableValue(fields=('influence_points',))
    def getInfluencePointsCount(self):
        return self.influence_points

    @fmtUnavailableValue(fields=('provinces_captured',))
    def getCapturedProvincesCount(self):
        return self.provinces_captured

    @fmtUnavailableValue(fields=('provinces_count',))
    def getCurrentProvincesCount(self):
        return self.provinces_count

    @fmtUnavailableValue(fields=('battles_played_on_6_level',))
    def getBattles6LevelCount(self):
        return self.battles_played_on_6_level

    @fmtUnavailableValue(fields=('battles_won_on_6_level',))
    def getWins6LevelCount(self):
        return self.battles_won_on_6_level

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battles_won_on_6_level', 'battles_played_on_6_level'))
    def getWins6LevelEfficiency(self):
        return _getEfficiency(self.battles_won_on_6_level, self.battles_played_on_6_level)

    @fmtUnavailableValue(fields=('battles_played_on_8_level',))
    def getBattles8LevelCount(self):
        return self.battles_played_on_8_level

    @fmtUnavailableValue(fields=('battles_won_on_8_level',))
    def getWins8LevelCount(self):
        return self.battles_won_on_8_level

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battles_won_on_8_level', 'battles_played_on_8_level'))
    def getWins8LevelEfficiency(self):
        return _getEfficiency(self.battles_won_on_8_level, self.battles_played_on_8_level)

    @fmtUnavailableValue(fields=('battles_played_on_10_level',))
    def getBattles10LevelCount(self):
        return self.battles_played_on_10_level

    @fmtUnavailableValue(fields=('battles_won_on_10_level',))
    def getWins10LevelCount(self):
        return self.battles_won_on_10_level

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battles_won_on_10_level', 'battles_played_on_10_level'))
    def getWins10LevelEfficiency(self):
        return _getEfficiency(self.battles_won_on_10_level, self.battles_played_on_10_level)


Building = namedtuple('Building', 'type direction level position')
_ClanStrongholdInfoData = namedtuple('ClanStrongholdData', ['buildings',
 'defence_attack_count',
 'defence_success_attack_count',
 'defence_battles_count',
 'defence_capture_enemy_building_total_count',
 'defence_combat_wins',
 'defence_defence_count',
 'defence_success_defence_count',
 'defence_enemy_base_capture_count',
 'defence_loss_own_building_total_count',
 'defence_resource_capture_count',
 'defence_resource_loss_count',
 'sortie_absolute_battles_count',
 'sortie_battles_count',
 'sortie_champion_battles_count',
 'sortie_fort_resource_in_middle',
 'sortie_fort_resource_in_champion',
 'sortie_fort_resource_in_absolute',
 'sortie_middle_battles_count',
 'sortie_wins',
 'sortie_losses',
 'level',
 'total_resource_amount',
 'defence_defence_efficiency',
 'defence_attack_efficiency',
 'fb_battles_count_8',
 'fb_battles_count_10',
 'defence_mode_is_activated',
 'defence_hour'])
_ClanStrongholdInfoData.__new__.__defaults__ = ([],) + tuple([0] * (len(_ClanStrongholdInfoData._fields) - 1))
DefClanStrongholdInfoData = _ClanStrongholdInfoData([], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None)

class ClanStrongholdInfoData(_ClanStrongholdInfoData, FieldsCheckerMixin):

    def hasFort(self):
        return self.level > 0

    def getBuildings(self):
        result = []
        for b in self.buildings:
            try:
                result.append(makeTupleByDict(Building, b))
            except Exception:
                LOG_WARNING('There is error while collecting Buildings list', self.buildings)

        return result

    @fmtUnavailableValue(fields=('level',))
    def getLevel(self):
        return self.level

    @fmtUnavailableValue(fields=('sortie_battles_count',))
    def getSortieBattlesCount(self):
        return self.sortie_battles_count

    @fmtUnavailableValue(fields=('sortie_wins',))
    def getSortieWinsCount(self):
        return self.sortie_wins

    @fmtUnavailableValue(fields=('sortie_losses',))
    def getSortieLossesCount(self):
        return self.sortie_losses

    @fmtUnavailableValue(fields=('sortie_middle_battles_count',))
    def getSortieMiddleBattlesCount(self):
        return self.sortie_middle_battles_count

    @fmtUnavailableValue(fields=('sortie_champion_battles_count',))
    def getSortieChampionBattlesCount(self):
        return self.sortie_champion_battles_count

    @fmtUnavailableValue(fields=('sortie_absolute_battles_count',))
    def getSortieAbsoluteBattlesCount(self):
        return self.sortie_absolute_battles_count

    @fmtUnavailableValue(fields=('sortie_fort_resource_in_middle',))
    def getSortieMiddleResourcesCount(self):
        return self.sortie_fort_resource_in_middle

    @fmtUnavailableValue(fields=('sortie_fort_resource_in_champion',))
    def getSortieChampionResourcesCount(self):
        return self.sortie_fort_resource_in_champion

    @fmtUnavailableValue(fields=('sortie_fort_resource_in_absolute',))
    def getSortieAbsoluteResourcesCount(self):
        return self.sortie_fort_resource_in_absolute

    @fmtUnavailableValue(fields=('defence_battles_count',))
    def getDefenceBattlesCount(self):
        return self.defence_battles_count

    @fmtUnavailableValue(fields=('defence_combat_wins',))
    def getDefenceCombatsCount(self):
        return self.defence_combat_wins

    @fmtUnavailableValue(fields=('defence_resource_capture_count',))
    def getDefenceCapturedResourcesCount(self):
        return self.defence_resource_capture_count

    @fmtUnavailableValue(fields=('defence_resource_loss_count',))
    def getDefenceLostResourcesCount(self):
        return self.defence_resource_loss_count

    @fmtUnavailableValue(fields=('defence_enemy_base_capture_count',))
    def getDefenceEnemyBaseCapturesPointsCount(self):
        return self.defence_enemy_base_capture_count

    @fmtUnavailableValue(fields=('defence_capture_enemy_building_total_count',))
    def getDefenceCapturedEnemyBuildingsCount(self):
        return self.defence_capture_enemy_building_total_count

    @fmtUnavailableValue(fields=('defence_loss_own_building_total_count',))
    def getDefenceLostOwnBuildingsCount(self):
        return self.defence_loss_own_building_total_count

    @fmtUnavailableValue(fields=('defence_attack_count',))
    def getAttacksCount(self):
        return self.defence_attack_count

    @fmtUnavailableValue(fields=('defence_success_attack_count',))
    def getSuccessAttacksCount(self):
        return self.defence_success_attack_count

    @fmtUnavailableValue(fields=('defence_defence_count',))
    def getDefencesCount(self):
        return self.defence_defence_count

    @fmtUnavailableValue(fields=('defence_hour',))
    def getDefenceHour(self):
        return self.defence_hour

    @fmtUnavailableValue(fields=('defence_success_defence_count',))
    def getSuccessDefencesCount(self):
        return self.defence_success_defence_count

    @fmtUnavailableValue(fields=('fb_battles_count_8',))
    def getFbBattlesCount8(self):
        return self.fb_battles_count_8

    @fmtUnavailableValue(fields=('fb_battles_count_10',))
    def getFbBattlesCount10(self):
        return self.fb_battles_count_10

    def isDefenceModeActivated(self):
        return self.defence_mode_is_activated


BuildingStats = namedtuple('BuildingStats', 'position type level hp storage')
BuildingStats.__new__.__defaults__ = (0, 0, 0, 0, 0)
_StrongholdStatisticsData = namedtuple('ClanStrongholdData', ['elo_10',
 'elo_8',
 'elo_6',
 'sorties_in_28_days',
 'fort_battles_in_28_days',
 'stronghold_level',
 'leagues'])
_StrongholdStatisticsData.__new__.__defaults__ = (None,
 None,
 None,
 None,
 None,
 None,
 [])

class StrongholdStatisticsData(_StrongholdStatisticsData, FieldsCheckerMixin):

    @simpleFormatter(backport.getIntegralFormat)
    def getElo10(self):
        return self.elo_10

    @simpleFormatter(backport.getIntegralFormat)
    def getElo8(self):
        return self.elo_8

    @simpleFormatter(backport.getIntegralFormat)
    def getElo6(self):
        return self.elo_6

    @simpleFormatter(backport.getIntegralFormat)
    def getSortiesIn28Days(self):
        return self.sorties_in_28_days

    @simpleFormatter(backport.getIntegralFormat)
    def getFortBattlesIn28Days(self):
        return self.fort_battles_in_28_days

    @simpleFormatter(int2roman)
    def getStrongholdLevel(self):
        return self.stronghold_level

    def getLeagues(self):
        return self.leagues

    def hasSorties(self):
        return self.sorties_in_28_days and self.sorties_in_28_days > 0

    def hasFortBattles(self):
        return self.fort_battles_in_28_days and self.fort_battles_in_28_days > 0


_AccountClanData = namedtuple('_AccountClanData', ('account_id', 'joined_at', 'clan_id', 'role_bw_flag', 'role_name', 'in_clan_cooldown_till'))
_AccountClanData.__new__.__defaults__ = (0,
 _defDateTime,
 0,
 0,
 '',
 _defDateTime)

class AccountClanData(_AccountClanData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('account_id',))
    def getDbID(self):
        return self.account_id

    def getClanCooldownTill(self):
        return time_utils.getTimestampFromUTC(self.in_clan_cooldown_till.timetuple())


_ClanMemberData = namedtuple('_ClanMemberData', 'account_id role_bw_flag clan_id joined_at ratings')
_ClanMemberData.__new__.__defaults__ = (0,
 0,
 0,
 _defDateTime,
 None)

class ClanMemberData(_ClanMemberData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('account_id',))
    def getDbID(self):
        return self.account_id

    @fmtUnavailableValue(fields=('role_bw_flag',))
    def getRole(self):
        return self.role_bw_flag

    @fmtUnavailableValue(fields=('role_bw_flag',))
    def getRoleString(self):
        return clans_fmts.getClanRoleString(self.role_bw_flag)

    @fmtUnavailableValue(fields=('role_bw_flag',))
    def getRoleIcon(self):
        return clans_fmts.getClanRoleIcon(self.role_bw_flag)

    def getClanDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('joined_at',))
    def getJoiningTime(self):
        return time_utils.getTimestampFromUTC(self.joined_at.timetuple())

    @fmtUnavailableValue(fields=('joined_at',))
    def getDaysInClan(self):
        return getTimeDeltaTillNow(self.getJoiningTime()) / ONE_DAY

    @fmtDelegat(path='ratings.getGlobalRating')
    def getGlobalRating(self):
        return self.ratings.getGlobalRating()

    @fmtDelegat(path='ratings.getBattlesCount')
    def getBattlesCount(self):
        return self.ratings.getBattlesCount()

    @fmtDelegat(path='ratings.getBattlesPerformanceAvg')
    def getBattlesPerformanceAvg(self):
        return self.ratings.getBattlesPerformanceAvg()

    @fmtDelegat(path='ratings.getXp')
    def getXp(self):
        return self.ratings.getXp()

    @fmtDelegat(path='ratings.getBattleXpAvg')
    def getBattleXpAvg(self):
        return self.ratings.getBattleXpAvg()


_AccountClanRatingsData = namedtuple('_AccountClanRatingsData', ['account_id',
 'global_rating',
 'battle_avg_xp',
 'battles_count',
 'battle_avg_performance',
 'xp_amount'])
_AccountClanRatingsData.__new__.__defaults__ = (0, 0, 0, 0, 0, 0)

class AccountClanRatingsData(_AccountClanRatingsData, FieldsCheckerMixin):

    def getAccountDbID(self):
        return self.account_id

    @fmtUnavailableValue(fields=('global_rating',))
    def getGlobalRating(self):
        return self.global_rating

    @fmtUnavailableValue(fields=('battles_count',))
    def getBattlesCount(self):
        return self.battles_count

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battle_avg_xp', 'battles_count'))
    def getBattleXpAvg(self):
        if self.battles_count > 0:
            return self.battle_avg_xp
        raise ZeroDivisionError()

    @fmtZeroDivisionValue()
    @fmtUnavailableValue(fields=('battle_avg_performance', 'battles_count'))
    def getBattlesPerformanceAvg(self):
        if self.battles_count > 0:
            return _toPercents(self.battle_avg_performance)
        raise ZeroDivisionError()

    @fmtUnavailableValue(fields=('xp_amount',))
    def getXp(self):
        return self.xp_amount


_ClanProvinceData = namedtuple('_ClanProvinceData', ['front_name',
 'province_id',
 'revenue',
 'hq_connected',
 'prime_time',
 'periphery',
 'game_map',
 'turns_owned',
 'province_id_localized',
 'front_name_localized',
 'frontInfo',
 'pillage_cooldown',
 'pillage_end_datetime',
 'arena_id'])
_ClanProvinceData.__new__.__defaults__ = ('',
 0,
 0,
 False,
 0,
 0,
 '',
 0,
 '',
 None,
 None,
 None,
 None,
 None)

class ClanProvinceData(_ClanProvinceData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('front_name_localized',))
    def getFrontLocalizedName(self):
        return self.front_name_localized

    @fmtDelegat(path='frontInfo.getMaxVehicleLevel')
    def getFrontLevel(self):
        return self.frontInfo.getMaxVehicleLevel()

    @fmtUnavailableValue(fields=('province_id_localized',))
    def getProvinceLocalizedName(self):
        return self.province_id_localized

    @fmtUnavailableValue(fields=('revenue',))
    def getRevenue(self):
        return self.revenue

    def isHqConnected(self):
        return self.hq_connected

    def getPrimeTime(self):
        return self.prime_time

    @fmtUnavailableValue(fields=('prime_time',))
    def getUserPrimeTime(self):
        return backport.getShortTimeFormat(self.prime_time.hour * time_utils.ONE_HOUR + self.prime_time.minute * time_utils.ONE_MINUTE)

    def getPeripheryID(self):
        return self.periphery

    @fmtUnavailableValue(fields=('periphery',))
    def getPeripheryName(self):
        periphery = g_preDefinedHosts.periphery(self.periphery)
        return periphery.name if periphery is not None else ''

    @fmtUnavailableValue(fields=('game_map',))
    def getArenaName(self):
        return self.game_map

    @fmtUnavailableValue(fields=('arena_id',))
    def getArenaId(self):
        return self.arena_id

    @fmtUnavailableValue(fields=('turns_owned',))
    def getTurnsOwned(self):
        return self.turns_owned

    @fmtUnavailableValue(fields=('pillage_cooldown',))
    def getPillageCooldown(self):
        return self.pillage_cooldown

    @fmtUnavailableValue(fields=('pillage_end_datetime',))
    def getPillageEndDatetime(self):
        return _getTimestamp(self.pillage_end_datetime) if self.pillage_end_datetime else 0


_GlobalMapFrontInfoData = namedtuple('_GlobalMapFrontInfoData', ['front_name', 'min_vehicle_level', 'max_vehicle_level'])
_GlobalMapFrontInfoData.__new__.__defaults__ = tuple([0] * len(_ClanRatingsData._fields))

class GlobalMapFrontInfoData(_GlobalMapFrontInfoData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('front_name',))
    def getFrontName(self):
        return self.front_name

    @fmtUnavailableValue(fields=('min_vehicle_level',))
    def getMinVehicleLevel(self):
        return self.min_vehicle_level

    @fmtUnavailableValue(fields=('max_vehicle_level',))
    def getMaxVehicleLevel(self):
        return self.max_vehicle_level


_ClanSearchData = namedtuple('_ClanSearchData', ['name',
 'tag',
 'motto',
 'clan_id',
 'leader_id',
 'members_count',
 'created_at',
 'accepts_join_requests',
 'treasury',
 'clan_ratings_data'])
_ClanSearchData.__new__.__defaults__ = ('',
 '',
 '',
 0,
 0,
 0,
 _defDateTime,
 False,
 0,
 ClanRatingsData())
_ClanSearchDataCriticalFields = ('tag', 'name', 'members_count')

class ClanSearchData(_ClanSearchData, FieldsCheckerMixin):

    def getClanDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('name',))
    def getClanName(self):
        return passCensor(self.name)

    @fmtUnavailableValue(fields=('tag',))
    def getClanAbbrev(self):
        return passCensor(self.tag)

    @fmtUnavailableValue(fields=('motto',))
    def getClanMotto(self):
        return passCensor(self.motto)

    @fmtUnavailableValue(fields=('leader_id',))
    def getLeaderDbID(self):
        return self.leader_id

    @fmtUnavailableValue(fields=('tag', 'name'))
    def getClanFullName(self):
        return clans_fmts.getClanFullName(self.getClanName(), self.getClanAbbrev())

    @fmtUnavailableValue(fields=('members_count',))
    def getMembersCount(self):
        return self.members_count

    @fmtUnavailableValue(fields=('created_at',))
    def getCreationDate(self):
        return time_utils.getTimestampFromUTC(self.created_at.timetuple())

    def canAcceptsJoinRequests(self):
        return self.accepts_join_requests

    @fmtDelegat(path='clan_ratings_data.getEfficiency')
    def getPersonalRating(self):
        return self.clan_ratings_data.getEfficiency()

    @fmtDelegat(path='clan_ratings_data.getBattlesCountAvg')
    def getBattlesCount(self):
        return self.clan_ratings_data.getBattlesCountAvg()

    @fmtDelegat(path='clan_ratings_data.getWinsRatioAvg')
    def getBattleXpAvg(self):
        return self.clan_ratings_data.getWinsRatioAvg()

    @fmtDelegat(path='clan_ratings_data.getBattlesPerformanceAvg')
    def getBattlesPerformanceAvg(self):
        return self.clan_ratings_data.getBattlesPerformanceAvg()

    def isClanActive(self):
        return self.clan_ratings_data.isActive()

    def isValid(self):
        return super(ClanSearchData, self).isValid() and self.clan_ratings_data.isValid()

    def _getCriticalFields(self):
        return _ClanSearchDataCriticalFields


_ClanInviteData = namedtuple('_ClanInviteData', ['account_id',
 'clan_id',
 'comment',
 'created_at',
 'id',
 'sender_id',
 'status',
 'updated_at',
 'status_changer_id'])
_ClanInviteData.__new__.__defaults__ = (0,
 0,
 '',
 _defDateTime,
 0,
 0,
 '',
 _defDateTime,
 0)

class ClanInviteData(_ClanInviteData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('id',))
    def getDbID(self):
        return self.id

    @fmtUnavailableValue(fields=('account_id',))
    def getAccountDbID(self):
        return self.account_id

    @fmtUnavailableValue(fields=('sender_id',))
    def getSenderDbID(self):
        return self.sender_id

    @fmtUnavailableValue(fields=('status_changer_id',))
    def getChangerDbID(self):
        return self.status_changer_id

    @fmtUnavailableValue(fields=('status_changer_id',))
    def getChangedBy(self):
        return self.status_changer_id

    @fmtUnavailableValue(fields=('clan_id',))
    def getClanDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('comment',))
    def getComment(self):
        return passCensor(str(self.comment))

    @fmtUnavailableValue(fields=('status',))
    def getStatus(self):
        return self.status

    @fmtUnavailableValue(fields=('created_at',))
    def getCreatedAt(self):
        return time_utils.getTimestampFromUTC(self.created_at.timetuple())

    @fmtUnavailableValue(fields=('updated_at',))
    def getUpdatedAt(self):
        return time_utils.getTimestampFromUTC(self.updated_at.timetuple())

    def isActive(self):
        return CLAN_INVITE_STATES.isActive(self.status)

    @classmethod
    def fromClanCreateInviteData(cls, data):
        return ClanInviteData(id=data.getDbID(), clan_id=data.getClanDbID(), account_id=data.getAccountDbID())

    @classmethod
    def fromClanInviteItem(cls, data):
        return ClanInviteData(id=data.getInviteId(), clan_id=data.getClanId(), account_id=data.getAccountDbID())

    @classmethod
    def fromClanApplicationItem(cls, data, clanDbID):
        return ClanInviteData(id=data.getApplicationID(), clan_id=clanDbID, account_id=data.getAccountID())


_ClanCreateInviteData = namedtuple('_ClanCreateInviteData', ['clan_id', 'id', 'account_id'])
_ClanCreateInviteData.__new__.__defaults__ = (0, 0, 0)

class ClanCreateInviteData(_ClanCreateInviteData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('id',))
    def getDbID(self):
        return self.id

    @fmtUnavailableValue(fields=('account_id',))
    def getAccountDbID(self):
        return self.account_id

    @fmtUnavailableValue(fields=('clan_id',))
    def getClanDbID(self):
        return self.clan_id


_ClanADInviteData = namedtuple('_ClanADInviteData', ['id',
 'transaction_id',
 'clan_id',
 'account_id'])
_ClanADInviteData.__new__.__defaults__ = (0, 0, 0, 0)

class ClanADInviteData(_ClanADInviteData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('id',))
    def getDbID(self):
        return self.id

    @fmtUnavailableValue(fields=('transaction_id',))
    def getTransactionID(self):
        return self.transaction_id

    @fmtUnavailableValue(fields=('clan_id',))
    def getClanDbID(self):
        return self.clan_id

    @fmtUnavailableValue(fields=('account_id',))
    def getAccountDbID(self):
        return self.account_id


class ClanInviteWrapper(object):

    def __init__(self, invite, account, accountName, sender, senderName, changerName):
        super(ClanInviteWrapper, self).__init__()
        self.__invite = invite or ClanInviteData()
        self.__account = account or AccountClanRatingsData()
        self.__sender = sender or AccountClanRatingsData()
        self.__accountName = accountName
        self.__senderName = senderName
        self.__changerName = changerName
        self.__statusCode = None
        return

    @property
    def status(self):
        return CLAN_INVITE_STATES_SORT_RULES.get(self.__invite.status, 0)

    @property
    def message(self):
        return self.__invite.comment

    @property
    def sent(self):
        return self.getCreatedAt()

    @property
    def createdAt(self):
        return self.getCreatedAt()

    @property
    def updatedAt(self):
        return self.getUpdatedAt()

    @property
    def userName(self):
        return self.getAccountName()

    @property
    def personalRating(self):
        return self.getPersonalRating()

    @property
    def battlesCount(self):
        return self.getBattlesCount()

    @property
    def awgExp(self):
        return self.getBattlesPerformanceAvg()

    @property
    def wins(self):
        return self.getBattleXpAvg()

    @property
    def invite(self):
        return self.__invite

    @property
    def account(self):
        return self.__account

    @property
    def sender(self):
        return self.__sender

    def getDbID(self):
        return self.__invite.getDbID()

    @fmtDelegat(path='invite.getClanDbID')
    def getClanDbID(self):
        return self.__invite.getClanDbID()

    @fmtDelegat(path='invite.getCreatedAt')
    def getCreatedAt(self):
        return self.__invite.getCreatedAt()

    @fmtDelegat(path='invite.getUpdatedAt')
    def getUpdatedAt(self):
        return self.__invite.getUpdatedAt()

    @fmtDelegat(path='invite.getAccountDbID')
    def getAccountDbID(self):
        return self.__invite.getAccountDbID()

    @fmtDelegat(path='invite.getSenderDbID')
    def getSenderDbID(self):
        return self.__invite.getSenderDbID()

    @fmtDelegat(path='invite.getChangedBy')
    def getChangedBy(self):
        return self.__invite.getChangedBy()

    @fmtDelegat(path='invite.getChangerDbID')
    def getChangerDbID(self):
        return self.__invite.getChangerDbID()

    @formatter(formatter=_formatString)
    def getAccountName(self):
        return self.__accountName

    @formatter(formatter=_formatString)
    def getSenderName(self):
        return self.__senderName

    @formatter(formatter=_formatString)
    def getChangerName(self):
        return self.__changerName

    @fmtDelegat(path='account.getGlobalRating')
    def getPersonalRating(self):
        return self.__account.getGlobalRating()

    @fmtDelegat(path='account.getBattlesCount')
    def getBattlesCount(self):
        return self.__account.getBattlesCount()

    @fmtDelegat(path='account.getBattleXpAvg')
    def getBattleXpAvg(self):
        return self.__account.getBattleXpAvg()

    @fmtDelegat(path='account.getBattlesPerformanceAvg')
    def getBattlesPerformanceAvg(self):
        return self.__account.getBattlesPerformanceAvg()

    @fmtDelegat(path='invite.getStatus')
    def getStatus(self):
        return self.__invite.getStatus()

    @fmtDelegat(path='invite.getComment')
    def getComment(self):
        return self.__invite.getComment()

    def getStatusCode(self):
        return self.__statusCode

    def setInvite(self, invite):
        self.__invite = invite

    def setSender(self, sender):
        self.__sender = sender

    def setSenderName(self, name):
        self.__senderName = name

    def setChangerName(self, name):
        self.__changerName = name

    def setUserName(self, name):
        self.__accountName = name

    def setStatusCode(self, code):
        self.__statusCode = code


class ClanPersonalInviteWrapper(object):

    def __init__(self, invite, clanInfo, clanRatings, senderName):
        super(ClanPersonalInviteWrapper, self).__init__()
        self.__invite = invite or ClanInviteData()
        self.__clanRatings = clanRatings or ClanRatingsData()
        self.__clanInfo = clanInfo or ClanExtInfoData()
        self.__senderName = senderName

    @property
    def status(self):
        return CLAN_INVITE_STATES_SORT_RULES.get(self.__invite.status, 0)

    @property
    def message(self):
        return self.__invite.comment

    @property
    def createdAt(self):
        return self.getCreatedAt()

    @property
    def sent(self):
        return self.getCreatedAt()

    @property
    def updatedAt(self):
        return self.getUpdatedAt()

    @property
    def clanName(self):
        return self.getClanFullName()

    @property
    def personalRating(self):
        return self.getPersonalRating()

    @property
    def battlesCount(self):
        return self.getBattlesCount()

    @property
    def wins(self):
        return self.getBattleXpAvg()

    @property
    def awgExp(self):
        return self.getBattlesPerformanceAvg()

    @property
    def invite(self):
        return self.__invite

    @property
    def clanInfo(self):
        return self.__clanInfo

    @property
    def clanRatings(self):
        return self.__clanRatings

    def getDbID(self):
        return self.__invite.getDbID()

    @fmtDelegat(path='invite.getChangerDbID')
    def getChangerDbID(self):
        return self.__invite.getChangerDbID()

    @fmtDelegat(path='invite.getChangedBy')
    def getChangedBy(self):
        return self.__invite.getChangedBy()

    @fmtDelegat(path='invite.getStatus')
    def getStatus(self):
        return self.__invite.getStatus()

    @fmtDelegat(path='invite.getCreatedAt')
    def getCreatedAt(self):
        return self.__invite.getCreatedAt()

    @fmtDelegat(path='invite.getUpdatedAt')
    def getUpdatedAt(self):
        return self.__invite.getUpdatedAt()

    @fmtDelegat(path='invite.getComment')
    def getComment(self):
        return self.__invite.getComment()

    @fmtDelegat(path='clanInfo.getFullName')
    def getClanFullName(self):
        return self.__clanInfo.getFullName()

    @fmtDelegat(path='clanInfo.getClanName')
    def getClanName(self):
        return self.__clanInfo.getClanName()

    @fmtDelegat(path='clanInfo.getMotto')
    def getClanMotto(self):
        return self.__clanInfo.getMotto()

    @fmtDelegat(path='clanInfo.getTag')
    def getClanAbbrev(self):
        return self.__clanInfo.getTag()

    def getClanDbID(self):
        return self.__clanInfo.getDbID()

    def isClanActive(self):
        return self.__clanRatings.isActive()

    @fmtDelegat(path='clanRatings.getEfficiency')
    def getPersonalRating(self):
        return self.__clanRatings.getEfficiency()

    @fmtDelegat(path='clanRatings.getBattlesCountAvg')
    def getBattlesCount(self):
        return self.__clanRatings.getBattlesCountAvg()

    @fmtDelegat(path='clanRatings.getWinsRatioAvg')
    def getBattleXpAvg(self):
        return self.__clanRatings.getWinsRatioAvg()

    @fmtDelegat(path='clanRatings.getBattlesPerformanceAvg')
    def getBattlesPerformanceAvg(self):
        return self.__clanRatings.getBattlesPerformanceAvg()

    @fmtDelegat(path='clanInfo.getLeaderDbID')
    def getLeaderDbID(self):
        return self.__clanInfo.getLeaderDbID()

    @formatter(formatter=_formatString)
    def getSenderName(self):
        return self.__senderName

    def setInvite(self, invite):
        self.__invite = invite

    def setSenderName(self, name):
        self.__senderName = name


class ClanCommonData(object):

    def __init__(self, proxy):
        self._proxy = proxy

    def getDbID(self):
        return self._proxy.getClanDbID()

    @fmtDelegat(path='_proxy.getClanName')
    def getName(self):
        return self._proxy.getClanName()

    @fmtDelegat(path='_proxy.getClanAbbrev')
    def getAbbrev(self):
        return self._proxy.getClanAbbrev()

    @fmtDelegat(path='_proxy.getClanMotto')
    def getMotto(self):
        return self._proxy.getClanMotto()

    @fmtDelegat(path='_proxy.getClanFullName')
    def getFullName(self):
        return self._proxy.getClanFullName()

    @fmtDelegat(path='_proxy.getPersonalRating')
    def getRating(self):
        return self._proxy.getPersonalRating()

    @fmtDelegat(path='_proxy.getBattlesCount')
    def getBattlesCount(self):
        return self._proxy.getBattlesCount()

    @fmtDelegat(path='_proxy.getBattleXpAvg')
    def getWinsRatio(self):
        return self._proxy.getBattleXpAvg()

    def isActive(self):
        return self._proxy.isClanActive()

    @fmtDelegat(path='_proxy.getBattlesPerformanceAvg')
    def getAvgExp(self):
        return self._proxy.getBattlesPerformanceAvg()

    @fmtDelegat(path='_proxy.getLeaderDbID')
    def getLeaderDbID(self):
        return self._proxy.getLeaderDbID()

    @classmethod
    def fromClanSearchData(cls, data):
        return ClanCommonData(data)

    @classmethod
    def fromClanPersonalInviteWrapper(cls, data):
        return ClanCommonData(data)


_ClanFavouriteAttrs = namedtuple('_ClanFavouriteAttrs', ['clan_id',
 'favorite_arena_6',
 'favorite_arena_8',
 'favorite_arena_10',
 'favorite_primetime',
 'favorite_arenas'])
_ClanFavouriteAttrs.__new__.__defaults__ = (0, None, None, None, 0, None)

class ClanFavouriteAttrs(_ClanFavouriteAttrs, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('favorite_arena_6',))
    def getFavouriteArena6(self):
        return self.favorite_arena_6

    @fmtUnavailableValue(fields=('favorite_arena_8',))
    def getFavouriteArena8(self):
        return self.favorite_arena_8

    @fmtUnavailableValue(fields=('favorite_arena_10',))
    def getFavouriteArena10(self):
        return self.favorite_arena_10

    @fmtUnavailableValue(fields=('favorite_primetime',))
    def getFavoritePrimetime(self):
        return self.favorite_primetime


_HofAttrs = namedtuple('_HofAttrs', ['status', 'errors'])
_HofAttrs.__new__.__defaults__ = (None, {})

class HofAttrs(_HofAttrs, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('status',))
    def getStatus(self):
        return self.status

    @fmtUnavailableValue(fields=('errors',))
    def getErrors(self):
        return self.errors.keys()


_YhaVideoData = namedtuple('_YhaVideoAttrs', ('available_at', 'video'))
_YhaVideoData.__new__.__defaults__ = (0, '')

class YhaVideoData(_YhaVideoData, FieldsCheckerMixin):

    @fmtUnavailableValue(fields=('available_at',), dummy=0)
    def getAvailableAt(self):
        return self.available_at

    @fmtUnavailableValue(fields=('video',), dummy='')
    def getVideo(self):
        return self.video
