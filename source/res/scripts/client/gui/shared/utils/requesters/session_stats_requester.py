# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/session_stats_requester.py
from collections import namedtuple
import BigWorld
from adisp import async
from constants import ARENA_BONUS_TYPE
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IRandomAccountStats, IRandomVehStats, ISessionStatsRequester
ValueWithDelta = namedtuple('ValueWithDelta', ['value', 'delta'])
RatioValue = namedtuple('RatioValue', ['ratio', 'dealt', 'received'])
CreditsDetails = namedtuple('CreditsDetails', ['base',
 'battlePayments',
 'noPenalty',
 'boosters',
 'event',
 'friendlyFireCompensation',
 'squadBonus',
 'aogasFactor',
 'friendlyFirePenalty',
 'autoRepair',
 'autoLoad',
 'autoEquip'])
CrystalDetails = namedtuple('CrystalDetails', ['base',
 'achievement',
 'event',
 'autoEquip'])

class _StatKind(object):
    DAY_STAT = 'dayStat'
    VEHICLE_DAY_STAT = 'vehDayStat'


class BaseStats(object):

    def __init__(self, data):
        super(BaseStats, self).__init__()
        self.data = data

    @property
    def battleCnt(self):
        return self.data.get('battle_cnt', {}).get('value', None)

    @property
    def incomeCredits(self):
        return self.data.get('income_credits', {}).get('value', None)

    @property
    def xp(self):
        return self.data.get('xp', {}).get('value', None)

    @property
    def incomeCrystal(self):
        return self.data.get('income_crystal', {}).get('value', None)

    @property
    def freeXP(self):
        return self.data.get('freeXP', {}).get('value', None)

    @property
    def averageXp(self):
        return ValueWithDelta(self.data.get('average_xp', {}).get('value', (None, None))[0], self.data.get('average_xp', {}).get('diff', None))

    @property
    def ratioDamage(self):
        ratio, dealt, received = self.data.get('ratio_damage', {}).get('value', (None, None, None))
        return ValueWithDelta(value=RatioValue(ratio, dealt, received), delta=self.data.get('ratio_damage', {}).get('diff', None))

    @property
    def helpDamage(self):
        return ValueWithDelta(value=self.data.get('help_damage', {}).get('value', (None, None))[0], delta=self.data.get('help_damage', {}).get('diff', None))

    @property
    def ratioKill(self):
        ratio, dealt, received = self.data.get('ratio_kill', {}).get('value', (None, None, None))
        return ValueWithDelta(value=RatioValue(ratio, dealt, received), delta=self.data.get('ratio_kill', {}).get('diff', None))

    @property
    def averageDamage(self):
        return ValueWithDelta(value=self.data.get('average_damage', {}).get('value', (None, None))[0], delta=self.data.get('average_damage', {}).get('diff', None))

    @property
    def blockedDamage(self):
        return ValueWithDelta(value=self.data.get('blocked_damage', {}).get('value', (None, None))[0], delta=self.data.get('blocked_damage', {}).get('diff', None))

    @property
    def winRatio(self):
        return ValueWithDelta(value=self.data.get('winner_ratio', {}).get('value', (None, None))[0], delta=None)


class BaseAccountStats(BaseStats):

    @property
    def netCredits(self):
        return self.data.get('net_credits', {}).get('value', None)

    @property
    def creditsDetails(self):
        replayCreditsData = self.data.get('credits_replay', {})
        data = self.data.get('credits_to_draw', {}).get('value', 0)
        creditsToDraw = data if data is not None else 0
        data = self.data.get('achievement_credits', {}).get('value', 0)
        achievementCredits = data if data is not None else 0
        return CreditsDetails(base=replayCreditsData.get('originalCredits', 0) + self._sumRecords(replayCreditsData, 'appliedPremiumCreditsFactor') - creditsToDraw - achievementCredits, noPenalty=self.data.get('achievement_credits', {}).get('value', 0), boosters=replayCreditsData.get('boosterCredits', 0) + replayCreditsData.get('boosterCreditsFactor100', 0), event=self._sumRecords(replayCreditsData, 'eventCreditsList_', 'eventCreditsFactor1000List_'), battlePayments=replayCreditsData.get('orderCreditsFactor100', 0), friendlyFirePenalty=replayCreditsData.get('originalCreditsPenalty', 0) + replayCreditsData.get('originalCreditsContributionOut', 0) + replayCreditsData.get('originalCreditsPenaltySquad', 0) + replayCreditsData.get('originalCreditsContributionOutSquad', 0), friendlyFireCompensation=replayCreditsData.get('originalCreditsContributionIn', 0) + replayCreditsData.get('originalCreditsContributionInSquad', 0), aogasFactor=replayCreditsData.get('aogasFactor10', 0), autoRepair=self.data.get('auto_repair_cost_credits', {}).get('value', 0), autoLoad=self.data.get('auto_load_cost_credits', {}).get('value', 0), autoEquip=self.data.get('auto_equip_cost_credits', {}).get('value', 0), squadBonus=replayCreditsData.get('originalPremSquadCredits', 0) + replayCreditsData.get('premSquadCreditsFactor100', 0) + replayCreditsData.get('originalCreditsToDrawSquad', 0))

    @property
    def netCrystal(self):
        return self.data.get('net_crystal', {}).get('value', None)

    @property
    def crystalDetails(self):
        replayCrystalData = self.data.get('crystals_replay', {})
        return CrystalDetails(base=replayCrystalData.get('originalCrystal', 0), achievement=self._sumRecords(replayCrystalData, 'eventCrystalList_'), event=0, autoEquip=self.data.get('auto_equip_cost_crystal', {}).get('value', 0))

    @staticmethod
    def _sumRecords(data, *startWithStrings):
        result = 0
        for key, val in data.iteritems():
            if key.startswith(startWithStrings):
                result += val

        return result


class BaseVehicleStats(BaseStats):
    pass


class RandomAccountStats(BaseAccountStats, IRandomAccountStats):

    @property
    def wtr(self):
        return ValueWithDelta(value=self.data.get('wtr', {}).get('value', None), delta=self.data.get('wtr', {}).get('diff', None))


class RandomVehStats(BaseVehicleStats, IRandomVehStats):

    @property
    def wtr(self):
        return ValueWithDelta(value=self.data.get('wtr', {}).get('value', None), delta=self.data.get('wtr', {}).get('diff', None))


_ARENA_TYPE_TO_RETURN_CLASS_MAP = {ARENA_BONUS_TYPE.REGULAR: (RandomAccountStats, RandomVehStats)}

class SessionStatsRequester(AbstractSyncDataRequester, ISessionStatsRequester):

    def getAccountStats(self, arenaType):
        return self.__getStats(arenaType, statsKind=_StatKind.DAY_STAT, isVehStats=False)

    def getVehiclesStats(self, arenaType, vehId):
        return self.__getStats(arenaType, statsKind=_StatKind.VEHICLE_DAY_STAT, isVehStats=True, vehicleId=vehId)

    def getStatsVehList(self, arenaType):
        statsDictData = self.getCacheValue('sessionStats', {})
        return statsDictData.get(arenaType, {}).get(_StatKind.VEHICLE_DAY_STAT, {}).keys()

    def getAccountWtr(self):
        return self.getCacheValue('wtr', {}).get('wtr_general', None)

    @staticmethod
    def resetStats():
        BigWorld.player().sessionStats.resetStats()

    @async
    def _requestCache(self, callback):
        BigWorld.player().sessionStats.getCache(lambda res_id, value: self._response(res_id, value, callback))

    def __getStats(self, arenaType, statsKind=_StatKind.DAY_STAT, isVehStats=False, vehicleId=None):
        statsDictData = self.getCacheValue('sessionStats', {})
        statsDictData = statsDictData.get(arenaType, {})
        wtr = self.__getWtr(statsDictData, arenaType, statsKind, vehicleId)
        outputDict = statsDictData.get(statsKind, {}).copy()
        if statsKind is _StatKind.VEHICLE_DAY_STAT:
            outputDict = outputDict.get(vehicleId, {})
        outputDict.update(wtr)
        mapTupleIndex = 1 if isVehStats else 0
        return _ARENA_TYPE_TO_RETURN_CLASS_MAP[arenaType][mapTupleIndex](outputDict)

    @staticmethod
    def __getWtr(data, arenaType, statsKind, vehicleId=None):
        if arenaType == ARENA_BONUS_TYPE.REGULAR:
            buff = data.get('wtrDayStat', {'value': None,
             'diff': None})
            if statsKind == _StatKind.VEHICLE_DAY_STAT:
                buff = buff.get('wtrForVeh', {}).get(vehicleId, {'value': None,
                 'diff': None})
            return {'wtr': {'value': buff.get('value', None),
                     'diff': buff.get('diff', None)}}
        else:
            return {}
