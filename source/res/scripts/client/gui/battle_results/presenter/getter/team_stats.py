# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/team_stats.py
from collections import namedtuple
import typing
from frameworks.wulf import Array
from gui.battle_results.presenter.getter.common import Field
from gui.impl.gen.view_models.views.lobby.postbattle.player_details_model import PlayerDetailsModel
from gui.impl.gen.view_models.views.lobby.postbattle.stats_one_value_item import StatsOneValueItem
from gui.impl.gen.view_models.views.lobby.postbattle.stats_two_values_item import StatsTwoValuesItem
from shared_utils import CONST_CONTAINER
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo

class _TeamStatsBlockIndexes(CONST_CONTAINER):
    EXP_SEGMENTS = 0
    SHOTS = 1
    DAMAGE_DEALT = 2
    HITS_RECEIVED = 3
    EXPLOSION_HITS = 4
    BLOCKED_DAMAGE = 5
    DAMAGE_TO_ALLIES = 6
    SPOTTED = 7
    DAMAGE_TO_ENEMIES = 8
    DAMAGE_ASSISTED = 9
    DAMAGE_ASSISTED_SELF = 10
    STUN_DURATION = 11
    DAMAGE_ASSISTED_STUN = 12
    DAMAGE_ASSISTED_STUN_SELF = 13
    STUN = 14
    BASE_CAPTURE = 15
    MILEAGE = 16
    START_TIME = 17
    BATTLE_DURATION = 18
    LIFETIME = 19


TeamStats = namedtuple('teamStats', ('expSegments', 'shots', 'damageDealt', 'hitsReceived', 'other', 'time'))
TeamStatsExpSegments = namedtuple('TeamStatsExpSegments', ('total', 'attack', 'assist', 'role'))
TeamStatsShots = namedtuple('shots', ('shots', 'hitsPiercings', 'explosionHits'))
TeamStatsDamageDealt = namedtuple('damageDealt', ('damageDealt', 'sniperDamageDealt'))
TeamStatsHitsReceived = namedtuple('hitsReceived', ('directHitsReceived', 'piercingsReceived', 'noDamageHitsReceived'))
TeamStatsOther = namedtuple('other', ('explosionHitsReceived', 'damageBlockedByArmor', 'damageToAllies', 'spotted', 'damageToEnemies', 'damageAssisted', 'damageAssistedSelf', 'stunDuration', 'damageAssistedStun', 'damageAssistedStunSelf', 'stunNum', 'baseCapture', 'mileage'))
TeamStatsTime = namedtuple('time', ('arenaCreateTime', 'battleDuration', 'playerLifetime'))

class TeamStatsField(Field):
    __slots__ = ('__blockIdx', '__valueType', '__hasTooltip', '__model')

    def __init__(self, stringID, blockIdx, valueType, model, hasTooltip=False):
        super(TeamStatsField, self).__init__(stringID)
        self.__blockIdx = blockIdx
        self.__valueType = valueType
        self.__model = model
        self.__hasTooltip = hasTooltip

    @property
    def valueType(self):
        return self.__valueType

    @property
    def blockIdx(self):
        return self.__blockIdx

    @property
    def model(self):
        return self.__model

    @property
    def hasTooltip(self):
        return self.__hasTooltip

    def _getRecord(self, *args):
        pass

    def _getValue(self, *args):
        pass


class TeamStatsOneValueField(TeamStatsField):
    __slots__ = ('_valueID',)

    def __init__(self, stringID, blockIdx, valueType, model, valueID, hasTooltip=False):
        super(TeamStatsOneValueField, self).__init__(stringID, blockIdx, valueType, model, hasTooltip)
        self._valueID = valueID

    def getFieldValues(self, playerInfo, results):
        return getattr(playerInfo, self._valueID)


class TeamStatsMultiValueField(TeamStatsField):
    __slots__ = ('_valueIDs',)

    def __init__(self, stringID, blockIdx, valueType, model, valueIDs, hasTooltip=False):
        super(TeamStatsMultiValueField, self).__init__(stringID, blockIdx, valueType, model, hasTooltip)
        self._valueIDs = valueIDs

    def getFieldValues(self, playerInfo, results):
        record = Array()
        record.reserve(2)
        for valueID in self._valueIDs:
            record.addNumber(getattr(playerInfo, valueID))

        return record


class TeamStatsArenaCreateTimeField(TeamStatsField):
    __slots__ = ()

    def getFieldValues(self, playerInfo, results):
        return results['common']['arenaCreateTime']


class TeamStatsBattleDurationField(TeamStatsField):
    __slots__ = ()

    def getFieldValues(self, playerInfo, results):
        return results['common']['duration']


class TeamStatsLifetimeField(TeamStatsField):
    __slots__ = ()

    def getFieldValues(self, playerInfo, results):
        return results['vehicles'][playerInfo.vehicleID][0]['lifeTime']


def getTeamStats():
    return TeamStats(expSegments=_getExpSegments(), shots=_getTeamStatsShots(), damageDealt=_getTeamStatsDamageDealt(), hitsReceived=_getTeamStatsHitsReceived(), other=_getTeamStatsOther(), time=_getTeamStatsTime())


def _getExpSegments():
    return TeamStatsExpSegments(total=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.EXP_SEGMENTS, stringID='xpTotal', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='xp'), attack=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.EXP_SEGMENTS, stringID='xpForAttack', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='xpForAttack', hasTooltip=True), assist=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.EXP_SEGMENTS, stringID='xpForAssist', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='xpForAssist', hasTooltip=True), role=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.EXP_SEGMENTS, stringID='xpOther', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='xpOther', hasTooltip=True))


def _getTeamStatsShots():
    return TeamStatsShots(shots=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.SHOTS, stringID='shots', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='shots'), hitsPiercings=TeamStatsMultiValueField(blockIdx=_TeamStatsBlockIndexes.SHOTS, stringID='hitsPiercings', valueType=PlayerDetailsModel.INT_ARRAY, model=StatsTwoValuesItem, valueIDs=('directHits', 'piercings')), explosionHits=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.SHOTS, stringID='explosionHits', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='explosionHits'))


def _getTeamStatsDamageDealt():
    return TeamStatsDamageDealt(damageDealt=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_DEALT, stringID='damageDealt', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageDealt'), sniperDamageDealt=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_DEALT, stringID='sniperDamageDealt', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='sniperDamageDealt'))


def _getTeamStatsHitsReceived():
    return TeamStatsHitsReceived(directHitsReceived=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.HITS_RECEIVED, stringID='directHitsReceived', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='directHitsReceived'), piercingsReceived=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.HITS_RECEIVED, stringID='piercingsReceived', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='piercingsReceived'), noDamageHitsReceived=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.HITS_RECEIVED, stringID='noDamageDirectHitsReceived', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='noDamageDirectHitsReceived'))


def _getTeamStatsOther():
    return TeamStatsOther(explosionHitsReceived=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.EXPLOSION_HITS, stringID='explosionHitsReceived', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='explosionHitsReceived'), damageBlockedByArmor=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.BLOCKED_DAMAGE, stringID='damageBlockedByArmor', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageBlockedByArmor'), damageToAllies=TeamStatsMultiValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_TO_ALLIES, stringID='damageToAllies', valueType=PlayerDetailsModel.INT_ARRAY, model=StatsTwoValuesItem, valueIDs=('tkills', 'tdamageDealt')), spotted=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.SPOTTED, stringID='spotted', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='spotted'), damageToEnemies=TeamStatsMultiValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_TO_ENEMIES, stringID='damageToEnemies', valueType=PlayerDetailsModel.INT_ARRAY, model=StatsTwoValuesItem, valueIDs=('damaged', 'kills')), damageAssisted=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_ASSISTED, stringID='damageAssisted', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageAssisted'), damageAssistedSelf=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_ASSISTED_SELF, stringID='damageAssistedSelf', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageAssisted'), stunDuration=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.STUN_DURATION, stringID='stunDuration', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='stunDuration'), damageAssistedStun=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_ASSISTED_STUN, stringID='damageAssistedStun', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageAssistedStun'), damageAssistedStunSelf=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.DAMAGE_ASSISTED_STUN_SELF, stringID='damageAssistedStunSelf', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='damageAssistedStun'), stunNum=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.STUN, stringID='stunNum', valueType=PlayerDetailsModel.INTEGER, model=StatsOneValueItem, valueID='stunNum'), baseCapture=TeamStatsMultiValueField(blockIdx=_TeamStatsBlockIndexes.BASE_CAPTURE, stringID='baseCapture', valueType=PlayerDetailsModel.INT_ARRAY, model=StatsTwoValuesItem, valueIDs=('capturePoints', 'droppedCapturePoints')), mileage=TeamStatsOneValueField(blockIdx=_TeamStatsBlockIndexes.MILEAGE, stringID='mileage', valueType=PlayerDetailsModel.MILEAGE, model=StatsOneValueItem, valueID='mileage'))


def _getTeamStatsTime():
    return TeamStatsTime(arenaCreateTime=TeamStatsArenaCreateTimeField(blockIdx=_TeamStatsBlockIndexes.START_TIME, stringID='arenaCreateTime', valueType=PlayerDetailsModel.LOCAL_TIME, model=StatsOneValueItem), battleDuration=TeamStatsBattleDurationField(blockIdx=_TeamStatsBlockIndexes.BATTLE_DURATION, stringID='duration', valueType=PlayerDetailsModel.BATTLE_DURATION, model=StatsOneValueItem), playerLifetime=TeamStatsLifetimeField(blockIdx=_TeamStatsBlockIndexes.LIFETIME, stringID='lifetime', valueType=PlayerDetailsModel.LIFETIME, model=StatsOneValueItem))
